#!/usr/bin/env python3
"""由 index.html 生成演示版 index-demo.html。
演示版将 localStorage 调用封装为 safeStorage（不可用时降级为内存），
适合静态托管发布；数据仅本次打开有效。用法：python3 scripts/make_demo.py"""
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
html = (ROOT / 'index.html').read_text(encoding='utf-8')

m2s = html.find('<script>', 1000)
m2e = html.find('</script>', m2s)
head, block, tail = html[:m2s], html[m2s:m2e], html[m2e:]
assert block.startswith('<script>'), '应用脚本块定位失败'
inner = block[len('<script>'):]

shim = """/* 演示版安全存储：localStorage 不可用时降级为内存（数据仅本次打开有效） */
var __memStore = {};
var safeStorage = {
  getItem: function(k) { try { return localStorage.getItem(k); } catch (e) { return (__memStore[k] !== undefined ? __memStore[k] : null); } },
  setItem: function(k, v) { try { localStorage.setItem(k, v); } catch (e) { __memStore[k] = String(v); } },
  removeItem: function(k) { try { localStorage.removeItem(k); } catch (e) { delete __memStore[k]; } }
};
"""
inner = inner.replace('localStorage.', 'safeStorage.')
new_block = '<script>' + shim + inner
(ROOT / 'index-demo.html').write_text(head + new_block + tail, encoding='utf-8')
print('已生成 index-demo.html')
