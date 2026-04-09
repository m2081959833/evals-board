import json, re

# Read the template
with open('viz_v2.html','r') as f:
    tpl = f.read()

# Read the data
with open('viz_data_v2.json','r') as f:
    data = json.load(f)

# ======== FIX 1: Change grid from 2 columns to 3 columns ========
tpl = tpl.replace(
    'grid-template-columns:1fr 1fr;',
    'grid-template-columns:1fr 1fr 1fr;'
)
# Also reduce chart height from 300px to 240px for better 3-col fit
tpl = tpl.replace(
    '.chart-wrap { position:relative; height:300px; }',
    '.chart-wrap { position:relative; height:240px; }'
)

# ======== FIX 2: Fix standard metrics (可用率,满分率,劝退率,均分) data alignment ========
# Replace the buggy "Standard metrics" block with correct 2-dataset approach
old_standard = """    // Standard metrics: 可用率,满分率,劝退率,均分
    const d = pd[m];
    if(!d) return;
    let labels=[], datasets=[];
    if(showSub && showObj) {
      labels = ['主观+客观','客观'];
    } else if(showSub) {
      labels = ['主观+客观'];
    } else {
      labels = ['客观'];
    }

    let dbSub=[], dbObj=[], qwSub=[], qwObj=[];
    if(showSub) { dbSub.push(pv(d['豆包_主客观'])); qwSub.push(pv(d['Qwen_主客观'])); }
    if(showObj) { dbObj.push(pv(d['豆包_客观'])); qwObj.push(pv(d['Qwen_客观'])); }

    if(showSub) {
      datasets.push({ label:'豆包 (主客观)', data:dbSub, backgroundColor:C.db_sub, borderRadius:4 });
      datasets.push({ label:'Qwen3.5 (主客观)', data:qwSub, backgroundColor:C.qw_sub, borderRadius:4 });
    }
    if(showObj) {
      datasets.push({ label:'豆包 (客观)', data:dbObj, backgroundColor:C.db_obj, borderRadius:4 });
      datasets.push({ label:'Qwen3.5 (客观)', data:qwObj, backgroundColor:C.qw_obj, borderRadius:4 });
    }"""

new_standard = """    // Standard metrics: 可用率,满分率,劝退率,均分
    const d = pd[m];
    if(!d) return;
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
    let datasets = [
      { label:'豆包', data:dbData, backgroundColor:C.db, borderRadius:4, barPercentage:0.6 },
      { label:'Qwen3.5', data:qwData, backgroundColor:C.qw, borderRadius:4, barPercentage:0.6 }
    ];"""

tpl = tpl.replace(old_standard, new_standard)

# ======== FIX 3: Fix GSB interpretation ========
# positive GSB = Qwen领先 (red), negative = 豆包领先 (green)
old_gsb_colors = """const colors = gsbData.map(v=> v!==null && v>0 ? 'rgba(52,199,89,.85)' : v!==null && v<0 ? 'rgba(255,59,48,.85)' : 'rgba(180,180,180,.5)');

      datasets.push({ label:'GSB (豆包领先为正)', data:gsbData, backgroundColor:colors, borderRadius:4, barPercentage:0.5 });"""

new_gsb_colors = """const colors = gsbData.map(v=> v!==null && v>0 ? 'rgba(255,59,48,.85)' : v!==null && v<0 ? 'rgba(52,199,89,.85)' : 'rgba(180,180,180,.5)');

      datasets.push({ label:'GSB (正值=Qwen领先, 负值=豆包领先)', data:gsbData, backgroundColor:colors, borderRadius:4, barPercentage:0.5 });"""

tpl = tpl.replace(old_gsb_colors, new_gsb_colors)

# Also fix the GSB datalabels color in gsbOpts
old_gsb_label_color = "color: v => v.raw>0?'#2e7d32':'#c62828'"
new_gsb_label_color = "color: v => v.raw>0?'#c62828':'#2e7d32'"
tpl = tpl.replace(old_gsb_label_color, new_gsb_label_color)

# ======== Inject data and write final page ========
data_json = json.dumps(data, ensure_ascii=False)
final = tpl.replace('INJECT_DATA_HERE', data_json)

with open('viz_page_v3.html', 'w') as f:
    f.write(final)

# Also save updated template
with open('viz_v3.html', 'w') as f:
    f.write(tpl)

print(f"Done! viz_page_v3.html = {len(final)} bytes")
print("Fixes applied:")
print("  1. Grid: 3 columns, chart height 240px")
print("  2. Standard metrics: 2 datasets (豆包/Qwen) aligned with labels")
print("  3. GSB: positive=Qwen领先(red), negative=豆包领先(green)")
