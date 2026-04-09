#!/usr/bin/env python3
"""Build the final v2 HTML with all fixes:
1. GSB bar shorter + data label not overlapping axis label
2. Legend positioned higher to avoid overlap with datalabels
3. Add 评估背景, 评估指标(客观+主客观), 统计指标 overview cards
"""
import json, re

with open('viz_data_final.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Fix known corrupted cells
data['stats']['双端整体']['session']['整体']['均分'] = {
    '豆包_客观': '61.13%', '豆包_主客观': '66.80%',
    'Qwen_客观': '55.07%', 'Qwen_主客观': '59.93%'
}
data['stats']['双端整体']['session']['整体']['回复字数'] = {'豆包': 371, 'Qwen': 612}

with open('chart.umd.min.js', 'r', encoding='utf-8') as f:
    chartjs = f.read()
with open('chartjs-plugin-datalabels.min.js', 'r', encoding='utf-8') as f:
    datalabels = f.read()

data_json = json.dumps(data, ensure_ascii=False)

# ---- Build HTML ----
CSS = '''
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:-apple-system,BlinkMacSystemFont,"Segoe UI","PingFang SC","Hiragino Sans GB","Microsoft YaHei",sans-serif;background:#f0f2f5;color:#1d2129;padding:20px}
.header{text-align:center;margin-bottom:28px}
.header h1{font-size:22px;font-weight:700;color:#1d2129}
.header p{font-size:13px;color:#86909c;margin-top:4px}

/* overview cards */
.section-card{background:#fff;border-radius:12px;padding:20px 24px;margin-bottom:20px;box-shadow:0 1px 4px rgba(0,0,0,.06)}
.section-title{font-size:16px;font-weight:700;color:#1d2129;padding-left:10px;border-left:3px solid #165dff;margin-bottom:16px}
.info-row{display:flex;gap:16px;flex-wrap:wrap}
.info-chip{flex:1;min-width:180px;background:#f7f8fa;border-radius:8px;padding:14px 16px}
.info-chip .ic-label{font-size:11px;color:#86909c;margin-bottom:4px;display:flex;align-items:center;gap:4px}
.info-chip .ic-value{font-size:14px;font-weight:600;color:#1d2129}
.metric-row{display:flex;gap:12px;flex-wrap:wrap;margin-bottom:12px}
.metric-row-label{font-size:13px;color:#86909c;margin-bottom:8px;margin-top:4px}
.mc{flex:1;min-width:140px;background:#fff;border:1px solid #e5e6eb;border-radius:10px;padding:14px 16px}
.mc .mc-title{font-size:13px;font-weight:600;color:#1d2129}
.mc .mc-sub{font-size:11px;color:#86909c;margin-top:2px}
.mc .mc-val{font-size:20px;font-weight:700;color:#165dff;margin-top:6px}
.mc .mc-val.green{color:#00b42a}
.mc .mc-val.red{color:#f53f3f}

/* nav & filters */
.top-nav{display:flex;gap:12px;margin-bottom:16px;border-bottom:2px solid #e5e6eb;padding-bottom:0}
.top-nav-item{padding:8px 18px;cursor:pointer;font-size:14px;font-weight:500;color:#4e5969;border-bottom:2px solid transparent;margin-bottom:-2px;transition:.2s}
.top-nav-item.active{color:#165dff;border-bottom-color:#165dff}
.top-nav-item:hover{color:#165dff}
.tab-panel{display:none}.tab-panel.active{display:block}
.filter-row{display:flex;flex-wrap:wrap;align-items:center;gap:8px;margin-bottom:12px}
.filter-row .label{font-size:13px;color:#86909c;min-width:70px}
.fbtn{padding:4px 14px;border:1px solid #e5e6eb;border-radius:16px;background:#fff;cursor:pointer;font-size:13px;color:#4e5969;transition:.2s}
.fbtn.active{background:#165dff;color:#fff;border-color:#165dff}
.fbtn:hover{border-color:#165dff}
.vol-strip{display:flex;gap:16px;margin-bottom:16px}
.vol-chip{background:#fff;border-radius:8px;padding:12px 20px;box-shadow:0 1px 3px rgba(0,0,0,.06)}
.vol-chip.c2{background:#f0f5ff}
.vol-num{font-size:22px;font-weight:700;color:#165dff}
.vol-lbl{font-size:12px;color:#86909c;margin-top:2px}

/* charts */
.charts-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:16px;margin-bottom:24px}
.chart-card{background:#fff;border-radius:10px;padding:16px;box-shadow:0 1px 3px rgba(0,0,0,.06)}
.chart-title{font-size:15px;font-weight:600;color:#1d2129;margin-bottom:2px}
.chart-subtitle{font-size:11px;color:#86909c;margin-bottom:8px}
.chart-wrap{position:relative;height:240px}
.legend-note{text-align:center;font-size:11px;color:#86909c;margin-top:4px}
@media(max-width:900px){.charts-grid{grid-template-columns:repeat(2,1fr)}}
@media(max-width:600px){.charts-grid{grid-template-columns:1fr}}
'''

# Overview cards HTML - static based on 双端整体 session整体 data
overview_html = '''
<!-- 评估背景 -->
<div class="section-card">
  <div class="section-title">评估背景</div>
  <div class="info-row">
    <div class="info-chip"><div class="ic-label">🎯 评估对象</div><div class="ic-value">豆包 vs Qwen3.5</div></div>
    <div class="info-chip"><div class="ic-label">📋 评估范围</div><div class="ic-value">文字、图文、视频</div></div>
    <div class="info-chip"><div class="ic-label">📦 评估题库</div><div class="ic-value">Session 215题 / Prompt 657题</div></div>
    <div class="info-chip"><div class="ic-label">📊 对比基准</div><div class="ic-value">3月流式竞对数据</div></div>
  </div>
</div>

<!-- 评估指标 -->
<div class="section-card" id="overviewMetrics">
  <div class="section-title">评估指标</div>
  <div class="metric-row-label">客观指标</div>
  <div class="metric-row" id="objMetrics"></div>
  <div class="metric-row-label">整体指标（主观+客观）</div>
  <div class="metric-row" id="subMetrics"></div>
</div>

<!-- 统计指标 -->
<div class="section-card">
  <div class="section-title">统计指标</div>
  <div class="metric-row" id="statMetrics"></div>
</div>
'''

BODY_HTML = '''
<div class="header">
<h1>3月流式竞对【豆包 vs Qwen3.5】</h1>
<p>数据来源: 3月流式竞对 Excel · 生成时间: 2026-04-02</p>
</div>

''' + overview_html + '''

<div class="top-nav" id="topNav">
<div class="top-nav-item active" data-tab="tabCharts">数据看板</div>
<div class="top-nav-item" data-tab="tabCases">案例探查</div>
</div>

<div id="tabCharts" class="tab-panel active">
<div class="filter-row" id="fPlatform">
<span class="label">数据端</span>
<button class="fbtn active" data-v="双端整体">双端整体</button>
<button class="fbtn" data-v="APP">APP</button>
<button class="fbtn" data-v="Web">Web</button>
</div>
<div class="filter-row" id="fScores">
<span class="label">评分维度</span>
<button class="fbtn active" data-v="主客观">主观+客观</button>
<button class="fbtn active" data-v="客观">客观</button>
</div>
<div class="filter-row" id="fDim">
<span class="label">统计维度</span>
<button class="fbtn active" data-v="session">Session维度</button>
<button class="fbtn" data-v="prompt">Prompt维度</button>
</div>
<div class="filter-row" id="fCat">
<span class="label">题目类型</span>
</div>
<div class="vol-strip" id="volStrip"></div>
<div class="charts-grid" id="chartsGrid"></div>
</div>

<div id="tabCases" class="tab-panel">
<div style="padding:40px;text-align:center;color:#86909c">案例探查模块 (待接入评估数据 Sheet)</div>
</div>
'''

APP_JS = r'''
var DATA = __DATA_PLACEHOLDER__;
var S = DATA.stats;
var V = DATA.volume || {};
var C = {db:'rgba(22,93,255,0.85)', qw:'rgba(255,125,0,0.85)'};
var charts = {};
var st = {plat:'双端整体',scores:['主客观','客观'],dim:'session',cat:'整体'};

function pv(s) {
  if (!s || s==='-' || s==='#DIV/0!' || s==='#N/A' || s==='#CALC!' || s==='None') return null;
  var n = parseFloat(String(s).replace('%',''));
  return isNaN(n) ? null : n;
}
function safeGet(obj, keys) {
  var cur = obj;
  for (var i=0;i<keys.length;i++){if(cur==null||typeof cur!=='object')return undefined;cur=cur[keys[i]];}
  return cur;
}

/* ---- overview cards ---- */
function renderOverview() {
  var sess = safeGet(S, ['双端整体','session','整体']) || {};
  var prom = safeGet(S, ['双端整体','prompt','整体']) || {};
  var base = sess; /* use session as primary */

  function fmtPct(d, kDb, kQw) {
    var a = pv(d[kDb]), b = pv(d[kQw]);
    if (a===null && b===null) return '无数据';
    return (a!==null?a.toFixed(1)+'%':'-') + ' / ' + (b!==null?b.toFixed(1)+'%':'-');
  }
  function fmtGsb(d, kQw) {
    var v = pv(d[kQw]);
    if (v===null) return '无数据';
    var neg = -v; /* positive = 豆包领先 */
    return (neg>0?'+':'')+neg.toFixed(2)+'%';
  }
  function gsbClass(d, kQw) {
    var v = pv(d[kQw]);
    if (v===null) return '';
    return (-v)>=0?'green':'red';
  }

  /* 客观指标 */
  var objHtml = '';
  var objItems = [
    {t:'GSB',s:'豆包 vs Qwen',v:fmtGsb(base.GSB||{},'Qwen_客观'),c:gsbClass(base.GSB||{},'Qwen_客观')},
    {t:'可用率',s:'豆包 vs Qwen',v:fmtPct(base['可用率']||{},'豆包_客观','Qwen_客观'),c:''},
    {t:'劝退率',s:'豆包 vs Qwen',v:fmtPct(base['劝退率']||{},'豆包_客观','Qwen_客观'),c:''},
    {t:'满分率',s:'豆包 vs Qwen',v:fmtPct(base['满分率']||{},'豆包_客观','Qwen_客观'),c:''}
  ];
  for(var i=0;i<objItems.length;i++){
    var it=objItems[i];
    objHtml+='<div class="mc"><div class="mc-title">'+it.t+'</div><div class="mc-sub">'+it.s+'</div><div class="mc-val '+it.c+'">'+it.v+'</div></div>';
  }
  document.getElementById('objMetrics').innerHTML=objHtml;

  /* 主观+客观 */
  var subHtml='';
  var subItems = [
    {t:'GSB',s:'豆包 vs Qwen',v:fmtGsb(base.GSB||{},'Qwen_主客观'),c:gsbClass(base.GSB||{},'Qwen_主客观')},
    {t:'可用率',s:'豆包 vs Qwen',v:fmtPct(base['可用率']||{},'豆包_主客观','Qwen_主客观'),c:''},
    {t:'劝退率',s:'豆包 vs Qwen',v:fmtPct(base['劝退率']||{},'豆包_主客观','Qwen_主客观'),c:''},
    {t:'满分率',s:'豆包 vs Qwen',v:fmtPct(base['满分率']||{},'豆包_主客观','Qwen_主客观'),c:''}
  ];
  for(var i=0;i<subItems.length;i++){
    var it=subItems[i];
    subHtml+='<div class="mc"><div class="mc-title">'+it.t+'</div><div class="mc-sub">'+it.s+'</div><div class="mc-val '+it.c+'">'+it.v+'</div></div>';
  }
  document.getElementById('subMetrics').innerHTML=subHtml;

  /* 统计指标 */
  var wordD = base['回复字数']||{};
  var dbW = wordD['豆包']||0, qwW = wordD['Qwen']||0;
  var ratio = qwW>0?(qwW/dbW).toFixed(1)+'x':'';
  var statHtml='';
  statHtml+='<div class="mc"><div class="mc-title">字数</div><div class="mc-sub">豆包 vs Qwen</div><div class="mc-val">'+dbW+' / '+qwW+(ratio?' ('+ratio+')':'')+'</div></div>';
  statHtml+='<div class="mc"><div class="mc-title">均分(客观)</div><div class="mc-sub">豆包 vs Qwen</div><div class="mc-val">'+fmtPct(base['均分']||{},'豆包_客观','Qwen_客观')+'</div></div>';
  statHtml+='<div class="mc"><div class="mc-title">均分(主客观)</div><div class="mc-sub">豆包 vs Qwen</div><div class="mc-val">'+fmtPct(base['均分']||{},'豆包_主客观','Qwen_主客观')+'</div></div>';
  statHtml+='<div class="mc"><div class="mc-title">Session题量</div><div class="mc-sub">双端/APP/Web</div><div class="mc-val">'+(safeGet(V,['session维度','双端整体'])||0)+' / '+(safeGet(V,['session维度','APP'])||0)+' / '+(safeGet(V,['session维度','Web'])||0)+'</div></div>';
  statHtml+='<div class="mc"><div class="mc-title">Prompt题量</div><div class="mc-sub">双端/APP/Web</div><div class="mc-val">'+(safeGet(V,['prompt维度','整体','双端整体'])||0)+' / '+(safeGet(V,['prompt维度','整体','APP'])||0)+' / '+(safeGet(V,['prompt维度','整体','Web'])||0)+'</div></div>';
  document.getElementById('statMetrics').innerHTML=statHtml;
}

/* ---- chart options ---- */
function barOpts(metric, showLegend) {
  var isPercent = (metric!=='回复字数' && metric!=='p-value');
  return {
    responsive:true, maintainAspectRatio:false,
    layout:{padding:{top:28}},
    plugins:{
      legend:{display:!!showLegend,position:'top',align:'end',
        labels:{font:{size:11},padding:12,boxWidth:12,boxHeight:12}},
      datalabels:{
        anchor:'end',align:'top',offset:4,
        font:{size:11,weight:600},
        formatter:function(value){
          if(value===null||value===undefined)return '';
          if(isPercent)return value.toFixed(2)+'%';
          if(metric==='p-value')return value.toFixed(4);
          return String(value);
        }
      }
    },
    scales:{
      y:{beginAtZero:true,
        ticks:{callback:function(v){return isPercent?v+'%':v;},font:{size:11}},
        grid:{color:'rgba(0,0,0,.06)'}},
      x:{ticks:{font:{size:11}},grid:{display:false}}
    }
  };
}

function gsbOpts() {
  return {
    responsive:true,maintainAspectRatio:false,
    layout:{padding:{top:28,bottom:8}},
    plugins:{
      legend:{display:false},
      datalabels:{
        anchor:function(ctx){return ctx.dataset.data[ctx.dataIndex]>=0?'end':'start';},
        align:function(ctx){return ctx.dataset.data[ctx.dataIndex]>=0?'top':'bottom';},
        offset:6,
        font:{size:11,weight:600},
        formatter:function(value){
          if(value===null||value===undefined)return '';
          return value.toFixed(2)+'%';
        }
      }
    },
    scales:{
      y:{ticks:{callback:function(v){return v+'%';},font:{size:11}},
        grid:{color:'rgba(0,0,0,.06)'}},
      x:{ticks:{font:{size:12,weight:500},padding:6},grid:{display:false}}
    }
  };
}

/* ---- nav ---- */
var topNavItems=document.querySelectorAll('#topNav .top-nav-item');
for(var ti=0;ti<topNavItems.length;ti++){
  (function(el){el.onclick=function(){
    for(var j=0;j<topNavItems.length;j++)topNavItems[j].classList.remove('active');
    var panels=document.querySelectorAll('.tab-panel');
    for(var j=0;j<panels.length;j++)panels[j].classList.remove('active');
    el.classList.add('active');
    document.getElementById(el.dataset.tab).classList.add('active');
  };})(topNavItems[ti]);
}

/* ---- filters ---- */
function bindSingle(cid,sk,cb){
  var btns=document.querySelectorAll('#'+cid+' .fbtn');
  for(var i=0;i<btns.length;i++){(function(b){b.onclick=function(){
    var sibs=document.querySelectorAll('#'+cid+' .fbtn');
    for(var j=0;j<sibs.length;j++)sibs[j].classList.remove('active');
    b.classList.add('active');st[sk]=b.dataset.v;cb();
  };})(btns[i]);}
}
function bindMulti(cid,sk,cb){
  var btns=document.querySelectorAll('#'+cid+' .fbtn');
  for(var i=0;i<btns.length;i++){(function(b){b.onclick=function(){
    b.classList.toggle('active');var arr=[];
    var actives=document.querySelectorAll('#'+cid+' .fbtn.active');
    for(var j=0;j<actives.length;j++)arr.push(actives[j].dataset.v);
    if(arr.length===0){b.classList.add('active');arr=[b.dataset.v];}
    st[sk]=arr;cb();
  };})(btns[i]);}
}
bindSingle('fPlatform','plat',function(){updateCats();render();});
bindMulti('fScores','scores',function(){render();});
bindSingle('fDim','dim',function(){updateCats();render();});

function updateCats(){
  var dimData=safeGet(S,[st.plat,st.dim]);
  var cats=dimData?Object.keys(dimData):['整体'];
  var c=document.getElementById('fCat');
  var h='<span class="label">题目类型</span>';
  for(var i=0;i<cats.length;i++){
    h+='<button class="fbtn '+(i===0?'active':'')+'" data-v="'+cats[i]+'">'+cats[i]+'</button>';
  }
  c.innerHTML=h;st.cat=cats[0];
  bindSingle('fCat','cat',function(){render();});
}

function destroyCharts(){var keys=Object.keys(charts);for(var i=0;i<keys.length;i++)charts[keys[i]].destroy();charts={};}

/* ---- main render ---- */
function render(){
  destroyCharts();
  var pd=safeGet(S,[st.plat,st.dim,st.cat]);
  if(!pd){
    document.getElementById('chartsGrid').innerHTML='<div style="padding:40px;text-align:center;color:#999;grid-column:1/-1">暂无该维度数据</div>';
    document.getElementById('volStrip').innerHTML='';return;
  }
  var pk=st.plat;
  var sCount=safeGet(V,['session维度',pk])||0;
  var pObj=safeGet(V,['prompt维度',st.cat,pk]);
  if(pObj==null)pObj=safeGet(V,['prompt维度','整体',pk]);
  document.getElementById('volStrip').innerHTML=
    '<div class="vol-chip"><div class="vol-num">'+sCount+'</div><div class="vol-lbl">Session 题量</div></div>'+
    '<div class="vol-chip c2"><div class="vol-num">'+(pObj||'-')+'</div><div class="vol-lbl">'+st.cat+' Prompt 题量</div></div>';

  var showSub=st.scores.indexOf('主客观')>=0;
  var showObj=st.scores.indexOf('客观')>=0;
  var metricList=['GSB','p-value','可用率','满分率','劝退率','均分','回复字数'];

  var html='';
  for(var mi=0;mi<metricList.length;mi++){
    var m=metricList[mi];
    html+='<div class="chart-card"><div class="chart-title">'+m+'</div>'+
      '<div class="chart-subtitle">'+st.plat+' / '+(st.dim==='session'?'Session维度':'Prompt维度')+' / '+st.cat+'</div>'+
      '<div class="chart-wrap"><canvas id="ch_'+mi+'"></canvas></div>';
    if(m==='GSB')html+='<div class="legend-note">↑ 正值=豆包领先(绿) · 负值=Qwen领先(红)</div>';
    html+='</div>';
  }
  document.getElementById('chartsGrid').innerHTML=html;

  for(var mi=0;mi<metricList.length;mi++){
    var m=metricList[mi];
    var ctx=document.getElementById('ch_'+mi);
    if(!ctx)continue;
    var d=pd[m];if(!d)continue;

    if(m==='回复字数'){
      var dbW=d['豆包'],qwW=d['Qwen'];
      if(dbW==null&&qwW==null)continue;
      charts['ch_'+mi]=new Chart(ctx,{type:'bar',
        data:{labels:['豆包','Qwen3.5'],datasets:[{data:[dbW||0,qwW||0],backgroundColor:[C.db,C.qw],borderRadius:4,barPercentage:0.5}]},
        plugins:[ChartDataLabels],options:barOpts(m,false)});
      continue;
    }

    if(m==='GSB'){
      var gL=[],gD=[],gC=[];
      if(showSub){gL.push('主观+客观');var v1=pv(d['Qwen_主客观']);var nv1=(v1!==null)?-v1:null;gD.push(nv1);
        gC.push(nv1!==null&&nv1>0?'rgba(52,199,89,0.85)':nv1!==null&&nv1<0?'rgba(255,59,48,0.85)':'rgba(200,200,200,0.5)');}
      if(showObj){gL.push('客观');var v2=pv(d['Qwen_客观']);var nv2=(v2!==null)?-v2:null;gD.push(nv2);
        gC.push(nv2!==null&&nv2>0?'rgba(52,199,89,0.85)':nv2!==null&&nv2<0?'rgba(255,59,48,0.85)':'rgba(200,200,200,0.5)');}
      if(gL.length===0)continue;
      charts['ch_'+mi]=new Chart(ctx,{type:'bar',
        data:{labels:gL,datasets:[{label:'GSB (正=豆包领先)',data:gD,backgroundColor:gC,borderRadius:4,barPercentage:0.4,maxBarThickness:60}]},
        plugins:[ChartDataLabels],options:gsbOpts()});
      continue;
    }

    if(m==='p-value'){
      var pL=[],pD=[];
      if(showSub){pL.push('主观+客观');pD.push(pv(d['Qwen_主客观']));}
      if(showObj){pL.push('客观');pD.push(pv(d['Qwen_客观']));}
      if(pL.length===0)continue;
      charts['ch_'+mi]=new Chart(ctx,{type:'bar',
        data:{labels:pL,datasets:[{label:'p-value',data:pD,backgroundColor:'rgba(134,144,156,0.7)',borderRadius:4,barPercentage:0.5}]},
        plugins:[ChartDataLabels],options:barOpts(m,false)});
      continue;
    }

    var sL=[],dbD=[],qwD=[];
    if(showSub){sL.push('主观+客观');dbD.push(pv(d['豆包_主客观']));qwD.push(pv(d['Qwen_主客观']));}
    if(showObj){sL.push('客观');dbD.push(pv(d['豆包_客观']));qwD.push(pv(d['Qwen_客观']));}
    if(sL.length===0)continue;
    charts['ch_'+mi]=new Chart(ctx,{type:'bar',
      data:{labels:sL,datasets:[
        {label:'豆包',data:dbD,backgroundColor:C.db,borderRadius:4,barPercentage:0.6},
        {label:'Qwen3.5',data:qwD,backgroundColor:C.qw,borderRadius:4,barPercentage:0.6}
      ]},plugins:[ChartDataLabels],options:barOpts(m,true)});
  }
}

renderOverview();
updateCats();
render();
'''

# Assemble final HTML
html = '<!DOCTYPE html>\n<html lang="zh-CN">\n<head>\n<meta charset="UTF-8">\n'
html += '<meta name="viewport" content="width=device-width,initial-scale=1.0">\n'
html += '<title>3月流式竞对【豆包 vs Qwen3.5】</title>\n'
html += '<script>\n' + chartjs + '\n</script>\n'
html += '<script>\n' + datalabels + '\n</script>\n'
html += '<style>\n' + CSS + '\n</style>\n'
html += '</head>\n<body>\n'
html += BODY_HTML
html += '\n<script>\n'
html += APP_JS.replace('__DATA_PLACEHOLDER__', data_json)
html += '\n</script>\n</body>\n</html>'

with open('viz_final_v2.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("Generated viz_final_v2.html: {} bytes".format(len(html)))

# Verify
scripts = re.findall(r'<script>(.*?)</script>', html, re.DOTALL)
app = scripts[2]
assert '=>' not in app, "Arrow functions!"
assert 'const ' not in app, "const!"
assert '__DATA_PLACEHOLDER__' not in app, "Placeholder!"
# Check chart IDs are unique
for i in range(7):
    assert "id=\"ch_{}\"".format(i) in html, "Missing ch_{}".format(i)
print("All checks passed!")
