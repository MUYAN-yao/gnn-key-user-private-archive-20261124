from pathlib import Path
import json,hashlib,re,csv,statistics,collections,shutil,difflib

P=Path('submission/computing-external-validation-20261015').resolve()
B=P/'contribution-action-revision-20261028'
R=P/'budget-interpretation-revision-20261031'
H=P.parent/'computing-strengthening-20261015'
def read(p): return p.read_text(encoding='utf-8')
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def save(name,s): (R/name).write_text(s,encoding='utf-8')
changes=json.loads(read(R/'qa/change_log.json'))
def change(rel,a,b):
    t=read(R/rel)
    assert a in t,(rel,a)
    save(rel,t.replace(a,b))
    changes.append(dict(file=rel,old=a,new=b,reason='二次核读：精确限定比较对象并整理段落'))
change('manuscript/manuscript.tex','Separate reference-transition comparisons show that set changes can accompany positive, negative or zero estimated spread changes.','Separate reference-transition comparisons distinguish changes in seed membership from the direction and magnitude of estimated spread changes.')
change('chinese/manuscript/manuscript_zh.tex','单独的参照预算转移比较表明，集合变化可伴随正、负或零的估计传播量变化。','单独的参照预算转移比较区分了种子成员变化与估计传播量变化的方向和大小。')
change('manuscript/manuscript.tex','rather than improvement of the reference alone. Degree ranks','rather than improvement of the reference alone.\n\nDegree ranks')
change('chinese/manuscript/manuscript_zh.tex','不能仅归因于参照的改善。Degree 按','不能仅归因于参照的改善。\n\nDegree 按')
change('manuscript/precision_budget_table.tex','Each entry is the mean incremental-loss percentage across five original paths at $W=80/320/1280$.','Each entry is the mean incremental-loss percentage across five original paths at $W=80/320/1280$, relative to the full reference selected at the same $W$.')

# Read-only evidence checks: no engine imports, no runner execution, no simulation.
sources={}
def load(p):
    sources[str(p)]=sha(p)
    return json.loads(read(p))
def rows(p):
    sources[str(p)]=sha(p)
    return list(csv.DictReader(read(p).splitlines()))
cfg=load(P/'config.json'); hc=load(H/'snapshot/config.json')
external=[load(p) for p in sorted((P/'results/main/conditions').glob('*.json'))]
history=[load(p) for p in sorted((H/'results/conditions').glob('*.json'))]
assert len(external)==54 and len(history)==520
assert sum(len(x['arms']) for x in external)==468
assert sum(len(x['arms']) for x in history)==4680
assert cfg['evaluation_worlds']==hc['evaluation_worlds']==10000
checks={}
for name,records in [('external',external),('historical_extension',history)]:
    assert all(d['evaluation_world_count']==10000 for d in records)
    # Fix p/h/k as well as graph/path/coupling when comparing budget records.
    groups=collections.defaultdict(list)
    for d in records:
        c=d['config']; key=tuple(c[k] for k in ['stage','dataset','path','k','p','h','coupling'])
        groups[key].append(d)
    comparisons=0
    for group in groups.values():
        if len(group)<2: continue
        comparisons+=1
        assert len({x['evaluation_world_sha256'] for x in group})==1
        assert len({x['selection_world_sha256'] for x in group})==len(group)
        for arm in group[0]['arms']:
            assert len({tuple(x['arms'][arm]['candidate_ids']) for x in group})==1
    checks[name]=dict(conditions=len(records),arms=sum(len(x['arms']) for x in records),evaluation_worlds=10000,budget_groups_with_fixed_evaluation_and_pools=comparisons)
strict=[load(p) for p in sorted((P/'review-v3-budget-precision/supplement-pr-budget-precision/conditions').glob('*.json'))]
assert len(strict)==30
for d in strict:
    p=P/'results/main/conditions'/f"resolution__{d['dataset']}__p{d['path']}__w{d['W']}__step.json"
    old=load(p)
    assert d['frozen_reference_json_sha256']==sha(p)
    for key in ['selection_world_sha256','evaluation_world_sha256']:
        assert d[key]==old[key]
checks['posthoc_lower_budget_precision']=dict(conditions=30,arms=sum(len(x['arms']) for x in strict),same_budget_reference_hash_match=True,world_hashes_match=True)
for p in [P/'snapshot/run_experiment.py',H/'snapshot/run_extension.py',P/'review-v3-budget-precision/src/run_precision_budget_control.py',P/'snapshot/legacy_engine.py',P/'review-v3-budget-precision/supplement-pr-budget-precision/protocol.md']:
    sources[str(p)]=sha(p)
