#!/usr/bin/env python3
"""Static consistency verifier for flight docs. No Spark/raw CSV access. Run from any cwd.
Checks documentary integrity only, NOT semantic truth of upstream data or actual pipeline operation.
"""
from pathlib import Path
from hashlib import sha256
from collections import Counter, defaultdict
import json, re, sys, zipfile

ROOT=Path(__file__).resolve().parents[1]
issues=[]; passed=[]
def require(v,msg):
    if v: passed.append(msg)
    else: issues.append(msg)
def load(rel): return (ROOT/rel).read_text(encoding='utf-8')
core_paths={
 'A': ['README.md','AGENTS.md','docs/01-planning/PRD.md','docs/01-planning/ROADMAP.md','docs/01-planning/BACKLOG.md','docs/02-design/ARCHITECTURE.md'],
 'B': ['docs/03-quality/TEST_PLAN.md','docs/03-quality/RISK_REGISTER.md','docs/02-design/DECISIONS.md','docs/03-quality/CHANGELOG.md','docs/03-quality/ROLLBACK_PLAN.md','docs/03-quality/SECURITY.md'],
 'C': ['docs/04-execution/PROJECT_STATE.md','docs/04-execution/AI_HANDOFF.md','docs/04-execution/TASK_TEMPLATE.md','docs/02-design/API_CONTRACTS.md','docs/02-design/DATA_DICTIONARY.md','docs/04-execution/DEPLOYMENT.md'],
 'supplementary': ['docs/02-design/DATA_CONTRACT.md','docs/02-design/KPI_SPEC.md','docs/02-design/ANALYSIS_PROTOCOL.md','docs/05-evidence/DATA_PROVENANCE.md','docs/05-evidence/DATA_QUALITY_REPORT.md','docs/05-evidence/RESULTS_REGISTER.md','docs/03-quality/G0_G1_REVIEW.md','docs/00-governance/DOCUMENT_REGISTER.md']
}
paths=sum(core_paths.values(),[])
require(all((ROOT/p).is_file() for p in paths),'18 A/B/C + 8 supplementary paths exist')
require(len(set(paths))==26 and all(len(v)==6 for k,v in core_paths.items() if k != 'supplementary') and len(core_paths['supplementary'])==8,'Doc group counts and unique roles')
active=[f for f in ROOT.rglob('*.md') if 'inputs' not in f.parts]
require(all(f.stat().st_size>100 for f in active),'Active docs are nonempty')

# Full explicit path references in active authored docs. Input snapshot paths to historical Aeolus repo ignored by excluding inputs.
path_pat=re.compile(r'(?<![A-Za-z0-9_./])(?:docs/(?:[A-Za-z0-9_.()\-]+/)+[A-Za-z0-9_.()\-]+\.(?:md|json))')
refbad=[]
for f in active:
    for n,line in enumerate(f.read_text(encoding='utf-8').splitlines(),1):
        for x in path_pat.findall(line):
            if not (ROOT/x).is_file(): refbad.append(f'{f.relative_to(ROOT)}:{n}:{x}')
require(not refbad,'All explicitly written docs/... MD/JSON paths resolve'+ (': '+repr(refbad[:12]) if refbad else ''))
for bad in ('`HANDOFF.md`', 'TEST-013 logs', 'Khóa 5 KPI lõi'):
    require(not any(bad in f.read_text(encoding='utf-8') for f in active if f.name not in ('CHANGELOG.md','V1_0_CONSISTENCY_AUDIT.md','DOCS_CONSISTENCY_AUDIT_v1.1.md')),'No stale actionable token '+bad)

# Primary owners and vocabulary policies.
dc=load('docs/02-design/DATA_CONTRACT.md'); kpi=load('docs/02-design/KPI_SPEC.md')
for s in ('raw_row_count = accepted_row_count + quarantined_row_count + rejected_row_count','count_metric_valid','metric_valid_rate','source_coverage_status','IDENTITY_UNVERIFIED','METADATA_MATCH_ONLY'):
    require(s in dc,'DC owns '+s)
