#!/usr/bin/env python3
"""
每日ETF数据采集脚本 — 收盘后运行
功能: 采集全量130ETF快照数据, 追加到历史记录文件
积累5日后可计算 stock_flow2amt_ma5 因子
"""
import subprocess, json, os, datetime
from collections import defaultdict

OUTPUT_DIR = "/Users/andy/WorkBuddy/2026-06-24-23-34-24/etf_history"
os.makedirs(OUTPUT_DIR, exist_ok=True)

today = datetime.date.today().strftime("%Y-%m-%d")

# === 周末检查: 非交易日跳过 ===
weekday = datetime.date.today().weekday()  # 0=周一, 6=周日
if weekday >= 5:
    print(f"⏭️ 今天({today})是周末, 非交易日, 跳过采集")
    exit(0)

# === 读取自选监控列表, 追加到采集 ===
WATCH_FILE = os.path.join(OUTPUT_DIR, "watchlist.json")

# 全量130指数ETF代码
ALL_CODES = [
    ("沪深300","sh510300"),("沪深300","sh510310"),("沪深300","sh510330"),("沪深300","sz159919"),
    ("上证50","sh510050"),("中证500","sh510500"),("中证1000","sh512100"),
    ("上证180","sh510180"),("上证380","sh530380"),("深证100","sz159901"),("深证50","sz159150"),
    ("中证A500","sz159338"),("中证A500","sz159339"),("中证A500","sz159353"),
    ("上证指数","sh510760"),("中证A50","sz159591"),("国证2000","sz159628"),
    ("创业板指","sz159915"),("创业板50","sz159949"),("科创50","sh588000"),("科创50","sh588080"),
    ("科创100","sh588220"),("中证800","sh515800"),("MSCI中国A股","sh515770"),
    ("沪深300价值","sz159510"),("沪深300成长","sz159656"),
    ("中证红利","sh515180"),("中证红利","sh515080"),("红利低波","sh563020"),
    ("半导体","sh512480"),("半导体设备","sz159558"),("芯片","sz159995"),
    ("人工智能","sz159819"),("新能源","sh516270"),("新能源车","sh515700"),
    ("新能源电池","sz159071"),("锂电池","sz159840"),("电池","sz159175"),
    ("医药","sh512010"),("医疗","sh512170"),("医疗器械","sz159883"),
    ("创新药","sh516080"),("生物医药","sz159859"),("疫苗","sh562860"),("中药","sz159647"),
    ("军工","sh512660"),("国防","sh512670"),("航空航天","sz159227"),
    ("机器人","sh562500"),("工业母机","sz159667"),("高端装备","sh516320"),("工业互联","sz159013"),
    ("证券","sh512880"),("证券保险","sh512070"),("银行","sh512800"),("金融科技","sz159299"),
    ("消费","sz159928"),("消费50","sh515650"),("消费电子","sz159732"),
    ("食品","sz159151"),("食品饮料","sh516900"),("酒","sh512690"),
    ("家电","sz159996"),("旅游","sz159766"),("游戏","sz159869"),
    ("影视","sh516620"),("传媒","sh512980"),("教育","sh513360"),
    ("通信","sh515880"),("5G","sz159811"),("物联网","sz159895"),
    ("大数据","sh515400"),("云计算","sh516510"),("软件","sh515230"),
    ("计算机","sz159586"),("数字经济","sh560800"),("信创","sz159538"),
    ("光伏","sh515790"),("绿色电力","sh562960"),("碳中和","sz159641"),("电力","sz159146"),
    ("煤炭","sh515220"),("石油","sz159181"),("有色","sh560470"),("稀有金属","sh561050"),
    ("黄金","sz159934"),("稀土","sh516150"),("钢铁","sh515210"),("化工","sh516020"),
    ("建材","sz159745"),("新材料","sh516710"),("豆粕","sz159985"),
    ("房地产","sh512200"),("基建","sh516970"),("一带一路","sh515110"),
    ("交通运输","sz159666"),("航空","sz159392"),("物流","sh516910"),
    ("农业","sz159825"),("养殖","sz159023"),("央企","sh510060"),
    ("央企创新","sh515900"),("央企科技","sh560170"),("央企结构调整","sh512960"),("央企能源","sh562850"),
    ("上海国企","sh510810"),("大湾区","sh512970"),("长三角","sh512650"),
    ("科创芯片","sh589130"),("集成电路","sz159546"),("电子","sh515260"),
    ("智能汽车","sh515250"),("环保","sh512580"),("养老","sh516560"),
    ("中概互联网","sh513050"),("可转债","sh511380"),
    ("短融","sh511360"),("十年国债","sh511260"),("国债ETF","sh511100"),
    ("30年国债","sh511090"),("信用债","sh511200"),
    ("恒生科技","hk03033"),("恒生指数","sh513600"),("恒生国企","sh510900"),
    ("恒生互联网","sh513330"),("恒生医疗","sh513060"),("港股科技","sh513020"),
    ("中概互联","sz159605"),("标普生物科技","sz159502"),("标普油气","sh513350"),
    ("纳斯达克100","sh513300"),("标普500","sh513500"),("日经225","sh513520"),
    ("德国DAX","sz159561"),("法国CAC40","sh513080"),("东南亚科技","sh513730"),
    ("沙特","sh520830"),    ("政金债","sh511580"),
]

