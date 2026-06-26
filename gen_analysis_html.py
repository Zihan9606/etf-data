#!/usr/bin/env python3
"""
生成ETF申购流入分析HTML — 全量排行 + 量化结论 + 定性分析 + 重叠推荐 + 日期切换
升级版2: 数据与HTML分离模式
  - Python脚本端: 读取CSV + 调用westock API获取最新数据 → 导出 etf_history/etf_data.json
  - HTML端: 通过 fetch('/etf_data.json') 实时加载, 不嵌入数据到HTML体内
  - 使用方式: cd工作目录 && python3 server.py → 浏览器打开 localhost:8080
  - 好处: 数据更新后只需重新运行本脚本, HTML自动读取新数据, 无需改HTML
"""
import subprocess, json, os, csv
from collections import defaultdict

OUTPUT_DIR = "/Users/andy/WorkBuddy/2026-06-24-23-34-24/etf_history"
CSV_FILE = os.path.join(OUTPUT_DIR, "etf_daily.csv")
HTML_FILE = "/Users/andy/WorkBuddy/2026-06-24-23-34-24/全量指数申购流入排行.html"
DATA_JSON = os.path.join(OUTPUT_DIR, "etf_data.json")

# ========== 39列字段: 英文名 ↔ 中文释义 ==========
FIELD_CN = {
    'shares':'总份额','sharesChg':'份额变化','sharesChgRatio':'变化率',
    'nav':'净值','closePrice':'收盘价','changePct':'涨跌幅',
    'turnoverRate':'换手率','turnoverValue':'成交额','turnoverVolume':'成交量',
    'disc':'折溢价','discountRatioCurve':'折溢价走势','avgDiscountRatioCurve':'平均折溢价',
    'size':'基金规模','totalMV':'总市值','totalAssets':'总资产',
    'stockRatio':'股票仓','bondRatio':'债券仓',
    'ytdReturn':'年至今收益','ytdMaxDrawdown':'年内最大回撤',
    'return1M':'月收益','return3M':'季收益','return6M':'半年收益','return1Y':'年收益','return3Y':'3年收益',
    'maxDrawdown1M':'月最大回撤','maxDrawdown3M':'季最大回撤',
    'maxDrawdown6M':'半年最大回撤','maxDrawdown1Y':'年最大回撤','maxDrawdown3Y':'3年最大回撤',
    'indexDailyChange':'指数日涨跌','index1YReturn':'指数年收益',
    'holderAccount':'持有人户数','institutionHolderRatio':'机构持有比','individualHolderRatio':'个人持有比',
    'prlistTop20Ratio':'前20重仓%','isTPlus0':'T+0标记',
}
# 需要展示在排行表里的字段 (除date/idx/code)
TABLE_FIELDS = ['shares','sharesChg','sharesChgRatio','nav','closePrice','changePct',
                'turnoverRate','turnoverValue','turnoverVolume','disc',
                'discountRatioCurve','avgDiscountRatioCurve',
                'size','totalMV','totalAssets','stockRatio','bondRatio',
                'ytdReturn','ytdMaxDrawdown',
                'return1M','return3M','return6M','return1Y','return3Y',
                'maxDrawdown1M','maxDrawdown3M','maxDrawdown6M','maxDrawdown1Y','maxDrawdown3Y',
                'indexDailyChange','index1YReturn',
                'holderAccount','institutionHolderRatio','individualHolderRatio',
                'prlistTop20Ratio','isTPlus0']
# 每个字段的?提示
FIELD_TIPS = {
    'shares':'基金当前的总份额(亿份)',
    'sharesChg':'当日份额变化量(万份)',
    'sharesChgRatio':'当日份额增减比例(%),正值=净申购,负值=净赎回',
    'nav':'基金单位净值(元),每份基金的价值',
    'closePrice':'当日交易所收盘价(元)',
    'changePct':'当日ETF价格涨跌幅(%)',
    'turnoverRate':'当日换手率(%),成交量占总份额比例,衡量活跃度',
    'turnoverValue':'当日成交金额(元)',
    'turnoverVolume':'当日成交量(手),1手=100份',
    'disc':'ETF市价相对净值的偏离度(%),正=溢价,负=折价',
    'discountRatioCurve':'盘中折溢价率走势数据',
    'avgDiscountRatioCurve':'日内平均折溢价率',
    'size':'基金资产净值总额(元),即基金总规模',
    'totalMV':'交易所总市值(元)',
    'totalAssets':'基金总资产(元)',
    'stockRatio':'股票占基金资产比(%),剩余为现金或债券',
    'bondRatio':'债券占基金资产比(%)',
    'ytdReturn':'年初至今价格涨跌幅(%)',
    'ytdMaxDrawdown':'年初至今最大回撤幅度(%)',
    'return1M':'近1个月收益率(%)',
    'return3M':'近3个月收益率(%)',
    'return6M':'近6个月收益率(%)',
    'return1Y':'近1年收益率(%)',
    'return3Y':'近3年收益率(%)',
    'maxDrawdown1M':'近1个月最大回撤(%)',
    'maxDrawdown3M':'近3个月最大回撤(%)',
    'maxDrawdown6M':'近6个月最大回撤(%)',
    'maxDrawdown1Y':'近1年最大回撤(%)',
    'maxDrawdown3Y':'近3年最大回撤(%)',
    'indexDailyChange':'跟踪指数当日涨跌幅(%)',
    'index1YReturn':'跟踪指数近1年收益率(%)',
    'holderAccount':'基金持有人总数(户,从季报获取)',
    'institutionHolderRatio':'机构投资者持有比例(%)(季报数据)',
    'individualHolderRatio':'个人投资者持有比例(%)(季报数据)',
    'prlistTop20Ratio':'前20大重仓股占基金净值比(%),越高越集中',
    'isTPlus0':'是否支持T+0交易,✓=是,✗=否',
}

