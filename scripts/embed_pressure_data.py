#!/usr/bin/env python3
"""将 data/pressure.json 内嵌进 index.html，生成"载入压力测试数据"一键按钮。
幂等：已内嵌时跳过。用法：python3 scripts/embed_pressure_data.py"""
import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
html_p = ROOT / 'index.html'
html = html_p.read_text(encoding='utf-8')

if 'const PRESSURE_DATA =' in html:
    print('压力测试数据已内嵌，跳过')
    raise SystemExit(0)

pdata = (ROOT / 'data' / 'pressure.json').read_text(encoding='utf-8')
json.loads(pdata)  # 校验合法
assert '</script' not in pdata.lower(), 'JSON 中含 script 标签'

anchor = 'function loadSampleData()'
assert anchor in html, '未找到 loadSampleData 锚点'
inject = (
    'const PRESSURE_DATA = ' + pdata + ';\n'
    '    function loadPressureData() {\n'
    '      appData = Object.assign({}, defaultData, JSON.parse(JSON.stringify(PRESSURE_DATA)));\n'
    '      saveToStorage();\n'
    '      updateRatesHeader();\n'
    "      if (typeof renderAll === 'function') renderAll();\n"
    "      showToast('压力测试数据已载入');\n"
    '    }\n'
    '    function loadSampleData()'
)
html = html.replace(anchor, inject, 1)

btn_anchor = '<button class="btn btn-primary" onclick="loadSampleData()">载入示例数据</button>'
assert btn_anchor in html, '未找到示例数据按钮锚点'
html = html.replace(
    btn_anchor,
    btn_anchor + '\n           <button class="btn btn-outline" onclick="loadPressureData()">载入压力测试数据</button>',
    1,
)
html_p.write_text(html, encoding='utf-8')
print('压力测试数据已内嵌进 index.html')
