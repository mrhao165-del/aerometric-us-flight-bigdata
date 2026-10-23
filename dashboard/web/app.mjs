import {YEARS, PERIODS, escapeHTML as e, number as n, signed, metric, periodRows, chronological,
        monthSeries, monthlyAxis, annualAxis, relativeChange, topRows, searchResults} from './core.mjs';
import {colors as C, icon, badge, field, action, metricCard, hero, note, researchNotes,
        chart, line, bars, chartJobs, drawCharts, tableRegistry, tablePanel, tableBody, sortTable, exportTable} from './ui.mjs';

const NAV = [
  ['overview','Tổng quan','Tổng quan'],['volume','Sản lượng','Sản lượng'],['delay','Độ trễ','Độ trễ'],
  ['compare','So sánh hiệu suất','So sánh hiệu suất'],['pandemic','Giai đoạn 2020','Giai đoạn 2020'],
  ['journey','Taxi & hành trình','Taxi & hành trình'],['evidence','Dữ liệu & phương pháp','Dữ liệu & pp'],
];
const state = {
  overview:{year:2019}, volume:{period:'all',mean:true,marks:true},
  delay:{period:'all',year:2019,arr:true,dep:true,zero:true,p90:true},
  compare:{tab:'carrier',year:2019,carrier:'WN',role:'origin',airport:'ORD',route:'LGA <-> ORD'},
  pandemic:{relative:false,highlight:true}, journey:{period:'all',year:2019}, evidence:{query:'',rq:'ALL'},
};
let db, page='overview', renderVersion=0;
const $ = id=>document.getElementById(id);
const table = name=>db.tables[name];
const M = (family,year,entity,stream)=>metric(db,family,year,entity,stream);
const annualMeta = (year,stream)=>M('year',year,'all',stream);
const pct=v=>v==null?'—':`${n(v,2)}%`;
const mins=v=>v==null?'—':`${signed(v)} phút`;
const numCol=(key,label,digits=0)=>({key,label,format:v=>n(v,digits)});
const pctCol=(key,label)=>({key,label,format:pct});
const minCol=(key,label)=>({key,label,format:mins});
const covCol={key:'coverage',label:'Coverage',html:r=>badge(r.coverage)};
const yearCol={key:'year',label:'Năm',format:v=>String(v)+(Number(v)===2024?' *':'')};
const yearOptions=YEARS.map(y=>[y,`${y}${y===2024?' · PARTIAL':''}`]);
function resetButton(){return action('Đặt lại', 'data-reset="true"','reset');}
function yearField(id,selected,years=yearOptions){return field('Năm quan sát',id,years,selected);}
function yearChips(selected){return `<div class="filter-group">${YEARS.map(y=>`<button class="chip ${y===selected?'active':''}" data-overview-year="${y}" aria-pressed="${y===selected}">${y}${y===2024?'*':''}</button>`).join('')}</div>`;}
function periods(s){return `<div class="filter-group">${PERIODS.map(p=>`<button class="chip ${s.period===p.id?'active':''}" data-period="${p.id}" aria-pressed="${s.period===p.id}">${e(p.label)}</button>`).join('')}</div>`;}
function activeYear(s,rows){if(!rows.some(r=>r.year===s.year))s.year=rows[0]?.year??2019;return s.year;}
function check(label,key,checked){return `<label class="mono"><input type="checkbox" data-check="${key}" ${checked?'checked':''}> ${e(label)}</label>`;}
function metadataRow(r,family,entity,stream){const m=M(family,r.year,entity,stream);return {...r,n_valid:m?.n??null,excluded:m?.excluded??null,coverage:m?.coverage??'UNKNOWN',min_n_status:m?.status??null};}
function countSeries(rows,field='annual_volume',selected=null){return bars('Số bản ghi',rows.map(r=>r.year),rows.map(r=>r[field]),rows.map(r=>annualMeta(r.year,'KPI-01')),C.blue,{millions:true,colors:rows.map(r=>r.year===2024?C.amber:r.year===selected?C.primary:'#4d80ed')});}
function yearHighlight(year){return [{type:'line',xref:'x',x0:year,x1:year,yref:'paper',y0:0,y1:1,line:{color:C.primary,width:1,dash:'dot'}}];}
function periodToolbar(s,extra=''){return `<div class="toolbar"><span class="toolbar-label">Khung thời gian</span>${periods(s)}${extra}<span class="toolbar-note">Chọn khoảng năm để xem từng điểm quan sát, không gộp phân vị.</span>${resetButton()}</div>`;}
function metadataDetails(){return 'Đơn vị CORE theo TS-018 Option B, kiểm chứng mẫu tháng 1/2019; không suy rộng thành chứng thực toàn bộ 9 năm. N_valid và coverage là hai khái niệm khác nhau.';}

function renderShell(){
  $('sidebar').innerHTML=`<a class="brand" href="#overview" aria-label="AeroMetric — Tổng quan"><div class="brand-logo">${icon('plane')}<span class="brand-name">AeroMetric</span></div><p class="brand-sub">US ANALYTICS 2016–2024</p><span class="engine-badge"><span class="dot"></span>Kết quả PySpark 4.0.1</span></a><nav>${NAV.map(([id,label,short])=>`<a href="#${id}" data-page="${id}" title="${e(label)}" ${id===page?'class="active" aria-current="page"':''}>${icon(id)}<span class="nav-label">${e(short)}</span></a>`).join('')}</nav><div class="side-foot"><div class="side-stat"><span>Dataset rows</span><b>54,674,003</b></div><div class="side-stat"><span>Quan sát</span><b>107 tháng</b></div><div class="side-stat"><span>CORE KPIs</span><b>8 / 12 streams</b></div><div class="side-version"><span>KPI v${e(db.kpi_version)}</span><span class="offline"><span class="dot"></span>OFFLINE</span></div></div>`;
  $('topbar').innerHTML=`<div class="top-warning"><span class="dot"></span><span><strong>2024 PARTIAL</strong> · Thiếu tháng 3/2024 — quan sát 335/366 ngày</span></div><div class="top-context"><span class="context-label">Dataset nghiên cứu · 2016–2024</span><a href="#evidence" class="offline">${icon('data')} Nguồn dữ liệu</a></div>`;
}

