已读研究卡、冻结协议、引擎、既有精度报告。未发现适用 AGENTS.md。默认 Python 缺少 numba、PySR、gplearn。
## 核实记录
- 无根级/父级/实验目录 AGENTS.md 检出。
- 原冻结协议与代码：IC p=.01,h=3,k=5；step-indexed hash；词典序同分；选择/评价world family分离。
- 真实图 raw 与 graph hash 在本轮运行中与冻结manifest逐项核对；ca-GrQc去自环后5241节点，不能照抄SNAP摘要5242。
- 安装Numba和llvmlite仅于vendor；未安装或调用PySR、gplearn。
- 三图PR实现在tol1e-6与安装NetworkX的最大分数差<2e-18，20候选均匹配继承实现。
- 文献事实及读取边界见sources.md。
