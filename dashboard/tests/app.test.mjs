// Rendering/event unit tests with DOM and Plotly doubles. These are NOT browser/visual QA.
import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
const bundle=process.env.AEROMETRIC_TEST_BUNDLE || 'D:/Flight_Audit_Exports/DASHBOARD_DEMO/stitch_v3';
const db=JSON.parse(fs.readFileSync(path.join(bundle,'data/dashboard.json'),'utf8'));
const listeners=new Map(), nodes=new Map(), plots=new Map(), errors=[];
let ready=0;
function node(id){
  if(!nodes.has(id))nodes.set(id,{id,innerHTML:'',textContent:'',dataset:{},hidden:true,
    on(name,callback){this[name]=callback;},showModal(){this.open=true;},close(){this.open=false;}});
  return nodes.get(id);
}
globalThis.document={getElementById:node,querySelectorAll:()=>[],body:{dataset:{}},
  addEventListener(type,handler){listeners.set(type,handler);},
  dispatchEvent(event){if(event.type==='aerometric:ready')ready++;},
  createElement:()=>({click(){}})};
globalThis.window={addEventListener(type,handler){listeners.set(type,handler);},scrollTo(){}};
globalThis.location={hash:'#overview'};
globalThis.fetch=async()=>({ok:true,json:async()=>structuredClone(db)});
globalThis.Plotly={purge(){},async newPlot(id,traces,layout){
  assert.equal(typeof id,'string');
  if(id==='volume-heatmap'){
    for(const axis of [layout.xaxis,layout.yaxis]){
      assert.equal(axis.type,'linear');assert.equal(axis.autorange,false);
    }
    for(const a of layout.annotations||[]){
      assert.equal(a.xref,'x');assert.equal(a.yref,'y');
      for(const [value,axis] of [[a.x,layout.xaxis],[a.y,layout.yaxis]]){
        assert.equal(typeof value,'number');
        assert.ok(value>=Math.min(...axis.range)&&value<=Math.max(...axis.range),'heatmap annotation outside cell grid');
      }
    }
  }
  for(const shape of layout.shapes||[]){
    if(shape.xref==='x'&&typeof shape.x0==='number'){
      assert.equal(layout.xaxis.type,'linear',`${id}: numeric year shape on category axis`);
      assert.equal(layout.xaxis.autorange,false);
      assert.ok(shape.x0>=layout.xaxis.range[0]&&shape.x1<=layout.xaxis.range[1]);
    }
  }
  for(const t of traces){
    assert.ok(['scatter','bar','heatmap'].includes(t.type));
    if(t.type!=='heatmap')assert.equal(t.x.length,t.y.length,`${id}: unequal coordinate lengths`);
    for(const value of (t.type==='heatmap'?t.z.flat():[...t.x,...t.y]))
      assert.ok(typeof value!=='number'||Number.isFinite(value),`${id}: non-finite data`);
  }
  plots.set(id,{traces,layout});
}};
const originalError=console.error;
console.error=(...args)=>errors.push(args.join(' '));
await import('../web/app.mjs');
async function settled(previous=ready){
  for(let i=0;i<100&&ready<=previous;i++)await new Promise(resolve=>setImmediate(resolve));
  assert.ok(ready>previous,'render did not finish');assert.deepEqual(errors,[]);
  assert.doesNotMatch(node('main').innerHTML,/undefined|NaN|Không thể mở gói/);
}
async function navigate(page){let prev=ready;location.hash='#'+page;listeners.get('hashchange')();await settled(prev);}
async function change(id,value){let prev=ready;listeners.get('change')({target:{id,value,dataset:{}}});await settled(prev);}
async function click(dataset={},id=''){let prev=ready;const button={dataset,id};listeners.get('click')({target:{closest:()=>button}});await settled(prev);}
await settled(0);