# === 追加自选标的到采集列表 ===
try:
    if os.path.exists(WATCH_FILE):
        with open(WATCH_FILE, 'r') as f:
            watch_codes = json.load(f)
        existing = set(c for _, c in ALL_CODES)
        for code in watch_codes:
            if code not in existing:
                ALL_CODES.append(("自选-"+code, code))
                existing.add(code)
        if watch_codes:
            print(f"📋 自选标的: 追加 {len(watch_codes)} 个代码 {watch_codes}")
except Exception as e:
    print(f"⚠️ 读取watchlist.json失败: {e}")

codes_str = ",".join([e[1] for e in ALL_CODES])
result = subprocess.run(
    ["/Users/andy/.workbuddy/binaries/node/versions/22.22.2/bin/westock-data-clawhub","etf",codes_str],
    capture_output=True, text=True, timeout=60
)

lines = result.stdout.strip().split('\n')
header_cols = []
for l in lines:
    if l.startswith('| code |'):
        header_cols = [c.strip() for c in l.split('|')]
        break
h2i = {h: i for i, h in enumerate(header_cols)}

records = []
for idx_name, code in ALL_CODES:
    for line in lines:
        if line.startswith('| '+code[:2]) and ('| '+code+' |') in line:
            cols = [c.strip() for c in line.split('|')]
            try:
                record = {'date': today, 'idx': idx_name, 'code': code}
                for field in ['shares','sharesChg','sharesChgRatio','nav','closePrice','changePct',
                              'turnoverRate','turnoverValue','turnoverVolume','disc','discountRatioCurve',
                              'avgDiscountRatioCurve','size','totalMV','totalAssets',
                              'stockRatio','bondRatio','ytdReturn','ytdMaxDrawdown',
                              'return1M','return3M','return6M','return1Y','return3Y',
                              'maxDrawdown1M','maxDrawdown3M','maxDrawdown6M','maxDrawdown1Y','maxDrawdown3Y',
                              'indexDailyChange','index1YReturn','holderAccount','institutionHolderRatio',
                              'individualHolderRatio','prlistTop20Ratio','isTPlus0']:
                    idx = h2i.get(field)
                    if idx is not None and idx < len(cols):
                        record[field] = cols[idx]
                records.append(record)
            except:
                pass
            break