function overview(){
  const y=state.overview.year;
  const vol=monthSeries(table('rq01_monthly_volume'),y,y);
  const arr=monthSeries(table('rq02_monthly_delays'),y,y,'arr_delay_ge_15_rate_pct');
  const dep=monthSeries(table('rq02_monthly_delays'),y,y,'dep_delay_ge_15_rate_pct');
  const monthMeta=(series,stream)=>series.map(r=>r.row?M('year-month',y,r.x,stream):null);
  const annotations=y===2024?[{xref:'x',x:'2024-03',yref:'paper',y:.92,text:'T3: Không có dữ liệu',showarrow:false,bgcolor:'#fff5e9',font:{size:10,color:C.amber}}]:[];
  const tools=`<div class="toolbar"><span class="toolbar-label">Bộ lọc năm</span>${yearChips(y)}<span class="toolbar-note">4 thẻ KPI: thống kê cả năm. Hai biểu đồ: từng tháng của năm đang chọn.</span></div>`;
  let html=hero('Overview','Tổng quan Nghiên cứu Hiệu suất Chuyến bay','Quy mô dữ liệu quan sát và xu hướng hiệu suất khai thác bay Hoa Kỳ trong giai đoạn 2016–2024.',tools);
  html+=`<section class="metrics-grid">${metricCard(`Số bản ghi trong dataset (${y})`,n(annualMeta(y,'KPI-01').value),'',annualMeta(y,'KPI-01'),{caption:'Accepted records thuộc năm quan sát.',icon:'data'})}${metricCard(`Tỷ lệ trễ đến ≥15 phút (${y})`,pct(annualMeta(y,'KPI-02').value*100),'',annualMeta(y,'KPI-02'),{color:'blue',caption:'Mẫu số hợp lệ ARR_DELAY; bao gồm đúng 15 phút.',icon:'delay'})}${metricCard(`Trễ đến trung bình có dấu (${y})`,signed(annualMeta(y,'KPI-03').value),'phút',annualMeta(y,'KPI-03'),{color:'amber',caption:'Giữ cả giá trị âm khi đến sớm hơn lịch.',icon:'delay'})}${metricCard(`P90 trễ đến (${y})`,n(annualMeta(y,'KPI-06/P90').value),'phút',annualMeta(y,'KPI-06/P90'),{caption:'Phân vị của riêng năm được chọn, không gộp các năm.'})}</section>`;
  const volumeTrace=bars('Số bản ghi accepted',vol.map(r=>r.x),vol.map(r=>r.value),monthMeta(vol,'KPI-01'),C.blue,{digits:0,unit:'bản ghi',hideText:true});
  const maxVolume=Math.max(...vol.map(r=>r.value??0)),step=Math.max(1000,Math.ceil(maxVolume/5000)*1000);
  const countTicks=Array.from({length:7},(_,i)=>i*step);
  html+=`<div class="cards-two overview-charts">${chart('overview-volume',`Sản lượng bản ghi theo tháng — năm ${y}`,'Đơn vị trục Y: nghìn bản ghi accepted; hover để xem số chính xác.',[volumeTrace],{xaxis:monthlyAxis(y),yaxis:{rangemode:'tozero',tickmode:'array',tickvals:countTicks,ticktext:countTicks.map(v=>n(v/1000)),title:{text:'Nghìn bản ghi'}},annotations,margin:{l:65,r:20,t:38,b:60}},{source:'rq01_monthly_volume',scope:y===2024?'PARTIAL · T3 thiếu dữ liệu':'12 tháng quan sát'})}${chart('overview-delay',`Tỷ lệ trễ đến và khởi hành theo tháng — năm ${y}`,'Ngưỡng ≥15 phút; mẫu số hợp lệ riêng cho ARR và DEP.',[line('Trễ đến',arr.map(r=>r.x),arr.map(r=>r.value),monthMeta(arr,'KPI-02'),C.blue,{unit:'%'}),line('Trễ khởi hành',dep.map(r=>r.x),dep.map(r=>r.value),monthMeta(dep,'KPI-04'),C.teal,{dash:'dash',unit:'%'})],{xaxis:monthlyAxis(y),yaxis:{ticksuffix:'%',rangemode:'tozero',title:{text:'Tỷ lệ (%)'}},annotations,margin:{l:65,r:20,t:38,b:60}},{source:'rq02_monthly_delays',scope:y===2024?'PARTIAL · Không nối qua T3':'N_valid riêng từng measure trong tooltip'})}</div>`;
  html+=`<section class="panel"><div class="card-heading"><h2>Bảng tóm tắt chỉ số quan sát & phương pháp</h2><span class="badge neutral">RQ-01 · RQ-02</span></div><div class="panel-inner"><div class="cards-two"><div class="note"><strong>Phạm vi quan sát</strong><br>54.674.003 bản ghi accepted · 9 năm · 107 tháng. Năm 2024 có 11 tháng, không được so tổng lượng như một năm đủ 12 tháng.</div><div class="note"><strong>Nguồn cố định</strong><br>KPI 1.0.0 / Analytics v4. Tất cả giá trị lấy từ sản phẩm đã xuất bản; không chạy lại pipeline khi dùng Dashboard.</div></div>${note('Quan sát nổi bật.', 'Sản lượng năm 2020 giảm 39,79% so với 2019; tỷ lệ trễ đến năm 2020 là 9,73%. Đây là mô tả dữ liệu quan sát, không xác lập quan hệ nhân quả.')}</div></section>`;
  return html;
}

function volume(){
  const s=state.volume,annual=chronological(periodRows(table('rq01_annual_volume'),s.period));
  const monthly=chronological(periodRows(table('rq01_monthly_volume'),s.period),'year_month');
  const p=PERIODS.find(p=>p.id===s.period),series=monthSeries(monthly,p.min,p.max);
  const total=annual.reduce((a,r)=>a+r.annual_volume,0),peak=topRows(monthly,'monthly_volume',1)[0],trough=topRows(monthly,'monthly_volume',1,false)[0],mean=total/monthly.length;
  let html=hero('RQ-01','Sản lượng Chuyến bay & Tính Mùa vụ (2016–2024)','Khám phá quy mô, nhịp tháng và những thay đổi trong dataset đã audit.',periodToolbar(s), 'Quy mô dữ liệu quan sát biến động thế nào theo năm và tháng?');
  html+=`<section class="metrics-grid">${metricCard('Số bản ghi trong phạm vi',n(total),'',null,{caption:`${annual.length} năm · ${monthly.length} tháng quan sát`,foot:'SUM số bản ghi năm · Không SUM các family',icon:'data'})}${metricCard('Tháng có sản lượng cao nhất',peak.year_month,'',null,{caption:`${n(peak.monthly_volume)} bản ghi`,foot:'Cực đại trong phạm vi đang chọn',compact:true,color:'blue'})}${metricCard('Tháng có sản lượng thấp nhất',trough.year_month,'',null,{caption:`${n(trough.monthly_volume)} bản ghi`,foot:'Chỉ xét tháng có dữ liệu, không tính tháng thiếu',compact:true,color:'amber'})}${metricCard('Trung bình mỗi tháng quan sát',n(mean),'',null,{caption:'Tổng số bản ghi / số tháng có dữ liệu.',foot:'Tháng thiếu không được thay bằng 0'})}</section>`;
  const monthMeta=series.map(r=>r.row?M('year-month',r.year,r.x,'KPI-01'):null);
  const traces=[line('Sản lượng tháng',series.map(r=>r.x),series.map(r=>r.value),monthMeta,C.blue,{digits:0,unit:'bản ghi'})];
  if(s.mean)traces.push(line('Trung bình tháng quan sát',series.map(r=>r.x),series.map(r=>r.value==null?null:mean),[],C.grey,{dash:'dash',digits:0,unit:'bản ghi'}));
  const marks=s.marks?[{type:'rect',xref:'x',x0:'2020-01',x1:'2020-12',yref:'paper',y0:0,y1:1,fillcolor:'#fff0df',line:{width:0},opacity:.5,layer:'below'},{type:'line',xref:'x',x0:'2024-03',x1:'2024-03',yref:'paper',y0:0,y1:1,line:{color:C.amber,width:2,dash:'dot'}}]:[];
  html+=`<div class="cards-two">${chart('volume-annual','Sản lượng hàng năm','Số bản ghi accepted; 2024 chỉ có 335 ngày.',[countSeries(annual)],{yaxis:{tickformat:'.2s',rangemode:'tozero'}},{source:'rq01_annual_volume'})}${chart('volume-monthly','Chu kỳ mùa vụ & dòng thời gian',`${monthly.length} tháng có dữ liệu · Tháng 3/2024 là khoảng trống.`,traces,{yaxis:{tickformat:'.2s'},xaxis:{nticks:8},shapes:marks},{source:'rq01_monthly_volume'})}</div><div class="toolbar" style="margin:0 0 20px">${check('Đường trung bình tháng','mean',s.mean)}${check('Đánh dấu 2020 / tháng 3-2024','marks',s.marks)}</div>`;
  const years=annual.map(r=>r.year),monthLabels=Array.from({length:12},(_,i)=>`T${i+1}`);
  const grid=years.map(year=>monthSeries(monthly,year,year).map(r=>r.value));
  // Use cell indices for both data and annotations. Numeric-looking year labels
  // are unsafe annotation coordinates on a categorical axis ("2024" -> 2024).
  const monthIndices=monthLabels.map((_,i)=>i),yearIndices=years.map((_,i)=>i);
  const cells=years.map(year=>monthSeries(monthly,year,year));
  const heat={type:'heatmap',x:monthIndices,y:yearIndices,z:grid,colorscale:[[0,'#eef3ff'],[.3,'#c7dcff'],[.65,'#5a93f6'],[1,'#004ac6']],xgap:3,ygap:3,hoverongaps:false,
    customdata:cells.map(row=>row.map(cell=>[cell.year,cell.month,cell.row?.source_coverage_status??'PARTIAL'])),
    text:grid.map(r=>r.map(v=>v==null?'':`${n(v/1000,0)}k`)),texttemplate:'%{text}',textfont:{size:10},showscale:false,
    hovertemplate:'<b>Năm %{customdata[0]} · T%{customdata[1]}</b><br>Số bản ghi: %{z:,.0f}<br>Coverage: %{customdata[2]}<extra></extra>'};
  const annotations=years.includes(2024)?[{xref:'x',yref:'y',x:2,y:years.indexOf(2024),text:'Thiếu',showarrow:false,xanchor:'center',yanchor:'middle',bgcolor:'#fff5e9',font:{color:C.amber,size:10}}]:[];
  html+=chart('volume-heatmap','Bản đồ mật độ mùa vụ: Năm × Tháng','Mỗi ô là một tháng quan sát. Ô tháng 3/2024 để trống, không nội suy.',[heat],{
    margin:{l:60,r:22,t:30,b:20},
    xaxis:{type:'linear',autorange:false,range:[-.5,11.5],tickmode:'array',tickvals:monthIndices,ticktext:monthLabels,side:'top',showgrid:false,fixedrange:true},
    yaxis:{type:'linear',autorange:false,range:[years.length-.5,-.5],tickmode:'array',tickvals:yearIndices,ticktext:years.map(String),showgrid:false,zeroline:false,fixedrange:true},
    annotations},{source:'rq01_monthly_volume',className:'tall',scope:'Màu đậm = nhiều bản ghi hơn; không phải chất lượng tốt hơn'});
  html+=tablePanel('volume-table','Bảng sản lượng theo năm','Share và YoY lấy từ bảng đã công bố; share có mẫu số cố định toàn dataset.',[yearCol,numCol('annual_volume','Bản ghi accepted'),pctCol('share_of_9yr_pct','Tỷ trọng toàn dataset (%)'),pctCol('yoy_growth_pct','YoY (%)'),covCol],annual.map(r=>({...r,coverage:r.source_coverage_status})),{source:'rq01_annual_volume',note:'YoY năm 2024 chịu ảnh hưởng thiếu tháng 3. Lọc phạm vi không tính lại tỷ trọng share_of_9yr_pct.'});
  html+=researchNotes([['Nhịp tháng trong dataset','So sánh từng tháng qua các năm bằng heatmap. Mọi nhận xét về đỉnh/đáy áp dụng cho phạm vi đang chọn.','Nguồn: rq01_monthly_volume'],['Giai đoạn 2020','Dữ liệu chính thức ghi tháng 4/2020 là 179.835 bản ghi; tháng 5/2020 đạt mức thấp hơn, 163.767 bản ghi.','RES-003 · Đã áp dụng đính chính nghiệm thu'],['Dữ liệu khuyết','Không quy đổi 2024 thành một năm đủ, không thêm chuyến bay giả hoặc thay ô tháng 3 bằng 0.','OR-05 · 335/366 ngày']]);
  return html;
}

