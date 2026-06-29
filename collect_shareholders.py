#!/usr/bin/env python3
"""
十大流通股东追踪脚本
从watchlist持仓股的top holdings中获取十大流通股东数据
分类: 社保/券商自营/基金/保险/QFII/其他
"""
import json, os, datetime, urllib.request, time

OUTPUT_DIR = "/Users/andy/WorkBuddy/2026-06-24-23-34-24/etf_history"
WATCH_FILE = os.path.join(OUTPUT_DIR, "watchlist.json")
HOLDINGS_FILE = os.path.join(OUTPUT_DIR, "holdings.json")
SHAREHOLDER_FILE = os.path.join(OUTPUT_DIR, "shareholders.json")

today = datetime.date.today().strftime("%Y-%m-%d")

def fetch_shareholders(code, market='SH'):
    """从东财API获取十大流通股东"""
    url = f"https://emweb.securities.eastmoney.com/PC_HSF10/ShareholderResearch/PageAjax?code={market}{code}"
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        resp = urllib.request.urlopen(req, timeout=15)
        data = json.loads(resp.read().decode())
        # 十大流通股东
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
                'endDate': g.get('END_DATE', ''),
            })
        return results
    except Exception as e:
        print(f"  ❌ {code}: {str(e)[:60]}")
        return []

def classify_holder(name, type_name):
    """分类股东类型"""
    name = name or ''
    if '全国社会保障基金' in name or '社保基金' in name:
        return '社保基金'
    if '基本养老保险' in name or '养老保险' in name:
        return '养老金'
    if '证券' in name and ('股份' in name or '有限' in name):
        return '券商自营'
    if '证券投资基金' in name or '基金' in name:
        return '基金'
    if '保险' in name:
        return '保险'
    if '香港中央结算' in name:
        return '北向资金(陆股通)'
    if '中央汇金' in name or '中国证金' in name:
        return '国家队'
    if 'QFII' in name.upper() or '合格境外' in name:
        return 'QFII'
    if '银行' in name or '信托' in name:
        return '银行/信托'
    return '其他'

def get_change_direction(change):
    """判断变化方向"""
    if change is None:
        return '未知'
    try:
        c = float(change)
        if c > 0: return '增持'
        elif c < 0: return '减持'
        else: return '持平'
    except:
        return '未知'

# ===== 主流程 =====

# 1. 加载watchlist ETF代码
watch_codes = []
if os.path.exists(WATCH_FILE):
    with open(WATCH_FILE) as f:
        watch_codes = json.load(f)

# 2. 加载holdings，找出每只ETF的前3重仓股
stock_codes = set()
if os.path.exists(HOLDINGS_FILE):
    with open(HOLDINGS_FILE) as f:
        all_holdings = json.load(f)
    # 获取最新日期的holdings
    dates = sorted(all_holdings.keys())
    if dates:
        latest_h = all_holdings[dates[-1]]
        for code in watch_codes:
            if code in latest_h:
                for h in latest_h[code][:3]:
                    stock_codes.add(h['code'])  # 完整代码含sh/sz前缀

if not stock_codes:
    print("⚠️ 没有找到需要追踪的股票（check watchlist和holdings）")
    exit(0)

print(f"📋 追踪 {len(stock_codes)} 只股票: {sorted(stock_codes)}")

# 3. 查询每只股票的十大流通股东
all_shareholders = {}
for full_code in sorted(stock_codes):
    code = full_code[2:]  # 去掉sh/sz
    market = full_code[:2].upper()
    print(f"🔍 查询 {full_code} ...", end=' ')
    holders = fetch_shareholders(code, market)
    if holders:
        all_shareholders[full_code] = holders
        print(f"{len(holders)} 位股东")
    time.sleep(0.5)  # 避免被封

# 4. 分类+标记变化
enriched = {}
for code, holders in all_shareholders.items():
    enriched_list = []
    for h in holders:
        cat = classify_holder(h['name'], h['type'])
        direction = get_change_direction(h.get('change'))
        h['category'] = cat
        h['direction'] = direction
        enriched_list.append(h)
    enriched[code] = enriched_list

# 5. 按股东类型汇总统计
summary = {
    '社保基金': [],
    '券商自营': [],
    '基金': [],
    '保险': [],
    '国家队': [],
    '北向资金(陆股通)': [],
    '养老金': [],
    '其他': [],
}
for code, holders in enriched.items():
    for h in holders:
        cat = h['category']
        if cat not in summary:
            cat = '其他'
        summary[cat].append({
            'stock': code,
            'holder': h['name'],
            'holdNum': h['holdNum'],
            'holdRatio': h['holdRatio'],
            'change': h.get('change', 0),
            'direction': h['direction'],
            'rank': h['rank'],
        })

# 高亮事件: 新进(top5), 大幅增减
alerts = []
for code, holders in enriched.items():
    for h in holders[:5]:  # 只看前5
        try:
            change_val = float(h.get('change', 0)) if h.get('change') else 0
        except:
            change_val = 0
        if h['direction'] == '增持' and abs(change_val) > 10000000:  # 增持超1千万股
            alerts.append({
                'type': '增持',
                'stock': code,
                'holder': h['name'],
                'category': h['category'],
                'change': f"{change_val/10000:.0f}万股",
                'ratio': f"{h.get('holdRatio', 0)}%",
            })
        if '新进' in str(h.get('change', '')):
            alerts.append({
                'type': '新进',
                'stock': code,
                'holder': h['name'],
                'category': h['category'],
                'change': '新进十大流通股东',
                'ratio': f"{h.get('holdRatio', 0)}%",
            })

print(f"\n📊 股东类型分布:")
for cat, items in summary.items():
    if items:
        stocks = set(i['stock'] for i in items)
        print(f"  {cat}: {len(items)}条, 涉及{len(stocks)}只股票")

if alerts:
    print(f"\n🚨 重要事件 {len(alerts)}条:")
    for a in alerts[:10]:
        print(f"  {a['type']}: {a['stock']} {a['holder']}({a['category']}) {a['change']}")

# 6. 保存
output = {
    'date': today,
    'watchlist': watch_codes,
    'stockCodes': list(stock_codes),
    'shareholders': enriched,
    'summary': {k: len(v) for k, v in summary.items() if v},
    'alerts': alerts,
}
with open(SHAREHOLDER_FILE, 'w', encoding='utf-8') as f:
    json.dump(output, f, ensure_ascii=False, indent=2)
print(f"\n✅ 股东数据已保存: {SHAREHOLDER_FILE}")
