# 修订说明 · 2026-10-31

## 版本依据与范围

采用 contribution-action-revision-20261028 的有效稿件：README记录贡献改写、10月29日章节标题与作者确认题名，正文与之对应。新稿另存 budget-interpretation-revision-20261031，旧版及冻结实验未覆盖。

## 简短修改对照

| 位置 | 原表述 | 修改后表述 | 理由 |
|---|---|---|---|
| 英中摘要 | varying reference budget；随参照预算增加 | vary the selection-world budget W for both full-candidate and candidate-restricted greedy selection | W控制两类选择，不是单独提高参照预算 |
| 引言问题及贡献1 | sampling budget can change the full-reference seeds | increasing W can change the seeds selected by both ...；贡献1明确两类臂共同扫描 | 相对差异来自双方选择随预算变化 |
| 贡献2、投稿信及编辑摘要 | spread gains；utility gained through additional sampling | independently estimated spread changes；direction, magnitude and conditional uncertainty | 描述同时包含正、负和零变化；正均值仍如实保留 |
| 方法及实验设置 | vary reference resolution through W | 两类臂每个W重新选择，池在给定排名设置下跨W固定；M单独固定 | 分开选择、评估与候选构建 |
| 精度控制与结果首段 | same full reference | same-budget full reference；固定W仅重算受限臂，跨W使用各自参照 | 准确限定这个单因素对照 |
| 机制图说明及预算图说明 | W确定finite-world reference | W用于两实验臂选择；τ/q定义候选池；M独立评估 | 修正说明，机制图资产未修改 |
| 参照转移结果及补充表 | mean gain；Mean gain | mean high-minus-low spread change；Mean change | 明确高预算减低预算；不是方法间差值，也不保证改善 |
| 讨论 | increasing the reference budget ... gain to loss | shared selection budget ... restricted-minus-full difference positive to negative | 不把符号变化全部归因于参照改善 |
| 一般限制 | 结果、多个讨论段和结论重复限制 | 联合控制缺口与求解器比较集中于讨论；结果保留统计/对照必要限定 | 减少防御性重复，保留不利结果与证据边界 |
| 结论 | 重复最优性及未来实验列表 | 总结共同预算响应、精度敏感性、传播差异与成本报告，最后限定范围 | 避免逐条重复讨论局限 |

## 一致性核查

核对两份冻结runner的代码文本及配置，并读取54个外部条件、520个历史扩展条件的已保存JSON。跨预算核对候选池、评估世界哈希及评估世界数量；对30个已有低预算精度条件，核对同预算冻结参照哈希和世界哈希。从已保存CSV核对ca-GrQc默认/严格容差的百分比、+0.02608节点及历史两项预算转移计数、均值、范围。无模拟、种子搜索或实验重跑。

同预算方法差值为“受限减全候选”；损失百分比与其反号；参照内部转移为“高预算减低预算”。保留特定数据条件下真实的正向均值和由正转负描述，未机械删除所有gain/improvement。中英稿、投稿信和编辑摘要同步。

作者声明、参考文献、全部图像及表内数字保持不变。新旧文稿差异和完整性记录见qa。编译、引用与逐页渲染结果见qa/final_checks.json、qa/render_checks.json。

## 尚未解决的问题与验证边界

本轮三项文字修订没有需要作者补充才能判断的设计字段。未重新计算全部NPZ、重跑实验或独立验证作者声明；既有审计仅按其原范围继承。此次数据核对不构成新增实验或新的统计检验。仍缺少的外部严格容差×固定边联合控制、方向干预等科学证据已保留为讨论中的局限，不在本轮补做。

标题沿用作者已选版本；文中明确其预算W同时作用于双方。期刊要求和文献未新增，本轮不重新进行投稿政策或文献检索。


最终核读还补充两点：摘要明确百分比是逐路径相对差异的跨路径均值；为补齐补充材料所指的复现文件，原样复制已有指南、依赖清单和复现/历史汇总入口，记录来源哈希但没有执行。原入口与已有算法均未修改。