function delay(){
  const s=state.delay,rows=chronological(periodRows(table('rq02_annual_delays'),s.period)),y=activeYear(s,rows),x=rows.map(r=>r.year);
  let html=hero('RQ-02','Phân tích Độ trễ Chuyến bay (2016–2024)','Phân biệt tỷ lệ trễ ngưỡng ≥15 phút, trung bình có dấu và phân vị của từng năm.',periodToolbar(s,yearField('delay-year',y,rows.map(r=>[r.year,String(r.year)]))));
  html+=`<section class="metrics-grid">${metricCard(`Tỷ lệ trễ đến (${y})`,pct(annualMeta(y,'KPI-02').value*100),'',annualMeta(y,'KPI-02'),{color:'blue',caption:'ARR_DELAY ≥ 15; cùng cohort với mẫu số.'})}${metricCard(`Tỷ lệ trễ khởi hành (${y})`,pct(annualMeta(y,'KPI-04').value*100),'',annualMeta(y,'KPI-04'),{color:'teal',caption:'DEP_DELAY ≥ 15; không dùng N của ARR_DELAY.'})}${metricCard(`Mean trễ đến có dấu (${y})`,signed(annualMeta(y,'KPI-03').value),'phút',annualMeta(y,'KPI-03'),{caption:'Bao gồm đến sớm, không lấy giá trị tuyệt đối.'})}${metricCard(`P90 trễ đến (${y})`,n(annualMeta(y,'KPI-06/P90').value),'phút',annualMeta(y,'KPI-06/P90'),{caption:`P50 cùng năm: ${n(annualMeta(y,'KPI-06/P50').value)} phút.`})}</section><div class="toolbar" style="margin:0 0 20px">${check('Trễ đến','arr',s.arr)}${check('Trễ khởi hành','dep',s.dep)}${check('Baseline 0 phút','zero',s.zero)}${check('Hiển thị P90','p90',s.p90)}</div>`;
  const rate=[],means=[];
  if(s.arr){rate.push(line('Trễ đến',x,rows.map(r=>r.arr_delay_ge_15_rate_pct),rows.map(r=>annualMeta(r.year,'KPI-02')),C.blue,{unit:'%'}));means.push(line('Mean trễ đến',x,rows.map(r=>r.arr_delay_signed_mean_min),rows.map(r=>annualMeta(r.year,'KPI-03')),C.blue,{unit:'phút',signed:true}));}
  if(s.dep){rate.push(line('Trễ khởi hành',x,rows.map(r=>r.dep_delay_ge_15_rate_pct),rows.map(r=>annualMeta(r.year,'KPI-04')),C.teal,{dash:'dash',unit:'%'}));means.push(line('Mean trễ khởi hành',x,rows.map(r=>r.dep_delay_signed_mean_min),rows.map(r=>annualMeta(r.year,'KPI-05')),C.teal,{dash:'dash',unit:'phút',signed:true}));}
  html+=`<div class="cards-two">${chart('delay-rates','Tỷ lệ trễ đến và trễ khởi hành','Cùng ngưỡng 15 phút; mẫu số riêng từng measure.',rate,{yaxis:{ticksuffix:'%',rangemode:'tozero'}},{source:'rq02_annual_delays',scope:rate.length?'Giá trị từng năm':'Bật ít nhất một chuỗi để xem'})}${chart('delay-means','Mức trễ trung bình có dấu','Trục âm biểu thị đến/đi sớm hơn thời gian dự kiến.',means,{yaxis:{ticksuffix:'m',zeroline:s.zero}},{source:'rq02_annual_delays',note:'Mean dùng toàn bộ accepted records đủ điều kiện của measure, không chỉ những bản ghi trễ dương.'})}</div>`;
  const quantiles=[line('P50 (Median)',x,rows.map(r=>r.arr_delay_p50_min),rows.map(r=>annualMeta(r.year,'KPI-06/P50')),C.ink,{unit:'phút',signed:true})];
  if(s.p90)quantiles.push(line('P90',x,rows.map(r=>r.arr_delay_p90_min),rows.map(r=>annualMeta(r.year,'KPI-06/P90')),C.blue,{unit:'phút',signed:true}));
  html+=chart('delay-quantiles','Phân vị trễ đến: P50 và P90','Phân vị đã xuất bản cho từng năm; không lấy trung bình phân vị giữa các năm.',quantiles,{yaxis:{ticksuffix:'m',zeroline:s.zero}},{source:'KPI-06 · rq02_annual_delays',className:'tall',scope:'percentile_approx · accuracy=10000',note:'Sai số thứ hạng tương đối ≤0,0001 = 0,01%. Không cam kết sai số giá trị bằng một số phút cố định; không có percentile toàn kỳ trong Dashboard.'});
  const enriched=rows.map(r=>({...r,n_arr:annualMeta(r.year,'KPI-02').n,n_dep:annualMeta(r.year,'KPI-04').n,coverage:annualMeta(r.year,'KPI-02').coverage}));
  html+=tablePanel('delay-table','Bảng chỉ số độ trễ theo năm','Số mẫu đến/khởi hành lấy từ chính stream KPI tương ứng.',[yearCol,numCol('n_arr','N_valid ARR'),numCol('n_dep','N_valid DEP'),pctCol('arr_delay_ge_15_rate_pct','Trễ đến (%)'),pctCol('dep_delay_ge_15_rate_pct','Trễ đi (%)'),minCol('arr_delay_signed_mean_min','Mean ARR (phút)'),minCol('dep_delay_signed_mean_min','Mean DEP (phút)'),numCol('arr_delay_p50_min','P50 (phút)'),numCol('arr_delay_p90_min','P90 (phút)'),covCol],enriched,{source:'rq02_annual_delays',note:metadataDetails()});
  html+=researchNotes([['Mean và phân vị trả lời khác nhau','Năm 2020, mean trễ đến là -5,11 phút và P50 là -11 phút. Năm 2022, P90 là 42 phút. Các giá trị được so sánh theo đúng năm quan sát.','RES-005 · RES-006 · RES-007'],['Giữ dấu của độ trễ','Một bản ghi đến sớm vẫn thuộc cohort hợp lệ; không clip giá trị âm về 0 hoặc đổi thành độ trễ tuyệt đối.','KPI-03 / KPI-05 · Signed means'],['Giới hạn suy luận','Xu hướng này là thống kê mô tả trên dataset; không phải kiểm định hiệu quả nhân quả hoặc phân bố độ trễ của mọi hành khách.','Không Bootstrap / CI / p-value giả']]);
  return html;
}

