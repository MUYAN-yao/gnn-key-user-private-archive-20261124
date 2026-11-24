"""Exhaustive finite-world IC; compiled acceleration, no pruning or CELF.

Node indices follow lexicographic original IDs. The step coupling reproduces
the archived v7/v10 hash. The edge coupling is a separately labelled control.
"""
from __future__ import annotations
import hashlib, json, time
from pathlib import Path
import numpy as np
import pandas as pd
import networkx as nx
from numba import njit

@njit(cache=True)
def uniform(world, step, source, target):
    value = ((world + np.uint64(0x9E3779B97F4A7C15))
             ^ (np.uint64(step + 1) * np.uint64(0xBF58476D1CE6E5B9))
             ^ (np.uint64(source + 1) * np.uint64(0x94D049BB133111EB))
             ^ (np.uint64(target + 1) * np.uint64(0xBF58476D1CE6E93)))
    value = (value ^ (value >> np.uint64(30))) * np.uint64(0xBF58476D1CE6E5B9)
    value = (value ^ (value >> np.uint64(27))) * np.uint64(0x94D049BB133111EB)
    value ^= value >> np.uint64(31)
    return (value >> np.uint64(11)) * (1.0 / (1 << 53))

@njit(cache=True)
def make_worlds(ids, sources, targets, probability, horizon, edge_coupled):
    depth = 1 if edge_coupled else max(1, horizon)
    out = np.empty((len(ids), depth, len(sources)), dtype=np.bool_)
    for w in range(len(ids)):
        for step in range(depth):
            for e in range(len(sources)):
                out[w, step, e] = uniform(ids[w], step, sources[e], targets[e]) < probability
    return out

@njit(cache=True)
def spread_one(indptr, targets, opened, seeds, horizon):
    n = len(indptr)-1
    active = np.zeros(n, dtype=np.bool_)
    frontier = np.empty(n, dtype=np.int64)
    following = np.empty(n, dtype=np.int64)
    size = 0
    for s in seeds:
        if not active[s]:
            active[s] = True
            frontier[size] = s
            size += 1
    count = size
    for step in range(horizon):
        nxt = 0
        t = 0 if opened.shape[0] == 1 else step
        for i in range(size):
            u = frontier[i]
            for e in range(indptr[u],indptr[u+1]):
                v = targets[e]
                if not active[v] and opened[t,e]:
                    active[v] = True
                    following[nxt] = v
                    nxt += 1
        count += nxt
        if nxt == 0:
            break
        tmp = frontier
        frontier = following
        following = tmp
        size = nxt
    return count

@njit(cache=True)
def evaluate(indptr, targets, worlds, seeds, horizon):
    out = np.empty(len(worlds),dtype=np.int64)
    for w in range(len(worlds)):
        out[w] = spread_one(indptr,targets,worlds[w],seeds,horizon)
    return out

@njit(cache=True)
def greedy(indptr, targets, worlds, candidates, k, horizon):
    # For W<=5120, different integer totals are separated by >1e-6 in
    # mean spread, so exact integer maximisation matches v7 micro rounding.
    candidates = np.sort(candidates)
    selected = np.empty(k,dtype=np.int64)
    totals = np.empty((k,len(candidates)),dtype=np.int64)
    for r in range(k):
        best = -1
        winner = -1
        for j in range(len(candidates)):
            node = candidates[j]
            used = False
            for q in range(r):
                if selected[q] == node:
                    used = True
            if used:
                totals[r,j] = -1
                continue
            selected[r] = node
            total = 0
            for w in range(len(worlds)):
                total += spread_one(indptr,targets,worlds[w],selected[:r+1],horizon)
            totals[r,j] = total
            if total > best:
                best = total
                winner = node
        selected[r] = winner
    return selected, totals

def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def world_ids(dataset,path,family,count,namespace='computing-extension-20261015-v1'):
    return np.asarray([int.from_bytes(hashlib.sha256(f'{namespace}|{dataset}|{path}|{family}|{i}'.encode()).digest()[:8],'big') & ((1<<63)-1) for i in range(count)],dtype=np.uint64)

