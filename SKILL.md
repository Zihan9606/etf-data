---
name: etf-share-flow-analysis
description: >
  全市场ETF份额申购流入分析。当用户需要查询指数ETF申购流入排行、
  份额变化数据、资金净流入分析时使用此技能。支持宽基/行业/主题/
  跨境/债券全类ETF分析, 查询当日份额、份额变化、资金流、K线走势等。
  还支持自选ETF监控、十大流通股东追踪(社保/券商/QFII)、QDII额度查询、
  成交活跃TOP3重仓股展示、ETF联接基金持有份额占比、热点板块速览报告。
  全自动数据采集(SH 15:05定时+打开页面时自动检查)+首页模块入口架构。
agent_created: true
---

# ETF份额申购流入分析技能

## 使用场景

- "指数申购流入排行" / "ETF份额变化排名"
- "宽基ETF份额数据" / "行业ETF资金流入"
- "哪些指数ETF在净申购" / "哪些ETF份额在增长"
- "全市场ETF申购流入分析"
- "查询ETF价格走势" / "获取ETF K线数据"
- "自选标的监控" / "添加自选ETF跟踪"
- "十大流通股东追踪" / "跟随社保券商投资"
- "QDII额度查询" / "最新QDII获批提醒"

## 全量130指数ETF索引

> ⚠️ **数据口径说明**: 每个指数只追踪**份额最大的1只ETF** (而非累加同指数多只ETF)，因ETF标的可能不全，取最大者最公平。**

所有代码可合并查询: `westock-data-clawhub etf <逗号拼接所有代码>`

### 一、宽基指数（20个指数, 20只ETF）

沪深300: sh510300
上证50: sh510050 | 中证500: sh510500 | 中证1000: sh512100
上证180: sh510180 | 上证380: sh530380
深证100: sz159901 | 深证50: sz159150
中证A500: sz159338
上证指数: sh510760 | 中证A50: sz159591
国证2000: sz159628 | 创业板指: sz159915
创业板50: sz159949 | 科创50: sh588000
科创100: sh588220 | 中证800: sh515800
MSCI中国A股: sh515770 | 沪深300价值: sz159510
沪深300成长: sz159656

### 二、策略指数（2个指数, 2只ETF）

中证红利: sh515180 | 红利低波: sh563020

### 三、行业/主题指数（85个指数, 85只ETF）

半导体: sh512480 | 芯片: sz159995 | 半导体设备: sz159558
人工智能: sz159819 | 新能源: sh516270 | 新能源车: sh515700
新能源电池: sz159071 | 锂电池: sz159840 | 电池: sz159175
医药: sh512010 | 医疗: sh512170 | 医疗器械: sz159883
创新药: sh516080 | 生物医药: sz159859 | 疫苗: sh562860 | 中药: sz159647
军工: sh512660 | 国防: sh512670 | 航空航天: sz159227
机器人: sh562500 | 工业母机: sz159667 | 高端装备: sh516320
工业互联: sz159013 | 证券: sh512880 | 证券保险: sh512070
银行: sh512800 | 金融科技: sz159299 | 消费: sz159928
消费50: sh515650 | 消费电子: sz159732 | 食品: sz159151
食品饮料: sh516900 | 酒: sh512690 | 家电: sz159996
旅游: sz159766 | 游戏: sz159869 | 影视: sh516620
传媒: sh512980 | 教育: sh513360 | 通信: sh515880
5G: sz159811 | 物联网: sz159895 | 大数据: sh515400
云计算: sh516510 | 软件: sh515230 | 计算机: sz159586
数字经济: sh560800 | 信创: sz159538 | 光伏: sh515790
绿色电力: sh562960 | 碳中和: sz159641 | 电力: sz159146
煤炭: sh515220 | 石油: sz159181 | 有色: sh560470
稀有金属: sh561050 | 黄金: sz159934 | 稀土: sh516150
钢铁: sh515210 | 化工: sh516020 | 建材: sz159745
新材料: sh516710 | 豆粕: sz159985 | 房地产: sh512200
基建: sh516970 | 一带一路: sh515110 | 交通运输: sz159666
航空: sz159392 | 物流: sh516910 | 农业: sz159825
养殖: sz159023 | 央企: sh510060 | 央企创新: sh515900
央企科技: sh560170 | 央企结构调整: sh512960 | 央企能源: sh562850
上海国企: sh510810 | 大湾区: sh512970 | 长三角: sh512650
科创芯片: sh589130 | 集成电路: sz159546 | 电子: sh515260
智能汽车: sh515250 | 环保: sh512580 | 养老: sh516560
中概互联网: sh513050 | 可转债: sh511380

