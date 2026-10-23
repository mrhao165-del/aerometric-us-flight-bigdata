import {escapeHTML as e, number, signed, csvString} from './core.mjs';

export const colors = {blue:'#2563eb', primary:'#004ac6', teal:'#006a63', amber:'#b45309', grey:'#8993a8', ink:'#14263d'};
const paths = {
  plane:'m3 17 7-2-4-9 3-1 6 8 5-1c3 0 3 3 0 4l-6 1-5 5-2-1 2-4-6 1z',
  overview:'M3 3h7v7H3z M14 3h7v7h-7z M3 14h7v7H3z M14 14h7v7h-7z',
  volume:'M5 20V11 M12 20V4 M19 20V8 M3 21h19',
  delay:'M12 8v5l4 2 M21 12a9 9 0 1 1-18 0 9 9 0 0 1 18 0',
  compare:'M3 7h17l-4-4 M21 17H4l4 4 M20 7l-4 4 M4 17l4-4',
  pandemic:'M3 12a9 9 0 1 1 3 7 M3 6v6h6 M12 7v6l3 2',
  journey:'M5 4h5a4 4 0 0 1 0 8H7a4 4 0 0 0 0 8h12 M5 1v6 M19 17v6',
  evidence:'M3 4h7l2 2 2-2h7v16h-7l-2 2-2-2H3z M12 6v16',
  info:'M12 11v6 M12 7h.01 M21 12a9 9 0 1 1-18 0 9 9 0 0 1 18 0',
  download:'M12 3v12m-5-5 5 5 5-5 M4 16v5h16v-5',
  reset:'M3 11a9 9 0 1 1 2 7 M3 4v7h7',
  data:'M21 5c0 2-4 3-9 3S3 7 3 5s4-3 9-3 9 1 9 3 M3 5v14c0 2 4 3 9 3s9-1 9-3V5 M3 12c0 2 4 3 9 3s9-1 9-3',
  arrow:'M5 12h14m-5-5 5 5-5 5',
};
export function icon(name) {return `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.65" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="${paths[name] ?? paths.info}"/></svg>`;}
export function badge(value) {
  if (!value || value === 'NOT_APPLICABLE') return `<span class="badge neutral">Năm / tháng</span>`;
  const cls = value === 'SUFFICIENT' ? 'ok' : value === 'PARTIAL' || value === 'LOW_SAMPLE_CAUTION' ? 'caution' : 'neutral';
  return `<span class="badge ${cls}">${e(value)}</span>`;
}
export function field(label, id, values, selected) {
  return `<label class="select-label" for="${id}">${e(label)}<select id="${id}">${values.map(v => {const [value,text] = Array.isArray(v) ? v : [v,v]; return `<option value="${e(value)}" ${String(value)===String(selected)?'selected':''}>${e(text)}</option>`;}).join('')}</select></label>`;
}
export function action(label, attrs = '', name = 'download') {return `<button class="button" ${attrs}>${icon(name)}${e(label)}</button>`;}
export function metricCard(label, value, unit = '', meta = null, options = {}) {
  return `<article class="metric-card"><div class="metric-body"><div class="metric-label"><span>${e(label)}</span>${icon(options.icon || 'info')}</div><div class="metric-value ${options.color || ''} ${options.compact?'compact':''}">${e(value)}<span class="metric-unit">${e(unit)}</span></div><div class="metric-caption">${e(options.caption || '')}</div></div><div class="metric-foot">${meta?`<span title="Mẫu hợp lệ của chính chỉ số này">N_valid = ${number(meta.n)}</span>${badge(meta.coverage==='PARTIAL'?'PARTIAL':meta.status)}`:`<span>${e(options.foot || 'Dữ liệu tổng hợp đã xuất bản')}</span>`}</div></article>`;
}
export function hero(rq, title, description, tools = '', question = '') {
  return `<section class="hero"><div class="eyebrow">${e(rq)} · US flight performance research</div><div class="hero-top"><div><h1>${e(title)}</h1><p class="description">${e(description)}</p></div><div class="dataset-stamp"><strong><span class="dot"></span> 54.674.003 bản ghi accepted</strong>2016–2024 · 9 năm · 107 tháng</div></div>${question?`<div class="question">${icon('info')}<span><strong>Câu hỏi nghiên cứu:</strong> ${e(question)}</span></div>`:''}${tools}</section>`;
}
export function note(title, body, warning = false) {return `<div class="note${warning?' warning':''}"><strong>${e(title)}</strong> ${e(body)}</div>`;}
export function researchNotes(items) {return `<section class="notes-three">${items.map((x,i)=>`<article class="research-note"><div class="eyebrow">Quan sát ${String(i+1).padStart(2,'0')}</div><h3>${e(x[0])}</h3><p>${e(x[1])}</p><div class="mono">${e(x[2]||'Thống kê mô tả · Không suy diễn nhân quả')}</div></article>`).join('')}</section>`;}
export const chartJobs = [];
export function chart(id, title, subtitle, traces, layout = {}, options = {}) {
  chartJobs.push({id,traces,layout});
  return `<article class="chart-card"><div class="card-heading"><div><h2>${e(title)}</h2><p>${e(subtitle)}</p></div>${options.badge?badge(options.badge):''}</div><div id="${id}" class="chart ${options.className || ''}" role="img" aria-label="${e(title)}"></div><div class="chart-foot"><span>Nguồn: ${e(options.source || 'T-014 Analytics v4')}</span><span class="scope">${e(options.scope || 'Giá trị đã công bố · N_valid trong tooltip')}</span></div>${options.note?`<details><summary>Cách đọc và giới hạn</summary><p>${e(options.note)}</p></details>`:''}</article>`;
}
export function line(name, x, y, meta = [], color = colors.blue, options = {}) {
  const hasSelection=options.selectedX!=null;
  return {type:'scatter', mode:hasSelection?'lines+markers+text':'lines+markers', name, x, y, connectgaps:false,
    line:{color,width:2.4,dash:options.dash || 'solid',shape:'linear'},
    marker:{size:hasSelection?x.map(v=>String(v)===String(options.selectedX)?12:6):6,
      color:x.map(v=>String(v)===String(options.selectedX)?colors.primary:String(v).startsWith('2024')?colors.amber:color),line:{width:1.2,color:'#fff'}},
    text:hasSelection?y.map((v,i)=>v!=null&&String(x[i])===String(options.selectedX)?`${number(v,2)} ${options.unit||''}`:''):undefined,
    textposition:'top center',textfont:{family:'JetBrains,monospace',size:11,color:colors.primary},cliponaxis:!hasSelection,
    customdata:y.map((v,i)=>[meta[i]?.n == null?'—':number(meta[i].n),meta[i]?.coverage || (String(x[i]).startsWith('2024')?'PARTIAL':'VERIFIED_WITH_SCOPE'),options.signed?signed(v):number(v,options.digits??2)]),
    hovertemplate:`<b>${e(name)}</b><br>%{x}<br>Giá trị: %{customdata[2]} ${e(options.unit || '')}<br>N_valid: %{customdata[0]}<br>%{customdata[1]}<extra></extra>`,
  };
}
export function bars(name, x, y, meta = [], color = colors.blue, options = {}) {
  const horizontal = options.horizontal;
  return {type:'bar',name,x:horizontal?y:x,y:horizontal?x:y,orientation:horizontal?'h':'v',
    marker:{color:options.colors || x.map(v=>String(v).startsWith('2024')?colors.amber:color),line:{color:'rgba(0,0,0,.02)',width:1}},
    width:horizontal?0.6:undefined,
    text:options.text || y.map(v=> options.unit === '%' ? `${number(v,1)}%` : options.millions?`${number(v/1e6,2)}M`:number(v,options.digits??0)),
    textposition:options.hideText?'none':'auto',textfont:{size:10,family:'JetBrains,monospace'},
    customdata:y.map((v,i)=>[meta[i]?.n == null?'—':number(meta[i].n),meta[i]?.coverage || (String(x[i]).startsWith('2024')?'PARTIAL':'VERIFIED_WITH_SCOPE'),number(v,options.digits??2),String(x[i])]),
    hovertemplate:`<b>%{customdata[3]}</b><br>${e(name)}: %{customdata[2]} ${e(options.unit || '')}<br>N_valid: %{customdata[0]}<br>%{customdata[1]}<extra></extra>`,
  };
}
export async function drawCharts(onClick) {
  if (!globalThis.Plotly) throw new Error('Không tìm thấy thư viện biểu đồ offline. Hãy kiểm tra lại bundle.');
  await Promise.all(chartJobs.map(async job=>{
    const base = {paper_bgcolor:'#fff',plot_bgcolor:'#fff',font:{family:'Inter,Segoe UI,sans-serif',size:11,color:'#596378'},
      margin:{l:54,r:20,t:35,b:43},hovermode:'closest',dragmode:false,
      legend:{orientation:'h',y:1.16,x:0,font:{size:10},bgcolor:'rgba(255,255,255,.9)'},
      xaxis:{type:'category',tickfont:{family:'JetBrains,monospace',size:9},linecolor:'#dce4f2',showgrid:false,zeroline:false,fixedrange:true},
      yaxis:{gridcolor:'#edf1fa',zerolinecolor:'#9ba8bd',zerolinewidth:1,tickfont:{family:'JetBrains,monospace',size:9},fixedrange:true},
      hoverlabel:{bgcolor:'#14263d',font:{color:'#fff',family:'Inter',size:12},bordercolor:'#14263d'},
      bargap:.32,showlegend:job.traces.length>1,
    };
    const layout = {...base,...job.layout,xaxis:{...base.xaxis,...job.layout.xaxis},yaxis:{...base.yaxis,...job.layout.yaxis}};
    await Plotly.newPlot(job.id,job.traces,layout,{responsive:true,displaylogo:false,displayModeBar:false,scrollZoom:false});
    if(onClick) document.getElementById(job.id)?.on('plotly_click', ev=>onClick(job.id,ev));
  }));
}
export const tableRegistry = new Map();
export function tablePanel(id, title, subtitle, columns, rows, options = {}) {
  tableRegistry.set(id,{id,title,subtitle,columns,rows:[...rows],options,sort:null,desc:false});
  return `<section class="panel" id="panel-${id}"><div class="card-heading"><div><h2>${e(title)}</h2><p>${e(subtitle)}</p></div><div class="panel-actions">${action('CSV',`data-export="${id}"`)}${options.source?`<a class="button" href="downloads/${e(options.source)}.parquet" download>Parquet nguồn</a>`:''}</div></div><div id="table-${id}">${tableBody(id)}</div><div class="table-footer"><span id="table-count-${id}">${number(rows.length)} dòng · Sắp xếp bằng tiêu đề cột</span><span>${e(options.foot || 'N_valid riêng từng chỉ số · Không truy vấn Spark')}</span></div>${options.note?`<details><summary>Thông tin mẫu và phạm vi</summary><p>${e(options.note)}</p></details>`:''}</section>`;
}
export function tableBody(id) {
  const t = tableRegistry.get(id);
  if (!t.rows.length) return '<div class="empty">Không có cohort đã xuất bản cho lựa chọn này.</div>';
  return `<div class="table-wrap"><table class="${t.options.className || ''}"><thead><tr>${t.columns.map(c=>`<th scope="col"><button class="sort-button" data-sort="${id}" data-key="${c.key}">${e(c.label)} ${t.sort===c.key?(t.desc?'↓':'↑'):'↕'}</button></th>`).join('')}</tr></thead><tbody>${t.rows.map(r=>`<tr class="${Number(r.year)===2024?'partial ':''}${t.options.selected?.(r)?'selected':''}">${t.columns.map(c=>`<td>${c.html?c.html(r):e(c.format?c.format(r[c.key],r):r[c.key])}</td>`).join('')}</tr>`).join('')}</tbody></table></div>`;
}
export function sortTable(id,key) {
  const t = tableRegistry.get(id); if(!t) return;
  t.desc = t.sort===key?!t.desc:false;t.sort=key;
  t.rows.sort((a,b)=>{
    const v=a[key],w=b[key];if(v==null) return 1;if(w==null)return -1;
    const diff=typeof v==='number'&&typeof w==='number'?v-w:String(v).localeCompare(String(w),'vi',{numeric:true});
    return t.desc?-diff:diff;
  });
  document.getElementById(`table-${id}`).innerHTML=tableBody(id);
}
export function exportTable(id) {
  const t = tableRegistry.get(id); if(!t) return;
  // Export raw numeric values, not formatted labels/HTML; include selected metadata columns.
  const columns=t.options.exportColumns || t.columns;
  const csv = csvString(columns.map(c=>c.label),t.rows.map(r=>columns.map(c=>r[c.key])));
  const url=URL.createObjectURL(new Blob([csv],{type:'text/csv;charset=utf-8'}));
  const a=document.createElement('a');a.href=url;a.download=`AeroMetric_${id}.csv`;a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);
}