def csr(nodes, adjacency):
    index = {node:i for i,node in enumerate(nodes)}
    lists = [sorted(index[t] for t in adjacency[node]) for node in nodes]
    indptr = np.asarray([0]+list(np.cumsum([len(v) for v in lists])),dtype=np.int64)
    targets = np.asarray([t for v in lists for t in v],dtype=np.int64)
    sources = np.repeat(np.arange(len(nodes),dtype=np.int64),np.diff(indptr))
    return indptr,targets,sources

def load_graph(project,dataset):
    started = time.perf_counter()
    if dataset.startswith('synthetic_'):
        if dataset == 'synthetic_ba2000':
            graph = nx.barabasi_albert_graph(2000,3,seed=20261015)
        elif dataset == 'synthetic_sbm2000':
            graph = nx.stochastic_block_model([500]*4,[[.012 if i==j else .0005 for j in range(4)] for i in range(4)],seed=20261015)
        else:
            raise ValueError(dataset)
        adjacency = {str(n):tuple(str(v) for v in graph[n]) for n in graph}
        nodes = sorted(adjacency)
        weighted = {n:len(adjacency[n]) for n in nodes}
        hashes = {}
        cutoff = None
        groups = None
        kind = 'synthetic; no independent empirical-network claim'
    else:
        directory = Path(project)/'data/processed/sociopatterns-confirmation-v0_1'/dataset
        edges = pd.read_csv(directory/'edges.csv',dtype={'src':str,'dst':str})
        edges['timestamp'] = pd.to_datetime(edges.timestamp,utc=True)
        timestamps = sorted(edges.timestamp.unique())
        cutoff = timestamps[max(1,int(len(timestamps)*.65))-1]
        history = edges[(edges.timestamp<=cutoff)&(edges.src!=edges.dst)]
        pairs = history.groupby(['src','dst'],sort=True).size()
        nodes = sorted(set(history.src)|set(history.dst))
        adjacency = {n:[] for n in nodes}
        for (u,v),_ in pairs.items():
            adjacency[u].append(v)
        weighted = history.groupby('src').size().to_dict()
        hashes = {name:digest(directory/name) for name in ['nodes.csv','edges.csv','cascades.csv','data_card.json']}
        cutoff = cutoff.isoformat()
        groups = len(timestamps)
        kind = 'historical contact-derived; simulated diffusion only'
    indptr,targets,sources = csr(nodes,adjacency)
    preparation = time.perf_counter()-started
    rankings = {}
    rank_times = {}
    for method in ['weighted','degree','pagerank']:
        t = time.perf_counter()
        if method == 'weighted':
            score = weighted
        elif method == 'degree':
            score = {n:len(adjacency[n]) for n in nodes}
        else:
            score = nx.pagerank(nx.DiGraph(adjacency),weight=None)
        order = sorted(range(len(nodes)),key=lambda i:(-float(score.get(nodes[i],0)),nodes[i]))
        rankings[method] = np.asarray(order,dtype=np.int64)
        rank_times[method] = time.perf_counter()-t
    return dict(nodes=nodes,indptr=indptr,targets=targets,sources=sources,rankings=rankings,
        metadata=dict(n=len(nodes),m=len(targets),dataset=dataset,kind=kind,history_cutoff=cutoff,timestamp_group_count=groups,input_sha256=hashes,graph_sha256=hashlib.sha256(indptr.tobytes()+targets.tobytes()+'|'.join(nodes).encode()).hexdigest()),
        preparation_seconds=preparation,ranking_seconds=rank_times)

def warmup():
    g=np.asarray([0,1,1],dtype=np.int64);t=np.asarray([1],dtype=np.int64)
    w=make_worlds(np.asarray([1,2],dtype=np.uint64),np.asarray([0],dtype=np.int64),t,.1,3,False)
    greedy(g,t,w,np.asarray([0,1],dtype=np.int64),1,3)
    evaluate(g,t,w,np.asarray([0],dtype=np.int64),3)
