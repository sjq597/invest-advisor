# 个人投资理财顾问

单文件、离线可用的个人投资组合管理应用。覆盖 A股、场内基金、场外基金、银行理财、港美股、存款六类资产，含 7 个模块：资产总览、持仓管理、交易流水、收益分析、定投计划、资产配置建议、财务目标。

- **在线体验**：打 tag 自动发布的 GitHub Pages 链接（见右侧 Releases）
- **本地使用**：下载 `index.html`，浏览器直接打开即可，零依赖、数据只存本地浏览器

## 仓库结构

```
├── index.html              # 应用本体（唯一的发布物）
├── echarts.min.js          # ECharts 源码（构建时内联用）
├── SPEC.md                 # 需求规格
├── data/pressure.json      # 压力测试数据（可导入）
├── scripts/
│   ├── gen_pressure_data.py  # 生成压力测试数据
│   └── make_demo.py          # 生成演示版（内存存储，供在线托管）
├── tests/smoke.js          # 冒烟测试：语法 + jsdom 真实渲染
├── docs/WORKFLOW.md        # 版本管理 / CI/CD / 发布 / 需求跟踪 手册
└── .github/workflows/      # CI（自动测试）+ Release（自动发版）
```

## 常用操作

| 想做什么 | 怎么做 |
|---|---|
| 看最新版效果 | 右侧 Releases → 最新版 → 在线链接 / 下载 index.html |
| 提需求 / 报 bug | Issues → New issue（手机装 GitHub App 也行） |
| 发新版 | `git tag vX.Y.Z && git push origin vX.Y.Z`（自动发版+部署） |
| 跑测试 | `npm install && npm test` |

## 版本历史

见 [CHANGELOG.md](CHANGELOG.md)。当前版本：v2.1.0。