s=rows(P/'review-v3-budget-precision/analysis/precision_budget/summary_by_budget_precision.csv')
ca=[x for x in s if x['dataset']=='ca_grqc' and x['method']=='pagerank_4k']
expected={'default':[-5.61,2.53,5.07],'strict':[-11.25,-2.96,-.54]}
for solver,values in expected.items():
    selected=sorted([x for x in ca if x['solver']==solver],key=lambda x:int(x['W']))
    assert [round(float(x['loss_percent_mean']),2) for x in selected]==values
checks['ca_grqc_incremental_loss_percent']=expected
checks['ca_grqc_strict_W1280_delta']=float(next(x for x in ca if x['solver']=='strict' and x['W']=='1280')['delta_nodes_mean'])
assert abs(checks['ca_grqc_strict_W1280_delta']-.02608)<1e-10
assert all(float(x['delta_nodes_mean'])<0 for x in s if x['solver']=='strict' and x['method']=='pagerank_4k' and x['dataset'] in ['college_msg','wiki_vote'])
t=rows(R/'analysis/historical_reference_transitions.csv')
for name,stage,coupling,lo,hi,changed,mean in [('step','resolution','step','1280','5120',16,.01111),('edge','coupling','edge','320','1280',29,.061845)]:
    selected=[x for x in t if x['stage']==stage and x['coupling']==coupling and x['k']=='5' and x['low']==lo and x['high']==hi]
    assert len(selected)==40
    assert sum(x['same_set']=='0' for x in selected)==changed
    delta=[float(x['delta_full_high_low']) for x in selected]
    assert abs(statistics.mean(delta)-mean)<1e-10
    checks['historical_'+name+'_transition']=dict(pairs=40,changed_sets=changed,mean=statistics.mean(delta),minimum=min(delta),maximum=max(delta),positive=sum(x>0 for x in delta),negative=sum(x<0 for x in delta),zero=sum(x==0 for x in delta))
checks['scope']='Stored JSON metadata and saved CSV summaries plus static source inspection; no NPZ recalculation, seed search, propagation or experimental rerun.'
save('qa/design_evidence.json',json.dumps(checks,ensure_ascii=False,indent=2))
save('qa/read_source_hashes.json',json.dumps(sources,ensure_ascii=False,indent=2))
save('qa/change_log.json',json.dumps(changes,ensure_ascii=False,indent=2))

# Preserve the old documentation, replace stale commands and stale version claims.
for f in ['claim_evidence_matrix.md','REPRODUCE.md','README.md','revision_report_zh.md']:
    shutil.copy2(B/f,R/'evidence'/('prior_'+f))