### 四、债券指数（5个指数, 5只ETF）

短融: sh511360 | 十年国债: sh511260 | 国债ETF: sh511100
30年国债: sh511090 | 信用债: sh511200

### 五、跨境指数（18个指数, 18只ETF）

恒生科技: hk03033 | 恒生指数: sh513600 | 恒生国企: sh510900
恒生互联网: sh513330 | 恒生医疗: sh513060 | 港股科技: sh513020
中概互联: sz159605 | 中概互联网: sh513050 | 标普生物科技: sz159502
标普油气: sh513350 | 纳斯达克100: sh513300 | 标普500: sh513500
日经225: sh513520 | 德国DAX: sz159561 | 法国CAC40: sh513080
东南亚科技: sh513730 | 沙特: sh520830 | 政金债: sh511580

---

## westockdata 数据字段说明

### etf命令 — ETF当前快照 (共64个字段, CSV采用39列)

命令: `westock-data-clawhub etf <代码>`

#### A类字段: CSV已收录(westock有数据) — 39列

| 字段名 | 中文释义 | 单位 | 说明 |
|--------|---------|------|------|
| shares | 总份额 | 份 | 基金当前总份额 |
| sharesChg | 份额变化 | 份 | 当日份额增减量 |
| sharesChgRatio | 变化率 | % | 当日份额增减百分比 |
| nav | 净值 | 元 | 每份基金净值 |
| closePrice | 收盘价 | 元 | 当日交易所收盘价 |
| changePct | 涨跌幅 | % | 当日价格涨跌百分比 |
| turnoverRate | 换手率 | % | 当日换手率 |
| turnoverValue | 成交额 | 元 | 当日交易金额 |
| turnoverVolume | 成交量 | 手 | 当日交易量(1手=100份) |
| disc | 折溢价率 | % | 正=溢价,负=折价 |
| discountRatioCurve | 折溢价走势 | % | 盘中折溢价率走势数据 |
| avgDiscountRatioCurve | 平均折溢价 | % | 日内平均折溢价率 |
| size | 基金规模 | 元 | 基金资产净值总额 |
| totalMV | 总市值 | 元 | 交易所总市值 |
| totalAssets | 总资产 | 元 | 基金总资产 |
| stockRatio | 股票仓位 | % | 股票占基金资产比 |
| bondRatio | 债券仓位 | % | 债券占基金资产比 |
| ytdReturn | 年至今收益 | % | YTD收益率 |
| ytdMaxDrawdown | 年内最大回撤 | % | YTD最大回撤幅度 |
| return1M/3M/6M/1Y/3Y | 阶段收益 | % | 各阶段收益率 |
| maxDrawdown1M/3M/6M/1Y/3Y | 最大回撤 | % | 各阶段最大回撤 |
| indexDailyChange | 指数日涨跌 | % | 跟踪指数当日涨跌幅 |
| index1YReturn | 指数年收益 | % | 跟踪指数近1年收益率 |
| isTPlus0 | T+0标记 | - | ✓=支持T+0, ✗=否 |
| prlistTop20Ratio | 前20重仓% | % | ETF前20大重仓股占比 |

#### B类字段: CSV已收录但westock返0(需其他数据源补充)

| 字段名 | 中文释义 | 单位 | westock状态 | 替代数据源 |
|--------|---------|------|------------|-----------|
| holderAccount | 持有人户数 | 户 | 全返0 | 基金半年报/年报(fundf10页面) |
| individualHolderRatio | 个人持有比例 | % | 全返0 | ✅ 天天基金pingzhongdata JS |
| institutionHolderRatio | 机构持有比例 | % | 全返0 | ✅ 天天基金pingzhongdata JS |

#### C类字段: westock有返回值但CSV未收录(暂未采用)

