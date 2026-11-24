import React, { useEffect, useMemo, useRef, useState } from "react";
import { createRoot } from "react-dom/client";
import * as d3 from "d3";
import * as echarts from "echarts";
import "./styles.css";

const API = import.meta.env.VITE_API_URL ?? "http://127.0.0.1:8000";
type Node = { node_id: string; score: number; community: number; is_seed: boolean };
type Edge = { source: string; target: string; probability: number };
type Result = { result: { top_k: string[]; mean_spread: number; spread_std: number; robust_objective: number; community_coverage: number }; calibration: Record<string, number | string | null>; graph: { nodes: Node[]; edges: Edge[] }; runtime_seconds: number; reproducibility: { backend: string; training_cutoff: string } };

function NetworkBand({ result }: { result: Result }) {
  const ref = useRef<SVGSVGElement>(null);
  useEffect(() => {
    if (!ref.current) return;
    const svg = d3.select(ref.current); svg.selectAll("*").remove();
    const width = ref.current.clientWidth || 760, height = 330;
    svg.attr("viewBox", `0 0 ${width} ${height}`);
    const colors = ["#1d5d83", "#d66a48", "#4b8f6d", "#7953a4", "#b88431"];
    const nodes = result.graph.nodes.map(n => ({ ...n }));
    const links = result.graph.edges.map(e => ({ ...e }));
    const sim = d3.forceSimulation(nodes as d3.SimulationNodeDatum[]).force("link", d3.forceLink(links as d3.SimulationLinkDatum<d3.SimulationNodeDatum>[]).id((d: any) => d.node_id).distance(80)).force("charge", d3.forceManyBody().strength(-270)).force("center", d3.forceCenter(width / 2, height / 2)).stop();
    for (let i = 0; i < 190; i++) sim.tick();
    svg.append("g").selectAll("line").data(links).join("line").attr("x1", (d: any) => d.source.x).attr("y1", (d: any) => d.source.y).attr("x2", (d: any) => d.target.x).attr("y2", (d: any) => d.target.y).attr("stroke", "#9fb2bb").attr("stroke-opacity", d => 0.18 + d.probability * .55).attr("stroke-width", d => 1 + d.probability * 2);
    const group = svg.append("g").selectAll("g").data(nodes).join("g").attr("transform", (d: any) => `translate(${d.x},${d.y})`);
    group.append("circle").attr("r", d => d.is_seed ? 12 : 6 + d.score * 7).attr("fill", d => colors[d.community % colors.length]).attr("stroke", d => d.is_seed ? "#1b2432" : "#f5f6f1").attr("stroke-width", d => d.is_seed ? 4 : 1.5);
    group.filter(d => d.is_seed).append("circle").attr("r", 17).attr("fill", "none").attr("stroke", "#d66a48").attr("stroke-width", 1.5).attr("stroke-dasharray", "3 3");
    group.append("text").text(d => d.node_id).attr("y", 25).attr("text-anchor", "middle").attr("fill", "#33434b").attr("font-size", 11).attr("font-family", "ui-monospace, monospace");
  }, [result]);
  return <svg className="network" ref={ref} aria-label="关键用户传播网络" />;
}

function ScoreChart({ result }: { result: Result }) {
  const ref = useRef<HTMLDivElement>(null);
  useEffect(() => {
    if (!ref.current) return;
    const chart = echarts.init(ref.current);
    const nodes = result.graph.nodes.slice(0, 8).reverse();
    chart.setOption({ animationDuration: 600, grid: { left: 55, right: 24, top: 12, bottom: 16 }, xAxis: { type: "value", max: 1, axisLabel: { color: "#63737d" }, splitLine: { lineStyle: { color: "#dbe3e3" } } }, yAxis: { type: "category", data: nodes.map(n => n.node_id), axisLabel: { color: "#33434b", fontFamily: "monospace" } }, series: [{ type: "bar", data: nodes.map(n => ({ value: n.score, itemStyle: { color: n.is_seed ? "#d66a48" : "#1d5d83" } })), barWidth: 13, showBackground: true, backgroundStyle: { color: "#edf1ee" } }], tooltip: { trigger: "axis" } });
    const resize = () => chart.resize(); window.addEventListener("resize", resize); return () => { window.removeEventListener("resize", resize); chart.dispose(); };
  }, [result]);
  return <div className="chart" ref={ref} />;
}

