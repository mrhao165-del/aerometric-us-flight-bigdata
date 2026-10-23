"""Read-only artifact adapter and loopback static server for the AeroMetric demo.

No pipeline modules are imported. Build creates a new external, immutable bundle.
Serve never reads production datasets, starts Spark, or downloads assets.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import json
import math
from pathlib import Path
import shutil
import sys
import urllib.request
import uuid

REPO = Path(__file__).resolve().parents[1]
HERE = Path(__file__).resolve().parent
DEFAULT_BUNDLE = Path("D:/Flight_Audit_Exports/DASHBOARD_DEMO/stitch_v3")
ANALYSIS_RUN = "t014_analysis_2016_2024_v4"
KPI_RUN = "kpi_run_2016_2024_v1"
PLOTLY_VERSION = "4.1.1"
ASSETS = {
    "plotly.min.js": f"https://cdn.plot.ly/plotly-{PLOTLY_VERSION}.min.js",
    "PLOTLY-LICENSE.txt": f"https://raw.githubusercontent.com/plotly/plotly.js/v{PLOTLY_VERSION}/LICENSE",
    "Inter.ttf": "https://raw.githubusercontent.com/google/fonts/main/ofl/inter/Inter%5Bopsz,wght%5D.ttf",
    "INTER-OFL.txt": "https://raw.githubusercontent.com/google/fonts/main/ofl/inter/OFL.txt",
    "JetBrainsMono.ttf": "https://raw.githubusercontent.com/google/fonts/main/ofl/jetbrainsmono/JetBrainsMono%5Bwght%5D.ttf",
    "JETBRAINS-OFL.txt": "https://raw.githubusercontent.com/google/fonts/main/ofl/jetbrainsmono/OFL.txt",
}


def load_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))


def sha256(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def require(condition, message):
    if not condition:
        raise ValueError(message)


def clean_json(value):
    if isinstance(value, dict):
        return {str(k): clean_json(v) for k, v in value.items()}
    if isinstance(value, (tuple, list)):
        return [clean_json(v) for v in value]
    if isinstance(value, float) and not math.isfinite(value):
        return None
    return value


def write_json(path, data):
    Path(path).write_text(json.dumps(clean_json(data), ensure_ascii=False,
                                     separators=(",", ":"), allow_nan=False), encoding="utf-8")


def classify_cohort(group):
    parts = dict(token.split("=", 1) for token in group.split(";"))
    year = parts["source_year"]
    if "ORIGIN" in parts and "DEST" in parts:
        return "route-year", year, parts["ORIGIN"] + ">" + parts["DEST"]
    for field, family in [("ORIGIN", "origin-year"), ("DEST", "dest-year"),
                          ("OP_CARRIER", "carrier-year"), ("YEAR_MONTH", "year-month")]:
        if field in parts:
            return family, year, parts[field]
    require(parts.get("cohort") == "all", f"Unknown cohort: {group}")
    return "year", year, "all"


def sample_status(n, family):
    threshold = {"carrier-year": 1000, "origin-year": 365,
                 "dest-year": 365, "route-year": 100}.get(family)
    if threshold is None:
        return "NOT_APPLICABLE"
    return "SUPPRESSED" if n < threshold else "LOW_SAMPLE_CAUTION" if n < 3 * threshold else "SUFFICIENT"


def collect_data(repo=REPO):
    """Select published values and metadata, never calculate CORE KPIs."""
    import pyarrow.parquet as pq

    ar = repo / "data/analytics/runs" / ANALYSIS_RUN
    kr = repo / "data/kpi/runs" / KPI_RUN
    km = repo / "data/metadata/kpi" / KPI_RUN
    am = load_json(ar / "analytics_run_manifest.json")
    manifest = load_json(km / "run_manifest.json")
    receipt = load_json(km / "execution_receipt.json")
    require(am["run_id"] == ANALYSIS_RUN and am["source_kpi_run_id"] == KPI_RUN, "Wrong Analytics baseline")
    require(manifest["run_id"] == KPI_RUN and receipt["status"] == "SUCCESS", "KPI run not successful")
    require(sha256(km / "run_manifest.json") == receipt["manifest_sha256"], "KPI receipt/manifest hash mismatch")
    require(am["status"] == "PUBLISHED_CONTROLLED", "Analytics run not published")
    sources, tables, schemas = [], {}, {}

    def attest(path, expected=None):
        digest = sha256(path)
        require(expected is None or digest == expected, f"Source hash mismatch: {path}")
        sources.append({"path": path.relative_to(repo).as_posix(), "bytes": path.stat().st_size, "sha256": digest})

    attest(ar / "analytics_run_manifest.json")
    attest(km / "run_manifest.json")
    attest(km / "execution_receipt.json")
    for t in am["tables"]:
        name = t["table_name"]
        p = ar / "tables" / t["parquet_file"]
        attest(p, t["parquet_sha256"])
        attest(ar / "tables" / t["csv_file"], t["csv_sha256"])
        pf = pq.ParquetFile(p)
        require(pf.metadata.num_rows == t["rows"], f"Table row mismatch: {name}")
        tables[name] = pf.read().to_pylist()
        schemas[name] = [{"name": f.name, "type": str(f.type)} for f in pf.schema_arrow]
    require(len(tables) == 12, "Expected 12 official tables")
    for filename, key in [("RESULTS_REGISTER.json", "results_register_sha256"),
                          ("CHART_INVENTORY.json", "chart_inventory_sha256")]:
        attest(ar / filename, am[key])
    register = load_json(ar / "RESULTS_REGISTER.json")
    charts = load_json(ar / "CHART_INVENTORY.json")["figures"]
    require(len(register["results"]) == 20 and len(charts) == 16, "Expected 20 RES and 16 charts")
    for c in charts:
        for suffix in ["png", "svg"]:
            p = ar / "charts" / c[f"{suffix}_file"]
            attest(p)
            require(p.stat().st_size == c[f"{suffix}_bytes"], f"Chart size mismatch: {p.name}")

    origins = {(str(r["year"]), r["origin_airport"]) for r in tables["rq03_origin_airports"]}
    dests = {(str(r["year"]), r["dest_airport"]) for r in tables["rq03_dest_airports"]}
    routes = set()
    for r in tables["rq03_directed_routes"]:
        for direction in ["fwd", "ret"]:
            routes.add((str(r["year"]), r[f"route_{direction}"].replace(" -> ", ">")))
    streams = {
        "carrier-year": {"KPI-01", "KPI-02", "KPI-03", "KPI-04", "KPI-05", "KPI-07/TAXI_OUT"},
        "origin-year": {"KPI-01", "KPI-04", "KPI-05", "KPI-07/TAXI_OUT"},
        "dest-year": {"KPI-01", "KPI-02", "KPI-03", "KPI-07/TAXI_IN"},
        "route-year": {"KPI-01", "KPI-02", "KPI-03"},
    }
    metrics = {}
    require(manifest["file_count"] == 9 and manifest["output_total_rows"] == 684180, "Wrong KPI inventory")
    for f in manifest["files"]:
        path = kr / f["relative_path"]
        attest(path, f["sha256"])
        cols = ["kpi_id", "submetric", "group_dimensions", "value", "count_records",
                "count_metric_valid", "excluded_count", "metric_valid_rate", "min_n_status",
                "source_coverage_status", "unit_status"]
        for batch in pq.ParquetFile(path).iter_batches(columns=cols, batch_size=65536):
            for r in batch.to_pylist():
                family, year, entity = classify_cohort(r["group_dimensions"])
                stream = r["kpi_id"] + ("/" + r["submetric"] if r["submetric"] else "")
                if family == "year-month":
                    if stream not in {"KPI-01", "KPI-02", "KPI-03", "KPI-04", "KPI-05"}:
                        continue
                elif family != "year":
                    if stream not in streams[family]:
                        continue
                    allowed = {"origin-year": origins, "dest-year": dests, "route-year": routes}.get(family)
                    if allowed is not None and (year, entity) not in allowed:
                        continue
                n = r["count_metric_valid"]
                require(r["count_records"] == n + r["excluded_count"], "DC-12 metadata mismatch")
                require(r["min_n_status"] == sample_status(n, family), "min-N metadata mismatch")
                require(year != "2024" or r["source_coverage_status"] == "PARTIAL", "2024 must be PARTIAL")
                key = "|".join((family, year, entity, stream))
                require(key not in metrics, f"Duplicate metric key: {key}")
                metrics[key] = {"value": r["value"], "records": r["count_records"], "n": n,
                                "excluded": r["excluded_count"], "valid_rate": r["metric_valid_rate"],
                                "status": r["min_n_status"], "coverage": r["source_coverage_status"],
                                "unit_status": r["unit_status"]}

    def metric(y, stream):
        return metrics[f"year|{y}|all|{stream}"]

    for r in tables["rq02_annual_delays"]:
        y = r["year"]
        for field, stream, scale in [("arr_delay_ge_15_rate_pct", "KPI-02", 100),
                                      ("dep_delay_ge_15_rate_pct", "KPI-04", 100),
                                      ("arr_delay_signed_mean_min", "KPI-03", 1),
                                      ("dep_delay_signed_mean_min", "KPI-05", 1),
                                      ("arr_delay_p50_min", "KPI-06/P50", 1),
                                      ("arr_delay_p90_min", "KPI-06/P90", 1)]:
            require(math.isclose(r[field], metric(y, stream)["value"] * scale, abs_tol=1e-9), f"Annual/KPI disagreement: {field}")
    require(sum(r["annual_volume"] for r in tables["rq01_annual_volume"]) == 54674003, "Wrong dataset count")
    for r in tables['rq01_monthly_volume']:
        key=f"year-month|{r['year']}|{r['year_month']}|KPI-01"
        require(r['monthly_volume']==metrics[key]['value'], f"Monthly volume/KPI disagreement: {key}")
    for r in tables['rq02_monthly_delays']:
        for field,stream in [('arr_delay_ge_15_rate_pct','KPI-02'),('dep_delay_ge_15_rate_pct','KPI-04')]:
            key=f"year-month|{r['year']}|{r['year_month']}|{stream}"
            require(math.isclose(r[field],metrics[key]['value']*100,abs_tol=1e-9), f"Monthly rate/KPI disagreement: {key}")
    return {"version": 1, "analysis_run": ANALYSIS_RUN, "kpi_run": KPI_RUN,
            "kpi_version": manifest["kpi_version"], "quality_version": manifest["quality_version"],
            "tables": tables, "schemas": schemas, "metrics": metrics,
            "results": register["results"], "charts": charts}, sources


def fetch_asset(url, destination):
    request = urllib.request.Request(url, headers={"User-Agent": "AeroMetric-offline-demo/1.0"})
    with urllib.request.urlopen(request, timeout=45) as response:
        content = response.read(15 * 1024 * 1024 + 1)
    require(0 < len(content) <= 15 * 1024 * 1024, "Unexpected asset size")
    destination.write_bytes(content)


def build(bundle=DEFAULT_BUNDLE, repo=REPO):
    bundle = Path(bundle).resolve()
    require(not bundle.is_relative_to(repo.resolve()), "Generated bundles must be outside the repository")
    require(not bundle.exists(), f"Immutable bundle already exists: {bundle}. Use --bundle with a new directory.")
    data, sources = collect_data(repo)
    bundle.parent.mkdir(parents=True, exist_ok=True)
    stage = bundle.parent / (".building_" + bundle.name + "_" + uuid.uuid4().hex[:8])
    stage.mkdir()
    shutil.copytree(HERE / "web", stage, dirs_exist_ok=True)
    (stage / "data").mkdir()
    write_json(stage / "data/dashboard.json", data)
    ar = repo / "data/analytics/runs" / ANALYSIS_RUN
    shutil.copytree(ar / "charts", stage / "charts")
    shutil.copytree(ar / "tables", stage / "downloads")
    for name in ["RESULTS_REGISTER.json", "CHART_INVENTORY.json"]:
        shutil.copy2(ar / name, stage / "downloads" / name)
    handoff = Path("D:/Flight_Audit_Exports/DASHBOARD_DISCOVERY_HANDOFF/DASHBOARD_PROJECT_HANDOFF.md")
    if handoff.exists():
        shutil.copy2(handoff, stage / "downloads/DASHBOARD_PROJECT_HANDOFF.md")
    vendor = stage / "vendor"
    vendor.mkdir()
    assets = []
    for name, url in ASSETS.items():
        print(f"Preparing offline asset: {name}", flush=True)
        fetch_asset(url, vendor / name)
        assets.append({"file": "vendor/" + name, "url": url, "sha256": sha256(vendor / name)})
    files = {p.relative_to(stage).as_posix(): {"sha256": sha256(p), "bytes": p.stat().st_size}
             for p in stage.rglob("*") if p.is_file()}
    write_json(stage / "bundle_manifest.json", {"bundle_version": 1, "created_utc": datetime.now(timezone.utc).isoformat(),
               "analysis_run": ANALYSIS_RUN, "kpi_run": KPI_RUN, "plotly_version": PLOTLY_VERSION,
               "sources": sources, "assets": assets, "files": files})
    stage.rename(bundle)
    print(f"BUILT: {bundle}")
    print(f"12 tables / 16 official charts / 20 RES / {len(data['metrics']):,} selected KPI rows")
    return bundle


def verify_bundle(bundle):
    bundle = Path(bundle).resolve()
    require(bundle.is_dir(), f"Bundle missing: {bundle}. Run build first.")
    m = load_json(bundle / "bundle_manifest.json")
    require(m.get("analysis_run") == ANALYSIS_RUN and m.get("kpi_run") == KPI_RUN, "Wrong bundle baseline")
    for name, item in m["files"].items():
        path = (bundle / name).resolve()
        require(path.is_relative_to(bundle) and path.is_file(), f"Unsafe/missing bundle path: {name}")
        require(sha256(path) == item["sha256"], f"Bundle modified: {name}. Create a new build.")
    return m


class DemoHandler(SimpleHTTPRequestHandler):
    # Windows registry may map .mjs to text/plain; module scripts require JS MIME.
    extensions_map = {**SimpleHTTPRequestHandler.extensions_map,
                      '.mjs': 'text/javascript', '.js': 'text/javascript',
                      '.ttf': 'font/ttf', '.svg': 'image/svg+xml'}

    def end_headers(self):
        self.send_header("Content-Security-Policy", "default-src 'self'; script-src 'self' 'unsafe-eval'; style-src 'self' 'unsafe-inline'; font-src 'self'; img-src 'self' data: blob:; connect-src 'self'; object-src 'none'; base-uri 'self'; frame-ancestors 'none'")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Cache-Control", "no-cache")
        super().end_headers()

    def list_directory(self, path):
        self.send_error(403, "Directory listing disabled")
        return None

    def translate_path(self, path):
        translated = Path(super().translate_path(path)).resolve()
        if not translated.is_relative_to(Path(self.directory).resolve()):
            return str(Path(self.directory) / ".blocked")
        return str(translated)


def serve(bundle, port):
    from functools import partial
    verify_bundle(bundle)
    try:
        server = ThreadingHTTPServer(("127.0.0.1", port), partial(DemoHandler, directory=str(Path(bundle).resolve())))
    except OSError as e:
        raise ValueError(f"Cannot listen on port {port}; use serve --port 8001. {e}") from e
    print(f"AeroMetric: http://127.0.0.1:{port}/", flush=True)
    print("Offline / read-only static bundle. Ctrl+C to stop.", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=["build", "serve", "verify"])
    parser.add_argument("--bundle", type=Path, default=DEFAULT_BUNDLE)
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args()
    try:
        if args.command == "build":
            build(args.bundle)
        elif args.command == "serve":
            serve(args.bundle, args.port)
        else:
            manifest = verify_bundle(args.bundle)
            print(f"VERIFIED: {len(manifest['files'])} bundle files")
    except (OSError, ValueError, KeyError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
