import json

# Read data
with open('viz_data_v2.json','r') as f:
    data = json.load(f)

# Write the complete fixed HTML template
tpl = r'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>3月流式竞对 · 豆包 vs Qwen3.5</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.1/dist/chart.umd.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/chartjs-plugin-datalabels@2.2.0/dist/chartjs-plugin-datalabels.min.js"></script>
<style>
:root {
  --primary: #3370ff;
  --primary-light: #eef3ff;
  --bg: #f0f2f5;
  --card: #ffffff;
  --text: #1d2129;
  --text2: #646a73;
  --border: #e5e6eb;
}
* { margin:0; padding:0; box-sizing:border-box; }
body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', 'Hiragino Sans GB', sans-serif; background:var(--bg); color:var(--text); }

.header { background: linear-gradient(135deg, #1a365d 0%, #2a5f8f 50%, #3b82c4 100%); color:#fff; padding:28px 0; text-align:center; }
.header h1 { font-size:26px; font-weight:700; }
.header p { font-size:13px; opacity:.75; margin-top:4px; }

.top-nav { background:#fff; border-bottom:1px solid var(--border); position:sticky; top:0; z-index:100; }
.top-nav-inner { max-width:1360px; margin:0 auto; display:flex; }
.top-nav-item { padding:13px 26px; font-size:14px; font-weight:600; cursor:pointer; border-bottom:3px solid transparent; color:var(--text2); transition:.15s; }
.top-nav-item:hover { color:var(--primary); background:var(--primary-light); }
.top-nav-item.active { color:var(--primary); border-bottom-color:var(--primary); }

.container { max-width:1360px; margin:0 auto; padding:20px; }

.filter-bar { background:#fff; border-radius:12px; padding:18px 22px; margin-bottom:20px; box-shadow:0 1px 3px rgba(0,0,0,.05); }
.filter-row { display:flex; align-items:center; gap:10px; margin-bottom:10px; flex-wrap:wrap; }
.filter-row:last-child { margin-bottom:0; }
.filter-label { font-size:12px; font-weight:700; color:var(--text2); min-width:110px; white-space:nowrap; }
.filter-opts { display:flex; flex-wrap:wrap; gap:6px; }
.fbtn { padding:5px 14px; border-radius:6px; border:1px solid var(--border); background:#fff; font-size:12px; cursor:pointer; transition:.12s; color:var(--text); white-space:nowrap; }
.fbtn:hover { border-color:var(--primary); color:var(--primary); }
.fbtn.active { background:var(--primary); color:#fff; border-color:var(--primary); }

/* FIX 1: 3 columns */
.charts-grid { display:grid; grid-template-columns:1fr 1fr 1fr; gap:16px; margin-bottom:24px; }
.chart-card { background:#fff; border-radius:12px; padding:20px; box-shadow:0 1px 3px rgba(0,0,0,.05); }
.chart-card.full-width { grid-column: 1 / -1; }
.chart-title { font-size:15px; font-weight:700; margin-bottom:4px; display:flex; align-items:center; gap:8px; }
.chart-title::before { content:''; display:inline-block; width:4px; height:18px; background:var(--primary); border-radius:2px; }
.chart-subtitle { font-size:11px; color:var(--text2); margin-bottom:12px; }
.chart-wrap { position:relative; height:240px; }

.vol-strip { display:flex; gap:12px; margin-bottom:16px; flex-wrap:wrap; }
.vol-chip { background:linear-gradient(135deg,#667eea,#764ba2); color:#fff; border-radius:8px; padding:10px 18px; min-width:140px; }
.vol-chip.c2 { background:linear-gradient(135deg,#f093fb,#f5576c); }
.vol-chip.c3 { background:linear-gradient(135deg,#4facfe,#00f2fe); color:#1a365d; }
.vol-num { font-size:28px; font-weight:800; }
.vol-lbl { font-size:11px; opacity:.85; }

.case-list { display:flex; flex-direction:column; gap:10px; }
.case-item { background:#fff; border-radius:10px; padding:16px 20px; box-shadow:0 1px 3px rgba(0,0,0,.05); border-left:4px solid transparent; transition:.15s; }
.case-item:hover { box-shadow:0 4px 12px rgba(0,0,0,.08); border-left-color:var(--primary); }
.case-tags { display:flex; gap:6px; margin-bottom:6px; flex-wrap:wrap; }
.ctag { font-size:11px; padding:2px 8px; border-radius:4px; font-weight:500; }
.ctag-d { background:#f0f5ff; color:#1d39c4; }
.ctag-s { background:#f6ffed; color:#389e0d; }
.ctag-t { background:#fff7e6; color:#d48806; }
.ctag-id { background:#f9f0ff; color:#722ed1; }
.case-q { font-size:13px; line-height:1.6; }
.case-q::before { content:'Q: '; font-weight:700; color:var(--primary); }
.paging { display:flex; justify-content:center; gap:6px; margin-top:16px; }
.pgb { padding:5px 12px; border-radius:6px; border:1px solid var(--border); background:#fff; cursor:pointer; font-size:12px; }
.pgb:hover { border-color:var(--primary); color:var(--primary); }
.pgb.active { background:var(--primary); color:#fff; border-color:var(--primary); }
.pgb:disabled { opacity:.35; cursor:not-allowed; }

.tab-panel { display:none; }
.tab-panel.active { display:block; }

@media(max-width:900px) { .charts-grid { grid-template-columns:1fr; } }
</style>
</head>
<body>

<div class="header">
  <h1>3月流式竞对评估 · 豆包 vs Qwen3.5</h1>
  <p>筛选条件驱动的多维度指标对比与Case探查</p>
</div>

<div class="top-nav">
  <div class="top-nav-inner" id="topNav">
    <div class="top-nav-item active" data-tab="dim">📊 维度对比</div>
    <div class="top-nav-item" data-tab="case">🔍 Case 探查</div>
  </div>
</div>

<div class="container">
  <div class="tab-panel active" id="panel-dim">
    <div class="filter-bar">
      <div class="filter-row">
        <span class="filter-label">数据端（单选）</span>
        <div class="filter-opts" id="fPlatform">
          <button class="fbtn active" data-v="双端整体">双端整体</button>
          <button class="fbtn" data-v="APP">APP</button>
          <button class="fbtn" data-v="Web">Web</button>
        </div>
      </div>
      <div class="filter-row">
        <span class="filter-label">评分维度（多选）</span>
        <div class="filter-opts" id="fScore">
          <button class="fbtn active" data-v="主客观">主观+客观</button>
          <button class="fbtn active" data-v="客观">客观</button>
        </div>
      </div>
      <div class="filter-row">
        <span class="filter-label">统计维度（单选）</span>
        <div class="filter-opts" id="fDim">
          <button class="fbtn active" data-v="session">Session维度</button>
          <button class="fbtn" data-v="prompt">Prompt维度</button>
        </div>
      </div>
      <div class="filter-row">
        <span class="filter-label">题目类型（单选）</span>
        <div class="filter-opts" id="fCat"></div>
      </div>
    </div>
    <div class="vol-strip" id="volStrip"></div>
    <div class="charts-grid" id="chartsGrid"></div>
  </div>

  <div class="tab-panel" id="panel-case">
    <div class="filter-bar">
      <div class="filter-row">
        <span class="filter-label">数据来源</span>
        <div class="filter-opts" id="cSrc">
          <button class="fbtn active" data-v="all">全部</button>
          <button class="fbtn" data-v="APP">APP</button>
          <button class="fbtn" data-v="Web">Web</button>
        </div>
      </div>
      <div class="filter-row">
        <span class="filter-label">评估方向</span>
        <div class="filter-opts" id="cDir"></div>
      </div>
    </div>
    <div class="case-list" id="caseList"></div>
    <div class="paging" id="casePg"></div>
  </div>
</div>

<script>
const DATA = INJECT_DATA_HERE;
const S = DATA.stats, V = DATA.volume, CS = DATA.cases;

const C = {
  db: 'rgba(51,112,255,.85)',
  qw: 'rgba(255,59,48,.85)'
};

let st = { plat:'双端整体', scores:['主客观','客观'], dim:'session', cat:'整体', csrc:'all', cdir:'all', cpg:1, cps:15 };

document.querySelectorAll('#topNav .top-nav-item').forEach(el=>{
  el.onclick=()=>{
    document.querySelectorAll('#topNav .top-nav-item').forEach(n=>n.classList.remove('active'));
    document.querySelectorAll('.tab-panel').forEach(n=>n.classList.remove('active'));
    el.classList.add('active');
    document.getElementById('panel-'+el.dataset.tab).classList.add('active');
  };
});

function bindSingle(containerId, stateKey, cb) {
  document.querySelectorAll('#'+containerId+' .fbtn').forEach(b=>{
    b.onclick=()=>{
      document.querySelectorAll('#'+containerId+' .fbtn').forEach(x=>x.classList.remove('active'));
      b.classList.add('active');
      st[stateKey]=b.dataset.v;
      cb();
    };
  });
}

function bindMulti(containerId, stateKey, cb) {
  document.querySelectorAll('#'+containerId+' .fbtn').forEach(b=>{
    b.onclick=()=>{
      b.classList.toggle('active');
      st[stateKey]=Array.from(document.querySelectorAll('#'+containerId+' .fbtn.active')).map(x=>x.dataset.v);
      if(!st[stateKey].length){b.classList.add('active');st[stateKey]=[b.dataset.v];}
      cb();
    };
  });
}

bindSingle('fPlatform','plat',()=>{ updateCats(); render(); });
bindMulti('fScore','scores',render);
bindSingle('fDim','dim',()=>{ updateCats(); render(); });

function updateCats() {
  const cats = S[st.plat]?.[st.dim] ? Object.keys(S[st.plat][st.dim]) : ['整体'];
  const c = document.getElementById('fCat');
  c.innerHTML = cats.map((k,i)=>`<button class="fbtn ${i===0?'active':''}" data-v="${k}">${k}</button>`).join('');
  st.cat = cats[0];
  bindSingle('fCat','cat',render);
}

let charts = {};
function destroyCharts() { Object.values(charts).forEach(c=>c.destroy()); charts={}; }
function pv(s) { if(!s||s==='-') return null; return parseFloat(s); }

function render() {
  destroyCharts();
  const pd = S[st.plat]?.[st.dim]?.[st.cat];
  if(!pd) { document.getElementById('chartsGrid').innerHTML='<div style="padding:40px;text-align:center;color:#999;grid-column:1/-1">暂无该维度数据</div>'; return; }

  const pk = st.plat;
  let sCount = V.session维度[pk]||0;
  let pCount = V.prompt维度[st.cat]?.[pk] ?? V.prompt维度['整体'][pk];
  document.getElementById('volStrip').innerHTML = `
    <div class="vol-chip"><div class="vol-num">${sCount}</div><div class="vol-lbl">Session 题量</div></div>
    <div class="vol-chip c2"><div class="vol-num">${pCount||'-'}</div><div class="vol-lbl">${st.cat} Prompt 题量</div></div>
  `;

  const showSub = st.scores.includes('主客观');
  const showObj = st.scores.includes('客观');

  const metricList = ['GSB','p-value','可用率','满分率','劝退率','均分','回复字数'];
  let html = '';
  metricList.forEach(m => {
    html += `<div class="chart-card"><div class="chart-title">${m}</div><div class="chart-subtitle">${st.plat} / ${st.dim==='session'?'Session维度':'Prompt维度'} / ${st.cat}</div><div class="chart-wrap"><canvas id="ch_${m.replace(/[^a-zA-Z]/g,'')}"></canvas></div></div>`;
  });
  document.getElementById('chartsGrid').innerHTML = html;

  metricList.forEach(m => {
    const canvasId = 'ch_'+m.replace(/[^a-zA-Z]/g,'');
    const ctx = document.getElementById(canvasId);
    if(!ctx) return;
    const d = pd[m];
    if(!d) return;

    // ========== 回复字数 ==========
    if(m === '回复字数') {
      charts[canvasId] = new Chart(ctx, {
        type:'bar',
        data:{
          labels:['豆包','Qwen3.5'],
          datasets:[{
            data:[d['豆包']||0, d['Qwen']||0],
            backgroundColor:[C.db, C.qw],
            borderRadius:4, barPercentage:0.5
          }]
        },
        plugins:[ChartDataLabels],
        options: barOpts(m, false)
      });
      return;
    }

    // ========== GSB: negate values so positive=豆包领先 ==========
    if(m === 'GSB') {
      let labels=[], gsbData=[];
      if(showSub) { labels.push('主观+客观'); gsbData.push(pv(d['Qwen_主客观'])!==null ? -pv(d['Qwen_主客观']) : null); }
      if(showObj) { labels.push('客观'); gsbData.push(pv(d['Qwen_客观'])!==null ? -pv(d['Qwen_客观']) : null); }

      const colors = gsbData.map(v=> v!==null && v>0 ? 'rgba(52,199,89,.85)' : v!==null && v<0 ? 'rgba(255,59,48,.85)' : 'rgba(180,180,180,.5)');

      charts[canvasId] = new Chart(ctx, {
        type:'bar',
        data:{ labels, datasets:[{ label:'GSB (正值=豆包领先, 负值=Qwen领先)', data:gsbData, backgroundColor:colors, borderRadius:4, barPercentage:0.5 }] },
        plugins:[ChartDataLabels],
        options: gsbOpts()
      });
      return;
    }

    // ========== p-value ==========
    if(m === 'p-value') {
      let labels=[], dbData=[], qwData=[];
      if(showSub) { labels.push('主观+客观'); dbData.push(pv(d['豆包_主客观'])); qwData.push(pv(d['Qwen_主客观'])); }
      if(showObj) { labels.push('客观'); dbData.push(pv(d['豆包_客观'])); qwData.push(pv(d['Qwen_客观'])); }

      charts[canvasId] = new Chart(ctx, {
        type:'bar',
        data:{ labels, datasets:[
          { label:'豆包', data:dbData, backgroundColor:C.db, borderRadius:4, barPercentage:0.6 },
          { label:'Qwen3.5', data:qwData, backgroundColor:C.qw, borderRadius:4, barPercentage:0.6 }
        ]},
        plugins:[ChartDataLabels, { id:'pline', afterDraw(chart){
          const y = chart.scales.y.getPixelForValue(0.05);
          const ctx2 = chart.ctx;
          ctx2.save(); ctx2.strokeStyle='#ff3b30'; ctx2.lineWidth=2; ctx2.setLineDash([6,4]);
          ctx2.beginPath(); ctx2.moveTo(chart.chartArea.left,y); ctx2.lineTo(chart.chartArea.right,y); ctx2.stroke();
          ctx2.font='11px sans-serif'; ctx2.fillStyle='#ff3b30'; ctx2.fillText('p=0.05',chart.chartArea.right-48,y-6);
          ctx2.restore();
        }}],
        options: barOpts(m, true)
      });
      return;
    }

    // ========== FIX 2: Standard metrics 可用率/满分率/劝退率/均分 ==========
    {
      let labels=[], dbData=[], qwData=[];
      if(showSub) {
        labels.push('主观+客观');
        dbData.push(pv(d['豆包_主客观']));
        qwData.push(pv(d['Qwen_主客观']));
      }
      if(showObj) {
        labels.push('客观');
        dbData.push(pv(d['豆包_客观']));
        qwData.push(pv(d['Qwen_客观']));
      }
      charts[canvasId] = new Chart(ctx, {
        type:'bar',
        data:{ labels, datasets:[
          { label:'豆包', data:dbData, backgroundColor:C.db, borderRadius:4, barPercentage:0.6 },
          { label:'Qwen3.5', data:qwData, backgroundColor:C.qw, borderRadius:4, barPercentage:0.6 }
        ]},
        plugins:[ChartDataLabels],
        options: barOpts(m, true)
      });
    }
  });
}

function barOpts(metric, showLegend) {
  return {
    responsive:true, maintainAspectRatio:false,
    plugins:{
      legend:{ display:showLegend, position:'top', labels:{ font:{size:11}, padding:10, usePointStyle:true, pointStyle:'circle' }},
      datalabels:{ anchor:'end', align:'end', font:{size:11,weight:600},
        formatter:(v)=>{ if(v===null||v===undefined) return ''; if(metric==='回复字数') return v; if(metric==='p-value') return v===null?'':v.toFixed(4); return v.toFixed(1)+'%'; },
        color: '#333'
      }
    },
    scales:{
      y:{
        beginAtZero: true,
        ticks:{ font:{size:11}, callback:v=>{ if(metric==='回复字数') return v; if(metric==='p-value') return v; return v+'%'; }},
        grid:{ color:'rgba(0,0,0,.06)' }
      },
      x:{ ticks:{font:{size:11}}, grid:{display:false} }
    },
    layout:{ padding:{top:28} }
  };
}

function gsbOpts() {
  return {
    responsive:true, maintainAspectRatio:false,
    plugins:{
      legend:{ display:true, position:'top', labels:{ font:{size:11}, padding:10, usePointStyle:true, pointStyle:'circle' }},
      datalabels:{ anchor:'end', align:'end', font:{size:12,weight:700},
        formatter:v=>{ if(v===null) return '-'; return (v>0?'+':'')+v.toFixed(2)+'%'; },
        color: v => v.raw>0?'#2e7d32':'#c62828'
      }
    },
    scales:{
      y:{
        ticks:{ font:{size:11}, callback:v=>v+'%' },
        grid:{ color:'rgba(0,0,0,.06)' }
      },
      x:{ ticks:{font:{size:11}}, grid:{display:false} }
    },
    layout:{ padding:{top:28} }
  };
}

function initCases() {
  const dirs = [...new Set(CS.map(c=>c.direction))].sort();
  document.getElementById('cDir').innerHTML = '<button class="fbtn active" data-v="all">全部</button>' + dirs.map(d=>`<button class="fbtn" data-v="${d}">${d}</button>`).join('');
  bindSingle('cSrc','csrc',()=>{st.cpg=1;renderCases();});
  bindSingle('cDir','cdir',()=>{st.cpg=1;renderCases();});
  renderCases();
}

function renderCases() {
  let f = CS.filter(c=>{
    if(st.csrc!=='all'&&c.source!==st.csrc) return false;
    if(st.cdir!=='all'&&c.direction!==st.cdir) return false;
    return true;
  });
  const total=f.length, tp=Math.ceil(total/st.cps)||1;
  const pg = f.slice((st.cpg-1)*st.cps, st.cpg*st.cps);

  document.getElementById('caseList').innerHTML = pg.length ? pg.map(c=>{
    const q = c.prompt.startsWith('{') ? '[多模态输入]' : esc(c.prompt);
    return `<div class="case-item"><div class="case-tags"><span class="ctag ctag-id">${c.session}/${c.promptId}</span><span class="ctag ctag-d">${c.direction}</span><span class="ctag ctag-s">${c.source}</span><span class="ctag ctag-t">${c.type}</span></div><div class="case-q">${q}</div></div>`;
  }).join('') : '<div style="text-align:center;color:#999;padding:40px">暂无匹配Case</div>';

  let ph=''; ph+=`<button class="pgb" ${st.cpg<=1?'disabled':''} onclick="goPg(${st.cpg-1})">‹</button>`;
  let s=Math.max(1,st.cpg-3),e=Math.min(tp,s+6); s=Math.max(1,e-6);
  for(let i=s;i<=e;i++) ph+=`<button class="pgb ${i===st.cpg?'active':''}" onclick="goPg(${i})">${i}</button>`;
  ph+=`<button class="pgb" ${st.cpg>=tp?'disabled':''} onclick="goPg(${st.cpg+1})">›</button><span style="font-size:11px;color:#999;padding:5px 8px">共${total}条</span>`;
  document.getElementById('casePg').innerHTML=ph;
}
function goPg(p){st.cpg=p;renderCases();document.getElementById('panel-case').scrollIntoView({behavior:'smooth'});}
function esc(t){const d=document.createElement('div');d.textContent=t;return d.innerHTML;}

updateCats();
render();
initCases();
</script>
</body>
</html>'''

# Inject data
data_json = json.dumps(data, ensure_ascii=False)
final = tpl.replace('INJECT_DATA_HERE', data_json)

with open('viz_page_v4.html', 'w') as f:
    f.write(final)

print(f"Done! viz_page_v4.html = {len(final)} bytes")