| 字段名 | 含义 | 单位 | 说明 |
|--------|------|------|------|
| etfType | ETF类别 | - | 规模/主题/跨境/债券/商品等 |
| establishDate | 成立日期 | - | 基金成立时间 |
| manageInstitution | 管理人 | - | 基金管理公司 |
| trusteeInstitution | 托管人 | - | 基金托管银行 |
| trackIndexCode/Name | 跟踪指数 | - | 标的指数代码和名称 |
| purchaseStatus | 申购状态 | - | 可申购/不可申购 |
| redemptionStatus | 赎回状态 | - | 可赎回/不可赎回 |
| managementFee | 管理费率 | %/年 | westock返0,从fundf10 jbgk页面获取 |
| custodyFee | 托管费率 | %/年 | westock返0,从fundf10 jbgk页面获取 |
| subscriptionFee | 申购费率 | % | westock返0 |
| serviceFee | 销售服务费率 | %/年 | westock返0 |
| indexDailyChange | 指数日涨跌 | % | ✅ CSV已收 |
| index1YReturn | 指数年收益 | % | ✅ CSV已收 |
| holderAccount | 持有人户数 | 户 | westock返0,需其他数据源 |
| individualHolderRatio | 个人持有比例 | % | westock返0,可从pingzhongdata获取 ✅ |
| institutionHolderRatio | 机构持有比例 | % | westock返0,可从pingzhongdata获取 ✅ |
| top10Share | 前10大持有人份额 | 份 | westock返0 |
| top10Ratio | 前10大持有人占比 | % | westock返0 |

### kline命令 — 历史K线

命令: `westock-data-clawhub kline <代码> --period day --limit <N>`

支持周期: day(日), week(周), month(月), season(季), year(年)
支持复权: qfq(前复权), hfq(后复权), bfq(不复权,默认)
最大返回: 2000条

| 字段 | 含义 | 单位 |
|------|------|------|
| date | 日期 | YYYY-MM-DD |
| open | 开盘价 | 元 |
| last | 收盘价 | 元 |
| high | 最高价 | 元 |
| low | 最低价 | 元 |
| volume | 成交量 | 手 |
| amount | 成交额 | 元 |
| exchange | 换手率 | % |

### minute命令 — 分时数据

命令: `westock-data-clawhub minute <代码> --days <N>`

### etf-nav命令 — 历史净值

命令: `westock-data-clawhub etf-nav <代码> --start YYYY-MM-DD --end YYYY-MM-DD`

返回字段: date(日期), nav(净值), navChange(净值变动), navChangePct(净值变动%), accNav(累计净值)

### asfund命令 — A股资金流向

命令: `westock-data-clawhub asfund <代码>`

字段: MainNetFlow(主力净流入), JumboNetFlow(超大单净流入), BlockNetFlow(大单净流入), MidNetFlow(中单净流入), SmallNetFlow(小单净流入)

### 其他命令

- `search <keyword>`: 搜索股票/ETF代码
- `hot stock/board/etf`: 热搜数据
- `technical <code> --group macd,rsi`: 技术指标
- `dividend <code>`: 分红数据
- `profile <code>`: 公司简况
- `board`: 热门板块行情

---

## 数据获取方式汇总

### 1. 当前份额/资金流（etf命令）
```bash
westock-data-clawhub etf <代码1>,<代码2>,...
```
解析shares(份额), sharesChg(日变化), nav(净值), 计算资金流=sharesChg×nav

### 2. 历史K线/价格走势（kline命令）
```bash
westock-data-clawhub kline <代码> --period day --limit 60
```

### 3. 历史净值走势（etf-nav命令）
```bash
westock-data-clawhub etf-nav <代码> --start 2026-01-01 --end 2026-06-24
```

### 4. 资金流向（asfund命令）
```bash
westock-data-clawhub asfund <代码>
```

### 5. 季度份额历史 + 机构/个人持有比例（天天基金JS）
```python
import requests, json, re
text = requests.get(f"https://fund.eastmoney.com/pingzhongdata/{fundCode}.js").text
# 搜索"总份额"取data数组, 配合"categories"日期数组
# 也支持: Data_holderStructure 获取机构/个人/内部持有比例
# 提取示例:
match = re.search(r'var Data_holderStructure\s*=\s*({.*?});', text, re.DOTALL)
if match:
    holder_data = json.loads(match.group(1))
    # holder_data['series'][0]['name']='机构持有比例'
    # holder_data['series'][1]['name']='个人持有比例'
    # holder_data['categories']=['2024-06-30','2024-12-31','2025-06-30','2025-12-31']
```

