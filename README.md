# 基于 GNN 的关键用户识别：研究归档

归档日期：2026-11-24。项目原名 **Robust Influence Lab**。

本仓库以完整保留研究资料为目标，保留原目录层级及历史版本。无法确定是否仍有用的材料（包括 tmp、旧稿、交付包、测试临时结果）均保留，方便以后由作者筛选。原项目没有 Git 历史，本仓库是文件快照。

## 从哪里开始

| 内容 | 入口 | 用途 |
|---|---|---|
| 项目运行 | [原 README](project/README.md) | 安装、API、前端、Docker |
| 认证和请求流程 | [认证说明](AUTHENTICATION.md) | 当前认证能力、组件、接口、凭据处理 |
| 后端 | [backend](project/backend/) | FastAPI、数据校验、GNN/传播分析 |
| 前端 | [web](project/web/) | React + TypeScript 可视化演示 |
| 测试与样例 | [tests](project/tests/)、[sample_data](project/sample_data/) | 原项目测试与最小输入 |
| 研究设计 | [protocols](project/protocols/)、[docs](project/docs/)、[data_cards](project/data_cards/) | 预注册、研究协议、数据说明 |
| 实验与结果 | [experiments](project/experiments/)、[results](project/results/)、[analysis](project/analysis/) | 实验脚本、运行结果、统计分析 |
| 论文及投稿 | [manuscript](project/manuscript/)、[submission](project/submission/) | 多版本论文、审查、投稿包 |
| 可复现证据 | [reproducibility](project/reproducibility/)、[audits](project/audits/) | 源码快照、证据链、核查记录 |
| 数据 | [data](project/data/)、[runtime-data](project/runtime-data/) | 原始/处理数据、演示输入 |
| 交付与图件 | [deliverables](project/deliverables/)、[figures](project/figures/)、[assets](project/assets/) | 历史打包、图件和资源 |
| 尚待筛选 | [tmp](project/tmp/) | 临时工作副本、重复解包、历史验证产物 |
| 研究进度 | [task_plan](project/task_plan.md)、[findings](project/findings.md)、[progress](project/progress.md) | 原有规划与工作记录 |

涉及个人隐私的项目申请材料及其提取文本仅在作者本地保存，不包含在公开仓库中。其他根目录材料保留在 `project/`。日期或版本号仅表示原文件命名，不代表已经确认哪一版可投稿。

## 完整性与恢复

- `inventory.json`：每个归档文件的原路径、字节数、SHA-256 和存储位置。
- `excluded.json`：未复制项及原因。依赖安装目录、Python 字节码缓存和 Git 元数据可重新生成；疑似凭据文件保留于原工作区，未上传。
- `large-files.json`：超大文件的分片清单；分片存于 `large-files/`，每片不超过 48 MiB。
- 在仓库根目录执行 `python restore_large_files.py`，恢复超大文件并验证所有归档文件的 SHA-256。Windows 长路径环境建议使用支持长路径的 Python/Git，或克隆到较短路径。
- `prepare_archive.py` 记录归档实现；其中来源目录是本次归档的本地路径，换电脑重新归档时需修改。

原目录中的文件未被删除或搬移。确认远端内容、恢复校验及排除清单后，再自行决定清理原资料。此归档并非对研究结论或投稿就绪状态的再次认证。

## 运行

先恢复分片，然后进入 `project/`，按原 README 安装依赖和启动。`web/dist` 保留以适配现有 Nginx Dockerfile；`node_modules` 未归档，可依据 `web/pnpm-lock.yaml` 重新安装。

仓库当前公开。2026-11-27 已移除个人项目申请材料及其提取文本，并清理分支提交历史。GitHub 仓库可见性与项目 API 认证是两件独立的事。