# === 解析持仓数据 ===
# 从etf输出的每个section中提取"基金经理"之后的持仓表
sections = result.stdout.strip().split('#### ')[1:]
holdings_by_code = {}  # code -> [{code, name, weight}]
for sec in sections:
    sec_code = sec.split()[0] if sec.split() else ''
    if sec_code not in [e[1] for e in ALL_CODES]:
        continue
    sec_lines = sec.split('\n')
    in_holdings = False
    for i, l in enumerate(sec_lines):
        if l.strip() == '**基金经理**':
            in_holdings = True
            continue
        if in_holdings:
            parts = [p.strip() for p in l.split('|')]
            if len(parts) >= 4 and parts[1] and parts[2]:
                try:
                    w = float(parts[3].replace('%',''))
                    if sec_code not in holdings_by_code:
                        holdings_by_code[sec_code] = []
                    if len(holdings_by_code[sec_code]) < 3:
                        holdings_by_code[sec_code].append({
                            'code': parts[1],
                            'name': parts[2],
                            'weight': w
                        })
                except:
                    pass

# 收集所有持仓股票代码(去重), 批量查询涨跌
all_stock_codes = set()
for code, holdings in holdings_by_code.items():
    for h in holdings:
        prefix = 'sh' if h['code'].startswith(('6','68')) else 'sz'
        all_stock_codes.add(prefix + h['code'])

stock_chg = {}  # 完整code -> {changePct, closePrice}
if all_stock_codes:
    codes_str2 = ",".join(sorted(all_stock_codes))
    print(f"📊 持仓股票: {len(all_stock_codes)}只, 已批量查询涨跌")
    result2 = subprocess.run(
        ["/Users/andy/.workbuddy/binaries/node/versions/22.22.2/bin/westock-data-clawhub","etf",codes_str2],
        capture_output=True, text=True, timeout=60
    )
    for line in result2.stdout.split('\n'):
        if not line.startswith('| '):
            continue
        parts = [p.strip() for p in line.split('|')]
        if len(parts) >= 16:
            sc = parts[1]  # 完整代码(含前缀)
            try:
                stock_chg[sc] = {
                    'changePct': parts[15].replace('%',''),
                    'closePrice': parts[14],
                    'name': parts[2],
                }
            except:
                pass

# 组装最终holdings数据(含涨跌)
final_holdings = {}
for code, holdings in holdings_by_code.items():
    enriched = []
    for h in holdings:
        prefix = 'sh' if h['code'].startswith(('6','68')) else 'sz'
        full_code = prefix + h['code']
        chg_info = stock_chg.get(full_code, {})
        enriched.append({
            'code': full_code,
            'name': h['name'],
            'weight': h['weight'],
            'chgPct': chg_info.get('changePct', 'N/A'),
            'closePrice': chg_info.get('closePrice', 'N/A'),
        })
    final_holdings[code] = enriched
    if enriched:
        top3 = ', '.join([f"{h['name']}({h['weight']}%)" for h in enriched])
        print(f"  {code}: {top3}")

# 保存holdings.json (按日期归档)
holdings_file = os.path.join(OUTPUT_DIR, "holdings.json")
if os.path.exists(holdings_file):
    with open(holdings_file, 'r') as f:
        all_holdings = json.load(f)
else:
    all_holdings = {}
all_holdings[today] = final_holdings
with open(holdings_file, 'w', encoding='utf-8') as f:
    json.dump(all_holdings, f, ensure_ascii=False, indent=2)
print(f"📋 持仓数据已保存: {len(final_holdings)}只ETF × 前3重仓")

# 保存今日数据
today_file = os.path.join(OUTPUT_DIR, f"{today}.json")
with open(today_file, 'w', encoding='utf-8') as f:
    json.dump(records, f, ensure_ascii=False, indent=2)

print(f"✅ {today}: 采集 {len(records)} 条ETF记录 → {today_file}")

# 追加到全量历史文件
history_file = os.path.join(OUTPUT_DIR, "history.jsonl")
with open(history_file, 'a', encoding='utf-8') as f:
    for r in records:
        f.write(json.dumps(r, ensure_ascii=False) + '\n')

