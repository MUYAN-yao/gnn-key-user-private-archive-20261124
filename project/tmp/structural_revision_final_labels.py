from pathlib import Path
R=Path(r'D:\校创\基于GNN的关键用户识别\submission\computing-external-validation-20261015\structural-language-revision-20261027')
for name in ['supp_tables.tex','precision_table.tex']:
    p=R/'manuscript'/name;s=p.read_text(encoding='utf-8')
    for a,b in [('Degree 4k','Degree-4k'),('Degree 5\\%','Degree-5\\%'),('PageRank 4k','PageRank-4k'),('PageRank 5\\%','PageRank-5\\%'),('History 4k','Weighted-4k'),('History 5\\%','Weighted-5\\%')]:s=s.replace(a,b)
    s=s.replace('versus frozen full greedy','versus the frozen full-candidate reference')
    s=s.replace('SD is across path mean differences.', 'Total is total spread (nodes); $\\Delta$ is restricted minus full spread (nodes); SD is across path mean differences.')
    p.write_text(s,encoding='utf-8')
p=R/'manuscript/manuscript.tex';s=p.read_text(encoding='utf-8')
s=s.replace('Default and tighter tolerances are $10^{-6}$ and $10^{-12}$, with unchanged candidate membership at $10^{-14}$.', 'The plotted labels Default and Strict denote tolerances $10^{-6}$ and $10^{-12}$; candidate membership is unchanged between $10^{-12}$ and $10^{-14}$.')
p.write_text(s,encoding='utf-8')
p=R/'src/verify_revision.py';s=p.read_text(encoding='utf-8')
old="    checks['unchanged_numeric_tables'][n] = re.findall(r'-?\\d+(?:\\.\\d+)?',a)==re.findall(r'-?\\d+(?:\\.\\d+)?',b)"
new="""    # Method-name hyphens are punctuation, not negative numerical data.
    for method in ('Degree', 'PageRank', 'Weighted'):
        a=a.replace(method+'-', method+' '); b=b.replace(method+'-', method+' ')
    checks['unchanged_numeric_tables'][n] = re.findall(r'-?\\d+(?:\\.\\d+)?',a)==re.findall(r'-?\\d+(?:\\.\\d+)?',b)"""
assert old in s;s=s.replace(old,new);p.write_text(s,encoding='utf-8')
print('Method labels harmonized; numerical cells unaffected.')