require('accepted_row_count(C)' in dc and 'ZERO_DENOMINATOR' in dc,'Group denominator and zero guard')
require('KPI-01..08' in load('docs/01-planning/ROADMAP.md') and 'KPI-01..KPI-08' in load('docs/01-planning/BACKLOG.md'),'8 CORE KPIs in roadmap and backlog')
# KPI rows, statuses and all per-measure submetrics
rows=re.findall(r'^\|\s*(KPI-\d\d)\s*\|.*$',kpi,re.M)
require(rows==[f'KPI-{i:02d}' for i in range(1,13)],'KPI catalog exactly 01..12 ordered')
require(sum(bool(re.search(r'^\|\s*KPI-(?:0[1-8])\s*\|.*CORE_DRAFT',l)) for l in kpi.splitlines())==8,'8 CORE_DRAFT rows')
for sub in ('TAXI_OUT','TAXI_IN','AIR_TIME','ACTUAL_ELAPSED_TIME','CRS_ELAPSED_TIME'):
    require(sub in kpi,'Submetric '+sub)

# Gate-to-backlog consistency and acyclic dependency.
backlog=load('docs/01-planning/BACKLOG.md'); roadmap=load('docs/01-planning/ROADMAP.md'); state=load('docs/04-execution/PROJECT_STATE.md')
tasks={}; deps={}
for line in backlog.splitlines():
    m=re.match(r'^\|\s*(T-\d{3})\s*\|\s*(G\d)\s*\|(.+?)\|(.+?)\|(.+?)\|(.+?)\|\s*$',line)
    if m:
        task,gate,descr,dependency,accept,status=m.groups()
        require(task not in tasks,'Unique task '+task)
        tasks[task]=gate;deps[task]=re.findall(r'T-\d{3}',dependency)
require(set(tasks)=={f'T-{i:03d}' for i in range(1,18)},'Exactly T-001..017')
require({t:tasks.get(t) for t in ('T-006','T-007','T-008','T-009','T-010','T-011','T-012','T-013','T-014','T-015','T-016','T-017')}=={'T-006':'G3','T-007':'G4','T-008':'G4','T-009':'G4','T-010':'G5','T-011':'G5','T-012':'G6','T-013':'G6','T-014':'G6','T-015':'G6','T-016':'G7','T-017':'G7'},'Gate assignment code/design/full run')
require(deps.get('T-007')==['T-009'] and deps.get('T-008')==['T-007'] and deps.get('T-009')==['T-006'],'T-009→T-007→T-008 dependency')
require(all(d in tasks for ls in deps.values() for d in ls),'All task dependencies defined')
visited=set(); path=set()
def dfs(k):
    if k in path: return False
    if k in visited: return True
    path.add(k)
    if not all(dfs(d) for d in deps[k]): return False
    path.remove(k);visited.add(k);return True
require(all(dfs(k) for k in tasks),'Task dependencies acyclic')
require('CONDITIONAL_PENDING' in backlog and 'CONDITIONAL_NO_GO' in backlog and 'CONDITIONAL_NO_GO' in roadmap,'Weather conditional gate exemption defined')
require('T-009' in state and 'T-007' in state and 'T-008' in state,'State follows bootstrap→ingestion→QA')
require('G2 | DRAFT / NOT_PASSED' in state and 'G1 | PARTIAL' in state,'Gate states not overclaimed')

# Tests: every TS-xxx defined uniquely in main test table and only existing references.
testtext=load('docs/03-quality/TEST_PLAN.md'); defined_tests=re.findall(r'^\|\s*(TS-\d{3})\s*\|',testtext,re.M)
require(defined_tests==[f'TS-{i:03d}' for i in range(1,21)],'Test catalog exactly TS-001..020 ordered')
ids=set(re.findall(r'\bTS-\d{3}\b','\n'.join(f.read_text(encoding='utf-8') for f in active)))
require(ids.issubset(set(defined_tests)),'All test IDs exist')
require('TS-013' in load('docs/03-quality/ROLLBACK_PLAN.md'),'Rollback points to TS-013')
require('G5 synthetic/G6 full' in testtext and 'TS-008' in load('docs/01-planning/BACKLOG.md').split('T-011')[1].split('| TODO')[0], 'T-011 eight-core smoke test TS-008 gate alignment')
require('không phải mean chỉ của chuyến trễ' in kpi, 'Optional KPI-09 is clear about unconditional positive-part denominator')

