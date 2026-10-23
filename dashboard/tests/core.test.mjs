import test from 'node:test';
import assert from 'node:assert/strict';
import {monthSeries, monthlyAxis, annualAxis, status, relativeChange, pointDifference, metric, csvString, periodRows, escapeHTML} from '../web/core.mjs';

test('March 2024 is a gap, not zero or an interpolated value',()=>{
  const s=monthSeries([{year_month:'2024-02',monthly_volume:12},{year_month:'2024-04',monthly_volume:18}],2024,2024);
  assert.equal(s.length,12);assert.equal(s[2].x,'2024-03');assert.equal(s[2].value,null);assert.equal(s[3].value,18);
});
test('time axes explicitly distinguish month categories from numeric year coordinates',()=>{
  const month=monthlyAxis(2024),year=annualAxis();
  assert.equal(month.type,'category');assert.deepEqual(month.range,[-.5,11.5]);
  assert.equal(month.categoryarray.length,12);assert.equal(month.categoryarray[2],'2024-03');
  assert.equal(month.ticktext[0],'T1');assert.equal(month.ticktext.at(-1),'T12');
  assert.equal(year.type,'linear');assert.deepEqual(year.range,[2015.5,2024.5]);
  assert.deepEqual(year.tickvals,[2016,2017,2018,2019,2020,2021,2022,2023,2024]);
  assert.equal(year.autorange,false);
});
test('sample thresholds apply to each valid denominator at both boundaries',()=>{
  for(const [family,min] of [['carrier-year',1000],['origin-year',365],['dest-year',365],['route-year',100]]){
    assert.equal(status(min-1,family),'SUPPRESSED');assert.equal(status(min,family),'LOW_SAMPLE_CAUTION');
    assert.equal(status(3*min-1,family),'LOW_SAMPLE_CAUTION');assert.equal(status(3*min,family),'SUFFICIENT');
  }
});
test('difference in percentage points stays distinct from relative change',()=>{
  assert.equal(pointDifference(20,10),10);assert.equal(relativeChange(20,10),100);
  assert.equal(relativeChange(10,0),null);assert.equal(relativeChange(null,10),null);
});
test('metric lookup never fabricates unsupported crossed cohorts',()=>{
  const db={metrics:{'carrier-year|2019|WN|KPI-02':{value:.2,n:10000}}};
  assert.equal(metric(db,'carrier-year',2019,'WN','KPI-02').n,10000);
  assert.equal(metric(db,'carrier-year',2019,'WN+ORD','KPI-02'),null);
});
test('CSV preserves signed numeric values, quotes, and null gaps',()=>{
  assert.equal(csvString(['Name','Value'],[['A,"B',-5.1],['missing',null]]),'\ufeff"Name","Value"\r\n"A,""B","-5.1"\r\n"missing",');
});
test('period selection keeps original observations without averaging percentiles',()=>{
  const rows=[{year:2019,p90:39},{year:2020,p90:14},{year:2021,p90:29},{year:2022,p90:42}];
  assert.deepEqual(periodRows(rows,'shock'),rows.slice(1,3));assert.equal(rows.length,4);
  assert.equal(escapeHTML('<script>"&'),'&lt;script&gt;&quot;&amp;');
});
