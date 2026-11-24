from pathlib import Path
import json,shutil,hashlib,difflib
R=Path(__file__).resolve().parents[1];P=R.parent
changes=json.loads((R/'qa/change_log.json').read_text(encoding='utf-8'))
def replace(rel,a,b):
    p=R/rel;t=p.read_text(encoding='utf-8');assert a in t
    p.write_text(t.replace(a,b),encoding='utf-8')
    changes.append(dict(file=rel,old=a,new=b,reason='明确百分比为路径内比值的跨路径均值，避免与均值之比混淆'))
replace('manuscript/manuscript.tex',r'On ca-GrQc, default PageRank-4k changes from 5.61\% higher to 5.07\% lower mean incremental spread relative to the same-budget full reference.',r'On ca-GrQc, the mean pathwise relative incremental-spread difference for default PageRank-4k changes from $+5.61$\% to $-5.07$\% against the same-budget full reference.')
replace('chinese/manuscript/manuscript_zh.tex',r'在 ca-GrQc 上，默认 PageRank-4k 相对同预算全候选参照的平均增量传播量，从高于参照 5.61\% 转为低于参照 5.07\%。',r'在 ca-GrQc 上，默认 PageRank-4k 相对同预算全候选参照的逐路径相对增量传播差异，取跨路径均值后由 $+5.61$\% 转为 $-5.07$\%。')
copied={}
for source,target in [
    (P/'structural-language-revision-20261027/EXTERNAL_REPRODUCE_INHERITED.md',R/'EXTERNAL_REPRODUCE_INHERITED.md'),
    (P/'structural-language-revision-20261027/REPRODUCE.md',R/'evidence/HISTORICAL_REPRODUCE_INHERITED.md'),
    (P/'structural-language-revision-20261027/src/reproduce.py',R/'src/reproduce.py'),
    (P/'structural-language-revision-20261027/src/integrate_historical.py',R/'src/integrate_historical.py'),
    (P/'requirements.txt',R/'requirements.txt')]:
    shutil.copy2(source,target)
    digest=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
    assert digest(source)==digest(target)
    copied[str(target.relative_to(R))]={'source':str(source),'sha256':digest(source),'executed_this_revision':False}
(R/'qa/inherited_reproduction_sources.json').write_text(json.dumps(copied,ensure_ascii=False,indent=2),encoding='utf-8')
p=R/'REPRODUCE.md'
p.write_text(p.read_text(encoding='utf-8')+r'''

## 既有实验及历史汇总的复现入口（本轮未执行）

EXTERNAL_REPRODUCE_INHERITED.md 原样保留外部实验的输入检查、环境与隔离复验说明。文内命令以外部冻结包根目录为工作目录，仍指向已存在的 narrative-revision-20261027/src/reproduce.py。本版 src/reproduce.py 为已有入口的逐字节副本；不是本轮检查脚本，不要把执行它算作文稿编译。参数 --base 指外部冻结包根目录，--output 必须为新目录，--replay 模式及其执行范围见继承指南。

历史汇总指令及统计口径见 evidence/HISTORICAL_REPRODUCE_INHERITED.md。该指南中的历史整合脚本位于 ../historical-evidence-revision-20261027/src/integrate_historical.py；本版也保留其已有副本 src/integrate_historical.py。它读取已保存数组而不运行传播模拟，但会生成表图，未来需要再生成时应在独立工作副本中操作，随后恢复本轮已编辑的表头和图注。不能让历史生成器覆盖当前正式稿。

这些入口、requirements.txt 和说明文件的原始路径与SHA-256见qa/inherited_reproduction_sources.json。复制不表示本轮再次执行复现；本轮只运行src/verify_revision.py中的文稿检查。
''',encoding='utf-8')
p=R/'revision_report_zh.md'
p.write_text(p.read_text(encoding='utf-8')+'''

最终核读还补充两点：摘要明确百分比是逐路径相对差异的跨路径均值；为补齐补充材料所指的复现文件，原样复制已有指南、依赖清单和复现/历史汇总入口，记录来源哈希但没有执行。原入口与已有算法均未修改。
''',encoding='utf-8')
(R/'qa/change_log.json').write_text(json.dumps(changes,ensure_ascii=False,indent=2),encoding='utf-8')
for rel in ['manuscript/manuscript.tex','chinese/manuscript/manuscript_zh.tex']:
    old=P/'contribution-action-revision-20261028'/rel;p=R/rel
    name=rel.replace('/','_')+'.diff'
    (R/'qa'/name).write_text(''.join(difflib.unified_diff(old.read_text(encoding='utf-8').splitlines(True),p.read_text(encoding='utf-8').splitlines(True),fromfile=str(old),tofile=str(p))),encoding='utf-8')
print('Editorial clarification and inherited reproduction files saved; no experiments executed.')
