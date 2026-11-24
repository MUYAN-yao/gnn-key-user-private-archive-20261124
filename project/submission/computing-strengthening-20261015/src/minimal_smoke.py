"""Portable, fast semantic smoke check; no empirical data required."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'snapshot'))
import engine
import numpy as np
engine.warmup()
graph={'a':('b',),'b':('c',),'c':()}
ip,tg,src=engine.csr(sorted(graph),graph)
ids=np.asarray([5],dtype=np.uint64)
step=engine.make_worlds(ids,src,tg,.5,2,False)
assert engine.evaluate(ip,tg,step,np.asarray([0],dtype=np.int64),2)[0]==3
assert engine.evaluate(ip,tg,step,np.asarray([0,1],dtype=np.int64),2)[0]==2
edge=engine.make_worlds(ids,src,tg,1.,2,True)
assert engine.evaluate(ip,tg,edge,np.asarray([0],dtype=np.int64),2)[0]==3
a,_=engine.greedy(ip,tg,edge,np.asarray([0,1,2],dtype=np.int64),1,2)
b,_=engine.greedy(ip,tg,edge,np.asarray([2,0,1],dtype=np.int64),1,2)
assert a.tolist()==b.tolist()==[0]
print('PASS: seed count, finite horizon, step-coupling counterexample, fixed-edge reachability, full-pool consistency')