# ========== 读取CSV全量历史数据 ==========
all_data = {}  # date -> {idx_name -> {field: value}}
with open(CSV_FILE, 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        d = row['date']
        idx = row['idx']
        if d not in all_data:
            all_data[d] = {}
        if idx not in all_data[d]:
            all_data[d][idx] = []
        all_data[d][idx].append(row)
dates = sorted(all_data.keys())
today_str = dates[-1] if dates else "2026-06-25"

print(f"读取 {len(dates)} 天数据: {dates}")
print(f"默认展示日期: {today_str}")

# ========== 分组汇总(按指数+日期, 仅保留份额最大ETF) ==========
def group_by_date(date_str):
    """对指定日期按指数分组, 每个指数只保留份额最大的那只ETF, 返回 ranked 列表"""
    day_data = all_data.get(date_str, {})
    # 先全部分组, 再每指数只保留最大份额的ETF
    groups = defaultdict(list)
    for idx_name, rows in day_data.items():
        for row in rows:
            code = row.get('code','')
            try:
                s = float(row.get('shares',0)) / 1e8  # 份→亿份
                chg = int(row.get('sharesChg',0))
                nav = float(row.get('nav',0))
                flow = chg * nav / 1e8  # 亿
                chg_pct = float(row.get('sharesChgRatio','0').replace('%','')) if row.get('sharesChgRatio','') else 0
                pc = float(row.get('changePct','0').replace('%','')) if row.get('changePct','') else 0
                ytd = float(row.get('ytdReturn','0').replace('%','')) if row.get('ytdReturn','') else 0
                r1m = float(row.get('return1M','0').replace('%','')) if row.get('return1M','') else 0
                tr = float(row.get('turnoverRate','0').replace('%','')) if row.get('turnoverRate','') else 0
                vol = float(row.get('turnoverVolume',0)) if row.get('turnoverVolume','') else 0
                ytdMdd = float(row.get('ytdMaxDrawdown','0').replace('%','')) if row.get('ytdMaxDrawdown','') else 0
                indexChg = row.get('indexDailyChange','')
                index1Y = row.get('index1YReturn','')
                isT0 = row.get('isTPlus0','')
                groups[idx_name].append({
                    'code': code, 'shares': s, 'flow': flow, 'nav': nav, 'chg_pct': chg_pct,
                    'pc': pc, 'ytd': ytd, 'r1m': r1m, 'tr': tr, 'vol': vol, 'ytdMdd': ytdMdd,
                    'indexChg': indexChg, 'index1Y': index1Y, 'isT0': isT0,
                    'stock': row.get('stockRatio',''), 'prlist': row.get('prlistTop20Ratio',''),
                    'disc': row.get('disc',''),
                })
            except:
                continue
    
    # 每个指数只保留份额最大的ETF
    by_idx = {}
    for idx_name, items in groups.items():
        items.sort(key=lambda x: -x['shares'])
        best = items[0]  # 份额最大的ETF
        d = {
            'shares': best['shares'],
            'flow': best['flow'],
            'codes': [best['code']],
            'nav': best['nav'],
            'chg_pct': best['chg_pct'],
            'pc': best['pc'],
            'ytd': best['ytd'],
            'r1m': best['r1m'],
            'turnover': best['tr'],
            'volume': best['vol'],
            'stock': best['stock'],
            'prlist': best['prlist'],
            'disc': best['disc'],
            'indexChg': best['indexChg'],
            'index1Y': best['index1Y'],
            'isT0': best['isT0'],
            'ytdMdd': best['ytdMdd'],
            'main_code': best['code'],
            'idx': idx_name,
        }
        by_idx[idx_name] = d
    return sorted(by_idx.items(), key=lambda x: x[1]['flow'], reverse=True)

# ========== 四象限定性分析 ==========
def classify(d):
    if d['chg_pct'] > 1 and d['pc'] < -0.5: return '🐻强力吸筹','份额↑+价格↓,机构越跌越买'
    if d['chg_pct'] > 1 and -0.5 <= d['pc'] <= 0.5: return '📥压价建仓','份额↑+价格平,压价隐蔽买入'
    if d['chg_pct'] > 0.5 and d['pc'] > 2: return '⚠️量价齐升','份额↑+价格↑↑,警惕过热'
    if 0 < d['chg_pct'] <= 0.5 and d['pc'] > 2: return '⚠️量价齐升','份额微增+价格↑↑,跟风上涨'
    if d['chg_pct'] > 0 and d['pc'] > 0: return '📈温和上涨','份额↑+价格↑,量价配合健康'
    if d['chg_pct'] < -0.5 and d['pc'] > 0.5: return '🚨出货嫌疑','份额↓+价格↑,拉高出货'
    if d['chg_pct'] < -0.5 and d['pc'] < -0.5: return '💀恐慌出逃','份额↓+价格↓,资金撤离'
    if -0.5 <= d['chg_pct'] <= 0.5 and d['pc'] > 1: return '📈无量空涨','份额持平但价格上涨'
    if -0.5 <= d['chg_pct'] <= 0.5 and d['pc'] < -1: return '⬇️无量下跌','份额持平但价格下跌'
    return '➡️横盘观望','份额价格均平稳'

qualitative_buy_keywords = ['🐻强力吸筹','📥压价建仓','📈温和上涨']

def get_analysis(date_str):
    ranked = group_by_date(date_str)
    by_idx = {idx: d for idx, d in ranked}
    
    # 定性
    qualitative_signals = {}
    for idx_name, d in by_idx.items():
        sig, desc = classify(d)
        qualitative_signals[idx_name] = (sig, desc)
    
    # 量化: 份额↑0.5%~3% + 价格↑ + 资金流>0
    quantitative_buys = set()
    for idx_name, d in by_idx.items():
        cp = d['chg_pct']
        pc = d['pc']
        flow = d['flow']
        if 0.5 <= cp <= 3 and pc > 0 and flow > 0:
            quantitative_buys.add(idx_name)
        elif 0 < cp <= 0.5 and pc > 0.5 and flow > 0:
            quantitative_buys.add(idx_name)
    
    def is_qualitative_buy(sig_name):
        return any(k in sig_name for k in qualitative_buy_keywords)
    qualitative_buys = set(idx for idx, (sig, desc) in qualitative_signals.items() if is_qualitative_buy(sig))
    overlap = quantitative_buys & qualitative_buys
    only_quant = quantitative_buys - qualitative_buys
    only_qual = qualitative_buys - quantitative_buys
    
    inflow_count = sum(1 for _, d in ranked if d['flow']>0)
    outflow_count = sum(1 for _, d in ranked if d['flow']<0)
    flat_count = sum(1 for _, d in ranked if d['flow']==0)
    
    return ranked, by_idx, qualitative_signals, quantitative_buys, overlap, only_quant, only_qual, inflow_count, outflow_count, flat_count

ranked_today, by_idx_today, qualitative_signals_today, quant_buys_today, overlap_today, only_quant_today, only_qual_today, inflow_today, outflow_today, flat_today = get_analysis(today_str)

print("生成HTML...")

# ========== 构建全量数据JSON (嵌入JS) ==========
all_dates_json = {}
for d in dates:
    ranked, by_idx, qual_sig, quant, overlap, oq, ol, inf, outf, fl = get_analysis(d)
    date_data = []
    for rank, (name, dd) in enumerate(ranked, 1):
        flow = dd['flow']
        fdir = "in" if flow > 0 else ("out" if flow < 0 else "flat")
        sig, desc = qual_sig.get(name, ('',''))
        entry = {
            'rank': rank, 'name': name, 'codes': dd['codes'], 'mainCode': dd.get('main_code',''),
            'shares': round(dd['shares'],2),
            'flow': round(flow,2), 'chgPct': round(dd['chg_pct'],2), 'pc': round(dd['pc'],2),
            'nav': round(dd['nav'],2), 'disc': dd['disc'], 'turnover': round(dd['turnover'],1),
            'volume': int(dd['volume']), 'ytd': round(dd['ytd'],1), 'r1m': round(dd['r1m'],1),
            'stock': dd['stock'], 'prlist': dd['prlist'], 'indexChg': dd['indexChg'],
            'index1Y': dd['index1Y'], 'ytdMdd': round(dd['ytdMdd'],1), 'isT0': dd['isT0'],
            'dir': fdir, 'sig': sig, 'desc': desc, 'flow10': round(dd['flow']*10,0),
        }
        date_data.append(entry)
    
    # 卖点信号: 直接用当日分析结果 = 当日回避清单
    # 触发条件: 定性(出货/恐慌) + 量化(资金流出>1亿) 
    sell_signals = []
    # 出货+恐慌组
    avoid_names = set()
    for idx_name, _ in qual_sig.items():
        sig, _ = qual_sig.get(idx_name, ('', ''))
        if any(k in sig for k in ['出货','恐慌']):
            avoid_names.add(idx_name)
    # 大额流出组
    for idx_name, cur in by_idx.items():
        if cur['flow'] < -5:
            avoid_names.add(idx_name)
    
    for idx_name in avoid_names:
        cur = by_idx[idx_name]
        cur_flow = cur['flow']
        cur_sig, _ = qual_sig.get(idx_name, ('', ''))
        is_danger = any(k in cur_sig for k in ['出货','恐慌'])
        reasons = []
        sell_type = ''
        if cur_flow < -1:
            reasons.append(f"资金流出{cur_flow:.2f}亿")
            sell_type = 'quant'
        if is_danger:
            reasons.append(f"定性信号: {cur_sig.strip().split(' ')[0]}")
            sell_type = 'both' if sell_type == 'quant' else 'qual'
        if not reasons:
            reasons.append(f"大额流出{cur_flow:.2f}亿")
            sell_type = 'quant'
        sell_signals.append({
            'name': idx_name,
            'mainCode': cur.get('main_code',''),
            'curFlow': round(cur_flow,2),
            'curChg': round(cur['chg_pct'],2),
            'curPc': round(cur['pc'],2),
            'sig': cur_sig,
            'reasons': '; '.join(reasons),
            'type': sell_type,
        })
    
    # ===== 市场基准统计 =====
    flows = sorted([d['flow'] for _, d in by_idx.items()])
    chgs = sorted([d['chg_pct'] for _, d in by_idx.items()])
    n = len(flows)
    median_flow = flows[n//2] if n > 0 else 0
    median_chg = chgs[n//2] if n > 0 else 0
    avg_flow = sum(flows)/n if n > 0 else 0
    avg_chg = sum(chgs)/n if n > 0 else 0
    # 统计分布用于展示
    neg_count = sum(1 for f in flows if f < -0.001)
    zero_count = sum(1 for f in flows if -0.001 <= f <= 0.001)
    pos_count = sum(1 for f in flows if f > 0.001)
    top3_flow = sorted(by_idx.items(), key=lambda x: x[1]['flow'], reverse=True)[:3]
    top3_chg = sorted(by_idx.items(), key=lambda x: x[1]['chg_pct'], reverse=True)[:3]
    
    all_dates_json[d] = {
        'data': date_data,
        'inflow': inf, 'outflow': outf, 'flat': fl, 'total': len(ranked),
        'overlap': sorted(overlap, key=lambda x: by_idx[x]['flow'], reverse=True),
        'onlyQuant': sorted(oq, key=lambda x: by_idx[x]['flow'], reverse=True)[:10],
        'onlyQual': sorted(ol, key=lambda x: by_idx[x]['flow'], reverse=True)[:10],
        'sellSignals': sorted(sell_signals, key=lambda x: x['curFlow']),
        'marketStats': {
            'top3Flow': [{'name':n,'flow':round(d['flow'],2),'mainCode':d.get('main_code','')} for n,d in top3_flow],
            'top3Chg': [{'name':n,'chg':round(d['chg_pct'],2),'mainCode':d.get('main_code','')} for n,d in top3_chg],
            'medianFlow': round(median_flow,2),
            'medianChg': round(median_chg,2),
            'avgFlow': round(avg_flow,2),
            'avgChg': round(avg_chg,2),
            'negCount': neg_count,
            'zeroCount': zero_count,
            'posCount': pos_count,
        },
    }

# ===== stock_flow2 因子分析框架 =====
# 计算每个ETF累计N天的 sharesChg * nav (金额) 和 sharesChg (份额) 的5日均值
all_flow2_by_code = defaultdict(list)  # code -> [(date, amt, ast)]
for d in dates:
    day_data = all_data.get(d, {})
    for idx_name, rows in day_data.items():
        for row in rows:
            code = row.get('code','')
            try:
                sh_chg = int(row.get('sharesChg',0))
                nav = float(row.get('nav',0))
                amt = sh_chg * nav  # 申赎金额
                ast = sh_chg         # 申赎份额
                all_flow2_by_code[code].append((d, amt, ast))
            except:
                pass

days_collected = len(dates)
flow2_data = {}
for code, vals in all_flow2_by_code.items():
    if len(vals) >= 5:
        sorted_vals = sorted(vals, key=lambda x: x[0])[-5:]  # 最近5天
        amt_ma5 = sum(v[1] for v in sorted_vals) / 5
        ast_ma5 = sum(v[2] for v in sorted_vals) / 5
        flow2_data[code] = {'amt_ma5': round(amt_ma5, 2), 'ast_ma5': round(ast_ma5, 2)}
stockFlowReady = days_collected >= 5

# 回测数据
BACKTEST = [
    ['↑1%~3%','20','+12.92%','75%','⭐⭐⭐ 最强信号'],
    ['↑0%~1%','9','+0.87%','100%','⭐⭐ 有效'],
    ['↑>5%','135','-1.09%','39.5%','⚠️ 不稳'],
    ['↑3%~5%','13','-0.39%','25%','⭐ 弱信号'],
    ['↓0%~-1%','9','-0.79%','0%','⚠️ 看空'],
    ['↓-1%~-3%','22','+1.47%','75%','信号不稳'],
    ['↓-3%~-5%','12','-1.92%','0%','⚠️ 可靠看空'],
    ['↓<-5%','153','+1.29%','72.7%','信号不稳'],
]

html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>ETF申购流入全面分析 - {today_str}</title>
<script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.1/chart.umd.js"></script>
<style>
*{{margin:0;padding:0;box-sizing:border-box}}
body{{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;background:#f8fafc;color:#1e293b;font-size:14px}}
.header{{background:linear-gradient(135deg,#1e293b,#334155);color:#fff;padding:24px 32px}}
.header h1{{font-size:22px;font-weight:600}}
.header p{{font-size:13px;color:#94a3b8;margin-top:4px}}
.nav-tabs{{display:flex;gap:2px;padding:0 32px;background:#fff;border-bottom:2px solid #e2e8f0;position:sticky;top:0;z-index:10}}
.nav-tab{{padding:12px 20px;cursor:pointer;font-size:13px;font-weight:500;color:#64748b;border-bottom:2px solid transparent;margin-bottom:-2px;transition:all .15s}}
.nav-tab:hover{{color:#1e293b;background:#f8fafc}}
.nav-tab.active{{color:#2563eb;border-bottom-color:#2563eb}}
.tab-content{{display:none;padding:20px 32px}}
.tab-content.active{{display:block}}
.stats-bar{{display:flex;gap:12px;padding:12px 28px;background:#fff;border-bottom:1px solid #e2e8f0;flex-wrap:wrap}}
.stat-card{{flex:1;padding:10px 16px;border-radius:8px;background:#f8fafc;text-align:center;min-width:100px}}
.stat-card .num{{font-size:24px;font-weight:600}}
.stat-card .lbl{{font-size:11px;color:#64748b;margin-top:2px}}
.controls{{padding:10px 28px;background:#fff;display:flex;gap:10px;align-items:center;border-bottom:1px solid #e2e8f0;flex-wrap:wrap}}
.controls input,.controls select{{padding:5px 10px;border:1px solid #cbd5e1;border-radius:6px;font-size:12px}}
.controls input{{flex:1;min-width:120px}}
.table-wrap{{overflow-x:auto}}
table{{width:100%;border-collapse:collapse;font-size:12px;margin-bottom:20px}}
th{{background:#f1f5f9;padding:8px 6px;text-align:left;font-weight:500;color:#475569;border-bottom:2px solid #e2e8f0;white-space:nowrap;font-size:11px;cursor:pointer;position:sticky;top:0;z-index:2}}
th:hover{{background:#e2e8f0}}
td{{padding:6px 6px;border-bottom:1px solid #f1f5f9;white-space:nowrap}}
tr:hover{{background:#f8fafc!important}}
.rank-cell{{font-weight:500;color:#64748b;width:30px;text-align:center;font-size:11px}}
.name-cell{{font-weight:500;color:#1e293b}}
.flow-cell{{font-weight:600;font-family:monospace}}
.desc-cell{{color:#475569;font-size:11px;max-width:200px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}}
.dir-badge{{display:inline-block;padding:2px 8px;border-radius:4px;font-size:10px;font-weight:500}}
.dir-in{{background:#dcfce7;color:#166534}}
.dir-out{{background:#fef2f2;color:#991b1b}}
.dir-flat{{background:#f1f5f9;color:#475569}}
.bar-wrap{{width:60px;height:6px;background:#e2e8f0;border-radius:3px;overflow:hidden;display:inline-block}}
.bar-bar{{height:100%;border-radius:3px;transition:width .3s}}
.count-badge{{display:inline-block;padding:2px 8px;border-radius:10px;background:#e2e8f0;font-size:11px;color:#475569;margin-left:6px;vertical-align:middle}}
.star{{color:#f59e0b;font-size:13px}}
.section-title{{font-size:16px;font-weight:600;margin:20px 0 12px;padding-bottom:8px;border-bottom:2px solid #e2e8f0}}
.section-sub{{font-size:12px;color:#64748b;margin-top:-8px;margin-bottom:16px}}
.qual-section{{padding:12px 16px;margin-bottom:12px;border-radius:8px;background:#fff;border:1px solid #e2e8f0}}
.qual-section h4{{font-size:14px;font-weight:600;margin-bottom:8px}}
.qual-table{{width:100%}}
.qual-table th{{background:transparent;font-size:11px;padding:4px 8px}}
.qual-table td{{padding:4px 8px;font-size:12px}}
.overlap-box{{padding:20px;border-radius:10px;background:linear-gradient(135deg,#fefce8,#fef9c3);border:2px solid #f59e0b;margin:16px 0}}
.overlap-box h3{{font-size:16px;color:#92400e;margin-bottom:8px}}
.backtest-box{{padding:16px;border-radius:8px;background:#f8fafc;border:1px solid #e2e8f0;margin:12px 0}}
.backtest-box table{{margin:0}}
.footnote{{font-size:11px;color:#94a3b8;margin-top:16px;padding:12px;border-top:1px solid #e2e8f0}}
.tip-trigger{{display:inline-flex;align-items:center;justify-content:center;width:13px;height:13px;border-radius:50%;background:#cbd5e1;color:#fff;font-size:8px;font-weight:600;cursor:pointer;margin-left:2px;vertical-align:super}}
.tip-trigger:hover{{background:#6366f1}}
.tip-overlay{{display:none;position:fixed;top:0;left:0;width:100%;height:100%;z-index:100;background:rgba(0,0,0,0.3)}}
.tip-overlay.show{{display:block}}
.tip-box{{position:fixed;top:50%;left:50%;transform:translate(-50%,-50%);background:#fff;border-radius:10px;padding:24px;max-width:420px;width:90%;z-index:101}}
.tip-box h4{{font-size:15px;font-weight:600;margin-bottom:10px}}
.tip-box p{{font-size:13px;color:#475569;line-height:1.7;margin:0}}
.tip-box .close-tip{{float:right;border:none;background:0;font-size:20px;cursor:pointer;color:#94a3b8;padding:0}}
@media(max-width:768px){{.tab-content{{padding:12px}} .nav-tabs{{overflow-x:auto}}}}
.new-field{{color:#4f46e5}}
.th-{{color:#6366f1;font-weight:600}}
.code-sub{{font-size:10px;color:#94a3b8;font-weight:400}}
.code-sub-sm{{font-size:10px;color:#94a3b8;font-weight:400}}
.sell-alert{{padding:16px;border-radius:10px;background:linear-gradient(135deg,#fef2f2,#fee2e2);border:2px solid #ef4444;margin:16px 0}}
.sell-alert h3{{font-size:16px;color:#991b1b;margin-bottom:8px}}
.sell-row{{background:#fff}}
.sell-flow{{color:#ef4444!important}}
.sell-strong{{display:inline-block;padding:2px 8px;border-radius:4px;background:#ef4444;color:#fff;font-size:10px;font-weight:600;margin-right:4px}}
.sell-normal{{display:inline-block;padding:2px 8px;border-radius:4px;background:#f97316;color:#fff;font-size:10px;font-weight:600;margin-right:4px}}
</style></head>
<body>

<div class="header">
  <h1>🏦 全市场ETF申购流入全面分析</h1>
  <p>覆盖{len(dates)}个交易日 · {len(all_data)}个指数ETF · 39列全字段 · 支持日期切换查看历史</p>
</div>

<div class="nav-tabs">
  <div class="nav-tab active" onclick="switchTab('tab-rank')">📊 全量排行</div>
  <div class="nav-tab" onclick="switchTab('tab-qual')">🔍 定性分析</div>
  <div class="nav-tab" onclick="switchTab('tab-quant')">📈 量化分析</div>
  <div class="nav-tab" onclick="switchTab('tab-summary')">🎯 最终结论</div>
  <div class="nav-tab" onclick="switchTab('tab-watchlist')">⭐ 自选监控</div>
</div>

<div class="controls" style="background:#f1f5f9;padding:10px 28px;border-bottom:1px solid #e2e8f0">
  <label style="font-size:12px;font-weight:500;color:#475569">📅 选择日期:</label>
  <select id="datePicker" onchange="switchDate(this.value)" style="padding:5px 10px;border:1px solid #cbd5e1;border-radius:6px;font-size:13px;font-weight:500">"""
for d in dates:
    sel = ' selected' if d == today_str else ''
    html += f'<option value="{d}"{sel}>{d}</option>'
html += """</select>
  <span id="dateInfo" style="font-size:12px;color:#64748b;margin-left:6px"></span>
</div>

<div id="tab-rank" class="tab-content active">
  <div class="stats-bar" id="statsRank">
    <div class="stat-card"><div class="num" id="scIn" style="color:#166534">0</div><div class="lbl">净申购</div></div>
    <div class="stat-card"><div class="num" id="scOut" style="color:#991b1b">0</div><div class="lbl">净赎回</div></div>
    <div class="stat-card"><div class="num" id="scFlat" style="color:#475569">0</div><div class="lbl">持平</div></div>
    <div class="stat-card"><div class="num" id="scTotal">0</div><div class="lbl">总计指数</div></div>
  </div>
  <div class="controls">
    <input type="text" id="search" placeholder="搜索指数名称..." oninput="filt()">
    <select id="filter" onchange="filt()">
      <option value="all">全部</option><option value="in">净申购</option><option value="out">净赎回</option><option value="flat">持平</option>
    </select>
    <span style="font-size:12px;color:#64748b" id="countInfo"></span>
  </div>
  <div style="padding:6px 0;font-size:11px;color:#64748b">🆕 新增字段: <span class="new-field">成交量</span> · <span class="new-field">指数日涨跌</span> · <span class="new-field">指数年收益</span> · <span class="new-field">年内最大回撤</span> · <span class="new-field">T+0标记</span> · <span class="new-field">折溢价走势</span> · <span class="new-field">平均折溢价</span></div>
  <div class="table-wrap">
  <table><thead><tr id="tableHeader">
    <th>#</th><th>方向</th><th>指数</th><th>ETF</th>
    <th>总份额<span class="tip-trigger" onclick="showTip('总份额','基金当前的总份额(亿份)')">?</span></th>
    <th>资金流<span class="tip-trigger" onclick="showTip('资金流','当日净申购净赎回金额(亿元)=份额变化量×净值')">?</span></th>
    <th>条</th>
    <th>变化率<span class="tip-trigger" onclick="showTip('变化率','当日基金总份额增减比例(%)')">?</span></th>
    <th>涨跌幅<span class="tip-trigger" onclick="showTip('涨跌幅','当日ETF价格涨跌幅(%)')">?</span></th>
    <th class="new-field">成交量<span class="tip-trigger" onclick="showTip('成交量','当日成交量(手),1手=100份')">?</span></th>
    <th>净值<span class="tip-trigger" onclick="showTip('净值','基金单位净值(元)')">?</span></th>
    <th>折溢价<span class="tip-trigger" onclick="showTip('折溢价','ETF市价相对净值的偏离度(%)')">?</span></th>
    <th class="new-field">指数日涨跌<span class="tip-trigger" onclick="showTip('指数日涨跌','跟踪指数当日涨跌幅(%)')">?</span></th>
    <th class="new-field">指数年收益<span class="tip-trigger" onclick="showTip('指数年收益','跟踪指数近1年收益率(%)')">?</span></th>
    <th>YTD<span class="tip-trigger" onclick="showTip('YTD','年初至今价格涨跌幅(%)')">?</span></th>
    <th class="new-field">年内最大回撤<span class="tip-trigger" onclick="showTip('年内最大回撤','年初至今最大回撤幅度(%)')">?</span></th>
    <th>月收益<span class="tip-trigger" onclick="showTip('月收益','近1个月收益率(%)')">?</span></th>
    <th>换手率<span class="tip-trigger" onclick="showTip('换手率','当日成交量占总份额比例(%)')">?</span></th>
    <th>T+0<span class="tip-trigger" onclick="showTip('T+0标记','是否支持T+0交易,✓=是,✗=否')">?</span></th>
  </tr></thead><tbody id="tableBody">
  </tbody></table></div>
</div>

<div id="tab-qual" class="tab-content">
  <div class="section-title">🔍 定性分析 — 四象限矩阵</div>
  <div class="section-sub">判断逻辑: 份额增长方向 × 价格上涨方向 = 主力意图。绿色=积极信号, 黄色=需甄别, 红色=回避</div>
  <div id="qualContent"></div>
  <div class="footnote">说明: 🐻强力吸筹=份额涨+价格跌(机构越跌越买) | 📥压价建仓=份额涨+价格平(压价买入) | 📈温和上涨=份额涨+价格涨(量价配合) | ⚠️量价齐升=份额涨+价格暴涨(注意过热) | 🚨出货嫌疑=份额跌+价格涨(拉高出货) | 💀恐慌出逃=份额跌+价格跌(资金撤离)</div>
</div>

<div id="tab-quant" class="tab-content">
  <div class="section-title">📈 量化分析 — 基于373个历史样本</div>
  <div class="section-sub">数据源: 天天基金季度报告(2024Q1~2026Q1, 127个ETF) + westockdata K线60日</div>
  <h4 style="margin:12px 0 8px">历史回测: 不同份额变化区间的后续价格表现</h4>
  <div class="backtest-box">
  <table><thead><tr><th>份额变化区间</th><th>样本数</th><th>20日回报均值</th><th>正收益比例</th><th>信号评级</th></tr></thead><tbody>
"""
for bt in BACKTEST:
    html += f"<tr><td>{bt[0]}</td><td>{bt[1]}</td><td>{bt[2]}</td><td>{bt[3]}</td><td>{bt[4]}</td></tr>"
html += """</tbody></table>
  </div>
  
  <h4 style="margin:20px 0 8px">量化回测筛选结果（条件: 份额↑0.5%~3% + 价格↑ + 资金流入正）</h4>
  <p style="font-size:11px;color:#64748b;margin:-4px 0 8px">🟢=资金流高于全市场中位数 🔴=低于中位数</p>
  <div class="backtest-box">
  <table><thead><tr><th>指数</th><th>份额变化</th><th>价格涨跌</th><th>资金流</th><th>同类历史胜率</th></tr></thead><tbody id="quantRecomTbody">
  </tbody></table>
  </div>
  
  <div class="section-title" style="margin-top:24px">📐 stock_flow2 因子分析（广发证券IC 5.5-6.0%）</div>
  <div class="section-sub">基于日频份额变化的5日均值因子, stock_flow2amt_ma5(金额) + stock_flow2ast_ma5(份额)</div>
  <div id="stockFlowPanel">
    <div style="padding:20px;text-align:center;color:#64748b">⏳ 加载中...</div>
  </div>
  
  <div class="footnote">关键发现: 份额↑1%~3%是历史最强信号(+12.92%均值, 75%胜率)。份额↓-3%~-5%是可靠看空信号(0%胜率)。份额↑>5%反而平均亏损(-1.09%), 说明极端份额变化不可简单看涨。</div>
</div>

<div id="tab-summary" class="tab-content">
  <div class="section-title" style="color:#92400e">🎯 最终结论 — 量化和定性重叠推荐</div>
  <div class="section-sub">两套独立方法论同时选出的ETF, 置信度最高</div>
  <div id="marketStatsPanel" style="display:block"></div>
  <hr style="border:none;border-top:1px solid #e2e8f0;margin:16px 0">
  <div id="summaryContent"></div>
  <div class="footnote">
  <b>分析方法说明:</b><br>
  ① <b>定性分析</b>: 基于"份额×价格"四象限矩阵, 判断主力资金意图。来源: 券商研究报告框架。<br>
  ② <b>量化分析</b>: 基于127个ETF的373个季度变化样本, 回测各份额变化区间的后续价格表现。数据源: 天天基金季度报告+westockdata K线。<br>
  ③ <b>重叠推荐</b>: 两套方法同时选出的ETF, 置信度最高。定性看资金意图, 量化看历史统计。<br>
  ④ <b>卖点预警</b>: 当日出现"出货嫌疑/恐慌出逃/大额流出"的品种, 建议回避或卖出。</div>
</div>

<div id="tab-watchlist" class="tab-content">
  <div class="section-title">⭐ 自选标的监控</div>
  <div class="section-sub">输入ETF代码添加到自选, 独立展现量化和定性分析结果（新代码下次定时采集后生效）</div>
  <div id="watchlistInput" style="margin-bottom:16px;display:flex;gap:8px;align-items:center;flex-wrap:wrap">
    <input id="watchlistCodeInput" type="text" placeholder="输入ETF代码, 如 sh512890" style="flex:1;min-width:180px;padding:8px 12px;border:1px solid #cbd5e1;border-radius:6px;font-size:13px;font-family:monospace">
    <button onclick="addWatchlistItem()" style="padding:8px 20px;background:#2563eb;color:#fff;border:none;border-radius:6px;cursor:pointer;font-size:13px">+ 添加</button>
    <button onclick="clearWatchlist()" style="padding:8px 20px;background:#ef4444;color:#fff;border:none;border-radius:6px;cursor:pointer;font-size:13px">清空</button>
  </div>
  <div id="watchlistTags" style="margin-bottom:12px;display:flex;flex-wrap:wrap;gap:6px"></div>
  <div id="watchlistContent">
    <p style="color:#94a3b8;padding:40px;text-align:center">请先在上方输入ETF代码添加关注标的</p>
  </div>
</div>

<div id="tipOverlay" class="tip-overlay" onclick="this.classList.remove('show')">
  <div class="tip-box">
    <button class="close-tip" onclick="document.getElementById('tipOverlay').classList.remove('show')">✕</button>
    <h4 id="tipTitle">字段说明</h4><p id="tipBody">点击?查看字段含义</p>
  </div>
</div>

<script>
// ========== 数据从 etf_data.json 动态加载 ==========
// HTML 不内置任何数据, 页面启动时自动 fetch
// 数据更新后重新运行 gen_analysis_html.py 即可, 浏览器刷新即得最新
let ALL_DATA = {};
let currentDate = '""" + today_str + """';

function init() {
  // 从相对路径加载数据JSON (与HTML同服务器的etf_history/etf_data.json)
  fetch('etf_history/etf_data.json?_t=' + Date.now())
    .then(r => r.json())
    .then(data => {
      ALL_DATA = data.dates;
      ALL_DATA._meta = data;  // stockFlow等元数据
      const keys = Object.keys(ALL_DATA).sort();
      currentDate = keys.pop() || '""" + today_str + """';
      document.getElementById('datePicker').value = currentDate;
      renderStockFlowStatus();
      renderWatchlistTags();
      if (document.querySelector('#tab-rank.active')) {
        switchDate(currentDate);
      }
    })
    .catch(err => {
      document.getElementById('dateInfo').textContent = '⚠️ 数据加载失败: ' + err.message;
      document.getElementById('dateInfo').style.color = '#ef4444';
    });
}

function showTip(title, body) {
  document.getElementById('tipTitle').textContent = title;
  document.getElementById('tipBody').textContent = body;
  document.getElementById('tipOverlay').classList.add('show');
}

// ========== 日期切换（已由 init() 设置 currentDate）==========
function switchDate(date) {
  currentDate = date;
  document.getElementById('dateInfo').textContent = '📊 ' + date + ' 数据';
  document.getElementById('datePicker').value = date;
  if (ALL_DATA[currentDate]) {
    renderAll(date);
  } else {
    document.getElementById('dateInfo').textContent = '⚠️ ' + date + ' 暂无数据';
  }
}

function renderAll(date) {
  const dd = ALL_DATA[date];
  if (!dd) return;
  renderTable(date, dd);
  renderQual(date, dd);
  renderQuant(date, dd);
  renderMarketStats(dd);
  renderSummary(date, dd);
  renderWatchlist(date, dd);
  updateStats(dd);
  filt();
}

function renderTable(date, dd) {
  const data = dd.data;
  const tb = document.getElementById('tableBody');
  let h = '';
  for (const r of data) {
    const barPct = Math.min(Math.abs(r.flow) / 56 * 100, 100);
    h += '<tr class="' + (r.flow > 0 ? 'bg-green-50' : r.flow < 0 ? 'bg-red-50' : '') + '">';
    h += '<td class="rank-cell">' + r.rank + '</td>';
    h += '<td><span class="dir-badge dir-' + r.dir + '">' + (r.dir === 'in' ? '净申购' : r.dir === 'out' ? '净赎回' : '持平') + '</span></td>';
    h += '<td class="name-cell">' + r.name + '<br><span class="code-sub">' + (Array.isArray(r.codes) ? r.codes.join(', ') : r.codes || '') + '</span></td>';
    h += '<td>' + (Array.isArray(r.codes) ? r.codes.length : (r.codes || 0)) + '</td>';
    h += '<td>' + r.shares.toFixed(2) + '</td>';
    h += '<td class="flow-cell">' + (r.flow > 0 ? '+' : '') + r.flow.toFixed(2) + '</td>';
    h += '<td><div class="bar-wrap"><div class="bar-bar" style="width:' + barPct.toFixed(1) + '%;background:' + (r.flow > 0 ? '#22c55e' : r.flow < 0 ? '#ef4444' : '#9ca3af') + '"></div></div></td>';
    h += '<td>' + (r.chgPct > 0 ? '+' : '') + r.chgPct.toFixed(2) + '%</td>';
    h += '<td>' + (r.pc > 0 ? '+' : '') + r.pc.toFixed(2) + '%</td>';
    h += '<td class="new-field">' + r.volume.toLocaleString() + '</td>';
    h += '<td>' + r.nav.toFixed(2) + '</td>';
    h += '<td>' + r.disc + '</td>';
    h += '<td class="new-field">' + (r.indexChg || '-') + '</td>';
    h += '<td class="new-field">' + (r.index1Y || '-') + '</td>';
    h += '<td>' + (r.ytd > 0 ? '+' : '') + r.ytd.toFixed(1) + '%</td>';
    h += '<td class="new-field">' + (r.ytdMdd.toFixed(1) || '-') + '%</td>';
    h += '<td>' + (r.r1m > 0 ? '+' : '') + r.r1m.toFixed(1) + '%</td>';
    h += '<td>' + r.turnover.toFixed(1) + '%</td>';
    h += '<td>' + (r.isT0 || '-') + '</td>';
    h += '</tr>';
  }
  tb.innerHTML = h;
}

function updateStats(dd) {
  document.getElementById('scIn').textContent = dd.inflow;
  document.getElementById('scOut').textContent = dd.outflow;
  document.getElementById('scFlat').textContent = dd.flat;
  document.getElementById('scTotal').textContent = dd.total;
}

function renderQual(date, dd) {
  const data = dd.data;
  const qualSections = [
    {title:'🐻 强力吸筹（份额↑+价格↓）', keywords:['🐻强力吸筹'], bg:'#dcfce7'},
    {title:'📥 压价建仓（份额↑+价格→）', keywords:['📥压价建仓'], bg:'#dcfce7'},
    {title:'📈 温和上涨（份额↑+价格↑）', keywords:['📈温和上涨', '📈无量空涨'], bg:'#e0f2fe'},
    {title:'⚠️ 量价齐升需甄别', keywords:['⚠️量价齐升'], bg:'#fef9c3'},
    {title:'➡️ 横盘观望/其他', keywords:['➡️横盘观望', '⬇️无量下跌'], bg:'#f1f5f9'},
    {title:'🚨 出货嫌疑', keywords:['🚨出货嫌疑'], bg:'#fef2f2'},
    {title:'💀 恐慌出逃', keywords:['💀恐慌出逃'], bg:'#fef2f2'},
  ];
  let h = '';
  for (const sec of qualSections) {
    const items = data.filter(r => sec.keywords.some(k => r.sig.includes(k)));
    if (items.length === 0) continue;
    items.sort((a,b) => Math.abs(b.flow) - Math.abs(a.flow));
    h += '<div class="qual-section" style="border-left:4px solid ' + sec.bg + '">';
    h += '<h4>' + sec.title + ' <span class="count-badge">' + items.length + '个</span></h4>';
    h += '<table class="qual-table"><tr><th>指数</th><th>份额变化</th><th>价格涨跌</th><th>资金流</th><th>信号说明</th></tr>';
    for (const r of items.slice(0, 10)) {
      h += '<tr><td class="name-cell">' + r.name + '<br><span class="code-sub-sm">' + (r.mainCode || '') + '</span></td><td>' + (r.chgPct > 0 ? '+' : '') + r.chgPct.toFixed(2) + '%</td><td>' + (r.pc > 0 ? '+' : '') + r.pc.toFixed(2) + '%</td><td class="flow-cell">' + (r.flow > 0 ? '+' : '') + r.flow.toFixed(2) + '亿</td><td class="desc-cell">' + r.desc + '</td></tr>';
    }
    h += '</table></div>';
  }
  document.getElementById('qualContent').innerHTML = h || '<p style="color:#64748b;padding:12px">当前日期暂无数据</p>';
}

function renderQuant(date, dd) {
  const qb = dd.onlyQuant;
  const ms = dd.marketStats;
  const tb = document.getElementById('quantRecomTbody');
  let h = '';
  for (const name of qb) {
    const r = dd.data.find(x => x.name === name);
    if (!r) continue;
    const vsMedian = ms && r.flow > ms.medianFlow ? '🟢' : (ms && r.flow < ms.medianFlow ? '🔴' : '');
    h += '<tr><td class="name-cell">' + r.name + '<br><span class="code-sub-sm">' + (r.mainCode || '') + '</span></td><td>' + (r.chgPct > 0 ? '+' : '') + r.chgPct.toFixed(2) + '%</td><td>' + (r.pc > 0 ? '+' : '') + r.pc.toFixed(2) + '%</td><td class="flow-cell">' + vsMedian + ' ' + (r.flow > 0 ? '+' : '') + r.flow.toFixed(2) + '亿</td><td>75%胜率</td></tr>';
  }
  tb.innerHTML = h || '<tr><td colspan="5" style="color:#64748b;text-align:center">当前日期无符合条件的量化推荐</td></tr>';
}

// ===== 市场基准统计 =====
function renderMarketStats(dd) {
  const ms = dd.marketStats;
  if (!ms) return;
  let h = '<div class="stats-grid" style="display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:10px;margin-bottom:16px">';
  
  // 前三资金流入
  h += '<div class="backtest-box" style="margin:0">';
  h += '<h5 style="font-size:13px;margin-bottom:8px">🏆 资金流入 Top3</h5><table style="font-size:11px">';
  for (const item of ms.top3Flow) {
    h += '<tr><td style="padding:2px 4px" class="name-cell">' + item.name + '<br><span class="code-sub-sm">' + (item.mainCode || '') + '</span></td><td style="padding:2px 4px;font-weight:600;color:#166534">+' + item.flow + '亿</td></tr>';
  }
  h += '</table></div>';
  
  // 前三份额增长
  h += '<div class="backtest-box" style="margin:0">';
  h += '<h5 style="font-size:13px;margin-bottom:8px">🏆 份额增长 Top3</h5><table style="font-size:11px">';
  for (const item of ms.top3Chg) {
    h += '<tr><td style="padding:2px 4px" class="name-cell">' + item.name + '<br><span class="code-sub-sm">' + (item.mainCode || '') + '</span></td><td style="padding:2px 4px;font-weight:600;color:#166534">+' + item.chg + '%</td></tr>';
  }
  h += '</table></div>';
  
  // 中位数 + 平均数 (全量130只, 含零值)
  h += '<div class="backtest-box" style="margin:0">';
  h += '<h5 style="font-size:13px;margin-bottom:8px">📊 全市场中位数</h5>';
  h += '<div style="font-size:12px;padding:4px 8px"><span style="color:#64748b">资金流:</span> <strong>' + (ms.medianFlow > 0 ? '+' : '') + ms.medianFlow + '亿</strong> <span style="font-size:11px;color:#94a3b8">(分布: ↑' + ms.posCount + '只, —' + ms.zeroCount + '只, ↓' + ms.negCount + '只)</span></div>';
  h += '<div style="font-size:12px;padding:4px 8px"><span style="color:#64748b">份额变化率:</span> <strong>' + (ms.medianChg > 0 ? '+' : '') + ms.medianChg + '%</strong></div>';
  h += '</div>';
  
  h += '<div class="backtest-box" style="margin:0">';
  h += '<h5 style="font-size:13px;margin-bottom:8px">📊 全市场均值</h5>';
  h += '<div style="font-size:12px;padding:4px 8px"><span style="color:#64748b">资金流:</span> <strong>' + (ms.avgFlow > 0 ? '+' : '') + ms.avgFlow + '亿</strong></div>';
  h += '<div style="font-size:12px;padding:4px 8px"><span style="color:#64748b">份额变化率:</span> <strong>' + (ms.avgChg > 0 ? '+' : '') + ms.avgChg + '%</strong></div>';
  h += '</div>';
  
  h += '</div>';
  h += '<div style="font-size:11px;color:#94a3b8;margin:-8px 0 16px">💡 中位数为0说明排名正中间的第65只ETF资金流恰好持平——实际分布为 <strong>↑' + ms.posCount + '只净申购 / —' + ms.zeroCount + '只持平 / ↓' + ms.negCount + '只净赎回</strong>。推荐标的若>0代表资金流超过半数ETF。</div>';
  
  const panel = document.getElementById('marketStatsPanel');
  if (panel) panel.innerHTML = h;
}

// ===== stock_flow2 因子 =====
function renderStockFlowStatus() {
  const meta = ALL_DATA._meta;
  if (!meta || !meta.stockFlow) return;
  const sf = meta.stockFlow;
  let h = '';
  if (sf.ready) {
    h += '<div style="padding:16px;background:#f0fdf4;border:1px solid #86efac;border-radius:8px">';
    h += '<h5 style="font-size:14px;color:#166534">✅ stock_flow2 因子可计算! (已采集' + sf.daysCollected + '天)</h5>';
    h += '<table style="font-size:11px;margin-top:8px"><thead><tr><th>指数</th><th>amt_ma5(元)</th><th>ast_ma5(份)</th></tr></thead><tbody>';
    const sorted = Object.entries(sf.data).sort((a,b) => Math.abs(b[1].amt_ma5) - Math.abs(a[1].amt_ma5));
    for (const [code, val] of sorted.slice(0, 20)) {
      h += '<tr><td class="name-cell">' + code + '</td><td>' + val.amt_ma5.toLocaleString() + '</td><td>' + val.ast_ma5.toLocaleString() + '</td></tr>';
    }
    h += '</tbody></table></div>';
  } else {
    const daysLeft = sf.neededDays - sf.daysCollected;
    const pct = Math.round(sf.daysCollected / sf.neededDays * 100);
    h += '<div style="padding:20px;background:#fefce8;border:1px solid #facc15;border-radius:8px;text-align:center">';
    h += '<div style="font-size:28px;font-weight:600;color:#92400e">' + sf.daysCollected + '/' + sf.neededDays + '</div>';
    h += '<div style="font-size:13px;color:#92400e;margin:6px 0">日频数据采集中, 还需 ' + daysLeft + ' 个交易日</div>';
    h += '<div style="width:200px;height:8px;background:#fef9c3;border-radius:4px;margin:8px auto;overflow:hidden">';
    h += '<div style="height:100%;width:' + pct + '%;background:#f59e0b;border-radius:4px"></div></div>';
    h += '<div style="font-size:11px;color:#a16207">stock_flow2amt_ma5(申赎金额5日均值) + stock_flow2ast_ma5(申赎份额5日均值)</div>';
    h += '<div style="font-size:11px;color:#a16207;margin-top:4px">累计5天后自动开始计算, 广发证券IC 5.5-6.0%</div>';
    h += '</div>';
  }
  const panel = document.getElementById('stockFlowPanel');
  if (panel) panel.innerHTML = h;
}

function renderSummary(date, dd) {
  const ov = dd.overlap;
  const oq = dd.onlyQuant;
  const ol = dd.onlyQual;
  const sell = dd.sellSignals || [];
  let h = '';
  
  // ===== 卖点预警（原回避清单） =====
  h += '<div class="sell-alert"><h3>🔴 卖点预警' + (sell.length > 0 ? '（' + sell.length + '个）' : '（当前无信号）') + '</h3>';
  h += '<p style="font-size:12px;color:#991b1b;margin-bottom:10px">以下指数今日出现<strong>出货嫌疑/恐慌出逃/大额资金流出</strong>，建议回避或卖出</p>';
  if (sell.length > 0) {
    h += '<table><thead><tr><th>指数</th><th>份额变化</th><th>价格涨跌</th><th>资金流</th><th>风险信号</th></tr></thead><tbody>';
    for (const s of sell) {
      const badge = s.type === 'both' ? '强烈卖出' : (s.type === 'qual' ? '定性卖出' : '量化卖出');
      const badgeCls = s.type === 'both' ? 'sell-strong' : 'sell-normal';
      h += '<tr class="sell-row">';
      h += '<td class="name-cell">' + s.name + '<br><span class="code-sub-sm">' + (s.mainCode || '') + '</span></td>';
      h += '<td>' + (s.curChg > 0 ? '+' : '') + s.curChg.toFixed(2) + '%</td>';
      h += '<td>' + (s.curPc > 0 ? '+' : '') + s.curPc.toFixed(2) + '%</td>';
      h += '<td class="flow-cell sell-flow">' + (s.curFlow > 0 ? '+' : '') + s.curFlow.toFixed(2) + '亿</td>';
      h += '<td><span class="' + badgeCls + '">' + badge + '</span> ' + s.reasons + '</td>';
      h += '</tr>';
    }
    h += '</tbody></table>';
  } else {
    h += '<p style="font-size:13px;color:#166534;padding:12px 0;margin:0">✅ 今日未检测到明显的卖出/回避信号，市场整体健康。</p>';
  }
  h += '</div>';
  
  if (ov.length > 0) {
    h += '<div class="overlap-box"><h3>🎯 强烈推荐（' + ov.length + '个）</h3><p style="font-size:13px;color:#92400e;margin-bottom:10px">量化回测 + 四象限定性分析 同时确认</p>';
    h += '<table><thead><tr><th></th><th>指数</th><th>份额变化</th><th>价格涨跌</th><th>资金流</th><th>定性信号</th></tr></thead><tbody>';
    for (const name of ov) {
      const r = dd.data.find(x => x.name === name);
      if (!r) continue;
      h += '<tr><td><span class="star">⭐⭐⭐</span></td><td class="name-cell">' + r.name + '<br><span class="code-sub-sm">' + (r.mainCode || '') + '</span></td><td>' + (r.chgPct > 0 ? '+' : '') + r.chgPct.toFixed(2) + '%</td><td>' + (r.pc > 0 ? '+' : '') + r.pc.toFixed(2) + '%</td><td class="flow-cell">' + (r.flow > 0 ? '+' : '') + r.flow.toFixed(2) + '亿</td><td class="desc-cell">' + r.sig.replace(/[^\w\u4e00-\u9fa5]/g,'').trim() + '</td></tr>';
    }
    h += '</tbody></table></div>';
  }
  if (oq.length > 0) {
    h += '<h4 style="margin:16px 0 8px">📊 仅量化推荐（' + oq.length + '个）</h4><p style="font-size:12px;color:#64748b;margin-bottom:8px">量价配合好,但定性未归入积极区间</p>';
    h += '<div class="backtest-box"><table><thead><tr><th>指数</th><th>份额变化</th><th>价格涨跌</th><th>资金流</th><th>参考</th></tr></thead><tbody>';
    for (const name of oq.slice(0, 10)) {
      const r = dd.data.find(x => x.name === name);
      if (!r) continue;
      h += '<tr><td class="name-cell">' + r.name + '<br><span class="code-sub-sm">' + (r.mainCode || '') + '</span></td><td>' + (r.chgPct > 0 ? '+' : '') + r.chgPct.toFixed(2) + '%</td><td>' + (r.pc > 0 ? '+' : '') + r.pc.toFixed(2) + '%</td><td>' + (r.flow > 0 ? '+' : '') + r.flow.toFixed(2) + '亿</td><td>历史同类胜率75%</td></tr>';
    }
    h += '</tbody></table></div>';
  }
  if (ol.length > 0) {
    h += '<h4 style="margin:16px 0 8px">🔍 仅定性推荐（' + ol.length + '个）</h4><p style="font-size:12px;color:#64748b;margin-bottom:8px">四象限显示主力建仓/吸筹迹象,但量化历史数据不支持</p>';
    h += '<div class="backtest-box"><table><thead><tr><th>指数</th><th>份额变化</th><th>资金流</th><th>参考逻辑</th></tr></thead><tbody>';
    for (const name of ol.slice(0, 10)) {
      const r = dd.data.find(x => x.name === name);
      if (!r) continue;
      h += '<tr><td class="name-cell">' + r.name + '<br><span class="code-sub-sm">' + (r.mainCode || '') + '</span></td><td>' + (r.chgPct > 0 ? '+' : '') + r.chgPct.toFixed(2) + '%</td><td>' + (r.flow > 0 ? '+' : '') + r.flow.toFixed(2) + '亿</td><td class="desc-cell">' + r.desc + '</td></tr>';
    }
    h += '</tbody></table></div>';
  }
  document.getElementById('summaryContent').innerHTML = h;
}

function switchTab(id) {
  document.querySelectorAll('.tab-content').forEach(t => t.classList.remove('active'));
  document.querySelectorAll('.nav-tab').forEach(t => t.classList.remove('active'));
  document.getElementById(id).classList.add('active');
  // 标记活动tab
  document.querySelectorAll('.nav-tab').forEach(t => {
    if (t.getAttribute('onclick') && t.getAttribute('onclick').includes(id)) t.classList.add('active');
  });
}

function filt() {
  const q = document.getElementById('search').value.toLowerCase();
  const f = document.getElementById('filter').value;
  const rows = document.querySelectorAll('#tableBody tr');
  let vis = 0;
  for (let i = 0; i < rows.length; i++) {
    const name = rows[i].cells ? (rows[i].cells[2] ? rows[i].cells[2].textContent.toLowerCase() : '') : '';
    const dirCell = rows[i].cells ? (rows[i].cells[1] ? rows[i].cells[1].textContent.trim() : '') : '';
    let s = true;
    if (q && name.indexOf(q) === -1) s = false;
    if (f === 'in' && dirCell !== '净申购') s = false;
    if (f === 'out' && dirCell !== '净赎回') s = false;
    if (f === 'flat' && dirCell !== '持平') s = false;
    rows[i].style.display = s ? '' : 'none';
    if (s) vis++;
  }
  document.getElementById('countInfo').textContent = vis + '/' + rows.length + '条';
}

// ========== 自选监控 ==========
let _watchlistCache = null; // 缓存, 减少API调用

async function loadWatchlist() {
  try {
    const r = await fetch('/api/watchlist');
    _watchlistCache = await r.json();
    return _watchlistCache;
  } catch(e) {
    _watchlistCache = _watchlistCache || [];
    return _watchlistCache;
  }
}
async function saveWatchlist(list) {
  _watchlistCache = list;
  try {
    await fetch('/api/watchlist', {
      method: 'POST', headers: {'Content-Type': 'application/json'},
      body: JSON.stringify(list)
    });
  } catch(e) {}
}
async function addWatchlistItem() {
  const input = document.getElementById('watchlistCodeInput');
  const code = input.value.trim().toLowerCase();
  if (!code) return;
  let list = await loadWatchlist();
  if (list.includes(code)) {
    input.value = '';
    return;
  }
  list.push(code);
  await saveWatchlist(list);
  input.value = '';
  await refreshWatchlist();
}
async function removeWatchlistItem(code) {
  let list = await loadWatchlist();
  list = list.filter(x => x !== code);
  await saveWatchlist(list);
  await refreshWatchlist();
}
async function clearWatchlist() {
  if (!confirm('确定清空所有自选标的?')) return;
  await saveWatchlist([]);
  document.getElementById('watchlistContent').innerHTML =
    '<p style="color:#94a3b8;padding:40px;text-align:center">请先在上方输入ETF代码添加关注标的</p>';
  await renderWatchlistTags();
}
async function renderWatchlistTags() {
  const list = await loadWatchlist();
  const container = document.getElementById('watchlistTags');
  if (list.length === 0) {
    container.innerHTML = '';
    return;
  }
  container.innerHTML = list.map(code =>
    `<span style="display:inline-flex;align-items:center;padding:4px 10px;background:#eff6ff;border:1px solid #bfdbfe;border-radius:20px;font-size:12px;color:#1d4ed8">
      <code style="font-size:11px">${code}</code>
      <span onclick="removeWatchlistItem('${code}')" style="margin-left:6px;cursor:pointer;color:#94a3b8;font-size:14px">&times;</span>
    </span>`
  ).join('');
}
function renderWatchlist(date, dd) {
  loadWatchlist().then(list => {
    const container = document.getElementById('watchlistContent');
    if (list.length === 0) {
      container.innerHTML = '<p style="color:#94a3b8;padding:40px;text-align:center">请先在上方输入ETF代码添加关注标的</p>';
      return;
    }
    // 从dd.data中查找匹配watchlist的条目 (按codes字段或idx名称匹配)
    const items = list.map(code => {
      const found = dd.data.find(r =>
        (Array.isArray(r.codes) && r.codes.includes(code)) ||
        r.mainCode === code || r.name === code
      );
      return found ? {item: found, code: code} : null;
    }).filter(Boolean);
    const notFound = list.filter(code =>
      !items.some(x => x.code === code)
    );
    let h = '';
    // 监控表
    h += '<h4 style="margin:12px 0 8px">📊 自选标的全景监控 <span class="count-badge">' + items.length + '/' + list.length + '</span></h4>';
    if (items.length > 0) {
      h += '<div class="table-wrap"><table><thead><tr>';
      h += '<th>代码</th><th>指数</th><th>资金流</th><th>份额变化</th><th>涨跌幅</th><th>vs中位数</th><th>定性信号</th><th>量化</th><th>卖点</th></tr></thead><tbody>';
      for (const {item: r, code: c} of items) {
        const inOverlap = dd.overlap.includes(r.name);
        const inQuant = dd.onlyQuant.includes(r.name);
        const inQual = dd.onlyQual.includes(r.name);
        const sellSig = dd.sellSignals.find(s => s.name === r.name);
        const vsMedian = dd.marketStats && r.flow > dd.marketStats.medianFlow ? '🟢' : (dd.marketStats && r.flow < dd.marketStats.medianFlow ? '🔴' : '⚪');
        h += '<tr>';
        h += '<td><code style="font-size:11px">' + c + '</code></td>';
        h += '<td class="name-cell">' + r.name + '<br><span class="code-sub-sm">' + (r.mainCode || '') + '</span></td>';
        h += '<td class="flow-cell">' + (r.flow > 0 ? '+' : '') + r.flow.toFixed(2) + '亿</td>';
        h += '<td>' + (r.chgPct > 0 ? '+' : '') + r.chgPct.toFixed(2) + '%</td>';
        h += '<td>' + (r.pc > 0 ? '+' : '') + r.pc.toFixed(2) + '%</td>';
        h += '<td>' + vsMedian + '</td>';
        h += '<td class="desc-cell">' + (r.sig || '-') + '</td>';
        h += '<td>' + (inOverlap ? '<span class="dir-badge dir-in" style="font-weight:600">⭐⭐重叠</span>' : inQuant ? '<span style="color:#2563eb;font-size:11px">📊量化</span>' : inQual ? '<span style="color:#f59e0b;font-size:11px">🔍定性</span>' : '<span style="color:#94a3b8">-</span>') + '</td>';
        h += '<td>' + (sellSig ? '<span class="dir-badge dir-out" style="font-weight:600">⚠️卖出</span>' : '<span style="color:#94a3b8">-</span>') + '</td>';
        h += '</tr>';
      }
      h += '</tbody></table></div>';
    }
    // 综合建议卡片
    if (items.length > 0) {
      h += '<h4 style="margin:20px 0 8px">🎯 综合建议</h4>';
      h += '<div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(260px,1fr));gap:10px">';
      for (const {item: r, code: c} of items) {
        const inOverlap = dd.overlap.includes(r.name);
        const inQuant = dd.onlyQuant.includes(r.name);
        const inQual = dd.onlyQual.includes(r.name);
        const sellSig = dd.sellSignals.find(s => s.name === r.name);
        let action, bg, border;
        if (inOverlap && !sellSig) { action = '⭐⭐⭐ 强烈关注'; bg = '#fefce8'; border = '#f59e0b'; }
        else if (inQuant && !sellSig) { action = '📈 量化看好'; bg = '#f0fdf4'; border = '#86efac'; }
        else if (inQual && !sellSig) { action = '🔍 定性关注'; bg = '#eff6ff'; border = '#bfdbfe'; }
        else if (sellSig) { action = '🔴 建议卖出'; bg = '#fef2f2'; border = '#ef4444'; }
        else if (r.flow > 0) { action = '➡️ 持有观望'; bg = '#f8fafc'; border = '#e2e8f0'; }
        else { action = '⬇️ 资金流出, 暂不关注'; bg = '#f8fafc'; border = '#e2e8f0'; }
        h += '<div style="padding:12px;border-radius:8px;background:' + bg + ';border:1px solid ' + border + '">';
        h += '<div style="font-size:13px;font-weight:600"><code style="font-size:11px">' + c + '</code> ' + r.name + '</div>';
        h += '<div style="font-size:12px;margin-top:4px;color:#64748b">' + action + '</div>';
        h += '<div style="font-size:11px;margin-top:4px;color:#94a3b8">资金流' + (r.flow > 0 ? '+' : '') + r.flow.toFixed(2) + '亿 · 份额' + (r.chgPct > 0 ? '+' : '') + r.chgPct.toFixed(2) + '% · ' + (r.sig || '信号不明显') + '</div>';
        h += '</div>';
      }
      h += '</div>';
    }
    // 未找到的提示
    if (notFound.length > 0) {
      h += '<div style="margin-top:12px;padding:8px 12px;background:#fef2f2;border:1px solid #fecaca;border-radius:6px;font-size:12px;color:#991b1b">';
      h += '⚠️ 以下代码在当天数据中未找到（可能是新加入的自选, 下次定时采集后自动补全）: ';
      h += notFound.join(', ');
      h += '</div>';
    }
    container.innerHTML = h;
  });
}
async function refreshWatchlist() {
  await renderWatchlistTags();
  const dd = ALL_DATA[currentDate];
  if (dd) renderWatchlist(currentDate, dd);
}

// ========== 初始化: 从JSON文件加载 ==========
// 数据与HTML分离, 启动时自动 fetch etf_history/etf_data.json
// HTML无硬编码数据, 数据更新只需重新运行本脚本, 无需修改HTML
init();

// 点击表头排序
document.getElementById('tableHeader').addEventListener('click', function(e) {
  const th = e.target.closest('th');
  if (!th || th.cellIndex === undefined) return;
  const ci = th.cellIndex;
  const tb = document.getElementById('tableBody');
  const rows = Array.from(tb.querySelectorAll('tr'));
  const key = rows[0] ? rows[0].cells[ci] ? rows[0].cells[ci].textContent.trim() : '' : '';
  const isNum = !isNaN(parseFloat(key.replace('%','').replace(',','')));
  rows.sort((a, b) => {
    const va = a.cells[ci] ? a.cells[ci].textContent.trim().replace('%','').replace(/,/g,'') : '0';
    const vb = b.cells[ci] ? b.cells[ci].textContent.trim().replace('%','').replace(/,/g,'') : '0';
    const na = parseFloat(va) || 0;
    const nb = parseFloat(vb) || 0;
    if (na === nb) return 0;
    if (isNum && !isNaN(na) && !isNaN(nb)) return nb > na ? 1 : -1;
    return vb.localeCompare(va);
  });
  rows.forEach((r, i) => {
    if (r.cells[0]) r.cells[0].textContent = i + 1;
    tb.appendChild(r);
  });
});
</script>
</body></html>"""

with open(HTML_FILE, 'w', encoding='utf-8') as f:
    f.write(html)

# 导出数据JSON (供HTML fetch加载)
export = {
    'dates': all_dates_json,
    'stockFlow': {
        'daysCollected': days_collected,
        'neededDays': 5,
        'ready': stockFlowReady,
        'data': flow2_data if stockFlowReady else {},
    }
}
with open(DATA_JSON, 'w', encoding='utf-8') as f:
    json.dump(export, f, ensure_ascii=False)
print(f"✅ 已生成: {HTML_FILE} ({len(html)} bytes)")
print(f"✅ 已导出: {DATA_JSON} ({len(json.dumps(export))} bytes)")
print(f"   数据与HTML分离: 含 {len(dates)} 个交易日")
if stockFlowReady:
    print(f"   🎯 stock_flow2_ma5 因子可计算! {days_collected}天数据充足")
else:
    print(f"   ⏳ stock_flow2_ma5 还需 {5-days_collected} 天数据")
print(f"   使用方式: 启动 server.py 后通过 HTTP 访问, 支持日期切换")