save('README.md', '''# 预算解释与差异措辞修订 · 2026-10-31

当前修订基于 `../contribution-action-revision-20261028`。该版 README 明确继承贡献修订，并记录2026-10-29题名及章节标题修改；正文内容与记录相符。未按文件时间直接选稿。原版完整保留。

- 英文正文：manuscript/manuscript.pdf；同名 .tex 为源码。
- 对应中文阅读稿：chinese/manuscript/manuscript_zh.pdf；同名 .tex 为源码。
- 英文补充材料：manuscript/Online_Resource_1.pdf。
- 投稿信：cover_letter_draft.txt；编辑摘要：summary_for_editor.txt。
- 中文修改对照与未解决事项：revision_report_zh.md。
- 设计核对：qa/design_evidence.json；源文件哈希：qa/read_source_hashes.json。
- 本轮最终检查：qa/final_checks.json；逐页可视检查：qa/render_checks.json。
- 逐处修改记录：qa/change_log.json；文本差异：qa/*.diff。
- 主张证据及术语：claim_evidence_matrix.md、terminology_ledger.md。
- 编译与检查：REPRODUCE.md。

本轮只读取已保存 JSON/CSV 和源码文本，修改文稿并编译、渲染 PDF。没有运行模型训练、种子搜索、传播模拟或实验 runner，也没有重新计算置信区间或显著性。所有结果表的数字、图像文件、参考文献和作者声明均保留。旧版审计记录仍属于其历史版本；不得把它们的 PDF 哈希或验证范围当作本轮检查。
''')
save('terminology_ledger.md','''# 术语与比较方向

| 符号/术语 | 本版固定含义 |
|---|---|
| W / selection-world budget / 选择世界预算 | 同预算条件中同时供全候选和受限候选贪心选择使用；并非只提高参照预算 |
| M / independent evaluation budget / 独立评估预算 | 外部实验及520条件扩展为10,000；最初42条件为2,000；资源预检为1,000，分别说明 |
| τ / ranking tolerance / 排名容差 | PageRank候选构建的数值设置，与W及M分离 |
| q / candidate-pool size / 候选池大小 | 决定候选资格；不裁剪传播图；既定排名下跨W固定 |
| restricted-minus-full difference | 同一W下受限方法减全候选参照，正值表示受限传播量更高 |
| incremental loss | -100 × 配对差值 / 全候选增量传播量；与上述差值反号；先逐路径计算再汇总 |
| reference-transition change | 只比较参照：高W减低W的独立估计传播量，与方法间差值不同 |
| same-budget precision control | 固定W，重算受限臂；复用对应W的冻结参照及评估世界 |

作者确认的标题保持不变；正文将其“Reference Budget”准确解释为两类选择共同使用的W。
''')
save('claim_evidence_matrix.md','''# 本轮主张—证据—适用范围

以下路径相对本版。来源文件哈希及实测核对计数见 qa/design_evidence.json、qa/read_source_hashes.json。

| 主张 | 直接证据 | 适用范围及不支持的推断 |
|---|---|---|
| W同时作用于两类选择 | ../snapshot/run_experiment.py:46–56；../../computing-strengthening-20261015/snapshot/run_extension.py:61–76；两包配置与全部54/520个条件JSON | 两类臂在每个W重新选择；不能归因为只改变参照 |
| M与候选池跨W固定 | 同上；条件evaluation_world_count、evaluation_world_sha256及candidate_ids逐组核对 | 按同图/路径/传播设置/耦合比较；不能把不同耦合世界逐元素配对 |
| 精度控制复用同预算参照 | ../review-v3-budget-precision/supplement-pr-budget-precision/protocol.md；../review-v3-budget-precision/src/run_precision_budget_control.py；30个低预算条件的参照及世界哈希 | 固定W只重算受限臂；跨W取各自W参照；不是全参照跨预算固定 |
| ca-GrQc默认符号反转随容差控制消失 | ../review-v3-budget-precision/analysis/precision_budget/summary_by_budget_precision.csv，ca_grqc/pagerank_4k/default及strict | 五条既有路径的事后敏感性研究；不证明普遍收益或每路径反转 |
| 参照集合变化与传播量变化分别量化 | analysis/historical_reference_transitions.csv，resolution/step/k5/1280→5120及coupling/edge/k5/320→1280 | 各40配对，均值+0.01111/+0.061845；同时保留负、正、零差值；不是保证增益 |
| 最高外部预算Degree一致，PR有向损失保留 | ../results/main/conditions/；上述precision summary | k5/p.01/h3、三外部图、五路径、W1280；不扩大独立网络数或声称期望最优 |
| 计算节省对应本实现计时范围 | manuscript/cost_table.tex；原稿方法与计时记录 | 选择实测与分项拼接区别保留；未与CELF/IMM进行运行时间比较 |

本轮没有增加科学证据，仅依据既有记录纠正解释。作者声明原样保留，不是由本轮脚本独立核实。
''')
save('revision_report_zh.md','''# 修订说明 · 2026-10-31

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
''')
save('REPRODUCE.md',r'''# 本轮文稿编译与核验

在本版 manuscript 目录运行 pdflatex -interaction=nonstopmode -halt-on-error manuscript.tex 两次，再对 Online_Resource_1.tex 同样编译两次。
在 chinese/manuscript 目录运行 xelatex -interaction=nonstopmode -halt-on-error manuscript_zh.tex 两次。
TeX程序：C:\texlive\2026\bin\windows；Python：C:\Users\36024\Miniconda3\python.exe。

在本版根目录执行：
```powershell
& 'C:\Users\36024\Miniconda3\python.exe' src\verify_revision.py
```
该核验脚本只读取原稿、修订稿、已有结果哈希、编译日志和PDF，并调用pdftoppm渲染。不会导入或执行实验代码。它检查原版未变、资产和表格数字、声明、引用、关键措辞及中英数值，并生成逐页缩略图；可视核验另存qa/render_checks.json。

src中的两个revision脚本是创建此次稿件的工作记录，使用项目根目录相对路径；完成版不应再次运行其构建步骤。没有机械调用旧版的贡献段限定验证器。实验复现记录仍在原始冻结包；本轮没有新实验或新增复现范围。
''')
# Save complete diffs and bilingual contributions.
for sub in ['manuscript','chinese/manuscript']:
    for p in (R/sub).glob('*.tex'):
        old=B/p.relative_to(R)
        if old.exists() and p.read_bytes()!=old.read_bytes():
            name=str(p.relative_to(R)).replace('/','_').replace('\\','_')+'.diff'
            save('qa/'+name,''.join(difflib.unified_diff(read(old).splitlines(True),read(p).splitlines(True),fromfile=str(old),tofile=str(p))))
save('contributions_bilingual.md','# 本版贡献（正文对应原文）\n\n'+ '\n\n'.join(re.findall(r'\\item\[\(\d\)\] (.*)',read(R/'manuscript/manuscript.tex'))+re.findall(r'\\item\[\(\d\)\] (.*)',read(R/'chinese/manuscript/manuscript_zh.tex'))))
shutil.copy2(__file__,R/'src'/Path(__file__).name)
print(json.dumps(checks,ensure_ascii=False,indent=2))