# 统计已有多少天的数据
dates = set()
if os.path.exists(history_file):
    with open(history_file, 'r', encoding='utf-8') as f:
        for line in f:
            try:
                d = json.loads(line).get('date')
                if d: dates.add(d)
            except:
                pass

print(f"📊 累计采集 {len(dates)} 天数据 ({sorted(dates)})")
if len(dates) >= 5:
    print(f"🎯 数据充足! 可以计算 stock_flow2amt_ma5 因子!")
else:
    print(f"⏳ 还需 {5-len(dates)} 天数据才能计算 5日均值因子")
    print(f"   当前交易日: {today}")

# === 新增: 导出CSV方便分析 ===
csv_file = os.path.join(OUTPUT_DIR, "etf_daily.csv")
import csv
CSV_FIELDS = ['date','idx','code','shares','sharesChg','sharesChgRatio','nav','closePrice',
              'changePct','turnoverRate','turnoverValue','turnoverVolume','disc','discountRatioCurve',
              'avgDiscountRatioCurve','size','totalMV','totalAssets','stockRatio','bondRatio',
              'ytdReturn','ytdMaxDrawdown','return1M','return3M','return6M','return1Y','return3Y',
              'maxDrawdown1M','maxDrawdown3M','maxDrawdown6M','maxDrawdown1Y','maxDrawdown3Y',
              'indexDailyChange','index1YReturn','holderAccount','institutionHolderRatio',
              'individualHolderRatio','prlistTop20Ratio','isTPlus0']
file_exists = os.path.exists(csv_file)
with open(csv_file, 'a', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    if not file_exists:
        writer.writerow(CSV_FIELDS)
    for r in records:
        writer.writerow([r.get(f, '') for f in CSV_FIELDS])

# === 新增: 推送到GitHub ===
try:
    import subprocess as sp
    result = sp.run(
        ['git', '-C', '/Users/andy/WorkBuddy/2026-06-24-23-34-24',
         'add', '-f', 'etf_history/etf_daily.csv', 'etf_history/history.jsonl', today_file],
        capture_output=True, text=True, timeout=10)
    result2 = sp.run(
        ['git', '-C', '/Users/andy/WorkBuddy/2026-06-24-23-34-24',
         'commit', '-m', f'ETF数据更新 {today}'],
        capture_output=True, text=True, timeout=10)
    env = {'GIT_SSH_COMMAND': 'ssh -o StrictHostKeyChecking=accept-new'}
    result3 = sp.run(
        ['git', '-C', '/Users/andy/WorkBuddy/2026-06-24-23-34-24',
         'push', 'origin', 'main'],
        capture_output=True, text=True, timeout=30, env={**__import__('os').environ, **env})
    if result3.returncode == 0:
        print(f"✅ 已推送到 GitHub: Zihan9606/etf-data")
    else:
        print(f"ℹ️ GitHub推送信息: {result3.stdout.strip()[-100:] if result3.stdout else ''}")
except Exception as e:
    print(f"ℹ️ GitHub推送: {str(e)[:80]}")

# === 最后: 重新生成 etf_data.json 供HTML动态加载 ===
try:
    collect_dir = os.path.dirname(os.path.abspath(__file__))
    gen_script = os.path.join(collect_dir, "gen_analysis_html.py")
    if os.path.exists(gen_script):
        result = subprocess.run(
            ["/Users/andy/.workbuddy/binaries/python/envs/default/bin/python", gen_script],
            capture_output=True, text=True, timeout=120)
        if result.returncode == 0:
            print(f"✅ etf_data.json 已同步刷新")
        else:
            print(f"ℹ️ gen_analysis_html 输出: {result.stdout.strip()[-100:]}")
except Exception as e:
    print(f"ℹ️ 跳过JSON刷新: {str(e)[:80]}")