### 6. 日频份额数据（妙想API）
```bash
MX_APIKEY=$MX_APIKEY python3 /Users/andy/.workbuddy/skills/mx-data/mx_data.py "查询语句"
# 限10次/天, code=113表示用尽
```

### 7. B类字段补充数据源

westock-data的以下字段全返0，需通过其他数据源补充：

#### 7.1 个人持有比例 / 机构持有比例 — 天天基金pingzhongdata JS ✅ 已验证

```python
import requests, json, re
text = requests.get(f"https://fund.eastmoney.com/pingzhongdata/{fundCode}.js").text
match = re.search(r'var Data_holderStructure\s*=\s*({.*?});', text, re.DOTALL)
if match:
    holder_data = json.loads(match.group(1))
    # series[0] = 机构持有比例, series[1] = 个人持有比例, categories = 日期
```

返回格式示例（沪深300ETF）:
```json
{"series":[
  {"name":"机构持有比例","data":[79.4,83.06,87.1,90.27]},
  {"name":"个人持有比例","data":[19.54,16.32,12.2,8.98]}
],"categories":["2024-06-30","2024-12-31","2025-06-30","2025-12-31"]}
```

#### 7.2 管理费率/托管费率 — 天天基金基金概况页面 ✅ 已验证

```python
requests.get(f"https://fundf10.eastmoney.com/jbgk_{fundCode}.html")
# HTML中搜索"管理费率"和"托管费率", 提取相邻数值
```

#### 7.3 持有人户数 — 待研究

暂未发现稳定的不开屏API。可能的路径:
- 基金半年报/年报PDF
- datacenter API（需找到正确的reportName）
- 天天基金 cyrjg 页面（需JS渲染，可用playwright）

---

## 核心分析流程

### Step 1: 获取数据
从全量索引中取出要查的ETF代码, 批量查询

### Step 2: 解析字段
从Markdown表格解析shares/sharesChg/nav/closePrice等

### Step 3: 计算指标
资金流(亿元) = sharesChg × nav / 1e8

### Step 4: 分组汇总 (单ETF最大法)
按指数名称分组, 每个指数只保留**份额最大的那只ETF**（不累加）。
原因: ETF覆盖面可能不全, 取最大者最公平, 且同指数多只ETF走势高度相关。

### Step 5: 补充走势
用kline获取价格走势, etf-nav获取净值走势

### Step 6: 输出排行
按资金流排序, 分为净申购/持平/净赎回三类

### Step 7: 生成HTML可视化页面（数据驱动+动态日期切换）
直接用脚本一键生成:
```bash
/Users/andy/.workbuddy/binaries/python/envs/default/bin/python \
  /Users/andy/.workbuddy/skills/etf-share-flow-analysis/scripts/gen_analysis_html.py
```
该脚本自动完成:
1. **前置自动采集**: 自动调 `collect_shareholders.py` + `collect_qdii.py` 更新股东和QDII数据
2. 读取CSV全量历史数据 + 每日采集(westock)获取今日最新
3. 按指数分组, 每指数只取份额最大的那只ETF
4. 计算资金流和四象限/量化/重叠推荐分析
5. 导出 `etf_history/etf_data.json` (数据文件)
6. 生成轻量HTML框架, 不含硬编码数据
7. HTML通过 `fetch('etf_data.json')` 动态加载, 支持**6个Tab**:
   - 📊 **全量排行** (39列字段 + 成交活跃TOP3, ETF代码显示, 搜索/排序)
   - 🔍 **定性分析** (四象限矩阵, 含成交活跃TOP3列)
   - 📈 **量化分析** (回测统计+市场基准统计Top3/中位数/均值+stock_flow2因子框架)
   - 🎯 **最终结论** (QDII额度监控面板 + 卖点预警+重叠推荐)
   - ⭐ **自选监控** (自定义ETF代码列表, 独立量化和定性分析)
   - 📋 **股东追踪** (十大流通股东分类展示, 社保/券商/国家队高亮)
8. 日期切换: 下拉选择任意交易日, 自动加载对应数据
9. 启动HTTP服务: `python3 server.py` → 浏览器访问 localhost:8080

