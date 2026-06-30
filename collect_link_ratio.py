#!/usr/bin/env python3
"""
ETF联接基金持有份额占比计算
从东财pingzhongdata获取联接基金总资产，计算占比
公式: P_link = A_link * 0.92 / A_etf
"""
import json, os, datetime, urllib.request, re, time

OUTPUT_DIR = "/Users/andy/WorkBuddy/2026-06-24-23-34-24/etf_history"
LINK_FILE = os.path.join(OUTPUT_DIR, "link_ratio.json")
DATA_FILE = os.path.join(OUTPUT_DIR, "etf_data.json")

# ===== ETF → 联接基金代码映射 =====
# key: ETF代码(sz/shiso格式), value: [联接A代码, 联接C代码, ...]
ETF_LINK_MAP = {
    # === 宽基 ===
    'sh510300': ['000051', '006131'],  # 华泰柏瑞沪深300ETF联接A/C
    'sh510050': ['110003', '110019'],  # 易方达上证50ETF联接A(易方达上证50增强A)
    'sh510500': ['160119', '160120'],  # 南方中证500ETF联接LOF
    'sh512100': ['006430', '006431'],  # 凯石中证1000(注意验证)
    'sz159338': ['022455', '022456'],  # 中证A500ETF联接
    'sz159915': ['110026', '110027'],  # 易方达创业板ETF联接A/C
    'sz159949': ['003766', '003767'],  # 广发创业板50ETF联接A/C
    'sh588000': ['011613', '011614'],  # 华夏科创板50ETF联接A/C
    
    # === 行业/主题 ===
    'sh512480': ['007301', '007302'],  # 国联安中证半导体ETF联接A/C
    'sz159995': ['008887', '008888'],  # 华夏芯片ETF联接A/C
    'sz159819': ['009239', '009240'],  # 华夏人工智能ETF联接A/C
    'sh516270': ['013572', '013573'],  # 嘉实新能源ETF联接A/C
    'sh512660': ['005603', '005604'],  # 华宝军工ETF联接A/C
    'sh512880': ['012716', '012717'],  # 华宝证券ETF联接A/C
    'sh512800': ['008298', '008299'],  # 华宝银行ETF联接A/C
    'sz159928': ['000248', '000249'],  # 汇添富消费ETF联接A/C
    'sh512690': ['009329', '009330'],  # 鹏华中证酒ETF联接A/C
    'sh512690': ['009329', '009330'],  # 鹏华中证酒ETF联接A/C
    
    # === 跨境 ===
    'sh513050': ['006327', '006328'],  # 易方达中概互联ETF联接A/C
    'sh513330': ['006329', '006330'],  # 华夏恒生互联网ETF联接A/C
    'sh513300': ['006479', '006480'],  # 广发纳斯达克100ETF联接A/C
    'sh513500': ['050025', '050025'],  # 博时标普500ETF联接A

    # === 自选 ===
    'sz159992': ['012767', '012768'],  # 中药ETF联接
    'sh512880': ['012716', '012717'],  # 证券ETF联接
    'sz159307': [],  # 无联接基金
    'sh515450': [],  # 无联接基金
    'sh515080': [],  # 无联接基金
}

def fetch_link_fund_asset(fund_code):
    """获取联接基金总资产(亿元)"""
    try:
        url = f'https://fund.eastmoney.com/pingzhongdata/{fund_code}.js'
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        resp = urllib.request.urlopen(req, timeout=10)
        text = resp.read().decode('utf-8')
        
        # Data_grandTotal: [{name:'基金名', data:[[ts, 规模(亿元)],...]}, ...]
        match = re.search(r'Data_grandTotal\s*=\s*(\[.*?\]);', text, re.DOTALL)
        if not match:
            return None
        
        data = json.loads(match.group(1))
        if not data or not isinstance(data, list) or len(data) < 3:
            return None
        
        # 找到本基金的真实规模数据
        fund_entry = None
        for entry in data:
            name = entry.get('name', '')
            if not name or name in ('同类平均', '沪深300', '中证500', '中证800', '业绩基准'):
                continue
            if entry.get('data') and len(entry['data']) > 0:
                latest = entry['data'][-1]
                val = latest[1]
                if val > 0:
                    fund_entry = entry
                    break
        
        if not fund_entry or not fund_entry.get('data'):
            return None
        
        latest = fund_entry['data'][-1]
        scale_yi = latest[1]
        if scale_yi <= 0:
            return None
        return scale_yi * 1e8
    except Exception as e:
        return None

def get_all_etf_data():
    """从etf_data.json获取所有ETF的totalAssets"""
    if not os.path.exists(DATA_FILE):
        return {}
    with open(DATA_FILE, 'r') as f:
        data = json.load(f)
    
    etf_assets = {}
    for date_key, date_data in data.get('dates', {}).items():
        for entry in date_data.get('data', []):
            code = entry.get('mainCode', '')
            name = entry.get('name', '')
            # shares=总份额(亿份), nav=单位净值(元)
            shares = float(entry.get('shares', 0)) if entry.get('shares') else 0
            nav = float(entry.get('nav', 0)) if entry.get('nav') else 0
            total_assets = shares * nav * 1e8  # 元
            if code and code not in etf_assets:
                etf_assets[code] = {
                    'name': name,
                    'totalAssets': total_assets,
                    'shares': shares,
                    'nav': nav,
                    'date': date_key,
                }
    return etf_assets

print("📊 计算ETF联接基金持有份额占比")
print(f"   公式: P_link = A_link × 0.92 / A_etf")

# 获取ETF数据
etf_data = get_all_etf_data()
print(f"   读取 {len(etf_data)} 只ETF数据")

# 计算每只ETF的联接基金占比
results = {}
for etf_code, link_codes in ETF_LINK_MAP.items():
    if not link_codes:
        continue
    if etf_code not in etf_data:
        print(f"  ❌ {etf_code}: 未找到ETF数据")
        continue
    
    etf_assets_total = etf_data[etf_code].get('totalAssets', 0)
    etf_name = etf_data[etf_code].get('name', '')
    
    if not etf_assets_total:
        print(f"  ❌ {etf_code}: 总资产为0")
        continue
    
    total_link_assets = 0
    for lc in link_codes:
        assets = fetch_link_fund_asset(lc)
        if assets:
            total_link_assets += assets
            print(f"  📥 {etf_code} {etf_name}: 联接{lc} 资产{assets/1e8:.1f}亿")
        time.sleep(0.5)
    
    if total_link_assets > 0:
        # 联接基金通常持有92%在目标ETF
        assumed_ratio = 0.92
        link_hold_ratio = total_link_assets * assumed_ratio / etf_assets_total * 100
        results[etf_code] = {
            'etfName': etf_name,
            'etfTotalAssets': etf_assets_total,
            'totalLinkAssets': total_link_assets,
            'linkFunds': link_codes,
            'linkHoldRatio': round(link_hold_ratio, 2),
            'assumedRatio': assumed_ratio,
        }
        print(f"  ✅ {etf_code} {etf_name}: 联接{link_hold_ratio:.2f}%")
    else:
        print(f"  ⚠️ {etf_code}: 未获取到联接基金数据")

# 保存
output = {
    'date': datetime.date.today().strftime("%Y-%m-%d"),
    'count': len(results),
    'data': results,
}
with open(LINK_FILE, 'w', encoding='utf-8') as f:
    json.dump(output, f, ensure_ascii=False, indent=2)
print(f"\n✅ 联接基金占比数据已保存 ({len(results)}只ETF)")
