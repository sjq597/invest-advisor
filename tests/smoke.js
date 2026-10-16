/**
 * 冒烟测试（CI 入口）：语法检查 + jsdom 真实渲染
 * 用法：npm install jsdom && node tests/smoke.js
 * 退出码 0 = 通过，非 0 = 失败
 */
const fs = require('fs');
const path = require('path');
const vm = require('vm');

const ROOT = path.join(__dirname, '..');
const HTML = path.join(ROOT, 'index.html');
const html = fs.readFileSync(HTML, 'utf-8');

let failed = false;
const ok = (c, msg) => {
  console.log((c ? 'PASS' : 'FAIL') + ': ' + msg);
  if (!c) failed = true;
};

// ---------- 1. 内联 JS 语法检查 ----------
const blocks = [...html.matchAll(/<script(?![^>]*\bsrc=)[^>]*>([\s\S]*?)<\/script>/g)];
ok(blocks.length > 0, `找到 ${blocks.length} 个内联 script 块`);
blocks.forEach((m, i) => {
  try {
    new vm.Script(m[1], { filename: `inline-${i}.js` });
    ok(true, `script 块 #${i} 语法通过`);
  } catch (e) {
    ok(false, `script 块 #${i} 语法错误: ${e.message.split('\n')[0]}`);
  }
});

// ---------- 2. jsdom 真实渲染 ----------
const { JSDOM, VirtualConsole } = require('jsdom');
const jsErrors = [];
const vc = new VirtualConsole();
vc.on('jsdomError', (e) => {
  const msg = String((e.detail && e.detail.message) || e.message || '');
  // canvas/dpr/scrollTo 为 jsdom 环境限制，非应用 bug
  if (!/scrollTo|canvas|getContext|dpr|clearRect|not implemented/i.test(msg)) {
    jsErrors.push(msg.slice(0, 200));
  }
});

const dom = new JSDOM(html, {
  url: 'http://localhost/',
  runScripts: 'dangerously',
  pretendToBeVisual: true,
  virtualConsole: vc,
  // 模拟 iOS 应用内浏览器吞掉系统弹窗
  beforeParse(w) { w.confirm = () => false; },
});

setTimeout(() => {
  try {
    const { document } = dom.window;

    // 底部 5 Tab 可切换
    const tabs = [...document.querySelectorAll('nav button')];
    ok(tabs.length === 5, `底部 Tab 数量为 5（实际 ${tabs.length}）`);
    tabs.forEach((b) => b.click());

    // 更多菜单可弹出
    const moreTab = tabs.find((b) => /更多/.test(b.textContent));
    moreTab && moreTab.click();
    ok(/定投|资产配置|财务目标/.test(document.body.textContent), '“更多”菜单内容可达');

    // 示例数据
    const sampleBtn = [...document.querySelectorAll('button')]
      .find((b) => /载入示例数据/.test(b.textContent));
    ok(!!sampleBtn, '存在“载入示例数据”按钮');
    sampleBtn && sampleBtn.click();

    setTimeout(() => {
      const t1 = document.body.textContent;
      ok(t1.includes('贵州茅台'), '示例数据渲染（贵州茅台）');

      // 压力数据：confirm 被吞时也必须能载入
      const pBtn = [...document.querySelectorAll('button')]
        .find((b) => /载入压力测试数据/.test(b.textContent));
      ok(!!pBtn, '存在“载入压力测试数据”按钮');
      pBtn && pBtn.click();

      setTimeout(() => {
        const t2 = document.body.textContent;
        ok(t2.includes('英伟达'), '压力数据渲染（英伟达）');
        ok(t2.includes('到期'), '理财到期预警渲染');
        ok(jsErrors.length === 0, `无真实 JS 错误（${jsErrors.length}）`);
        jsErrors.slice(0, 5).forEach((e) => console.error('JS-ERR:', e));
        console.log(failed ? 'SMOKE FAILED' : 'SMOKE OK');
        process.exit(failed ? 1 : 0);
      }, 1500);
    }, 1500);
  } catch (e) {
    console.error('FAIL: 测试异常', e.message);
    process.exit(1);
  }
}, 2000);
