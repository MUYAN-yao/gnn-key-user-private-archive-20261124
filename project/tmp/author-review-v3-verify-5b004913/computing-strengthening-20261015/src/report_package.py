"""Generate traceable author-facing report and submission drafts from validated data."""
import sys,json
from pathlib import Path
import numpy as np
import pandas as pd

REAL=['invs2013','invs2015','kenya2012','sfhh2009']
METHODS=['weighted_2k','weighted_4k','weighted_8k','degree_4k','pagerank_4k','random_4k']

def mdtable(headers,rows):
    return '\n|'+'|'.join(headers)+'|\n|'+'|'.join(['---']*len(headers))+'|\n'+'\n'.join('|'+'|'.join(map(str,r))+'|' for r in rows)+'\n'

def main(base):
    base=Path(base);a=base/'analysis'
    v=json.loads((a/'validation.json').read_text());assert v['status']=='PASS'
    s=json.loads((a/'summary.json').read_text());meta=json.loads((base/'manuscript/metadata.json').read_text())
    g=pd.read_csv(a/'group_summary.csv');d=pd.read_csv(a/'path_level_metrics.csv');tr=pd.read_csv(a/'reference_transitions.csv');tt=pd.read_csv(a/'tolerance_sensitivity.csv');tests=pd.read_csv(a/'primary_sign_tests_holm.csv')
    p=g[(g.stage=='resolution')&(g.W==5120)];last=tr[(tr.stage=='resolution')&(tr.high==5120)]
    weighted=p[p.method=='weighted_4k'];primary=d[(d.stage=='resolution')&(d.W==5120)]
    text='# Computing 修订结果与投稿判断\n\n'
    text+='本轮已实际完成代码审计、冻结扩展协议、全部实验、统计分析及稿件构建。研究定位仍是候选限制的评价研究；没有添加 GNN，也没有将编译加速包装成新算法。原始数据、旧稿与原42条件结果保持独立。稿件可交作者最终审核，但资助、作者批准、公开复现安排等仍待处理。\n\n'
    text+=f'扩展包含 **{v["conditions"]} 个条件、{v["arm_executions"]:,} 次实验臂执行、{v["evaluation_values"]:,} 个保留的逐世界评估计数**；串行总耗时 {s["runtime_minutes"]:.1f} 分钟，峰值进程工作集 {s["max_peak_mb"]:.0f} MiB。四张真实图各有10条路径，两张合成图各5条。这些数量不能当作独立网络样本量。\n'
    deg=primary[primary.method=='degree_4k'];pr=primary[primary.method=='pagerank_4k']
    text+=f'\n最重要的结果是：最高两档预算间虽有 {int((~last.same_set).sum())}/40 个集合变化，平均收益仅增加 {last.delta_full_high_low.mean():.4f} 个节点；加权4k的均值对比随预算从正转负，而非加权度、PageRank在最高预算分别复现 {int(deg.same_order.sum())}/40、{int(pr.same_order.sum())}/40 条完整有序轨迹。**应收窄“截断失败”的表述，转而解释预算与排序怎样改变成本和收益判断。**\n'
    text+='\n## 1. 相对原稿的变化\n'
    text+=mdtable(['项目','原稿','本轮'],[
      ['真实图','4张，75–402节点','保留相同4张；另加两张2,000节点合成实例'],
      ['选择预算','20/80/320','k=5真实图增加1280/5120；其他设置依协议'],
      ['随机路径','2','真实图10；合成图5'],
      ['评估世界','2,000','10,000，与选择家族分离'],
      ['候选','加权度2k/4k/8k','另加非加权度、PageRank、3个随机4k池'],
      ['参数/耦合','p=.01,h=3,按步耦合','p/h敏感性及固定边耦合'],
      ['统计','主要条件MC区间','另报路径SD/自助区间及完整24对比Holm检验'],
      ['计时','固定顺序单次，选择与评估合并','分项、随机顺序及180次额外计时观察']])
    text+='\n## 2. 参照集合变化与实际收益\n'
    rows=[]
    for (low,high),b in tr[tr.stage=='resolution'].groupby(['low','high']):
        excl=(b.mc_lower>0)|(b.mc_upper<0)
        rows.append([f'{low}→{high}',f'{int((~b.same_set).sum())}/{len(b)}',f'{b.jaccard.mean():.3f}',f'{b.delta_full_high_low.mean():+.4f}',f'{int(excl.sum())}/{len(b)}'])
    text+=mdtable(['预算变化','最终集合变化','平均Jaccard','高减低平均传播量','条件MC区间不跨零'],rows)
    text+='这里每行是40个“网络×路径”块，不是40张独立网络。最后一列是未多重校正的条件诊断，不能据此宣称跨网络显著性。集合仍变化和收益接近可以同时发生；也不能凭较高预算证明已收敛。证据：Fig1、`analysis/reference_transitions.csv`。\n'
    rows=[]
    for ds in REAL:
        b=last[last.dataset==ds];rows.append([ds,f'{int((~b.same_set).sum())}/10',f'{b.delta_full_high_low.mean():+.4f}',f'{b.delta_full_high_low.min():+.4f}～{b.delta_full_high_low.max():+.4f}'])
    text+=mdtable(['网络','1280→5120集合变化','平均收益变化','十条路径收益变化范围'],rows)
    text+='\n## 3. 截断结论怎样随预算变化\n'
    rows=[]
    for ds in REAL:
        for method in ['weighted_4k','degree_4k']:
            b=g[(g.stage=='resolution')&(g.dataset==ds)&(g.method==method)].set_index('W')
            rows.append([ds,method,f'{b.loc[20,"delta_mean"]:+.4f}',f'{b.loc[5120,"delta_mean"]:+.4f}',f'{100*b.loc[20,"relative_incremental_loss_mean"]:.1f}%',f'{100*b.loc[5120,"relative_incremental_loss_mean"]:.1f}%'])
    text+=mdtable(['网络','方法','W20绝对差','W5120绝对差','W20新增传播损失','W5120新增传播损失'],rows)
    text+='绝对差为候选方法减全候选；损失以全候选新增传播量为分母。负损失表示候选方法在该独立评估中的估计更高。不同预算共用评估世界，差值可以配对；此表是描述性对比，没有据结果挑选最终方案。完整所有方法与预算见 `group_summary.csv`。\n'
    text+='\n## 4. 最高预算的所有候选对照\n'
    rows=[]
    for ds in REAL:
        for method in METHODS:
            b=p[(p.dataset==ds)&(p.method==method)].iloc[0]
            rows.append([ds,method,f'{100*b.coverage_mean:.1f}%',f'{b.delta_mean:+.4f}',f'[{b.delta_lo:+.4f}, {b.delta_hi:+.4f}]',f'{100*b.relative_incremental_loss_mean:.1f}%',f'{100*b.selection_saving_mean:.1f}%'])
    text+=mdtable(['网络','候选','实际覆盖','绝对差','路径均值95%自助区间','新增传播损失','选择时间节省'],rows)
    text+=f'24个预先指定双侧符号检验中，{int((tests.p_holm<.05).sum())} 个通过 Holm 0.05 校正。检验针对非零路径差值的正负方向，不是均值等价检验。随机池先在每条路径内平均3次，未把样本量扩大成30。证据：Fig2、`primary_sign_tests_holm.csv`、补充材料完整表。\n'
    text+='\n## 5. 何时可以说有时间—收益优势\n'
    rows=[]
    for ds in REAL:
        for method in METHODS:
            b=primary[(primary.dataset==ds)&(primary.method==method)]
            q=tt[(tt.dataset==ds)&(tt.method==method)].set_index('tolerance')
            rows.append([ds,method,f'{int(round(q.loc[.01,"point_fraction"]*10))}/10',f'{int(round(q.loc[.05,"point_fraction"]*10))}/10',f'{int(round(q.loc[.1,"point_fraction"]*10))}/10',f'{b.end_to_end_saving.mean()*100:.1f}%',f'{b.selection_seconds.mean():.4f}'])
    text+=mdtable(['网络','方法','≤1%损失','≤5%损失','≤10%损失','含公共准备成本节省','平均选择秒数'],rows)
    text+='这些是给定容忍度的点估计满足比例，不能直接变成“保留效用”的确认结论。完整0/1/2.5/5/10/20%曲线及较保守的条件损失上界描述见 `tolerance_sensitivity.csv`；该上界除以点估计分母也不是比值置信区间。单次实验臂成本与随机重复的平均单臂成本有别：若用户实际执行三个随机池并再挑一个，必须另外计算选择规则、总成本并重新评估。证据：Fig3、Fig5和计时CSV。\n'
    text+='\n## 6. 参数、结构和耦合的适用边界\n'
    rows=[]
    for ds in REAL:
        for coupling in ['step','edge']:
            b=g[(g.dataset==ds)&(g.k==5)&(g.W==1280)&(g.p==.01)&(g.h==3)&(g.coupling==coupling)&(g.method=='weighted_4k')].iloc[0]
            rows.append([ds,coupling,f'{b.delta_mean:+.4f}',f'{100*b.relative_incremental_loss_mean:.1f}%'])
    text+=mdtable(['网络','耦合','加权4k绝对差','新增传播损失'],rows)
    text+='固定边对照用于检查耦合敏感性，不能由两种实现的结果差异直接推断哪一种更符合真实传播。原按步耦合的三节点反例只否定其固定世界目标自动单调的说法；本轮保持逐轮全枚举，没有使用未经证明适用的CELF。\n\n'
    text+='参数实验覆盖 p=.005/.01/.05 与 h=1/3/5 的预定子集，不是全部排列。更大种子预算仍不包含 SFHH k=20；原范围限制没有隐藏。两张较大图为合成实例，其加权/非加权度按构造相同。全部设置与结果见 Fig4、`group_summary.csv`、`network_metadata.json`；失败或不利结果均保留。\n'
    text+='\n## 7. 可以支持的贡献与下一步优先方向\n'
    text+='可支持的贡献是：在明确的有限模拟参照下，把轨迹/集合、独立传播效用、实际候选覆盖和分项计算成本一起评价；给出排序、参数和耦合的对照，以及可复核的输出与诊断脚本。创新点必须放在这些可量化证据与评价问题的交叉处，不能把“采样越多通常越稳定”本身称为新发现。\n\n'
    text+='后续优先级：**第一，新增不同来源及较大真实网络的外部验证；第二，若要主张实际可用，确定有领域依据的损失容忍度并另做前瞻性验证；第三，在传播期限与质量目标一致的条件下比较高效IM基线。** GNN不是当前稿必须补上的模块；把它加入需要新的训练/验证/跨图评估设计，容易分散当前论文问题。\n'
    text+='\n## 8. 交付与尚未完成\n'
    text+='已完成并可核验：实现审计、全部冻结条件、完整逐世界输出、统计/图表生成和论文源码。PDF编译、页数和可视检查的实际结果以 `qa/verification.json` 为准。\n\n'
    text+='已完成但局限明确：小型真实图加合成扩展、10条真实图路径、描述性容忍度和本机计时。未完成的科学扩展为更大/独立真实网络、实测信息级联、应用阈值确认与公平高效算法运行基线；这些没有写成完成。它们是外部有效性和贡献强度方面的后续投入，不是本轮冻结矩阵的缺失条件。\n\n'
    text+='需作者输入：资助、作者/贡献/批准、利益冲突、其他投稿状态、完整AI披露、代码许可和公开访问安排，详见 `author_checklist_zh.md`。没有因本轮资源限制丢弃冻结条件。编辑是否认为评价研究的新意充分仍有不确定性；格式合规不等于能录用。\n'
    text+='\n## 9. 主张—证据索引\n'
    text+=mdtable(['主张','直接证据'],[
      ['旧结果语义连续、未静默换算法','audit/research-audit.md；audit-and-preflight.json及计数勘误'],
      ['新矩阵完整且哈希/数值校验通过','snapshot/config.json；results/manifest.json；analysis/validation.json'],
      ['参考变化及独立收益','Fig1；reference_transitions.csv'],
      ['排序与真实损失','Fig2；group_summary.csv；primary_sign_tests_holm.csv'],
      ['容忍度和成本','Fig3/5；tolerance_sensitivity.csv；timing_repeats.csv'],
      ['参数、耦合、合成规模','Fig4；所有条件JSON/NPZ；group_summary.csv'],
      ['有序一致、首分歧、Jaccard、边际收益与次优分差','all_arm_metrics.csv；round_diagnostics.csv'],
      ['Computing格式与定位','audit/literature-and-journal.md；qa/verification.json']])
    (base/'research_report_zh.md').write_text(text,encoding='utf-8')
    summary=(f'Title: {meta["title"]}\n\nSummary of uniqueness, contribution and evaluation\n\n'
      'This manuscript evaluates candidate-restricted influence maximization when the full-candidate reference is itself a finite Monte Carlo computation. Its contribution is a joint empirical analysis of selection resolution, seed-set membership, independently evaluated utility, actual candidate coverage and attributable computation cost. The study does not propose a new optimizer, approximation theorem or learned ranking model. It explicitly relates the protocol to established sampling and optimization methods, including StaticGreedy, CELF and IMM.\n\n'
      'Evaluation preserves an archived 42-condition study and adds a prospectively frozen 520-condition extension with 4,680 arm executions. Four contact-derived real topologies and two synthetic 2,000-node instances are tested. The extension includes ten paths per real graph, selection budgets up to 5,120 worlds, 10,000 disjoint evaluation worlds, alternative rankings, propagation controls, fixed-edge coupling and repeated randomized timing. All per-world outcomes and round-level scores are retained. Implementation equivalence is checked against the archived simulator and an independent reachability oracle.\n\n'
      f'At the final 1,280-to-5,120 transition, {int((~last.same_set).sum())}/40 full-reference final sets changed. Weighted-degree 4k mean candidate-minus-full spread differences at the highest budget ranged from {weighted.delta_mean.min():.3f} to {weighted.delta_mean.max():.3f} activated nodes across the four real graphs. The complete ranking, tolerance and timing results distinguish decision reproduction from practical utility. A concrete step-coupling counterexample motivates the explicitly labeled fixed-edge control.\n\n'
      f'The last reference transition increased independent spread by only {last.delta_full_high_low.mean():.4f} nodes on average. Topology-degree and PageRank 4k pools reproduced {int(deg.same_order.sum())}/40 and {int(pr.same_order.sum())}/40 highest-budget ordered references. Thus the results also identify a successful restriction setting and limit any general claim based only on weighted-degree losses.\n\n'
      'The scope is conditional on the tested graphs and simulated diffusion settings. Synthetic instances do not establish real-network generalization, and illustrative tolerances are not confirmatory noninferiority margins. The local reproducibility package is prepared for author review; public access details and author declarations must be finalized before submission.\n')
    (base/'summary_for_editor.txt').write_text(summary,encoding='utf-8')
    letter=(f'DRAFT FOR AUTHOR REVIEW — not submitted\n\nDear Editors of Computing,\n\n'
      f'Please consider our manuscript, "{meta["title"]}," for publication in Computing.\n\n'
      'Candidate restriction reduces the search cost of influence maximization, but its apparent quality depends on how the full greedy reference is simulated and evaluated. We study this issue by separating selection resolution, random-world coupling, independently evaluated utility and attributable cost. The contribution is an auditable evaluation of these interacting choices rather than a new influence-maximization algorithm.\n\n'
      f'The paper reports a preserved historical experiment and a 520-condition prospective extension on four contact-derived graphs and two larger synthetic instances. The extension contains 4,680 arm executions, independent evaluation streams, alternative candidate rankings, propagation/coupling controls and repeated timing. It finds {int((~last.same_set).sum())}/40 changed full-reference final sets between 1,280 and 5,120 selection worlds, while reporting utility differences separately. Complete effects and unfavorable outcomes are retained rather than judging restriction solely by sequence agreement.\n\n'
      f'The corresponding average utility increase was {last.delta_full_high_low.mean():.4f} activated nodes. At the highest budget, topology-degree and PageRank restrictions reproduced {int(deg.same_order.sum())}/40 and {int(pr.same_order.sum())}/40 full traces, respectively. This limits the interpretation of weighted-degree losses and makes the ranking-specific cost-quality findings central to the paper.\n\n'
      'The manuscript is relevant to Computing\'s scope in network science, social networks and computational methodology. It provides explicit simulation semantics, validated implementation continuity, condition-level results and reusable analysis scripts. Its limitations concerning contact-derived topology, synthetic diffusion and external validity are stated directly.\n\n'
      'The main manuscript, supplementary methods/results, novelty-and-evaluation summary, editable sources and figures are prepared. Before sending this letter, the authors must confirm originality/exclusive consideration, all-author approval, competing interests and the final data/code access statement. These confirmations are intentionally not asserted in this draft.\n\n'
      'Sincerely,\nBinbin Yong, corresponding author (identity and submission authorization to be confirmed)\nyongbb14@lzu.edu.cn\n')
    (base/'cover_letter_draft.txt').write_text(letter,encoding='utf-8')
    catalog='Figure\tData source\tSelection rule\nFig1\treference_transitions.csv;group_summary.csv\tall real graphs, resolution, full reference\nFig2\tgroup_summary.csv\tall six candidate types, W5120 real resolution\nFig3\tpath_level_metrics.csv;tolerance_sensitivity.csv\tprespecified weighted4k diagnostic, all real paths\nFig4\tgroup_summary.csv\tpredefined weighted4k parameter/coupling panels; all synthetic rankings\nFig5\ttiming_repeats.csv\tall 180 repeats, all nine arms\n'
    (a/'figure_catalog.tsv').write_text(catalog,encoding='utf-8')
    print('Created research report, editor summary, cover letter, figure catalog')

if __name__=='__main__':main(sys.argv[1])
