import pandas as p
a=p.read_csv('pagerank.csv')
print(a[a.m==20][['graph','tol','residual','iterations','gap','certified','replacements']].to_string(index=False))
r=p.read_csv('runs.csv')
print(r[r.arm.str.startswith('pr_')][['graph','arm','seeds','spread','delta_reference','delta_se']].to_string(index=False))
