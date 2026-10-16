#!/usr/bin/env python3
"""生成投资理财顾问应用的压力测试数据（JSON，可直接导入）。
数据逻辑与应用内计算方式保持一致：加权平均成本、买卖数量勾稽。"""
import json, random, math, pathlib
from datetime import date, timedelta

random.seed(20261016)
TODAY = date(2026, 10, 16)
START = date(2024, 10, 16)
DAYS = (TODAY - START).days  # 730

def dstr(d): return d.isoformat()

# ---------- 1. 证券定义：(分类, 名称, 代码, 币种, 现价, 两年前起点价, 年化波动) ----------
SECS = [
    ('a_stock', '贵州茅台', '600519', 'CNY', 1750.0, 1500.0, 0.25),
    ('a_stock', '宁德时代', '300750', 'CNY', 250.0, 180.0, 0.35),
    ('a_stock', '招商银行', '600036', 'CNY', 45.0, 35.0, 0.20),
    ('a_stock', '长江电力', '600900', 'CNY', 30.0, 25.0, 0.15),
    ('a_stock', '万华化学', '600309', 'CNY', 85.0, 95.0, 0.25),
    ('etf_lof', '沪深300ETF', '510300', 'CNY', 3.92, 3.40, 0.18),
    ('etf_lof', '科创50ETF', '588000', 'CNY', 1.10, 0.85, 0.30),
    ('etf_lof', '红利低波ETF', '512890', 'CNY', 1.52, 1.35, 0.15),
    ('mutual_fund', '易方达蓝筹精选', '005827', 'CNY', 2.05, 2.30, 0.20),
    ('mutual_fund', '富国天惠成长', '161005', 'CNY', 1.85, 1.50, 0.22),
    ('hk_us_stock', '腾讯控股', '00700', 'HKD', 385.0, 300.0, 0.30),
    ('hk_us_stock', '阿里巴巴', '09988', 'HKD', 110.0, 85.0, 0.35),
    ('hk_us_stock', '苹果公司', 'AAPL', 'USD', 228.0, 175.0, 0.25),
    ('hk_us_stock', '英伟达', 'NVDA', 'USD', 130.0, 90.0, 0.40),
]

def price_path(start_p, end_p, vol, n):
    """几何随机游走后重缩放，保证终点=现价"""
    rets = [random.gauss(0.0004, vol / math.sqrt(252)) for _ in range(n)]
    p = [start_p]
    for r in rets:
        p.append(p[-1] * math.exp(r))
    k = end_p / p[-1]
    return [x * k for x in p]

paths = {s[1]: price_path(s[5], s[4], s[6], DAYS) for s in SECS}
def price_at(name, d):
    idx = min(max((d - START).days, 0), DAYS)
    return paths[name][idx]

# ---------- 2. 生成交易流水 ----------
txns = []
tid = 0
def add_txn(d, hid, tname, typ, shares, price, fee, ccy):
    global tid
    tid += 1
    txns.append({'id': f'tx{tid:04d}', 'date': dstr(d), 'holdingId': hid,
                 'targetName': tname, 'type': typ, 'shares': shares,
                 'price': round(price, 4), 'fee': round(fee, 2), 'currency': ccy})

holdings_meta = []
for hi, (cat, name, code, ccy, cur, st, vol) in enumerate(SECS, 1):
    hid = f'h{hi:03d}'
    tname = f'{name} ({code})'
    lot = 100 if cat == 'a_stock' else (10 if ccy != 'CNY' and cat == 'hk_us_stock' else 100)
    n_buy = random.randint(5, 9)
    # 买入日期：分散在两年内，越近越密一点
    bdays = sorted(random.randint(0, DAYS - 5) for _ in range(n_buy))
    held = 0
    for bd in bdays:
        d = START + timedelta(days=bd)
        sh = lot * random.randint(1, 6)
        px = price_at(name, d) * random.uniform(0.995, 1.005)
        fee = max(5.0, sh * px * 0.0003) if cat == 'a_stock' else 0.0
        add_txn(d, hid, tname, 'buy', sh, px, fee, ccy)
        held += sh
    # 1~2 笔卖出（部分仓位）
    for _ in range(random.randint(0, 2)):
        if held <= lot: break
        sd = START + timedelta(days=random.randint(int(DAYS * 0.5), DAYS - 2))
        sh = min(held - lot, lot * random.randint(1, 3))
        px = price_at(name, sd) * random.uniform(0.995, 1.005)
        fee = max(5.0, sh * px * 0.0003) if cat == 'a_stock' else 0.0
        add_txn(sd, hid, tname, 'sell', sh, px, fee, ccy)
        held -= sh
    holdings_meta.append((hid, cat, name, code, ccy, cur))

txns.sort(key=lambda t: t['date'])

# ---------- 3. 按应用逻辑轧出持仓（加权平均成本） ----------
pos = {}  # hid -> [shares, totalCost]
for t in txns:
    hid = t['holdingId']
    s, c = pos.get(hid, [0, 0.0])
    if t['type'] == 'buy':
        s += t['shares']; c += t['shares'] * t['price'] + t['fee']
    else:
        avg = c / s if s else 0
        s -= t['shares']; c -= t['shares'] * avg
    pos[hid] = [s, c]