---

## 量化+定性双重分析（核心流程）

获取ETF数据后, 执行以下分析:

### 1. 定性分析 — 四象限矩阵

基于"份额变化(%) × 价格涨跌(%)"二维矩阵判断主力意图:

| 象限 | 份额 | 价格 | 信号含义 | 建议 |
|:---:|:----:|:----:|:---------|:----|
| 🔥强力吸筹 | ↑>1% | ↓<-0.5% | 机构越跌越买 | 关注 |
| 📥压价建仓 | ↑>1% | →(-0.5%~0.5%) | 压制价格买入 | 关注 |
| 📈温和上涨 | ↑>0 | ↑>0 | 量价配合健康 | 关注 |
| ⚠️量价齐升 | ↑>0.5% | ↑↑>2% | 警惕过热 | 甄别 |
| 🚨出货嫌疑 | ↓<-0.5% | ↑>0.5% | 拉高出货 | 回避 |
| 💀恐慌出逃 | ↓<-0.5% | ↓<-0.5% | 资金撤离 | 回避 |

### 2. 量化分析 — 基于373个历史样本

份额变化区间 → 后续20日价格的实证表现:

| 份额变化 | 后续20日均值 | 胜率 | 评级 |
|:--------:|:-----------:|:----:|:----:|
| ↑1%~3% | +12.92% | 75% | ⭐⭐⭐ 最强 |
| ↑0%~1% | +0.87% | 100% | ⭐⭐ |
| ↑>5% | -1.09% | 39.5% | ⚠️ 不稳 |
| ↓-3%~-5% | -1.92% | 0% | ⚠️ 看空 |
| ↓0%~-1% | -0.79% | 0% | ⚠️ 看空 |

**关键发现:** 份额↑1%~3%+价格↑的组合是历史回测中回报最好的信号

### 3. 重叠推荐机制

```
定性看好的ETF  ∩  量化看好的ETF  =  ⭐⭐⭐ 推荐购买
```

- 定性看好: 四象限在🔍/📥/📈象限的ETF
- 量化看好: 份额↑0.5%~3% + 价格↑ + 资金流入正的ETF
- 重叠越多, 置信度越高

### 4. 一键综合分析脚本（推荐用这个）

```bash
cd /Users/andy/.workbuddy/skills/etf-share-flow-analysis
/Users/andy/.workbuddy/binaries/python/envs/default/bin/python scripts/gen_analysis_html.py
```
该脚本自动完成所有分析并生成:
1. `etf_history/etf_data.json` — 全量交易日数据 (供HTML动态加载)
2. `全量指数申购流入排行.html` — 轻量HTML框架 (无硬编码数据)
3. 启动HTTP服务后浏览器访问, 支持4个Tab和日期切换

#### HTML页面包含:
- 📊 **全量排行**: 39列字段 + 成交活跃TOP3, ETF代码显示, 搜索/排序/方向筛选
- 🔍 **定性分析**: 四象限矩阵, 分7组显示, 每组含成交活跃TOP3列
- 📈 **量化分析**: 
  - 历史回测统计 (373样本)
  - 市场基准统计 (Top3/中位数/均值, 看你推荐标的是否相对强势)
  - 📐 stock_flow2因子框架 (采集满5天后自动计算)
- 🎯 **最终结论**:
  - 📊 QDII投资额度概况面板（新获批额度🚀红色提醒）
  - 🔴 卖点预警 (当日出现出货/恐慌/大额流出的品种)
  - 🎯 重叠推荐 (定量+定性双重确认)
  - 📊 仅量化推荐 / 🔍 仅定性推荐
- ⭐ **自选监控**: 用户自定义ETF代码列表, 独立量化和定性分析, 综合建议卡片
- 📋 **股东追踪**: 十大流通股东, 按社保/券商/国家队分类, 增持/新进事件高亮
- 📅 日期切换: 下拉选择任意交易日

#### 使用方式:
```bash
cd /Users/andy/WorkBuddy/2026-06-24-23-34-24
python3 server.py
# 浏览器打开 http://localhost:8080/全量指数申购流入排行.html
```