test('all seven page renderers generate real chart/table data without runtime errors',async()=>{
  for(const page of ['overview','volume','delay','compare','pandemic','journey','evidence']){
    await navigate(page);assert.equal(window.aerometric.page,page);
    assert.match(node('topbar').innerHTML,/2024 PARTIAL/);
    assert.match(node('main').innerHTML,/<h1>/);
    const links=[...node('main').innerHTML.matchAll(/(?:href|src)="((?:downloads|charts)\/[^"#]+)"/g)];
    for(const link of links)assert.ok(fs.existsSync(path.join(bundle,link[1])),`${page}: missing ${link[1]}`);
  }
});
test('volume filters preserve missing March and change observed scope',async()=>{
  await navigate('volume');
  let trace=plots.get('volume-monthly').traces[0];
  assert.equal(trace.y[trace.x.indexOf('2024-03')],null);
  await click({period:'shock'});trace=plots.get('volume-monthly').traces[0];assert.equal(trace.x.length,24);
  assert.match(node('main').innerHTML,/24 tháng quan sát/);
});
test('seasonality heatmap has bounded cell coordinates and accurate tooltips across repeated period changes',async()=>{
  await navigate('volume');
  const scopes={all:[2016,2024,107],before:[2016,2019,48],shock:[2020,2021,24],after:[2022,2024,35]};
  for(const period of ['all','after','before','shock','all','before','after','all']){
    await click({period});
    const [start,end,count]=scopes[period],p=plots.get('volume-heatmap'),t=p.traces[0];
    const years=Array.from({length:end-start+1},(_,i)=>start+i);
    const months=Array.from({length:12},(_,i)=>i);
    assert.deepEqual(t.x,months);assert.deepEqual(t.y,years.map((_,i)=>i));
    assert.deepEqual(p.layout.xaxis.range,[-.5,11.5]);
    assert.deepEqual(p.layout.yaxis.range,[years.length-.5,-.5]);
    assert.deepEqual(p.layout.xaxis.ticktext,months.map(i=>`T${i+1}`));
    assert.deepEqual(p.layout.yaxis.ticktext,years.map(String));
    assert.equal(t.z.length,years.length);assert.equal(t.z.flat().filter(v=>v!=null).length,count);
    assert.equal(t.hoverongaps,false);assert.match(t.hovertemplate,/%\{customdata\[0\]\}/);
    assert.match(t.hovertemplate,/%\{customdata\[1\]\}/);assert.doesNotMatch(t.hovertemplate,/%\{[xy]\}/);
    for(let row=0;row<years.length;row++){
      assert.equal(t.z[row].length,12);assert.equal(t.customdata[row].length,12);
      for(let col=0;col<12;col++){
        const date=`${years[row]}-${String(col+1).padStart(2,'0')}`;
        const source=db.tables.rq01_monthly_volume.find(r=>r.year_month===date);
        assert.equal(t.z[row][col],source?.monthly_volume??null);
        assert.deepEqual(t.customdata[row][col].slice(0,2),[years[row],col+1]);
        if(source)assert.equal(t.customdata[row][col][2],source.source_coverage_status);
        else{assert.equal(years[row],2024);assert.equal(col,2);assert.equal(t.text[row][col],'');}
      }
    }
    if(end===2024){
      assert.equal(p.layout.annotations.length,1);assert.equal(p.layout.annotations[0].x,2);
      assert.equal(p.layout.annotations[0].y,years.indexOf(2024));
      assert.equal(p.layout.annotations[0].text,'Thiếu');
    }else assert.deepEqual(p.layout.annotations,[]);
  }
});
test('overview year chips drive 12 monthly columns and both rate streams with correct denominators',async()=>{
  await navigate('overview');
  for(let year=2016;year<=2024;year++){
    await click({overviewYear:String(year)});
    const v=plots.get('overview-volume'),d=plots.get('overview-delay');
    for(const plot of [v,d]){
      assert.equal(plot.layout.xaxis.type,'category');
      assert.deepEqual(plot.layout.xaxis.range,[-.5,11.5]);
      assert.equal(plot.layout.xaxis.tickvals.length,12);
      assert.deepEqual(plot.layout.xaxis.ticktext,Array.from({length:12},(_,i)=>`T${i+1}`));
      assert.equal(plot.layout.shapes,undefined);
    }
    assert.match(node('main').innerHTML,new RegExp(`theo tháng — năm ${year}`));
    for(let i=0;i<12;i++){
      const key=`${year}-${String(i+1).padStart(2,'0')}`;
      const volume=db.tables.rq01_monthly_volume.find(r=>r.year_month===key);
      const delay=db.tables.rq02_monthly_delays.find(r=>r.year_month===key);
      assert.equal(v.traces[0].x[i],key);assert.equal(v.traces[0].y[i],volume?.monthly_volume??null);
      for(const [j,stream,field] of [[0,'KPI-02','arr_delay_ge_15_rate_pct'],[1,'KPI-04','dep_delay_ge_15_rate_pct']]){
        assert.equal(d.traces[j].y[i],delay?.[field]??null);
        assert.equal(d.traces[j].connectgaps,false);
        if(delay){
          const m=db.metrics[`year-month|${year}|${key}|${stream}`];
          assert.equal(d.traces[j].customdata[i][0],new Intl.NumberFormat('vi-VN').format(m.n));
        }
      }
    }
    assert.equal(v.traces[0].y.filter(v=>v!=null).length,year===2024?11:12);
    if(year===2024){
      assert.equal(d.traces[0].y[2],null);
      for(const plot of [v,d])assert.equal(plot.layout.annotations[0].text,'T3: Không có dữ liệu');
    }
  }
});
test('clicking a monthly volume bar cannot turn the selected year into NaN',async()=>{
  await navigate('overview');const year=window.aerometric.state.overview.year;
  node('overview-volume').plotly_click({points:[{x:`${year}-01`}]});
  assert.equal(window.aerometric.state.overview.year,year);assert.deepEqual(errors,[]);
});
test('airport taxi and carrier trend keep nine readable annual slots and highlight the selected year',async()=>{
  await navigate('compare');await click({tab:'airport'});await change('compare-year','2019');
  await change('airport-role','origin');await change('compare-airport','ORD');
  for(const [role,name,source,key,measure,stream] of [
    ['origin','ORD','rq03_origin_airports','origin_airport','taxi_out_mean_min','KPI-07/TAXI_OUT'],
    ['dest','ATL','rq03_dest_airports','dest_airport','taxi_in_mean_min','KPI-07/TAXI_IN']]){
    await change('airport-role',role);await change('compare-airport',name);
    for(const year of [2016,2019,2024]){
      await change('compare-year',String(year));const p=plots.get('airport-taxi'),t=p.traces[0];
      assert.equal(p.layout.xaxis.type,'linear');assert.deepEqual(p.layout.xaxis.range,[2015.5,2024.5]);
      assert.equal(t.x.length,9);assert.equal(p.layout.shapes[0].x0,year);assert.equal(t.connectgaps,false);
      const index=t.x.indexOf(year),row=db.tables[source].find(r=>r[key]===name&&r.year===year);
      assert.equal(t.y[index],row[measure]);assert.equal(t.marker.size[index],12);
      assert.equal(t.text.filter(Boolean).length,1);assert.match(t.name,new RegExp(name));
      assert.equal(t.customdata[index][0],new Intl.NumberFormat('vi-VN').format(db.metrics[`${role==='origin'?'origin-year':'dest-year'}|${year}|${name}|${stream}`].n));
    }
  }
  await click({tab:'carrier'});const p=plots.get('carrier-trend');
  assert.equal(p.layout.xaxis.type,'linear');assert.deepEqual(p.layout.xaxis.range,[2015.5,2024.5]);
  assert.equal(p.traces[0].x.length,9);
});
test('delay year selection uses that year quantiles and signed mean',async()=>{
  await navigate('delay');await change('delay-year','2020');
  assert.match(node('main').innerHTML,/-5,11/);assert.match(node('main').innerHTML,/P90 trễ đến \(2020\)/);
  await click({period:'after'});assert.equal(window.aerometric.state.delay.year,2022);
});
test('carrier, airport role, and fixed route comparison controls',async()=>{
  await navigate('compare');await change('compare-year','2024');await change('compare-carrier','DL');
  assert.ok(plots.has('carrier-rank'));
  await click({tab:'airport'});await change('airport-role','dest');await change('compare-year','2020');
  assert.ok(plots.has('airport-rank'));assert.match(node('main').innerHTML,/Taxi-in/);
  await click({tab:'route'});assert.match(node('main').innerHTML,/2019/);
  assert.doesNotMatch(node('main').innerHTML,/id="compare-year"/);
});
test('pandemic relative button changes values with 2019=0 baseline',async()=>{
  await navigate('pandemic');await click({},'relative-toggle');
  const t=plots.get('pandemic-volume').traces[0];assert.equal(t.y[0],0);assert.ok(t.y[1]<-39&&t.y[1]>-40);
});
test('all published year/entity selectors and period ranges render safely',async()=>{
  await navigate('compare');await click({tab:'carrier'});
  for(let y=2016;y<=2024;y++)await change('compare-year',String(y));
  await click({tab:'airport'});
  for(const role of ['origin','dest']){
    await change('airport-role',role);
    for(let y=2016;y<=2024;y++)await change('compare-year',String(y));
  }
  await click({tab:'route'});
  for(const r of db.tables.rq03_directed_routes)await change('compare-route',r.city_pair);
  for(const page of ['volume','delay','journey']){
    await navigate(page);
    for(const period of ['before','shock','after','all'])await click({period});
  }
});
test('journey cards and tables expose distinct 2020 measure denominators',async()=>{
  await navigate('journey');await change('journey-year','2020');
  assert.match(node('main').innerHTML,/4\.312\.090/);assert.match(node('main').innerHTML,/4\.312\.091/);
});
test('RES query and RQ filter return actual observations; gallery opens original SVG',async()=>{
  await navigate('evidence');
  listeners.get('input')({target:{id:'res-search',value:'RES-018'}});
  assert.match(node('table-res-table').innerHTML,/RES-018/);assert.doesNotMatch(node('table-res-table').innerHTML,/RES-019/);
  assert.equal(node('table-count-res-table').textContent,'1/20 RES phù hợp');
  listeners.get('click')({target:{closest:()=>({dataset:{chart:'0'},id:''})}});
  assert.equal(node('chart-dialog').open,true);assert.match(node('dialog-image').src,/\.svg$/);
  await change('res-rq','RQ-05');assert.equal(window.aerometric.state.evidence.rq,'RQ-05');
});
test.after(()=>{console.error=originalError;});