function compare(){
  const s=state.compare;
  let html=hero('RQ-03','So sánh Hiệu suất Vận hành','So sánh các cohort đã xuất bản theo hãng, sân bay và tuyến bay có hướng. Không ghép giao các chiều không có trong dữ liệu.');
  html+=`<div class="tabs" role="tablist" aria-label="Nhóm so sánh">${[['carrier','Hãng bay','plane'],['airport','Sân bay','volume'],['route','Tuyến bay có hướng','compare']].map(([id,label,ic])=>`<button class="tab ${s.tab===id?'active':''}" role="tab" aria-selected="${s.tab===id}" data-tab="${id}">${icon(ic)}${e(label)}</button>`).join('')}</div>`;
  return html+(s.tab==='carrier'?carrierView():s.tab==='airport'?airportView():routeView());
}
function carrierView(){
  const s=state.compare,rows=table('rq03_carrier_performance').filter(r=>r.year===s.year);
  if(!rows.some(r=>r.carrier===s.carrier))s.carrier=rows[0]?.carrier;
  const selected=rows.find(r=>r.carrier===s.carrier),rank=topRows(rows.filter(r=>M('carrier-year',r.year,r.carrier,'KPI-02')?.status==='SUFFICIENT'),'volume',10);
  const trend=YEARS.map(year=>table('rq03_carrier_performance').find(r=>r.carrier===s.carrier&&r.year===year)??{year,carrier:s.carrier,arr_delay_ge_15_rate_pct:null});
  let html=`<div class="filters-panel"><div class="control-row">${yearField('compare-year',s.year)}${field('Hãng phân tích','compare-carrier',rows.map(r=>[r.carrier,r.carrier]),s.carrier)}${resetButton()}</div><div class="sample-rule">Carrier-year: N_min = 1.000<br>${badge('SUFFICIENT')} N_valid ≥3.000<br>Ranking chính thức: chỉ tập SUFFICIENT của KPI đang xếp hạng.</div></div>`;
  html+=`<div class="cards-two">${chart('carrier-rank',`Tỷ lệ trễ đến của nhóm hãng có sản lượng lớn (${s.year})`,'Chọn tối đa 10 hãng theo volume, không phải danh sách 10 hãng tốt nhất.',[bars('Tỷ lệ trễ đến',rank.map(r=>r.carrier),rank.map(r=>r.arr_delay_ge_15_rate_pct),rank.map(r=>M('carrier-year',r.year,r.carrier,'KPI-02')),C.blue,{horizontal:true,unit:'%',digits:2,colors:rank.map(r=>r.carrier===s.carrier?C.primary:'#5b8ff5')})],{margin:{l:45,r:35,t:15,b:38},xaxis:{type:'linear',ticksuffix:'%',rangemode:'tozero'},yaxis:{type:'category',autorange:'reversed',showgrid:false}},{source:'rq03_carrier_performance',className:'horizontal',scope:'Bấm vào thanh hoặc dòng bảng để chọn hãng'})}${chart('carrier-trend',`Xu hướng ${s.carrier} (2016–2024)`,'Tỷ lệ trễ đến; năm đang chọn được đánh dấu.',[line('Trễ đến',trend.map(r=>r.year),trend.map(r=>r.arr_delay_ge_15_rate_pct),trend.map(r=>M('carrier-year',r.year,r.carrier,'KPI-02')),C.blue,{unit:'%',selectedX:s.year})],{xaxis:annualAxis(),yaxis:{ticksuffix:'%',rangemode:'tozero'},shapes:yearHighlight(s.year)},{source:'rq03_carrier_performance',className:'horizontal'})}</div>`;
  const enriched=rows.map(r=>({...metadataRow(r,'carrier-year',r.carrier,'KPI-02'),n_dep:M('carrier-year',r.year,r.carrier,'KPI-04')?.n}));
  html+=tablePanel('carrier-table',`Hiệu suất hãng bay năm ${s.year}`,'Mã hãng theo dataset. Chọn dòng để xem xu hướng của hãng.',[{key:'carrier',label:'Hãng',html:r=>`<button class="table-pick" data-carrier="${e(r.carrier)}"><span class="selection-ring"></span>${e(r.carrier)}</button>`},numCol('volume','Accepted records'),numCol('n_valid','N_valid ARR'),numCol('n_dep','N_valid DEP'),pctCol('arr_delay_ge_15_rate_pct','Trễ đến (%)'),pctCol('dep_delay_ge_15_rate_pct','Trễ đi (%)'),minCol('arr_delay_signed_mean_min','Mean ARR (phút)'),{key:'min_n_status',label:'Mức mẫu ARR',html:r=>badge(r.min_n_status)},covCol],enriched,{source:'rq03_carrier_performance',selected:r=>r.carrier===s.carrier,note:'N_valid ARR and DEP are listed separately. Cohort ranks are descriptive and do not imply causality.'});
  html+=note('Phạm vi của bảng.',`Hãng ${s.carrier} năm ${s.year}: ${n(selected.volume)} bản ghi. Biểu đồ xu hướng giữ các năm hãng có dữ liệu, không suy thêm năm vắng mặt.`);
  return html;
}

function airportView(){
  const s=state.compare,origin=s.role==='origin',family=origin?'origin-year':'dest-year',key=origin?'origin_airport':'dest_airport',name=origin?'rq03_origin_airports':'rq03_dest_airports',rateKey=origin?'dep_delay_ge_15_rate_pct':'arr_delay_ge_15_rate_pct',meanKey=origin?'dep_delay_signed_mean_min':'arr_delay_signed_mean_min',taxiKey=origin?'taxi_out_mean_min':'taxi_in_mean_min',stream=origin?'KPI-04':'KPI-02',taxiStream=origin?'KPI-07/TAXI_OUT':'KPI-07/TAXI_IN';
  const rows=table(name).filter(r=>r.year===s.year);if(!rows.some(r=>r[key]===s.airport))s.airport=rows[0]?.[key];
  const rank=topRows(rows,rateKey,10),trend=YEARS.map(year=>table(name).find(r=>r[key]===s.airport&&r.year===year)??{year,[key]:s.airport,[taxiKey]:null});
  let html=`<div class="filters-panel"><div class="control-row">${yearField('compare-year',s.year)}${field('Vai trò sân bay','airport-role',[['origin','Khởi hành · Origin'],['dest','Điểm đến · DEST']],s.role)}${field('Sân bay','compare-airport',rows.map(r=>r[key]).sort(),s.airport)}${resetButton()}</div><div class="sample-rule">Airport-year: N_min=365<br>SUFFICIENT: N_valid ≥1.095<br>T-014 chỉ giữ cohort SUFFICIENT trên từng measure liên quan.</div></div>`;
  const taxiTrace=line(`Taxi-${origin?'out':'in'} · ${s.airport} · ${origin?'Origin':'DEST'}`,trend.map(r=>r.year),trend.map(r=>r[taxiKey]),trend.map(r=>M(family,r.year,r[key],taxiStream)),C.teal,{unit:'phút',selectedX:s.year});
  html+=`<div class="cards-two">${chart('airport-rank',`10 sân bay có tỷ lệ trễ ${origin?'khởi hành':'đến'} cao (${s.year})`,'Xếp hạng trong tập sân bay đã xuất bản đủ mẫu.',[bars('Tỷ lệ trễ',rank.map(r=>r[key]),rank.map(r=>r[rateKey]),rank.map(r=>M(family,r.year,r[key],stream)),origin?C.teal:C.blue,{horizontal:true,unit:'%',digits:2,colors:rank.map(r=>r[key]===s.airport?C.primary:origin?'#379c91':'#5b8ff5')})],{margin:{l:50,r:35,t:15,b:38},xaxis:{type:'linear',ticksuffix:'%',rangemode:'tozero'},yaxis:{type:'category',autorange:'reversed',showgrid:false}},{source:name,className:'horizontal',scope:'Bấm vào thanh để chọn sân bay'})}${chart('airport-taxi',`Taxi-${origin?'out':'in'} tại ${s.airport} theo năm`,'Xu hướng toàn kỳ; năm chọn được làm nổi bật. Chưa có dữ liệu sân bay–tháng.',[taxiTrace],{xaxis:annualAxis(),yaxis:{ticksuffix:'m',rangemode:'tozero',title:{text:'Phút'}},shapes:yearHighlight(s.year)},{source:name,className:'horizontal',scope:'N_valid riêng measure taxi · 2024 PARTIAL'})}</div>`;
  const enriched=rows.map(r=>({...metadataRow(r,family,r[key],stream),n_taxi:M(family,r.year,r[key],taxiStream)?.n}));
  html+=tablePanel('airport-table',`Sân bay ${origin?'khởi hành':'điểm đến'} — năm ${s.year}`,'Không cộng tổng Origin và DEST thành hai quần thể độc lập.',[{key,label:'Sân bay',html:r=>`<button class="table-pick" data-airport="${e(r[key])}"><span class="selection-ring"></span>${e(r[key])}</button>`},numCol('volume','Accepted records'),numCol('n_valid',origin?'N_valid DEP':'N_valid ARR'),pctCol(rateKey,'Tỷ lệ trễ (%)'),minCol(meanKey,'Mean trễ (phút)'),numCol('n_taxi','N_valid taxi'),numCol(taxiKey,origin?'Taxi-out (phút)':'Taxi-in (phút)',2),covCol],enriched,{source:name,selected:r=>r[key]===s.airport,note:'Các sân bay ngoài tập SUFFICIENT không có trong bảng T-014 này; bảng không đại diện mọi sân bay hoặc mọi cohort của T-013.'});
  return html;
}

