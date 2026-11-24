import sys
print('before', flush=True)
import matplotlib
print('matplotlib', matplotlib.__version__, flush=True)
matplotlib.use('Agg')
print('backend-set', flush=True)
import matplotlib.pyplot as p
print('pyplot', flush=True)
f,a=p.subplots()
print('subplots', flush=True)
a.plot([1,2])
print('plot', flush=True)
f.savefig('tmp/agg-smoke.png')
print('saved', flush=True)
