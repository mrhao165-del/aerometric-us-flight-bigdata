"""Dashboard-only contract tests. No pipeline execution or production writes."""
import importlib.util
import json
import os
from pathlib import Path
import tempfile
import threading
import urllib.request
import urllib.error
from functools import partial
import unittest

MODULE = Path(__file__).resolve().parents[1] / 'demo.py'
spec = importlib.util.spec_from_file_location('dashboard_demo', MODULE)
demo = importlib.util.module_from_spec(spec)
spec.loader.exec_module(demo)


class AdapterTests(unittest.TestCase):
    def test_six_families_are_distinct(self):
        cases = {
            'cohort=all;source_year=2019': ('year', '2019', 'all'),
            'YEAR_MONTH=2019-01;source_year=2019': ('year-month', '2019', '2019-01'),
            'OP_CARRIER=WN;source_year=2019': ('carrier-year', '2019', 'WN'),
            'ORIGIN=ORD;source_year=2019': ('origin-year', '2019', 'ORD'),
            'DEST=ATL;source_year=2019': ('dest-year', '2019', 'ATL'),
            'ORIGIN=LGA;DEST=ORD;source_year=2019': ('route-year', '2019', 'LGA>ORD'),
        }
        for group, expected in cases.items():
            self.assertEqual(demo.classify_cohort(group), expected)
        with self.assertRaises(ValueError):
            demo.classify_cohort('unknown=x;source_year=2019')

    def test_status_boundaries(self):
        for family, minimum in [('carrier-year',1000), ('origin-year',365), ('dest-year',365), ('route-year',100)]:
            self.assertEqual(demo.sample_status(minimum-1,family), 'SUPPRESSED')
            self.assertEqual(demo.sample_status(minimum,family), 'LOW_SAMPLE_CAUTION')
            self.assertEqual(demo.sample_status(3*minimum,family), 'SUFFICIENT')

    def test_bundle_modification_and_path_escape_fail_closed(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory)
            (root/'index.html').write_text('original',encoding='utf-8')
            manifest={'analysis_run':demo.ANALYSIS_RUN,'kpi_run':demo.KPI_RUN,
                      'files':{'index.html':{'sha256':demo.sha256(root/'index.html')}}}
            demo.write_json(root/'bundle_manifest.json',manifest)
            demo.verify_bundle(root)
            (root/'index.html').write_text('modified',encoding='utf-8')
            with self.assertRaisesRegex(ValueError,'Bundle modified'):
                demo.verify_bundle(root)
            manifest['files']={'../outside':{'sha256':'x'}}
            demo.write_json(root/'bundle_manifest.json',manifest)
            with self.assertRaisesRegex(ValueError,'Unsafe/missing'):
                demo.verify_bundle(root)

    def test_build_never_overwrites_existing_bundle_or_repository(self):
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaises(ValueError):
                demo.build(Path(directory))
        with self.assertRaises(ValueError):
            demo.build(demo.REPO/'dashboard'/'forbidden-output')


class PublishedDataTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        bundle=Path(os.environ.get('AEROMETRIC_TEST_BUNDLE', str(demo.DEFAULT_BUNDLE)))
        cls.manifest=demo.verify_bundle(bundle)
        cls.db=demo.load_json(bundle/'data/dashboard.json')

    def test_exact_published_inventory(self):
        self.assertEqual(len(self.db['tables']),12)
        self.assertEqual(len(self.db['results']),20)
        self.assertEqual(len(self.db['charts']),16)
        self.assertEqual(sum(r['annual_volume'] for r in self.db['tables']['rq01_annual_volume']),54674003)
        self.assertEqual(len(self.db['tables']['rq01_monthly_volume']),107)
        self.assertFalse(any(r['year_month']=='2024-03' for r in self.db['tables']['rq01_monthly_volume']))

    def test_signed_delay_and_quantiles_are_original_cohort_values(self):
        m=self.db['metrics']
        self.assertAlmostEqual(m['year|2020|all|KPI-03']['value'],-5.10783956,places=7)
        self.assertEqual(m['year|2020|all|KPI-06/P50']['value'],-11)
        self.assertEqual(m['year|2020|all|KPI-06/P90']['value'],14)
        self.assertTrue(all(v['coverage']=='PARTIAL' for k,v in m.items() if k.split('|')[1]=='2024'))

    def test_each_journey_measure_keeps_its_own_denominator(self):
        m=self.db['metrics']
        self.assertEqual(m['year|2020|all|KPI-08/CRS_ELAPSED_TIME']['n'],4312090)
        self.assertEqual(m['year|2020|all|KPI-08/ACTUAL_ELAPSED_TIME']['n'],4312091)

    def test_route_controls_restricted_to_published_2019_pairs(self):
        self.assertEqual({r['year'] for r in self.db['tables']['rq03_directed_routes']},{2019})
        keys=[k for k in self.db['metrics'] if k.startswith('route-year|')]
        self.assertEqual(len(keys),60)  # 10 pairs x 2 directions x 3 streams
        self.assertTrue(all(k.split('|')[1]=='2019' for k in keys))

    def test_http_module_mime_and_read_only_surface(self):
        bundle=Path(os.environ.get('AEROMETRIC_TEST_BUNDLE', str(demo.DEFAULT_BUNDLE)))
        class QuietHandler(demo.DemoHandler):
            def log_message(self,*args):
                pass
        server=demo.ThreadingHTTPServer(('127.0.0.1',0),partial(QuietHandler,directory=str(bundle)))
        thread=threading.Thread(target=server.serve_forever,daemon=True)
        thread.start()
        base=f'http://127.0.0.1:{server.server_port}/'
        try:
            for name,mime in [('','text/html'),('app.mjs','text/javascript'),('ui.mjs','text/javascript'),
                              ('core.mjs','text/javascript'),('styles.css','text/css'),
                              ('data/dashboard.json','application/json'),('vendor/Inter.ttf','font/ttf')]:
                with urllib.request.urlopen(base+name) as response:
                    self.assertEqual(response.status,200)
                    self.assertEqual(response.headers.get_content_type(),mime)
                    self.assertIn("connect-src 'self'",response.headers['Content-Security-Policy'])
                    self.assertGreater(len(response.read()),0)
            for route,code in [('downloads/',403),('../docs/04-execution/PROJECT_STATE.md',404)]:
                with self.assertRaises(urllib.error.HTTPError) as caught:
                    urllib.request.urlopen(base+route)
                self.assertEqual(caught.exception.code,code)
            with self.assertRaises(urllib.error.HTTPError) as caught:
                urllib.request.urlopen(urllib.request.Request(base,data=b'x',method='POST'))
            self.assertEqual(caught.exception.code,501)
        finally:
            server.shutdown();server.server_close();thread.join()


if __name__=='__main__':
    unittest.main()