function routeView(){
  const s=state.compare,rows=table('rq03_directed_routes');let r=rows.find(r=>r.city_pair===s.route)??rows[0];s.route=r.city_pair;
  const dirs=['fwd','ret'].map(d=>({route:r[`route_${d}`],volume:r[`volume_${d}`],rate:r[`arr_delay_rate_${d}_pct`],mean:r[`arr_delay_mean_${d}_min`],entity:r[`route_${d}`].replace(' -> ','>')}));
  const metas=dirs.map(d=>M('route-year',2019,d.entity,'KPI-02'));
  let html=`<div class="filters-panel"><div class="control-row"><span class="badge neutral">Năm 2019 · Phạm vi cố định</span>${field('Cặp tuyến đã xuất bản','compare-route',rows.map(r=>r.city_pair),s.route)}${resetButton()}</div><div class="sample-rule">Directed route-year: N_min=100<br>SUFFICIENT: N_valid ≥300 mỗi hướng.<br>Chỉ 10 cặp tuyến năm 2019 của T-014.</div></div>`;
  html+=`<section class="metrics-grid">${dirs.map((d,i)=>metricCard(d.route,pct(d.rate),'',metas[i],{color:i?'teal':'blue',caption:`${n(d.volume)} accepted records · Mean ${signed(d.mean)} phút`})).join('')}${metricCard('Chênh lệch tỷ lệ trễ',n(r.delay_rate_diff_pct,2),'điểm %',null,{caption:'Hiệu tuyệt đối giữa hai tỷ lệ đã công bố.',foot:'Không phải phần trăm thay đổi',color:'amber'})}${metricCard('Tổng bản ghi hai hướng',n(r.total_pair_volume),'',null,{caption:'Không dùng làm mẫu số chung cho tỷ lệ từng chiều.',foot:'Cộng hai tập route có hướng rời nhau'})}</section>`;
  html+=chart('route-pair',`Tính bất đối xứng của cặp tuyến ${r.city_pair} (2019)`,'Hai hướng có mẫu số riêng; không giải thích khác biệt bằng thời tiết hoặc nhân quả.',dirs.map((d,i)=>bars(d.route,[d.route],[d.rate],[metas[i]],i?C.teal:C.blue,{unit:'%',digits:2})),{yaxis:{ticksuffix:'%',rangemode:'tozero'},barmode:'group'},{source:'rq03_directed_routes',scope:'KPI-02 · N_valid của từng hướng'});
  const data=rows.map(r=>({...r,n_fwd:M('route-year',2019,r.route_fwd.replace(' -> ','>'),'KPI-02')?.n,n_ret:M('route-year',2019,r.route_ret.replace(' -> ','>'),'KPI-02')?.n}));
  html+=tablePanel('route-table','10 cặp tuyến đối ứng năm 2019','Chọn cặp tuyến bằng bộ chọn bên trên.',[{key:'city_pair',label:'Cặp tuyến'},{key:'route_fwd',label:'Hướng 1'},numCol('n_fwd','N_valid hướng 1'),pctCol('arr_delay_rate_fwd_pct','Trễ hướng 1 (%)'),{key:'route_ret',label:'Hướng 2'},numCol('n_ret','N_valid hướng 2'),pctCol('arr_delay_rate_ret_pct','Trễ hướng 2 (%)'),numCol('delay_rate_diff_pct','Chênh lệch (điểm %)',2)],data,{source:'rq03_directed_routes',selected:r=>r.city_pair===s.route});
  return html;
}

function pandemic(){
  const s=state.pandemic,rows=chronological(table('rq04_pandemic_comparison')),base=rows.find(r=>r.year===2019),shock=rows.find(r=>r.year===2020),x=rows.map(r=>r.year);
  let html=hero('RQ-04','Giai đoạn 2020: So sánh Dữ liệu Quan sát 2019–2021','So sánh quy mô và hiệu suất trước, trong và sau năm 2020. Đây là phân tích mô tả trên dataset.',`<div class="toolbar"><span class="badge neutral">Phạm vi cố định · 2019–2021</span><button class="button ${s.relative?'toggled':''}" id="relative-toggle" aria-pressed="${s.relative}">${icon('compare')}Biến động sản lượng so với 2019 (%)</button><button class="button ${s.highlight?'toggled':''}" id="event-toggle" aria-pressed="${s.highlight}">${icon('pandemic')}Đánh dấu tháng 4 & 5/2020</button>${resetButton()}</div>`);
  html+=`<section class="metrics-grid">${metricCard('Số bản ghi năm 2020',n(shock.total_records),'',annualMeta(2020,'KPI-01'),{caption:`${signed(relativeChange(shock.total_records,base.total_records))}% so với 2019`,icon:'data'})}${metricCard('Tỷ lệ trễ đến năm 2020',pct(shock.arr_delay_ge_15_rate_pct),'',annualMeta(2020,'KPI-02'),{color:'blue',caption:`2019: ${pct(base.arr_delay_ge_15_rate_pct)}`})}${metricCard('Mean trễ đến năm 2020',signed(shock.arr_delay_signed_mean_min),'phút',annualMeta(2020,'KPI-03'),{color:'teal',caption:`2019: ${signed(base.arr_delay_signed_mean_min)} phút`})}${metricCard('P90 trễ đến năm 2020',n(shock.arr_delay_p90_min),'phút',annualMeta(2020,'KPI-06/P90'),{caption:`2019: ${n(base.arr_delay_p90_min)} phút; không gộp phân vị.`})}</section>`;
  const volumes=rows.map(r=>s.relative?relativeChange(r.total_records,base.total_records):r.total_records);
  html+=`<div class="cards-two">${chart('pandemic-volume',s.relative?'Biến động sản lượng so với năm 2019':'Sản lượng bản ghi hàng năm (2019–2021)',s.relative?'Baseline 2019 = 0% thay đổi.':'Số bản ghi accepted trong dataset.',[bars('Sản lượng',x,volumes,rows.map(r=>annualMeta(r.year,'KPI-01')),C.blue,{millions:!s.relative,unit:s.relative?'%':'bản ghi',digits:s.relative?2:0,colors:[C.blue,C.amber,C.teal]})],{yaxis:{tickformat:s.relative?'.0f':'.2s',ticksuffix:s.relative?'%':'',rangemode:'tozero'}},{source:'rq04_pandemic_comparison'})}${chart('pandemic-rates','Tỷ lệ trễ đến và trễ khởi hành','Tỷ lệ riêng từng năm; đơn vị phần trăm.',[bars('Trễ đến',x,rows.map(r=>r.arr_delay_ge_15_rate_pct),rows.map(r=>annualMeta(r.year,'KPI-02')),C.blue,{unit:'%',digits:2}),bars('Trễ khởi hành',x,rows.map(r=>r.dep_delay_ge_15_rate_pct),rows.map(r=>annualMeta(r.year,'KPI-04')),C.teal,{unit:'%',digits:2})],{barmode:'group',yaxis:{ticksuffix:'%',rangemode:'tozero'}},{source:'rq04_pandemic_comparison'})}</div>`;
  const monthly=table('rq01_monthly_volume').filter(r=>r.year>=2019&&r.year<=2021),series=monthSeries(monthly,2019,2021);
  const marks=s.highlight?[{type:'line',xref:'x',x0:'2020-04',x1:'2020-04',yref:'paper',y0:0,y1:1,line:{color:C.amber,dash:'dot',width:2}},{type:'line',xref:'x',x0:'2020-05',x1:'2020-05',yref:'paper',y0:0,y1:1,line:{color:C.teal,dash:'dot',width:2}}]:[];
  const ann=s.highlight?[{x:'2020-04',y:179835,text:'T4/2020: 179.835',showarrow:true,arrowcolor:C.amber,font:{size:10,color:C.amber},ax:-80,ay:-40},{x:'2020-05',y:163767,text:'Đáy T5/2020: 163.767',showarrow:true,arrowcolor:C.teal,font:{size:10,color:C.teal},ax:90,ay:20}]:[];
  html+=chart('pandemic-monthly','Dòng thời gian sản lượng hàng tháng (2019–2021)','36 tháng quan sát; tháng 4 giảm sâu, tháng 5/2020 là đáy thực trong dữ liệu.',[line('Số bản ghi',series.map(r=>r.x),series.map(r=>r.value),series.map(r=>M('year-month',r.year,r.x,'KPI-01')),C.blue,{digits:0,unit:'bản ghi'})],{yaxis:{tickformat:'.2s',rangemode:'tozero'},xaxis:{nticks:12},shapes:marks,annotations:ann},{source:'rq01_monthly_volume',className:'tall',scope:'RES-003 · Không gọi tháng 4 là minimum'});
  html+=tablePanel('pandemic-table','Bảng so sánh giai đoạn 2019–2021','Giá trị gốc được giữ nguyên dù biểu đồ chuyển sang chế độ % thay đổi.',[yearCol,numCol('total_records','Accepted records'),pctCol('arr_delay_ge_15_rate_pct','Trễ đến (%)'),pctCol('dep_delay_ge_15_rate_pct','Trễ đi (%)'),minCol('arr_delay_signed_mean_min','Mean ARR (phút)'),minCol('dep_delay_signed_mean_min','Mean DEP (phút)'),numCol('arr_delay_p50_min','P50 (phút)'),numCol('arr_delay_p90_min','P90 (phút)')],rows,{source:'rq04_pandemic_comparison'});
  html+=researchNotes([['Biến động quan sát','Năm 2020 có 4.312.091 bản ghi, giảm 39,79% so với 2019. Tỷ lệ trễ đến là 9,73%.','RES-012 · Giá trị nghiệm thu'],['Thành phần mẫu','Quy mô và cơ cấu hoạt động có thể thay đổi qua từng năm. So sánh các tổng thể quan sát không đồng nghĩa một stable panel.','Không có stable-panel dataset được công bố'],['Giới hạn diễn giải','Không quy mọi thay đổi cho một nguyên nhân duy nhất, không trình bày p-value hay confidence interval chưa được nghiệm thu.','Descriptive / observational']]);
  return html;
}

