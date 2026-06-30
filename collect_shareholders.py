#!/usr/bin/env python3
"""
十大流通股东追踪脚本 — 使用F10 API获取持仓股股东数据 + 补充查询holdingDetail页
"""
import json, os, datetime, urllib.request, time, subprocess

OUTPUT_DIR = "/Users/andy/WorkBuddy/2026-06-24-23-34-24/etf_history"
WATCH_FILE = os.path.join(OUTPUT_DIR, "watchlist.json")
HOLDINGS_FILE = os.path.join(OUTPUT_DIR, "holdings.json")
SHAREHOLDER_FILE = os.path.join(OUTPUT_DIR, "shareholders.json")

today = datetime.date.today().strftime("%Y-%m-%d")

def fetch_f10_holders(code, market='SH'):
    """从东财F10 API获取十大流通股东(按季度报告)"""
    url = f"https://emweb.securities.eastmoney.com/PC_HSF10/ShareholderResearch/PageAjax?code={market}{code}"
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        resp = urllib.request.urlopen(req, timeout=15)
        data = json.loads(resp.read().decode())
        sdltgd = data.get('sdltgd', [])
        results = []
        for g in sdltgd:
            results.append({
                'rank': g.get('HOLDER_RANK', ''),
                'name': g.get('HOLDER_NAME', ''),
                'type': g.get('HOLDER_TYPE', ''),
                'holdNum': g.get('HOLD_NUM', 0),
                'holdRatio': g.get('HOLD_NUM_RATIO', 0),
                'change': g.get('CHANGE', 0),
                'changeRatio': g.get('CHANGE_RATIO', 0),
                'sharesType': g.get('SHARES_TYPE', ''),
                'endDate': str(g.get('END_DATE', ''))[:10],
            })
        return results
    except Exception as e:
        print(f"  ❌ {code}: {str(e)[:60]}")
        return []

def classify(name, type_name):
    name = name or ''
    if '全国社会保障基金' in name or '社保基金' in name:
        return '社保基金'
    if '基本养老保险' in name or '养老保险' in name:
        return '养老金'
    if '证券' in name and ('股份' in name or '有限' in name) and '基金' not in name:
        return '券商自营'
    if '证券投资基金' in name or ('基金' in name and '基金管理' in name):
        return '基金'
    if '保险' in name:
        return '保险'
    if '香港中央结算' in name:
        return '北向资金(陆股通)'
    if '中央汇金' in name or '中国证金' in name:
        return '国家队'
    if 'QFII' in name.upper():
        return 'QFII'
    if '银行' in name or '信托' in name:
        return '银行/信托'
    return type_name if type_name else '其他'

def change_direction(change):
    if change is None: return '未知'
    try:
        c = float(change)
        if c > 0: return '增持'
        elif c < 0: return '减持'
        else: return '不变'
    except: return '未知'

# ===== 1. 获取watchlist持仓股 =====
watch_codes = []
if os.path.exists(WATCH_FILE):
    with open(WATCH_FILE) as f:
        watch_codes = json.load(f)

stock_codes_full = set()
if os.path.exists(HOLDINGS_FILE):
    with open(HOLDINGS_FILE) as f:
        all_holdings = json.load(f)
    dates = sorted(all_holdings.keys())
    if dates:
        latest_h = all_holdings[dates[-1]]
        for code in watch_codes:
            if code in latest_h:
                for h in latest_h[code][:5]:
                    stock_codes_full.add(h['code'])

if not stock_codes_full:
    print("⚠️ 没有需要追踪的股票")
    exit(0)

print(f"📋 追踪 {len(stock_codes_full)} 只持仓股: {sorted(stock_codes_full)}")

# ===== 2. F10 API获取十大流通股东 =====
print(f"\n📊 通过F10 API获取十大流通股东(季度报告):")
all_holders = {}
for full_code in sorted(stock_codes_full):
    code = full_code[2:]
    market = full_code[:2].upper()
    print(f"  {full_code} ...", end=' ')
    holders = fetch_f10_holders(code, market)
    if holders:
        all_holders[full_code] = holders
        # 统计
        cats = {}
        for h in holders:
            cat = classify(h['name'], h['type'])
            cats[cat] = cats.get(cat, 0) + 1
        cat_str = ', '.join(f'{k}{v}人' for k, v in sorted(cats.items())[:3])
        print(f"✓ {cat_str}")
    time.sleep(0.3)

# ===== 3. 分类+标记 =====
by_category = {}
all_entries = []
for code, holders in all_holders.items():
    for h in holders:
        cat = classify(h['name'], h['type'])
        direction = change_direction(h.get('change'))
        entry = {
            'stockCode': code,
            'holderName': h['name'],
            'holderType': h['type'],
            'category': cat,
            'rank': h['rank'],
            'holdNum': h['holdNum'],
            'holdRatio': h['holdRatio'],
            'change': h.get('change', 0),
            'direction': direction,
            'endDate': h.get('endDate', ''),
        }
        if cat not in by_category:
            by_category[cat] = []
        by_category[cat].append(entry)
        all_entries.append(entry)

print(f"\n📊 分类统计:")
for cat in ['社保基金','券商自营','国家队','北向资金(陆股通)','养老金','基金','保险','银行/信托','QFII','个人','其他']:
    items = by_category.get(cat, [])
    if items:
        codes = set(i['stockCode'] for i in items)
        print(f"  {cat}: {len(items)}条, {len(codes)}只股票")

# ===== 4. 高亮事件 =====
alerts = []
for e in all_entries:
    if e['direction'] == '增持' and float(e.get('change',0) or 0) > 10000000:
        alerts.append(f"📈 增持: {e['stockCode']} {e['holderName'][:20]}({e['category']}) +{float(e['change'])/10000:.0f}万股")
    elif e['direction'] == '减持' and abs(float(e.get('change',0) or 0)) > 10000000:
        alerts.append(f"📉 减持: {e['stockCode']} {e['holderName'][:20]}({e['category']}) {float(e['change'])/10000:.0f}万股")

if alerts:
    print(f"\n🚨 重要事件 ({len(alerts)}条):")
    for a in alerts[:10]:
        print(f"  {a}")

# ===== 5. 保存历史 =====
history = {}
if os.path.exists(SHAREHOLDER_FILE):
    with open(SHAREHOLDER_FILE) as f:
        prev = json.load(f)
        history = prev.get('history', {})

quarter = today[:7]
if quarter not in history:
    history[quarter] = {}
history[quarter] = {f"{e['stockCode']}_{e['holderName']}": e for e in all_entries}

# 保留最近6个月
quarters = sorted(history.keys(), reverse=True)
if len(quarters) > 6:
    for q in quarters[6:]:
        del history[q]

# ===== 6. 保存 =====
output = {
    'date': today,
    'quarter': quarter,
    'watchlist': watch_codes,
    'stockCodes': list(stock_codes_full),
    'shareholders': by_category,
    'allEntries': all_entries,
    'history': history,
    'alerts': alerts[:30],
    'summary': {k: len(v) for k, v in by_category.items()},
}
with open(SHAREHOLDER_FILE, 'w', encoding='utf-8') as f:
    json.dump(output, f, ensure_ascii=False, indent=2)
print(f"\n✅ 股东数据已保存 ({len(all_entries)}条, {len(by_category)}类)")
