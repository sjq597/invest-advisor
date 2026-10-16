# 研发流水线手册：版本管理 / 需求跟踪 / CI/CD / 发布

> 面向王大锤。日常协作模式不变：你在聊天里说需求，小M 在 VM 里干活。
> 这套流程解决的是"黑盒"问题——每一步都留下记录，你在手机上随时能看。

## 一、版本管理（Git）

- 仓库：`invest-advisor`（GitHub 私有仓库）
- 主分支：`main`，永远可运行
- 小M 每次改完都会 commit，信息格式：`类型: 一句话`
  - `feat` 新功能 / `fix` 修 bug / `docs` 文档 / `chore` 杂项
- 版本号：`v主.次.修`（如 v2.1.0），打 tag 即发版

你在 GitHub App / 网页上能看到：每次改了什么、谁改的、diff 对比。

## 二、需求跟踪（Issues）

所有需求和 bug 都进 Issues，不再只靠聊天记录：

| Label | 含义 |
|---|---|
| `enhancement` | 新功能需求 |
| `bug` | 缺陷 |
| `done` | 已完成（发版后关闭） |

- 你提：在 GitHub App 里点 Issues → New issue，选"功能需求"或"缺陷报告"模板填两行就行
- 小M 提：你在聊天里说的需求，小M 干完后会同步建 issue 并关联 commit，关闭时注明版本号
- 看进度：Issues 列表一眼看到"待做 / 已完成"

### 当前 backlog（小M 建仓后会录入）

1. [done] 底部导航拥挤 → v2.1.0
2. [done] 图标丑 → Lucide 线性图标 → v2.1.0
3. [done] iOS 导入 JSON 无反应 → 数据内嵌一键载入 → v2.1.0
4. [open] iOS 附件查看器不执行 JS 的长期方案（正式版在手机上的使用方式）
5. [open] 持仓列表支持手动排序
6. [open] 收益分析增加年化收益率指标

## 三、CI（持续集成）：每次提交自动测试

`push` 到 main 或提 PR 时，GitHub Actions 自动跑 `tests/smoke.js`：

1. 全部内联 JS 语法检查
2. jsdom 真实加载页面：5 个 Tab 切换、"更多"菜单、示例数据/压力数据载入
3. 断言 0 真实 JS 错误（模拟 iOS 吞弹窗环境）

测试挂了会显示红叉 ❌，小M 收到后修复；全绿 ✅ 才算可发布。

## 四、CD（持续发布）：打 tag 即上线

```
git tag v2.2.0 && git push origin v2.2.0
```

自动完成三件事（约 1-2 分钟）：

1. 创建 GitHub Release，附上 `index.html` 下载包 + 自动生成的更新说明
2. 部署到 GitHub Pages，得到永久在线链接：`https://<用户名>.github.io/invest-advisor/`
3. 小M 在聊天里把链接和更新内容发你

回滚：Pages 保留历史版本，Release 页可下载任意旧版 `index.html`。

## 五、你在手机上怎么看、怎么管

装 **GitHub App**（iOS 有），打开 `invest-advisor` 仓库：

- **Code**：看文件、看提交历史（每次改了什么一目了然）
- **Actions**：看 CI 每次跑是绿 ✅ 还是红 ❌
- **Releases**：右侧，下载历史版本 / 复制在线链接
- **Issues**：提需求、报 bug、看 backlog 进度

## 六、小M 的工作流（VM 侧）

```
你说需求 → 小M 改代码 → 本地跑 npm test
        → commit → push → CI 自动跑
        → CI 绿了 → 告诉你改了什么
        → 你要发版 → 小M 打 tag → 自动 Release + Pages → 发你链接
```

## 七、本地目录说明

```
~/workspace/projects/invest-advisor/  ← git 仓库根目录
├── index.html          # 唯一的发布物（main 分支上的即最新稳定版）
├── index-demo.html     # 演示版（生成物，不入库，scripts/make_demo.py 可重建）
├── data/pressure.json  # 压力测试数据
└── docs/WORKFLOW.md    # 本文件
```

`index.html` 永远是唯一真相来源；demo/link 变体都是由它生成的。