function App() {
  const [file, setFile] = useState<File | null>(null), [count, setCount] = useState(3), [status, setStatus] = useState("上传 ZIP 数据包以开始分析"), [result, setResult] = useState<Result | null>(null);
  const submit = async () => {
    if (!file) return setStatus("请选择包含三份 CSV 的 ZIP 文件。");
    setStatus("正在核验数据结构…"); const form = new FormData(); form.append("file", file);
    try { const upload = await fetch(`${API}/datasets`, { method: "POST", body: form }); if (!upload.ok) throw new Error((await upload.json()).detail); const dataset = await upload.json();
      setStatus(`数据已核验：${dataset.nodes} 个用户，正在运行稳健搜索…`); const analysis = await fetch(`${API}/analyses`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ dataset_id: dataset.dataset_id, seed_count: count, epochs: 40, ants: 12, iterations: 7, simulations: 20 }) }); const task = await analysis.json();
      for (let i = 0; i < 120; i++) { await new Promise(r => setTimeout(r, 800)); const current = await (await fetch(`${API}/analyses/${task.analysis_id}`)).json(); if (current.status === "completed") { const data = await (await fetch(`${API}/analyses/${task.analysis_id}/result`)).json(); setResult(data); return setStatus("分析完成：时间带呈现训练窗口内的稳健种子集。"); } if (current.status === "failed") throw new Error(current.error); }
      throw new Error("任务超时，请缩小数据集或降低仿真次数。");
    } catch (error) { setStatus(error instanceof Error ? error.message : "请求失败"); }
  };
  return <main><header><div><p className="eyebrow">ROBUST INFLUENCE LAB / V0.1</p><h1>让传播选择<br/><em>经得起时间检验。</em></h1></div><p className="lede">从历史互动学习边激活概率，以不确定性惩罚和跨社区覆盖共同选择 Top-K 种子用户。</p></header>
    <section className="control-strip"><label className="upload"><span>输入数据包</span><input type="file" accept=".zip" onChange={e => setFile(e.target.files?.[0] ?? null)} />{file?.name ?? "选择 ZIP"}</label><label><span>种子数量 K</span><input type="number" value={count} min="1" max="20" onChange={e => setCount(Number(e.target.value))} /></label><button onClick={submit}>运行稳健分析 <b>→</b></button><p>{status}</p></section>
    {!result ? <section className="empty"><div className="ribbon">T₀　历史互动　——　概率校准　——　稳健搜索　——　跨社区扩散　T₊</div><p>结果将显示关键节点、社区分布与传播覆盖置信区间。</p></section> : <><section className="metrics"><article><span>稳健覆盖</span><strong>{result.result.mean_spread.toFixed(1)}</strong><small>± {result.result.spread_std.toFixed(2)} 个节点</small></article><article><span>跨社区触达</span><strong>{result.result.community_coverage}</strong><small>种子集覆盖的社区数</small></article><article><span>下置信界目标</span><strong>{result.result.robust_objective.toFixed(2)}</strong><small>{result.reproducibility.backend}</small></article><article><span>运行时长</span><strong>{result.runtime_seconds.toFixed(2)}s</strong><small>截止至 {result.reproducibility.training_cutoff.slice(0, 10)}</small></article></section><section className="content"><article className="panel map"><div className="panel-head"><div><p className="eyebrow">COMMUNITY BAND</p><h2>传播网络与关键种子</h2></div><p>虚线环为 Top-K；颜色表示社区。</p></div><NetworkBand result={result} /></article><article className="panel ranking"><div className="panel-head"><div><p className="eyebrow">INFLUENCE PRIOR</p><h2>节点影响力先验</h2></div></div><ScoreChart result={result} /></article></section><section className="seeds"><p className="eyebrow">SELECTED SEEDS</p>{result.result.top_k.map((node, i) => <div key={node}><span>0{i + 1}</span><b>{node}</b><small>稳健传播候选</small></div>)}</section></>}</main>;
}
createRoot(document.getElementById("root")!).render(<App />);
