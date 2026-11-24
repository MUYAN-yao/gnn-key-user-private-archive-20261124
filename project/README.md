# Robust Influence Lab

面向社交传播网络的可复现研究与演示原型。系统在历史时间窗内学习边激活概率及不确定性，以“传播覆盖下置信界 + 跨社区覆盖奖励”为目标，选择 Top-K 种子用户。

## Quick start

```powershell
python -m pip install -r requirements.txt
python -m uvicorn app.main:app --app-dir backend --reload
```

打开 `http://127.0.0.1:8000/docs` 查看 API。上传 ZIP 数据包，包内必须包含：

- `nodes.csv`: `node_id`，可选 `text`、`followers`
- `edges.csv`: `src`,`dst`,`timestamp`，可选 `event_type`,`weight`
- `cascades.csv`: `cascade_id`,`user_id`,`parent_user_id`,`event_time`

`sample_data/` 提供可直接压缩上传的最小样例。运行核心实验测试：

```powershell
python -m pytest -q
```

## Reproducibility contract

- 所有训练仅使用输入边时间排序的前 70%；后 30% 仅用于评估。
- 分析结果记录随机种子、配置、数据集 ID 和运行时间。
- 若未安装 `torch-geometric`，系统会使用纯 PyTorch 的时间边聚合回退实现并在结果中标识；正式实验应安装 PyG。

## Web client

`web/` 是 Vite + React + TypeScript 前端。安装 Node.js 20+ 后执行 `pnpm --config.node-linker=hoisted install && pnpm --config.node-linker=hoisted dev`。`hoisted` 选项适配本工作区的 exFAT 文件系统。前端使用传播时间带与社区色带呈现分析结果。

Docker 环境可通过 `docker compose up --build` 同时启动 API（8000）与生产前端（8080）。