function journey(){
  const s=state.journey,rows=chronological(periodRows(table('rq05_annual_journey_times'),s.period)),y=activeYear(s,rows),selected=rows.find(r=>r.year===y),x=rows.map(r=>r.year);
  let html=hero('RQ-05','Taxi & Thời gian Hành trình (2016–2024)','Thời gian lăn, thời gian trên không và so sánh thời lượng hành trình dự kiến với thực tế.',periodToolbar(s,yearField('journey-year',y,rows.map(r=>[r.year,String(r.year)]))));
  html+=`<section class="metrics-grid">${metricCard(`Taxi-out trung bình (${y})`,n(selected.taxi_out_mean_min,2),'phút',annualMeta(y,'KPI-07/TAXI_OUT'),{color:'blue',caption:'Thời gian lăn ra trước khi cất cánh.'})}${metricCard(`Taxi-in trung bình (${y})`,n(selected.taxi_in_mean_min,2),'phút',annualMeta(y,'KPI-07/TAXI_IN'),{color:'teal',caption:'Thời gian lăn vào sau khi hạ cánh.'})}${metricCard(`Air Time trung bình (${y})`,n(selected.air_time_mean_min,2),'phút',annualMeta(y,'KPI-08/AIR_TIME'),{caption:'Measure có mẫu số độc lập.'})}${metricCard(`Chênh lệch CRS − Actual (${y})`,signed(selected.schedule_buffer_mean_min),'phút',null,{caption:`N CRS: ${n(annualMeta(y,'KPI-08/CRS_ELAPSED_TIME').n)} · N Actual: ${n(annualMeta(y,'KPI-08/ACTUAL_ELAPSED_TIME').n)}`,foot:'Hiệu hai trung bình biên đã công bố',color:'teal'})}</section>`;
  html+=`<div class="cards-two">${chart('journey-taxi','Taxi-out và Taxi-in theo năm','Hai measure dùng N_valid riêng.',[line('Taxi-out',x,rows.map(r=>r.taxi_out_mean_min),rows.map(r=>annualMeta(r.year,'KPI-07/TAXI_OUT')),C.blue,{unit:'phút'}),line('Taxi-in',x,rows.map(r=>r.taxi_in_mean_min),rows.map(r=>annualMeta(r.year,'KPI-07/TAXI_IN')),C.teal,{unit:'phút'})],{yaxis:{ticksuffix:'m'}},{source:'rq05_annual_journey_times'})}${chart('journey-elapsed','So sánh thời gian hành trình','CRS Elapsed, Actual Elapsed và Air Time; không xếp chồng.',[line('CRS',x,rows.map(r=>r.crs_elapsed_mean_min),rows.map(r=>annualMeta(r.year,'KPI-08/CRS_ELAPSED_TIME')),C.blue,{dash:'dot',unit:'phút'}),line('Actual',x,rows.map(r=>r.actual_elapsed_mean_min),rows.map(r=>annualMeta(r.year,'KPI-08/ACTUAL_ELAPSED_TIME')),C.teal,{unit:'phút'}),line('Air Time',x,rows.map(r=>r.air_time_mean_min),rows.map(r=>annualMeta(r.year,'KPI-08/AIR_TIME')),C.grey,{unit:'phút'})],{yaxis:{ticksuffix:'m'}},{source:'rq05_annual_journey_times'})}</div>`;
  html+=chart('journey-difference','Chênh lệch giữa hai trung bình đã công bố','mean(CRS Elapsed Time) − mean(Actual Elapsed Time)',[bars('Hiệu hai trung bình',x,rows.map(r=>r.schedule_buffer_mean_min),[],C.blue,{digits:2,unit:'phút',text:rows.map(r=>signed(r.schedule_buffer_mean_min))})],{yaxis:{ticksuffix:'m',rangemode:'tozero'}},{source:'rq05_annual_journey_times',note:'Không phải trung bình hiệu số trên từng chuyến; không phải bằng chứng về hành vi đệm lịch trình. N_valid CRS và ACTUAL có thể khác nhau; xem bảng mẫu bên dưới.',scope:'Đơn vị phút · Không có mẫu số chung cho hiệu hai means'});
  const enriched=rows.map(r=>({...r,n_taxi_out:annualMeta(r.year,'KPI-07/TAXI_OUT').n,n_taxi_in:annualMeta(r.year,'KPI-07/TAXI_IN').n,n_air:annualMeta(r.year,'KPI-08/AIR_TIME').n,n_actual:annualMeta(r.year,'KPI-08/ACTUAL_ELAPSED_TIME').n,n_crs:annualMeta(r.year,'KPI-08/CRS_ELAPSED_TIME').n,coverage:annualMeta(r.year,'KPI-08/CRS_ELAPSED_TIME').coverage}));
  html+=tablePanel('journey-table','Bảng thời gian hành trình theo năm','Giá trị và mẫu số riêng; cuộn ngang để xem đủ measures.',[yearCol,numCol('taxi_out_mean_min','Taxi-out (phút)',2),numCol('taxi_in_mean_min','Taxi-in (phút)',2),numCol('air_time_mean_min','Air Time (phút)',2),numCol('actual_elapsed_mean_min','Actual (phút)',2),numCol('crs_elapsed_mean_min','CRS (phút)',2),minCol('schedule_buffer_mean_min','CRS − Actual (phút)'),covCol],enriched,{source:'rq05_annual_journey_times',note:metadataDetails()});
  html+=tablePanel('journey-samples','N_valid của từng measure','Ví dụ 2020: N_valid CRS =4.312.090, N_valid Actual =4.312.091.',[yearCol,numCol('n_taxi_out','N Taxi-out'),numCol('n_taxi_in','N Taxi-in'),numCol('n_air','N Air Time'),numCol('n_actual','N Actual'),numCol('n_crs','N CRS')],enriched);
  html+=researchNotes([['Giữ độc lập mẫu số','Taxi và các thời lượng có thể có số bản ghi đủ điều kiện khác nhau. Không copy denominator của measure khác.','DC-12 · KPI-07 / KPI-08'],['Giới hạn của hiệu trung bình','Năm 2020: CRS 138,47 phút, Actual 131,39 phút; hiệu khoảng +7,08 phút. Không phải ước lượng paired ở cấp từng chuyến.','RES-018 · Difference of published means'],['Đơn vị và phạm vi','7 measure CORE được kiểm chứng mẫu theo TS-018 Option B; không tính thời lượng từ chuỗi timestamp hoặc tự cộng 24 giờ.','OR-03 · FP-DEC-007 /019']]);
  return html;
}

