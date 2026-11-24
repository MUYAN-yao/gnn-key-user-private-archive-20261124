# 信息移动与保留台账

| 原位置 / 内容 | 新位置 | 处理结果 |
|---|---|---|
| 正文 4.3：SHA-256 元组、63 位 world ID、pool hash 组成 | 补充材料 11.1；正文 4.3 保留明确指引 | 细节原已在补充材料完整存在，本轮消除正文重复；独立世界、前缀嵌套、固定随机池仍在正文 |
| 正文 4.3：fresh output、代表性/全部回放、数组及 PNG 验收、PDF 元数据例外 | 补充材料 11.2、REPRODUCE.md、EXTERNAL_REPRODUCE_INHERITED.md | 正文只说明实际验证范围与入口；精确验收规则完整保留 |
| history_evidence.tex：The present integration reads ... | 补充材料 12.1 改为历史汇总审计范围；本报告记录执行身份 | 520 对文件、1040 哈希、4680 数组、3640/378/240 汇总核对及限制保留；不声称本轮重跑 |
| history_evidence.tex：旧 Fig4 如何保留、未当作全方法敏感性图 | REPRODUCE.md 的历史整合记录 | 原图仍在历史冻结包；当前历史参数图完整展示 D/P/W，均无改动 |
| history_evidence.tex：脚本不导入实验 runner、本轮无新实验等任务措辞 | README.md、REPRODUCE.md、revision_report_zh.md | 正式补充材料只保留脚本、数据来源、统计单位和范围 |
| 早期 GNN、risk penalty、community reward 分支排除说明 | REPRODUCE.md 的范围记录 | 不计入本论文直接证据或实验数；未删旧数据、代码或结果 |
| 补充材料的 26 October 2026 修订日期及版本沿革 | REPRODUCE.md 的历史核验记录 | 补充材料保留“代表性重跑和分析再生成，非全部条件重跑”实质边界 |
| PowerShell 内存显示与 psutil 的区别 | REPRODUCE.md 的历史核验记录 | SI 保留真实 psutil 值、进程生命周期峰值口径及预检评估规模差别 |

未移动或删去：ca-GrQc 先去自环再收集节点的事实和原协议措辞歧义；原 runner 未强制校验原始哈希的执行缺口；事后 PageRank 身份；没有外部 tighter PageRank × fixed-edge 联合验证；统计口径及计时排除项。
