from pathlib import Path
p=Path('analyze.py');s=p.read_text(encoding='utf-8-sig');a=s.index(' for arm,gg in realtrans.groupby');b=s.index(" fig.savefig(figdir/'models_utility.png'",a)
s=s[:a]+''' forest=realtrans[realtrans.path==4101].copy().reset_index(drop=True)
 for arm,gg in forest.groupby('arm'):
  axes[1].errorbar(gg.delta,gg.index,xerr=1.96*gg.se,fmt='o',label=arm,alpha=.8)
 labels=[f'{r.graph} {r.arm} {r.W_from}->{r.W_to}' for r in forest.itertuples()]
 axes[1].set_yticks(range(len(forest)),labels,fontsize=6)
 axes[1].axvline(0,c='black',lw=.8);axes[1].set(xlabel='Spread change with conditional 95% CI',title='Each arm, path 4101');axes[1].legend(fontsize=7)
'''+s[b:];p.write_text(s,encoding='utf-8')
