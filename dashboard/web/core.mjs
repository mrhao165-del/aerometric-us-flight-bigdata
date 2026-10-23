export const YEARS = Array.from({length: 9}, (_, i) => 2016 + i);
export const PERIODS = [
  {id: 'all', label: 'Toàn kỳ 2016–2024', min: 2016, max: 2024},
  {id: 'before', label: '2016–2019', min: 2016, max: 2019},
  {id: 'shock', label: '2020–2021', min: 2020, max: 2021},
  {id: 'after', label: '2022–2024', min: 2022, max: 2024},
];
export function escapeHTML(s) {
  return String(s ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
}
export function number(n, digits = 0) {
  return n == null || !Number.isFinite(Number(n)) ? '—' : new Intl.NumberFormat('vi-VN', {minimumFractionDigits: digits, maximumFractionDigits: digits}).format(Number(n));
}
export function signed(n, digits = 2) {
  return n == null || !Number.isFinite(Number(n)) ? '—' : `${n > 0 ? '+' : ''}${number(n, digits)}`;
}
export function metric(db, family, year, entity, stream) {
  return db.metrics[`${family}|${year}|${entity}|${stream}`] ?? null;
}
export function status(n, family) {
  const min = {'carrier-year':1000, 'origin-year':365, 'dest-year':365, 'route-year':100}[family];
  if (!min) return 'NOT_APPLICABLE';
  return n < min ? 'SUPPRESSED' : n < 3 * min ? 'LOW_SAMPLE_CAUTION' : 'SUFFICIENT';
}
export function periodRows(rows, period = 'all') {
  const p = PERIODS.find(x => x.id === period) ?? PERIODS[0];
  return rows.filter(r => Number(r.year) >= p.min && Number(r.year) <= p.max);
}
export function chronological(rows, field = 'year') {
  return [...rows].sort((a,b) => String(a[field]).localeCompare(String(b[field]), 'en', {numeric:true}));
}
export function monthSeries(rows, min = 2016, max = 2024, valueKey = 'monthly_volume') {
  const lookup = new Map(rows.map(r => [r.year_month, r]));
  const values = [];
  for (let y = min; y <= max; y++) for (let m = 1; m <= 12; m++) {
    const key = `${y}-${String(m).padStart(2,'0')}`;
    const row = lookup.get(key);
    values.push({x:key, year:y, month:m, value:row?.[valueKey] ?? null, row:row ?? null});
  }
  return values;
}
export function annualAxis() {
  return {type:'linear',autorange:false,range:[YEARS[0]-.5,YEARS.at(-1)+.5],
    tickmode:'array',tickvals:YEARS,ticktext:YEARS.map(String),tickformat:'d',title:{text:'Năm'},fixedrange:true};
}
export function monthlyAxis(year) {
  const months=Array.from({length:12},(_,i)=>`${year}-${String(i+1).padStart(2,'0')}`);
  return {type:'category',categoryorder:'array',categoryarray:months,
    autorange:false,range:[-.5,11.5],tickmode:'array',tickvals:months,
    ticktext:months.map((_,i)=>`T${i+1}`),title:{text:`Tháng · ${year}`},fixedrange:true};
}
export function csvString(headers, rows) {
  const cell = v => v == null ? '' : `"${String(v).replaceAll('"','""')}"`;
  return '\ufeff' + [headers, ...rows].map(row => row.map(cell).join(',')).join('\r\n');
}
export function relativeChange(current, baseline) {
  return current == null || baseline == null || baseline === 0 ? null : (current / baseline - 1) * 100;
}
export function pointDifference(a, b) { return a == null || b == null ? null : a - b; }
export function topRows(rows, field, count = 10, descending = true) {
  return [...rows].filter(r => Number.isFinite(r[field])).sort((a,b) => descending ? b[field]-a[field] : a[field]-b[field]).slice(0,count);
}
export function searchResults(results, query, rq = 'ALL') {
  const q = query.trim().toLocaleLowerCase('vi');
  return results.filter(r => (rq === 'ALL' || r.rq_id === rq) &&
    `${r.res_id} ${r.rq_id} ${r.cohort_id} ${r.kpi_id} ${r.table_reference}`.toLocaleLowerCase('vi').includes(q));
}