# Results: each mandatory RQ has planned slot; no production results claim.
results=load('docs/05-evidence/RESULTS_REGISTER.md')
res_ids=re.findall(r'^\|\s*(RES-\d{3})\s*\|',results,re.M)
require(res_ids==[f'RES-{i:03d}' for i in range(1,13)],'RES-001..012 planned exactly once')
for rq in range(1,7):
    require(bool(re.search(r'^\|\s*RES-\d{3}\s*\|\s*RQ-'+f'{rq:02d}',results,re.M)),'Result slots contain RQ-'+f'{rq:02d}')
require('RQ-04' in results and '2020' in results,'2020 result slot present')
require('NO_PRODUCTION_RESULTS' in results and not re.search(r'\|\s*PASS\s*\|$',results,re.M),'No fabricated production results')
reg=load('docs/00-governance/DOCUMENT_REGISTER.md')
for rq in range(1,7):
    require('RQ-'+f'{rq:02d}' in reg,'Traceability row RQ-'+f'{rq:02d}')
require('TS-017' in testtext and 'TS-018' in testtext and 'TS-019' in testtext and 'TS-020' in testtext,'QA test additions')

# Verify immutable source files against original source manifest.
source=json.loads((ROOT/'docs/05-evidence/inputs/SOURCE_MANIFEST.json').read_text())
entries=source['sources']; require(len(entries)==13,'13 preserved source entries')
for x in entries:
    f=ROOT/x['path'];require(f.is_file() and len(f.read_bytes())==x['bytes'] and sha256(f.read_bytes()).hexdigest()==x['sha256'],'Input immutable '+x['path'])

# Check schema JSON numerics, complete, one 34-field schema, yearly rows, finite late counts.
js=[json.loads((ROOT/f'docs/05-evidence/inputs/schema_{y}.json').read_text()) for y in range(2016,2025)]
require(all(x.get('is_complete') and x['column_count']==34 and x['columns']==js[0]['columns'] for x in js),'9 complete 34-column matching schemas')
require(sum(x['row_count'] for x in js)==54674003,'54,674,003 audited rows')
require(sum(x['arr_delay']['gte_15']['count'] for x in js)==10116916,'10,116,916 audit late arrivals')
require(all(x['arr_delay']['finite_count']==x['row_count'] for x in js),'audit finite ARR_DELAY equal row count')
require(all(x['year']==y for y,x in zip(range(2016,2025),js)),'9 calendar year audit labels')
qa=load('docs/05-evidence/DATA_QUALITY_REPORT.md')
require('13,474' in qa and '15,046' in qa,'Weather missing aggregates preserved')
require('2400_SEMANTICS_NOT_PROVEN' in load('docs/05-evidence/inputs/canonical_schedule_datetime_representation_audit.md'),'Time uncertainty source preserved')

# Package manifest (only after finalization; allow initial absence)
pm_path=ROOT/'PACKAGE_MANIFEST.json'
if pm_path.exists():
    pm=json.loads(pm_path.read_text());
    if pm.get('version')=='docs-v1.1':
        files=set()
        for obj in pm['generated_files']:
            name=obj['path']; files.add(name);ff=ROOT/name
            require(ff.exists() and ff.stat().st_size==obj['bytes'] and sha256(ff.read_bytes()).hexdigest()==obj['sha256'],'Package manifest hash '+name)
        require(files=={str(f.relative_to(ROOT)) for f in ROOT.rglob('*') if f.is_file() and f.name!='PACKAGE_MANIFEST.json'},'Package manifest covers every other file')

print(f'PASS assertions: {len(passed)}; FAIL: {len(issues)}')
for i in issues: print('FAIL:',i)
if issues: sys.exit(1)