> **每次修改代码或数据后, 必须:**
> 1. 运行 `gen_analysis_html.py` 重新生成HTML和数据
> 2. 重启 `server.py` （`kill $(lsof -ti:8080) && python3 server.py`）
> 3. 用 `preview_url` 工具打开页面让用户查看变化

数据更新后刷新浏览器即可, 无需重启服务器（如果server.py没停）。

### 8. 持仓解析 + 成交活跃TOP3

`daily_collect.py` 采集时自动解析每只ETF的持仓列表:
- 在westock etf输出中定位 `**基金经理**` 行之后的持仓表格
- 提取前20大重仓股: code, name, weight
- 对每只持仓股票, 用 marketplace 前缀(6xxxxx→sh, 其他→sz)补全
- **批量查询**所有持仓股票的当日行情(成交额、涨跌幅)
- 按成交金额降序排列, 取**交易额TOP3** → `holdings.json`
- HTML的**所有Tab**均展示"成交活跃TOP3"列: 股票名(成交额亿) +/-涨跌幅%

### 9. 自选监控

支持用户输入任意ETF代码进行跟踪:
- 输入框支持**纯6位数字** (自动补全 sh/sz 前缀: 5开头→sh, 其他→sz)
- 数据保存在 `etf_history/watchlist.json` (服务端文件)
- 通过 `server.py` 的 `GET/POST /api/watchlist` API 读写
- `daily_collect.py` 采集时自动读取watchlist, 追加到查询列表
- 新加入代码下次定时采集后自动补全数据
- HTML的**⭐自选监控Tab**展示: 监控表 + 综合建议卡片

### 10. 十大流通股东追踪

跟踪自选ETF重仓股的股东变化:
- 数据源: 东财F10 API `https://emweb.securities.eastmoney.com/PC_HSF10/ShareholderResearch/PageAjax`
- 脚本: `collect_shareholders.py`
- 读取 `holdings.json` 获取自选ETF的前3重仓股代码
- 查询每只股票的 `sdltgd` (十大流通股东)
- 分类: 社保基金 / 券商自营 / 基金 / 保险 / 国家队 / 北向资金 / 养老金
- 检测: 新进 / 增持 / 减持
- HTML的**📋股东追踪Tab**展示:
  - 🚨 重要事件提醒 (新进/大幅增持)
  - 按股东类型分组表格

### 11. QDII额度监控

跟踪国家外汇管理局每月发布的QDII投资额度:
- 数据源: SAFE官网PDF `https://www.safe.gov.cn/safe/2018/0425/16849.html`
- 脚本: `collect_qdii.py`
- 下载最新PDF → pdftotext提取 → 解析193家机构+额度
- 对比上次数据, 标记是否有新批准
- HTML的**🎯最终结论Tab顶部**展示:
  - 📊 QDII投资额度概况面板
  - 如1个月内有新批准: 🚀 红色提醒 + 新机构详情
  - 如无: 统计面板 + 上次更新日期

### 12. 自动更新机制

`gen_analysis_html.py` 启动时自动执行:
```
gen_analysis_html.py
  ├── 📋 自动采集股东数据 (collect_shareholders.py)
  │   → 18+只持仓股 × 十大流通股东
  ├── 📄 自动检查QDII额度 (collect_qdii.py)
  │   → 下载SAFE最新PDF
  ├── 📊 读取ETF数据 + 分析
  └── ✅ 生成HTML + etf_data.json
```
定时任务(交易日15:05) → daily_collect.py → gen_analysis_html.py → 全数据更新

**数据时效检查机制:**
- `server.py` 启动时自动检查 `etf_data.json` 中是否有今日数据, 无则调用 `gen_analysis_html.py`
- `gen_analysis_html.py` 启动时先检查CSV今日数据是否存在, 无则先调 `daily_collect.py`
- `gen_analysis_html.py` 自动前置采集股东(`collect_shareholders.py`)+QDII(`collect_qdii.py`)+联接基金(`collect_link_ratio.py`)
- 每次修改代码后, 必须: 重新生成 → 重启server → preview_url打开页面

### 13. 首页 + 模块入口架构 (index.html)

生成脚本: `gen_index.py`
- 基于westock-data的`board`命令实时数据生成热点板块速览报告
- 支持模块入口: ETF模块 + 个股模块(预留)
- 首页主要展示:
  - 🔥 热点板块TOP5表格(涨停数/最高连板/主力资金流)
  - 📌 龙虎榜&资金风向专栏(机构买卖/游资/北向资金)