const resultTitles={
  'RES-001':'Quy mô 9 năm của dataset','RES-002':'Số năm tháng 7 đạt đỉnh sản lượng','RES-003':'Sản lượng tháng 4/2020; đáy thực tháng 5',
  'RES-004':'Tỷ lệ trễ đến năm 2022','RES-005':'Mean trễ đến có dấu năm 2020','RES-006':'P50 trễ đến năm 2020','RES-007':'P90 trễ đến năm 2022',
  'RES-008':'Sản lượng gộp 9 năm của WN','RES-009':'Tỷ lệ trễ đến gộp của DL','RES-010':'Tỷ lệ trễ khởi hành EWR năm 2022','RES-011':'Bất đối xứng tuyến LGA ↔ ORD năm 2019',
  'RES-012':'Biến động sản lượng 2020 so với 2019','RES-013':'Tỷ lệ đến dưới ngưỡng 15 phút, tháng 4/2020','RES-014':'Tỷ lệ trễ đến năm 2022',
  'RES-015':'Taxi-out trung bình năm 2020','RES-016':'Taxi-in trung bình năm 2020','RES-017':'Taxi-out JFK năm 2023','RES-018':'Hiệu CRS − Actual trung bình năm 2020',
  'RES-019':'Actual Elapsed trung bình năm 2016','RES-020':'Số ngày quan sát năm 2024',
};
function resultValue(r){const unit={percent:'%',percentage_points:'điểm %',percent_change:'%',minutes:'phút',flights:'bản ghi',days:'ngày',years:'năm'}[r.unit]||r.unit;return `${n(r.observed_value,['flights','days','years'].includes(r.unit)?0:2)} ${unit}`;}
function resultLimit(r){
  if(r.res_id==='RES-018')return 'Hiệu 2 means; N CRS2020=4.312.090, Actual=4.312.091; N register là cohort context.';
  if(r.res_id==='RES-003')return 'T4:179.835; T5:163.767 là đáy. Không gọi tháng 4 là minimum.';
  if(r.res_id==='RES-008'||r.res_id==='RES-009'||r.res_id==='RES-001'||r.res_id==='RES-002')return 'Có năm 2024 PARTIAL; không phải coverage toàn thị trường Mỹ.';
  if(r.res_id==='RES-010')return 'Cohort EWR2022; ảnh liên quan có thể vẽ bối cảnh năm khác.';
  if(r.res_id==='RES-011')return '2019; N_valid riêng mỗi hướng; chênh lệch đơn vị điểm phần trăm.';
  if(r.res_id==='RES-017')return 'Chỉ primary observation JFK2023; không sao chép thứ hạng phụ trong narrative cũ.';
  return r.source_coverage_status==='PARTIAL'?'2024: thiếu tháng 3, chỉ335/366 ngày.':r.kpi_id==='KPI-06'?'Phân vị xấp xỉ của riêng cohort; không gộp các năm.':'Giới hạn mô tả; units bounded TS-018 Option B; không nhân quả.';
}
function evidence(){
  const s=state.evidence;
  let html=hero('Data provenance','Nguồn Dữ liệu, Phương pháp & Sổ Kết quả (RES)','Truy vết từ bảng tổng hợp đã nghiệm thu đến biểu đồ và các quan sát nghiên cứu.',`<div class="toolbar"><a class="button" href="downloads/RESULTS_REGISTER.json" download>${icon('download')}Results Register JSON</a><a class="button" href="downloads/CHART_INVENTORY.json" download>${icon('download')}Chart Inventory</a><a class="button primary" href="downloads/DASHBOARD_PROJECT_HANDOFF.md" download>Handoff Doc</a></div>`);
  html+=`<section class="metrics-grid">${metricCard('Curated Parquet',n(117),'files',null,{caption:'9 run theo năm · 3.308.617.408 bytes',foot:'Không được đọc lại khi chạy website',icon:'data'})}${metricCard('Dòng KPI đã xuất bản',n(684180),'',null,{caption:'8 CORE KPIs · 12 streams · 57.015 cohorts',foot:'kpi_run_2016_2024_v1',icon:'data'})}${metricCard('Kết quả nghiên cứu (RES)',n(db.results.length),'',null,{caption:'Giá trị primary theo register hiện hành',foot:'Không phải kiểm định ý nghĩa thống kê'})}${metricCard('Biểu đồ chính thức',n(db.charts.length),'',null,{caption:'16 PNG + 16 SVG, giữ nguyên ảnh gốc',foot:'t014_analysis_2016_2024_v4'})}</section>`;
  html+=`<section class="panel"><div class="card-heading"><h2>4 giới hạn nghiên cứu bắt buộc</h2><span class="badge caution">MINH BẠCH PHẠM VI</span></div><div class="panel-inner limit-grid">${[
    ['OR-03 · Kiểm chứng mẫu đơn vị CORE','TS-018 Option B: 1.500 bản ghi tháng 1/2019 ×7 measures =10.500 đối soát. Không tương đương xác thực mọi giá trị của 9 năm; PARQUET_PARITY_NOT_TESTED.'],
    ['OR-05 · Năm 2024 thiếu tháng 3','Chỉ335/366 ngày,11 tháng quan sát. Không điền 0, không nội suy và không so tổng lượng như năm đủ mà thiếu cảnh báo.'],
    ['OR-07 · Weather ngoài CORE','Weather có CONDITIONAL_NO_GO. Không thêm biểu đồ thời tiết hoặc giả định đơn vị/join đã được xác minh.'],
    ['OR-08 · Source identity chưa xác minh','IDENTITY_UNVERIFIED / ACCEPTED_NON_BLOCKING. Hash cục bộ và mẫu BTS không chứng thực danh tính upstream đầy đủ.'],
  ].map((r,i)=>`<article class="limit"><h3><span class="limit-number">${i+1}</span>${e(r[0])}</h3><p>${e(r[1])}</p></article>`).join('')}</div></section>`;
  html+=`<div class="cards-two"><section class="panel"><div class="card-heading"><h2>Định nghĩa thống kê</h2></div><div class="panel-inner"><p class="note"><strong>Ngưỡng trễ:</strong> ARR_DELAY hoặc DEP_DELAY ≥15 phút trên mẫu số hợp lệ của chính measure.<br><strong>Signed mean:</strong> giữ giá trị âm của bản ghi đến/đi sớm.<br><strong>Phân vị:</strong> percentile_approx, accuracy=10000, ε_rank ≤0,0001=0,01%. Không hứa sai số phút cố định.</p></div></section><section class="panel"><div class="card-heading"><h2>Quy tắc mẫu FP-DEC-016</h2></div><div class="panel-inner"><p class="note"><strong>N_min:</strong> carrier-year1.000; airport-year365; directed route-year100.<br><strong>SUPPRESSED:</strong> N_valid &lt;N_min.<br><strong>LOW_SAMPLE_CAUTION:</strong> N_min ≤N_valid &lt;3×N_min.<br><strong>SUFFICIENT:</strong> N_valid ≥3×N_min. Không phải confidence/significance.</p></div></section></div>`;
  const filtered=searchResults(db.results,s.query,s.rq);
  const resultRows=filtered.map(r=>({...r,title:resultTitles[r.res_id],formatted_value:resultValue(r),limit:resultLimit(r)}));
  html+=`<section class="panel"><div class="card-heading"><div><h2>Tra cứu 20 kết quả nghiên cứu thực nghiệm</h2><p>Primary observation và cohort gốc. Không tự thay đổi kết quả đã nghiệm thu.</p></div><div class="panel-actions"><label class="select-label" for="res-search">Tìm RES / cohort / bảng<input class="search-field" id="res-search" type="search" placeholder="Ví dụ: RES-018, 2020, JFK…" value="${e(s.query)}"></label>${field('Câu hỏi nghiên cứu','res-rq',[['ALL','Tất cả RQ'],...['01','02','03','04','05'].map(v=>[`RQ-${v}`,`RQ-${v}`])],s.rq)}</div></div><div class="panel-inner" style="padding-top:0">${note('Lưu ý.', 'RES là phát hiện của cohort gốc, không phải nhận xét tự động cho mọi lựa chọn filter. Register gốc được giữ nguyên để tải về.')}</div></section>`;
  html+=tablePanel('res-table','Results Register','N trong register có thể là context cohort (ví dụ RES-018); xem giới hạn từng dòng.',[{key:'res_id',label:'RES',html:r=>`<span class="result-id">${e(r.res_id)}</span><br>${e(r.rq_id)}`},{key:'title',label:'Quan sát chính',html:r=>`<strong>${e(r.title)}</strong><br><span class="mono">${e(r.formatted_value)}</span><br><span class="muted">Cohort: ${e(r.cohort_id)}</span>`},numCol('count_metric_valid','N register'),{key:'table_reference',label:'Bảng nguồn',html:r=>`<a class="mono" href="downloads/${e(r.table_reference.replace('.parquet','.csv'))}" download>${e(r.table_reference)}</a>`},{key:'chart_id',label:'Chart',html:r=>{const i=db.charts.findIndex(c=>c.chart_id===r.chart_id);return i<0?e(r.chart_id):`<button class="link-button" data-chart="${i}">Xem ảnh<br>${e(r.chart_id)}</button>`;}},{key:'limit',label:'Giới hạn áp dụng'}],resultRows,{className:'result-table',exportColumns:[{key:'res_id',label:'RES'},{key:'rq_id',label:'RQ'},{key:'title',label:'Observation'},{key:'cohort_id',label:'Cohort'},{key:'observed_value',label:'Value'},{key:'unit',label:'Unit'},{key:'count_metric_valid',label:'N register'},{key:'table_reference',label:'Source table'},{key:'chart_id',label:'Chart'},{key:'limit',label:'Limitations'}],foot:'20 RES chính thức · Lọc theo RQ/cohort/bảng'});
  const charts=db.charts.map((c,i)=>({...c,index:i})).filter(c=>s.rq==='ALL'||c.rq_id===s.rq);
  html+=`<section class="panel"><div class="card-heading"><div><h2>Thư viện biểu đồ chính thức</h2><p>Ảnh gốc từ Analytics v4. Bộ lọc RQ chỉ chọn ảnh; không thay đổi nội dung ảnh theo năm/entity.</p></div><span class="badge ok">${charts.length}/16 figures · PNG / SVG</span></div><div class="gallery">${charts.map(c=>`<article class="gallery-card"><button class="gallery-preview" data-chart="${c.index}" aria-label="Xem ${e(c.title_vi)}"><img loading="lazy" src="charts/${e(c.png_file)}" alt="${e(c.title_vi)}"></button><div class="gallery-text"><span class="badge neutral">${e(c.rq_id)}</span><strong>${e(c.title_vi)}</strong><p class="mono">${e(c.chart_id)}<br>${e(c.supporting_res_ids.join(' · '))}</p></div><div class="gallery-links"><a href="charts/${e(c.svg_file)}" download>SVG ↓</a><a href="charts/${e(c.png_file)}" download>PNG ↓</a></div></article>`).join('')}</div></section>`;
  html+=`<section class="panel"><div class="card-heading"><h2>Nguồn kỹ thuật & cách đọc Dashboard</h2></div><div class="panel-inner"><p class="mono">Analytics: ${e(db.analysis_run)}<br>KPI: ${e(db.kpi_run)}<br>KPI version: ${e(db.kpi_version)} · Quality contract: ${e(db.quality_version)}</p><p class="description muted" style="margin-top:12px">Dashboard chỉ đọc gói tổng hợp local. Không có truy vấn Spark, dữ liệu trực tiếp hoặc quyền production D5. Size/mtime không phải bằng chứng content identity; thông tin nguồn và các khác biệt giữa mockup với artifact được ghi trong tài liệu bàn giao.</p></div></section>`;
  return html;
}