holdings = []
for hid, cat, name, code, ccy, cur in holdings_meta:
    s, c = pos[hid]
    if s <= 0: continue
    holdings.append({'id': hid, 'category': cat, 'name': name, 'code': code,
                     'currency': ccy, 'shares': s,
                     'costPrice': round(c / s, 4), 'currentPrice': cur})

# ---------- 4. 银行理财 / 存款 / 现金 ----------
FIXED = [
    ('bank_wealth', '招行季季开1号', 'CNY', 150000, 3.10, date(2026, 6, 1), date(2026, 11, 5)),   # 20天到期
    ('bank_wealth', '工行添利宝', 'CNY', 80000, 2.80, date(2026, 8, 15), date(2027, 2, 15)),
    ('bank_wealth', '建行龙宝季季盈', 'CNY', 200000, 3.40, date(2025, 10, 16), date(2026, 10, 30)), # 14天到期
    ('deposit', '工行三年期大额存单', 'CNY', 300000, 3.00, date(2024, 11, 1), date(2027, 11, 1)),
    ('deposit', '招行一年期定存', 'CNY', 100000, 1.90, date(2026, 3, 1), date(2027, 3, 1)),
]
for i, (cat, name, ccy, principal, rate, sd, ed) in enumerate(FIXED, 1):
    holdings.append({'id': f'hf{i:02d}', 'category': cat, 'name': name, 'currency': ccy,
                     'principal': principal, 'annualRate': rate,
                     'startDate': dstr(sd), 'endDate': dstr(ed)})
holdings.append({'id': 'hc01', 'category': 'cash', 'name': '活期存款与货币基金',
                 'currency': 'CNY', 'amount': 60000})

# ---------- 5. 月度快照（用交易+价格路径精确轧差） ----------
# 重放交易得到每个快照日的持仓与成本
by_date = sorted(txns, key=lambda t: t['date'])
snapshots = []
cur = TODAY.replace(day=1)
first = (START.replace(day=1))
d = first
while d <= cur:
    # 月末
    nxt = (d.replace(day=28) + timedelta(days=4)).replace(day=1)
    m_end = min(nxt - timedelta(days=1), TODAY)
    p2 = {}
    for t in by_date:
        if t['date'] > dstr(m_end): break
        hid = t['holdingId']
        s, c = p2.get(hid, [0, 0.0])
        if t['type'] == 'buy':
            s += t['shares']; c += t['shares'] * t['price'] + t['fee']
        else:
            avg = c / s if s else 0
            s -= t['shares']; c -= t['shares'] * avg
        p2[hid] = [s, c]
    meta = {h[0]: h for h in holdings_meta}
    tot_asset = 0.0; tot_cost = 0.0
    for hid, (s, c) in p2.items():
        if s <= 0: continue
        _, cat, name, code, ccy, curp = meta[hid]
        tot_asset += s * price_at(name, m_end)
        tot_cost += c
    for (cat, name, ccy, principal, rate, sd, ed) in FIXED:
        if sd <= m_end:
            days = (min(m_end, ed) - sd).days if m_end < ed else (ed - sd).days
            tot_asset += principal * (1 + rate / 100 * days / 365)
            tot_cost += principal
    tot_asset += 60000; tot_cost += 60000
    snapshots.append({'date': dstr(m_end), 'totalAsset': round(tot_asset, 2),
                      'totalCost': round(tot_cost, 2)})
    d = nxt

# ---------- 6. 定投 / 目标 / 风险 ----------
aipPlans = [
    {'id': 'aip1', 'name': '沪深300ETF 周定投', 'holdingId': 'h006',
     'targetName': '沪深300ETF (510300)', 'cycle': 'weekly', 'deductDay': 1,
     'amount': 1000, 'lastDeductDate': dstr(TODAY - timedelta(days=4)), 'totalInvested': 52000},
    {'id': 'aip2', 'name': '易方达蓝筹精选 月定投', 'holdingId': 'h009',
     'targetName': '易方达蓝筹精选 (005827)', 'cycle': 'monthly', 'deductDay': 10,
     'amount': 2000, 'lastDeductDate': dstr(TODAY - timedelta(days=42)), 'totalInvested': 48000},
]
goals = [
    {'id': 'g1', 'name': '三年后换车首付', 'targetAmount': 300000,
     'targetDate': dstr(TODAY + timedelta(days=1095)), 'notes': '增程 SUV 首付预算'},
    {'id': 'g2', 'name': '十年养老储备', 'targetAmount': 2000000,
     'targetDate': dstr(TODAY + timedelta(days=3650)), 'notes': '长期复利目标'},
]

data = {
    'settings': {'usdRate': 7.20, 'hkdRate': 0.92},
    'holdings': holdings,
    'transactions': txns,
    'snapshots': snapshots,
    'aipPlans': aipPlans,
    'riskProfile': {'score': 22, 'type': '积极型', 'targetEquity': 60,
                    'targetFixed': 40, 'answers': [4, 4, 4, 4, 3, 3]},
    'goals': goals,
}
out = pathlib.Path(__file__).resolve().parent.parent / 'data' / 'pressure.json'
json.dump(data, open(out, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
print('持仓:', len(holdings), '| 流水:', len(txns), '| 快照:', len(snapshots))
print('写出:', out)