- `server.py` 增加了 `/etf` 路径指向ETF分析页, `/` 指向 `index.html`

### 14. ETF联接基金持有份额占比

数据源: 天天基金网(东方财富)基金详情页
```python
# 从基金详情页提取总资产
url = f'https://fund.eastmoney.com/{fund_code}.html'
# 搜索 "规模</a>：X.XX亿元" 提取基金总资产
```

公式: `P_link = A_link × 0.92 / A_etf`
- A_link: 联接基金总资产(从天天基金详情页提取)
- A_etf: ETF总资产(shares×nav)
- 0.92: 联接基金持有目标ETF的典型比例(实际90-95%)

脚本: `collect_link_ratio.py`
- ETF → 联接基金代码硬编码映射
- 支持A/C类份额合并计算
- 输出: `etf_history/link_ratio.json`

已覆盖19只ETF(含红利、宽基、行业、跨境等), 后续可持续补充映射。

### 15. 数据源汇总

| 数据 | 数据源 | 获取方式 | 脚本 |
|:----|:------|:--------|:----|
| ETF份额/资金流 | westock-data-clawhub (腾讯自选股数据) | `etf` 命令批量查询(139只ETF) | daily_collect.py |
| ETF持仓(前20重仓) | westock-data-clawhub | etf命令输出尾部"基金经理"之后的持仓表 | daily_collect.py |
| 持仓股票行情/成交额 | westock-data-clawhub | `etf` 命令查询个股(带sh/sz前缀) | daily_collect.py |
| 板块行情+资金流 | westock-data-clawhub | `board` 命令 | gen_index.py |
| 龙虎榜/热点 | westock-data-clawhub | `hot stock/board` 命令 | (预留) |
| 十大流通股东(季度) | 东方财富F10 API | `PC_HSF10/ShareholderResearch/PageAjax` | collect_shareholders.py |
| 联接基金总资产 | 天天基金网(东方财富) | 基金详情页HTML解析 | collect_link_ratio.py |
| QDII投资额度 | 国家外汇管理局(SAFE) | 官网PDF下载+pdftotext | collect_qdii.py |
| 基金历史规模 | 天天基金pingzhongdata JS | `Data_grandTotal` 变量 | (备用方案) |

### 6. 结果呈现

- 在回复中明确输出"定性结论"和"量化结论"两个章节, 分别独立呈现
- 如果有重叠ETF, 用 **🎯 强烈推荐: ETF名称** 高亮
- 如果没有重叠, 分别给出两种逻辑的推荐并说明差异
- 最后生成/更新 `全量指数申购流入排行.html` 用于可视化查看

### 7. 每日数据采集 + GitHub结构化存储 + HTML自动生成

已设每日定时任务 `ETF每日数据采集`，在**每个交易日 15:05** 自动运行（市场15:00收盘，收盘后立刻采集）：
- 调用 `scripts/daily_collect.py` 采集全量139只ETF快照
- 保存到 `etf_history/` 目录，**三种格式同时存储**：

```
etf_history/
├── etf_daily.csv        # 结构化CSV(推荐用于分析/迁移)
├── history.jsonl        # JSONL每行一条记录
├── 2026-06-25.json      # 每日原始快照
└── ...
```

CSV字段(39列): date, idx, code, shares, sharesChg, sharesChgRatio, nav, closePrice, changePct, turnoverRate, turnoverValue, turnoverVolume, disc, discountRatioCurve, avgDiscountRatioCurve, size, totalMV, totalAssets, stockRatio, bondRatio, ytdReturn, ytdMaxDrawdown, return1M, return3M, return6M, return1Y, return3Y, maxDrawdown1M, maxDrawdown3M, maxDrawdown6M, maxDrawdown1Y, maxDrawdown3Y, indexDailyChange, index1YReturn, holderAccount, institutionHolderRatio, individualHolderRatio, prlistTop20Ratio, isTPlus0

脚本采集完成后自动 git commit + push 数据文件到GitHub。

### GitHub数据仓库配置