const renderers={overview,volume,delay,compare,pandemic,journey,evidence};
async function render(){
  const version=++renderVersion;
  for(const el of document.querySelectorAll('.js-plotly-plot'))globalThis.Plotly?.purge(el);
  chartJobs.length=0;tableRegistry.clear();renderShell();
  $('main').innerHTML=renderers[page]();document.title=`${NAV.find(n=>n[0]===page)[1]} · AeroMetric`;
  try{await drawCharts((id,ev)=>{
    const pt=ev.points?.[0];if(!pt)return;
    if(id==='carrier-rank'){state.compare.carrier=String(pt.y);render();}
    if(id==='airport-rank'){state.compare.airport=String(pt.y);render();}
  });if(version===renderVersion)document.dispatchEvent(new Event('aerometric:ready'));}
  catch(error){document.body.dataset.runtimeError='true';console.error(error);toast(error.message);}
}
function toast(message){$('toast').textContent=message;$('toast').hidden=false;setTimeout(()=>$('toast').hidden=true,4000);}
function resetCurrent(){
  const defaults={overview:{year:2019},volume:{period:'all',mean:true,marks:true},delay:{period:'all',year:2019,arr:true,dep:true,zero:true,p90:true},compare:{tab:state.compare.tab,year:2019,carrier:'WN',role:'origin',airport:'ORD',route:'LGA <-> ORD'},pandemic:{relative:false,highlight:true},journey:{period:'all',year:2019}};
  if(defaults[page])state[page]=defaults[page];render();
}
document.addEventListener('click',event=>{
  const b=event.target.closest('button');if(!b)return;
  if(b.dataset.overviewYear){state.overview.year=Number(b.dataset.overviewYear);render();}
  else if(b.dataset.period){state[page].period=b.dataset.period;render();}
  else if(b.dataset.reset){resetCurrent();}
  else if(b.dataset.tab){state.compare.tab=b.dataset.tab;render();}
  else if(b.dataset.carrier){state.compare.carrier=b.dataset.carrier;render();}
  else if(b.dataset.airport){state.compare.airport=b.dataset.airport;render();}
  else if(b.dataset.sort){sortTable(b.dataset.sort,b.dataset.key);}
  else if(b.dataset.export){exportTable(b.dataset.export);toast('Đã xuất CSV của bảng đang hiển thị.');}
  else if(b.id==='relative-toggle'){state.pandemic.relative=!state.pandemic.relative;render();}
  else if(b.id==='event-toggle'){state.pandemic.highlight=!state.pandemic.highlight;render();}
  else if(b.dataset.chart!=null){const c=db.charts[Number(b.dataset.chart)];$('dialog-title').textContent=c.title_vi;$('dialog-image').src=`charts/${c.svg_file}`;$('dialog-image').alt=c.title_vi;$('dialog-note').textContent=`${c.rq_id} · ${c.table_reference} · ${c.supporting_res_ids.join(', ')} · Ảnh chính thức giữ nguyên cohort gốc.`;$('chart-dialog').showModal();}
  else if(b.id==='close-dialog'){$('chart-dialog').close();}
});
document.addEventListener('change',event=>{
  const t=event.target;if(t.dataset.check){state[page][t.dataset.check]=t.checked;render();return;}
  const ids={'delay-year':()=>state.delay.year=Number(t.value),'journey-year':()=>state.journey.year=Number(t.value),'compare-year':()=>state.compare.year=Number(t.value),'compare-carrier':()=>state.compare.carrier=t.value,'airport-role':()=>state.compare.role=t.value,'compare-airport':()=>state.compare.airport=t.value,'compare-route':()=>state.compare.route=t.value,'res-rq':()=>state.evidence.rq=t.value};
  if(ids[t.id]){ids[t.id]();render();}
});
document.addEventListener('input',event=>{
  if(event.target.id!=='res-search')return;
  state.evidence.query=event.target.value;
  const t=tableRegistry.get('res-table');
  t.rows=searchResults(db.results,state.evidence.query,state.evidence.rq).map(r=>({...r,title:resultTitles[r.res_id],formatted_value:resultValue(r),limit:resultLimit(r)}));
  $('table-res-table').innerHTML=tableBody('res-table');$('table-count-res-table').textContent=`${t.rows.length}/20 RES phù hợp`;
});
window.addEventListener('hashchange',()=>{if(location.hash==='#main'){$('main').focus();return;}page=NAV.some(n=>n[0]===location.hash.slice(1))?location.hash.slice(1):'overview';window.scrollTo(0,0);if(db)render();});
window.addEventListener('error',()=>{document.body.dataset.runtimeError='true';});

async function boot(){
  try{
    const response=await fetch('data/dashboard.json');if(!response.ok)throw new Error(`Không đọc được dữ liệu (${response.status}).`);
    db=await response.json();if(db.analysis_run!=='t014_analysis_2016_2024_v4'||db.kpi_run!=='kpi_run_2016_2024_v1')throw new Error('Sai run dữ liệu đã phê duyệt.');
    page=NAV.some(n=>n[0]===location.hash.slice(1))?location.hash.slice(1):'overview';await render();
    // Read-only diagnostics for reproducible local verification, not a runtime API.
    window.aerometric={get page(){return page;},get state(){return structuredClone(state);},get versions(){return {analytics:db.analysis_run,kpi:db.kpi_run};}};
  }catch(error){console.error(error);$('main').innerHTML=`<section class="fatal"><h1>Không thể mở gói dữ liệu Dashboard</h1><p>${e(error.message)}</p><p class="muted">Chạy qua server local, không mở trực tiếp file HTML. Kiểm tra gói bằng lệnh verify trong hướng dẫn.</p></section>`;}
}
boot();
