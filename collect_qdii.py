#!/usr/bin/env python3
"""
QDII投资额度采集脚本
从国家外汇管理局官网下载PDF并提取数据
"""
import json, os, re, subprocess, urllib.request, datetime

OUTPUT_DIR = "/Users/andy/WorkBuddy/2026-06-24-23-34-24/etf_history"
QDII_FILE = os.path.join(OUTPUT_DIR, "qdii.json")

def fetch_qdii():
    """下载并解析QDII额度PDF"""
    # SAFE的QDII页面
    page_url = "https://www.safe.gov.cn/safe/2018/0425/16849.html"
    req = urllib.request.Request(page_url, headers={'User-Agent': 'Mozilla/5.0'})
    resp = urllib.request.urlopen(req, timeout=15)
    html = resp.read().decode('utf-8', errors='replace')
    
    # 提取PDF链接
    pdf_match = re.search(r'href="([^"]*\.pdf)"', html)
    if not pdf_match:
        print("❌ 未找到PDF链接")
        return None
    
    pdf_path = pdf_match.group(1)
    if pdf_path.startswith('/'):
        pdf_url = "https://www.safe.gov.cn" + pdf_path
    else:
        pdf_url = pdf_path
    
    print(f"📄 下载PDF: {pdf_url}")
    pdf_file = "/tmp/qdii_latest.pdf"
    urllib.request.urlretrieve(pdf_url, pdf_file)
    
    # 用pdftotext提取文本
    txt_file = "/tmp/qdii_latest.txt"
    result = subprocess.run(["pdftotext", "-layout", pdf_file, txt_file],
                           capture_output=True, text=True, timeout=30)
    if result.returncode != 0:
        print(f"❌ pdftotext失败: {result.stderr[:100]}")
        return None
    
    with open(txt_file, 'r') as f:
        text = f.read()
    
    # 解析表格
    lines = text.strip().split('\n')
    records = []
    for line in lines:
        m = re.match(r'^\s*(\d+)\s+(.+?)\s+(\d{4}\.\d{2}\.\d{2})\s+([\d.]+)', line)
        if m:
            records.append({
                'rank': int(m.group(1)),
                'name': m.group(2).strip(),
                'approveDate': m.group(3),
                'quota': float(m.group(4)),
            })
    
    # 提取截至日期
    date_match = re.search(r'截至日期：(\S+)', text)
    report_date = date_match.group(1) if date_match else 'unknown'
    
    # 提取合计
    total_match = re.search(r'总\s*计\s+([\d.]+)', text)
    total = float(total_match.group(1)) if total_match else 0
    
    # 分类统计
    categories = {'银行类': 0, '证券基金类': 0, '保险类': 0, '信托类': 0}
    for cat_name in categories:
        cat_match = re.search(rf'{cat_name}合计\s+([\d.]+)', text)
        if cat_match:
            categories[cat_name] = float(cat_match.group(1))
    
    # 最新批准
    latest_date = max(r['approveDate'] for r in records) if records else ''
    latest_approved = [r for r in records if r['approveDate'] == latest_date]
    
    result_data = {
        'reportDate': report_date,
        'totalQuota': total,
        'categories': categories,
        'totalOrgs': len(records),
        'latestApproveDate': latest_date,
        'latestApproved': latest_approved,
        'allRecords': records,  # 全量记录用于下次对比
    }
    
    print(f"📊 QDII数据: {report_date}")
    print(f"   总计: {total}亿美元, {len(records)}家机构")
    print(f"   最新批准日期: {latest_date}")
    print(f"   本轮新获额度: {len(latest_approved)}家")
    
    return result_data

# === 主流程 ===
current = fetch_qdii()
if current:
    # 读取历史数据
    last_data = {}
    if os.path.exists(QDII_FILE):
        with open(QDII_FILE, 'r') as f:
            last_data = json.load(f)
    
    # 对比变化: 比较机构名单和额度变动
    if last_data and 'allRecords' in last_data:
        old_records = {r['name']: r for r in last_data['allRecords']}
        new_records = {r['name']: r for r in records}
        
        new_orgs = []  # 新出现的机构
        quota_up = []  # 额度增加的机构
        for name, nr in new_records.items():
            if name not in old_records:
                new_orgs.append(nr)
            else:
                old_q = old_records[name].get('quota', 0)
                if nr['quota'] > old_q:
                    quota_up.append({'name': name, 'oldQuota': old_q, 'newQuota': nr['quota'], 'increase': nr['quota'] - old_q})
        
        current['newOrgs'] = new_orgs
        current['quotaIncrease'] = quota_up
        current['newSinceLastCheck'] = len(new_orgs) > 0 or len(quota_up) > 0
        
        if current['newSinceLastCheck']:
            print(f"🚀 有变化! 新机构{len(new_orgs)}家, 额度提升{len(quota_up)}家")
            if new_orgs:
                for o in new_orgs[:5]:
                    print(f"  ✨ {o['name']} 额度{o['quota']}亿美元")
            if quota_up:
                for q in quota_up[:5]:
                    print(f"  📈 {q['name']}: {q['oldQuota']}→{q['newQuota']}亿 (+{q['increase']}亿)")
        else:
            print(f"⏸️ 无变化, 机构名单和额度与上次相同")
    else:
        current['newOrgs'] = []
        current['quotaIncrease'] = []
        current['newSinceLastCheck'] = False
        print("📋 首次采集, 跳过对比")
    
    current['fetchedAt'] = datetime.date.today().strftime("%Y-%m-%d")
    
    with open(QDII_FILE, 'w', encoding='utf-8') as f:
        json.dump(current, f, ensure_ascii=False, indent=2)
    print(f"✅ QDII数据已保存: {QDII_FILE}")
else:
    print("❌ 获取QDII数据失败")