| 项目 | 值 |
|:----|:----|
| 远程仓库 | `git@github.com:Zihan9606/etf-data.git` |
| SSH密钥 | `~/.ssh/id_rsa` (公钥已添加到GitHub) |
| 本地路径 | `/Users/andy/WorkBuddy/2026-06-24-23-34-24/` |
| 首次推送 | 已完成(2026-06-25) |

如需在其他机器上拉取数据:
```bash
git clone git@github.com:Zihan9606/etf-data.git
```

### 数据文件说明

| 文件 | 格式 | 说明 | 推荐用途 |
|:----|:----|:-----|:---------|
| `etf_daily.csv` | CSV(39列) | 全量结构化数据,每天追加 | **数据分析/迁移推荐** |
| `history.jsonl` | JSONL | 每行一条完整JSON记录 | 程序化处理 |
| `YYYY-MM-DD.json` | JSON数组 | 每日原始快照 | 逐日回溯 |

### 自动化推送机制

`daily_collect.py` 每次采集完成后自动执行:
1. 追加数据到CSV和JSONL
2. `git add` 数据文件
3. `git commit -m "ETF数据更新 YYYY-MM-DD"`
4. `git push origin main`
5. **自动调用 gen_analysis_html.py** → 生成 `etf_data.json`
6. 用户刷新浏览器即看到最新分析结果

> ⚠️ 自动化任务已更新。路径必须使用 managed venv，不要用 homebrew 路径。
> 自动化配置位于 ~/.workbuddy/workbuddy.db 中, 可用 `automation_update` 工具查看和修改。

| 自动化任务 | 参数 |
|:----------|:-----|
| 名称 | ETF每日数据采集 |
| 计划 | 交易日 15:05 (RRULE: FREQ=DAILY;BYDAY=MO,TU,WE,TH,FR;BYHOUR=15;BYMINUTE=05) |
| CWD | /Users/andy/WorkBuddy/2026-06-24-23-34-24 |

SSH主机密钥已在 `~/.ssh/known_hosts` 中保存, 推送无需手动确认。

如果遇到SSH连接问题:
```bash
GIT_SSH_COMMAND="ssh -o StrictHostKeyChecking=accept-new" git push origin main
```

手动运行:
```bash
/Users/andy/.workbuddy/binaries/python/envs/default/bin/python \
  /Users/andy/.workbuddy/skills/etf-share-flow-analysis/scripts/daily_collect.py
```

---

## 环境配置（新机器部署清单）

换电脑后，按以下步骤完整部署：

### 必须做的

```bash
# 1. 克隆数据仓库（含历史数据）
git clone git@github.com:Zihan9606/etf-data.git
cd etf-data

# 2. 安装核心工具
npm install -g westock-data-clawhub   # ETF数据查询

# 3. 安装Python依赖
python3 -m venv venv
source venv/bin/activate
pip install pandas requests playwright
playwright install chromium

# 4. 配置SSH密钥（推送数据到GitHub用）
# 方案A: 从旧机器复制 ~/.ssh/id_rsa 和 ~/.ssh/id_rsa.pub
# 方案B: 新生成密钥: ssh-keygen -t rsa -b 4096
#        然后加到GitHub: https://github.com/settings/keys
#        公钥内容: cat ~/.ssh/id_rsa.pub

# 5. 首次Push时接受主机指纹
GIT_SSH_COMMAND="ssh -o StrictHostKeyChecking=accept-new" git push origin main
```

### 可选的

```bash
# 妙想API（用于日频份额数据, 限10次/天）
export MX_APIKEY="你的API密钥"
```

### 环境清单

| 组件 | 安装方式 | 说明 |
|:----|:---------|:-----|
| `westock-data-clawhub` | `npm install -g westock-data-clawhub` | ETF/个股行情查询 |
| Python 3.13+ | 系统自带或brew安装 | 脚本运行环境 |
| pandas, requests, playwright | `pip install` | 数据处理+浏览器自动化 |
| Git | 系统自带 | 数据版本管理 |
| SSH密钥 | 复制或生成后加GitHub | GitHub推送认证 |
| MX_APIKEY | 环境变量(可选) | 妙想API配额(日常采集不需要) |

### 数据流向

```
westockdata API ──→ daily_collect.py ──→ CSV/JSONL ──→ git commit ──→ GitHub
     ↑                  ↑                      ↑
  无需认证        需要Python+Node           需要SSH密钥
```
