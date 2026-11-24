"""Exact fixed-world greedy search and conservative partial-world pruning.

This module implements the independent v7 numerical contract.  It is
deliberately separate from the older NumPy/``round`` v6 scorer: completed
scores are compared as mathematical half-even rounded micro-units, while a
partial score is used only to *exclude* a candidate when its conservative
integer upper bound is strictly below the incumbent.

The guarantee is limited to a finite, supplied list of common random worlds.
It is not a submodularity, expectation, or real-world diffusion guarantee.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from fractions import Fraction
from math import isqrt
from typing import Callable, Iterable, Mapping, Sequence


MICRO = 1_000_000
MASK64 = (1 << 64) - 1
Node = str
Graph = Mapping[Node, Sequence[Node]]
ProbabilityMap = Mapping[tuple[Node, Node], float]


class SearchLimitExceeded(RuntimeError):
    """Raised before a requested exact-search budget is exceeded."""


def canonical_nodes(nodes: Iterable[Node]) -> tuple[Node, ...]:
    return tuple(sorted({str(node) for node in nodes}))


def round_half_even_fraction(value: Fraction, scale: int = MICRO) -> int:
    """Round a rational number to integer ``scale`` units, ties to even."""
    if scale <= 0:
        raise ValueError("scale must be positive")
    numerator = value.numerator * scale
    denominator = value.denominator
    lower, remainder = divmod(numerator, denominator)
    comparison = 2 * remainder - denominator
    if comparison < 0:
        return lower
    if comparison > 0:
        return lower + 1
    return lower if lower % 2 == 0 else lower + 1


def ceil_fraction(value: Fraction) -> int:
    return -((-value.numerator) // value.denominator)


def _sqrt_interval(value: int, max_decimal_places: int = 160) -> tuple[Fraction, Fraction]:
    """Return a rational interval containing ``sqrt(value)``.

    The lower endpoint is inclusive; the upper endpoint is inclusive for a
    perfect square and otherwise is a strict but safe upper endpoint.
    """
    if value < 0:
        raise ValueError("square-root input must be non-negative")
    root = isqrt(value)
    if root * root == value:
        exact = Fraction(root, 1)
        return exact, exact
    for places in range(1, max_decimal_places + 1):
        unit = 10**places
        lower_integer = isqrt(value * unit * unit)
        lower = Fraction(lower_integer, unit)
        upper = Fraction(lower_integer + 1, unit)
        if lower * lower <= value <= upper * upper:
            return lower, upper
    raise RuntimeError("could not enclose a square root at the configured precision")


def exact_score_micro(
    world_spreads: Sequence[int],
    coverage: int,
    *,
    risk_lambda: Fraction = Fraction(7, 20),
    community_weight: Fraction = Fraction(1, 4),
) -> int:
    """Return the v7 completed objective rounded to a half-even micro-unit."""
    if not world_spreads:
        raise ValueError("at least one fixed world is required")
    if risk_lambda < 0:
        raise ValueError("risk_lambda must be non-negative")
    if any(value < 0 for value in world_spreads):
        raise ValueError("world spreads must be non-negative activation counts")
    width = len(world_spreads)
    total = sum(world_spreads)
    squared_total = sum(value * value for value in world_spreads)
    variance_numerator = width * squared_total - total * total
    baseline = Fraction(total, width) + community_weight * coverage
    if risk_lambda == 0 or variance_numerator == 0:
        return round_half_even_fraction(baseline)

    lower_root, upper_root = _sqrt_interval(variance_numerator)
    # Larger root gives a lower score.  Both endpoints must round to the same
    # micro-unit before a numerical result is admitted.
    lower_score = baseline - risk_lambda * upper_root / width
    upper_score = baseline - risk_lambda * lower_root / width
    lower_micro = round_half_even_fraction(lower_score)
    upper_micro = round_half_even_fraction(upper_score)
    if lower_micro != upper_micro:
        # A non-square irrational cannot remain exactly on a rational half-unit
        # boundary.  Refine rather than silently choosing a floating result.
        for places in range(1, 321):
            unit = 10**places
            lower_integer = isqrt(variance_numerator * unit * unit)
            lower = Fraction(lower_integer, unit)
            upper = Fraction(lower_integer + 1, unit)
            lower_micro = round_half_even_fraction(baseline - risk_lambda * upper / width)
            upper_micro = round_half_even_fraction(baseline - risk_lambda * lower / width)
            if lower_micro == upper_micro:
                return lower_micro
        raise RuntimeError("score rounding interval did not converge")
    return lower_micro


def partial_upper_micro(
    observed_spreads: Sequence[int],
    total_worlds: int,
    structural_upper: int,
    coverage: int,
    *,
    risk_lambda: Fraction = Fraction(7, 20),
    community_weight: Fraction = Fraction(1, 4),
    use_risk_lower_bound: bool = True,
    decimal_places: int = 32,
) -> int:
    """Ceiling micro-unit upper bound for an incompletely evaluated candidate."""
    if total_worlds <= 0 or structural_upper < 0:
        raise ValueError("world count and structural upper must be positive/non-negative")
    if len(observed_spreads) > total_worlds:
        raise ValueError("more observed worlds than configured worlds")
    if risk_lambda < 0:
        raise ValueError("risk_lambda must be non-negative")
    if any(value < 0 or value > structural_upper for value in observed_spreads):
        raise ValueError("observed spread is outside the structural range")
    observed = len(observed_spreads)
    total = sum(observed_spreads)
    mean_upper = Fraction(total + (total_worlds - observed) * structural_upper, total_worlds)
    risk_lower = Fraction(0, 1)
    if observed and use_risk_lower_bound and risk_lambda:
        squares = sum(value * value for value in observed_spreads)
        dispersion_numerator = observed * squares - total * total
        denominator = observed * total_worlds
        unit = 10**decimal_places
        lower_root = isqrt((dispersion_numerator * unit * unit) // denominator)
        risk_lower = Fraction(lower_root, unit)
    upper = mean_upper - risk_lambda * risk_lower + community_weight * coverage
    return ceil_fraction(upper * MICRO)


def deterministic_uniform(world: int, step: int, source_code: int, target_code: int) -> float:
    """Process-independent edge-time uniform, matching the prior IC semantics."""
    value = (
        (world + 0x9E3779B97F4A7C15)
        ^ ((step + 1) * 0xBF58476D1CE6E5B9)
        ^ ((source_code + 1) * 0x94D049BB133111EB)
        ^ ((target_code + 1) * 0xBF58476D1CE6E93)
    ) & MASK64
    value = ((value ^ (value >> 30)) * 0xBF58476D1CE6E5B9) & MASK64
    value = ((value ^ (value >> 27)) * 0x94D049BB133111EB) & MASK64
    value ^= value >> 31
    return (value >> 11) * (1.0 / (1 << 53))


def simulate_ic_common_world(
    graph: Graph,
    seeds: Iterable[Node],
    probabilities: ProbabilityMap,
    horizon: int,
    world: int,
    codes: Mapping[Node, int],
) -> int:
    """Run finite-horizon independent cascade on one deterministic world."""
    if horizon < 0:
        raise ValueError("horizon must be non-negative")
    active = set(canonical_nodes(seeds))
    frontier = set(active)
    for step in range(horizon):
        next_frontier: set[Node] = set()
        for source in sorted(frontier, key=codes.__getitem__):
            for target in sorted(graph.get(source, ()), key=codes.__getitem__):
                if target in active:
                    continue
                probability = probabilities[(source, target)]
                if deterministic_uniform(world, step, codes[source], codes[target]) < probability:
                    active.add(target)
                    next_frontier.add(target)
        frontier = next_frontier
        if not frontier:
            break
    return len(active)


def reachable_total_upper_bound(graph: Graph, seeds: Iterable[Node], horizon: int) -> int:
    """Size of the directed <=h-hop union reachable from the supplied seeds."""
    if horizon < 0:
        raise ValueError("horizon must be non-negative")
    reached = set(canonical_nodes(seeds))
    frontier = set(reached)
    for _ in range(horizon):
        next_frontier = {target for source in frontier for target in graph.get(source, ()) if target not in reached}
        reached.update(next_frontier)
        frontier = next_frontier
        if not frontier:
            break
    return len(reached)


@dataclass
class SimulationCache:
    """Per-arm cache; callers create a fresh instance for every method arm."""

    values: dict[tuple[tuple[Node, ...], int], int] = field(default_factory=dict)
    hits: int = 0
    misses: int = 0

    def clear(self) -> None:
        self.values.clear()
        self.hits = 0
        self.misses = 0


@dataclass
class CandidateEvaluator:
    graph: Graph
    probabilities: ProbabilityMap
    horizon: int
    codes: Mapping[Node, int]
    cache: SimulationCache
    max_world_evaluations: int | None = None
    calls: int = 0

    def values(self, seeds: Iterable[Node], worlds: Sequence[int]) -> list[int]:
        key_seeds = canonical_nodes(seeds)
        output: list[int] = []
        for world in worlds:
            key = (key_seeds, int(world))
            if key in self.cache.values:
                self.cache.hits += 1
                output.append(self.cache.values[key])
                continue
            if self.max_world_evaluations is not None and self.calls >= self.max_world_evaluations:
                raise SearchLimitExceeded("candidate-world evaluation limit reached before certificate")
            value = simulate_ic_common_world(
                self.graph, key_seeds, self.probabilities, self.horizon, int(world), self.codes
            )
            self.cache.values[key] = value
            self.cache.misses += 1
            self.calls += 1
            output.append(value)
        return output


def _coverage(communities: Mapping[Node, str], seeds: Iterable[Node]) -> int:
    return len({communities[node] for node in canonical_nodes(seeds)})


def _better(left: tuple[int, Node], right: tuple[int, Node] | None) -> bool:
    return right is None or left[0] > right[0] or (left[0] == right[0] and left[1] < right[1])


def full_greedy(
    graph: Graph,
    probabilities: ProbabilityMap,
    communities: Mapping[Node, str],
    worlds: Sequence[int],
    *,
    horizon: int,
    seed_count: int,
    codes: Mapping[Node, int] | None = None,
    risk_lambda: Fraction = Fraction(7, 20),
    community_weight: Fraction = Fraction(1, 4),
    prefix: Sequence[Node] = (),
    candidate_universe: Sequence[Node] | None = None,
    max_world_evaluations: int | None = None,
) -> dict:
    """Reference greedy scan under the finite-world v7 objective."""
    graph_nodes = canonical_nodes(graph)
    nodes = canonical_nodes(candidate_universe) if candidate_universe is not None else graph_nodes
    selected = list(canonical_nodes(prefix))
    if not nodes or any(node not in graph_nodes for node in nodes):
        raise ValueError("candidate universe must be a non-empty graph-node subset")
    if len(nodes) < seed_count:
        raise ValueError("candidate universe is smaller than seed_count")
    if len(selected) > seed_count or any(node not in nodes for node in selected):
        raise ValueError("invalid selected prefix")
    codes = codes or {node: index for index, node in enumerate(graph_nodes)}
    evaluator = CandidateEvaluator(graph, probabilities, horizon, codes, SimulationCache(), max_world_evaluations)
    rounds: list[dict] = []
    while len(selected) < seed_count:
        incumbent: tuple[int, Node] | None = None
        scored: dict[Node, int] = {}
        for node in nodes:
            if node in selected:
                continue
            trial = selected + [node]
            score = exact_score_micro(
                evaluator.values(trial, worlds), _coverage(communities, trial),
                risk_lambda=risk_lambda, community_weight=community_weight,
            )
            scored[node] = score
            if _better((score, node), incumbent):
                incumbent = (score, node)
        assert incumbent is not None
        selected.append(incumbent[1])
        rounds.append({"winner": incumbent[1], "score_micro": incumbent[0], "scores": scored})
    return {"selected": selected, "rounds": rounds, "cache": evaluator.cache, "world_evaluations": evaluator.calls}


def risk_bound_greedy(
    graph: Graph,
    probabilities: ProbabilityMap,
    communities: Mapping[Node, str],
    worlds: Sequence[int],
    *,
    horizon: int,
    seed_count: int,
    ranking: Sequence[Node] | None = None,
    initial_count: int | None = None,
    batch_size: int = 4,
    codes: Mapping[Node, int] | None = None,
    risk_lambda: Fraction = Fraction(7, 20),
    community_weight: Fraction = Fraction(1, 4),
    use_risk_lower_bound: bool = True,
    prefix: Sequence[Node] = (),
    max_world_evaluations: int | None = None,
) -> dict:
    """Exact greedy scan using a complete initial pool and safe promotions.

    ``ranking`` changes only which candidates establish the incumbent first.
    Every remaining candidate is either fully evaluated or retained only after
    its conservative upper micro-unit is strictly below that incumbent.
    """
    if batch_size <= 0:
        raise ValueError("batch_size must be positive")
    nodes = canonical_nodes(graph)
    selected = list(canonical_nodes(prefix))
    if len(selected) > seed_count or any(node not in nodes for node in selected):
        raise ValueError("invalid selected prefix")
    codes = codes or {node: index for index, node in enumerate(nodes)}
    rank_order = [str(node) for node in (ranking or nodes)]
    if len(rank_order) != len(nodes) or len(set(rank_order)) != len(nodes) or set(rank_order) != set(nodes):
        raise ValueError("ranking must contain every graph node exactly once")
    evaluator = CandidateEvaluator(graph, probabilities, horizon, codes, SimulationCache(), max_world_evaluations)
    rounds: list[dict] = []
    while len(selected) < seed_count:
        available = [node for node in nodes if node not in selected]
        count = min(len(available), initial_count if initial_count is not None else 2 * seed_count)
        initial = [node for node in rank_order if node in available][:count]
        incumbent: tuple[int, Node] | None = None
        statuses: dict[Node, dict] = {}
        for node in initial:
            trial = selected + [node]
            values = evaluator.values(trial, worlds)
            score = exact_score_micro(values, _coverage(communities, trial), risk_lambda=risk_lambda, community_weight=community_weight)
            statuses[node] = {"status": "initial_full", "observed_worlds": len(values), "score_micro": score}
            if _better((score, node), incumbent):
                incumbent = (score, node)
        assert incumbent is not None
        pending = [node for node in available if node not in initial]
        pending.sort(key=lambda node: (-reachable_total_upper_bound(graph, selected + [node], horizon), node))
        for node in pending:
            trial = selected + [node]
            structural_upper = reachable_total_upper_bound(graph, trial, horizon)
            values: list[int] = []
            while True:
                bound = partial_upper_micro(
                    values, len(worlds), structural_upper, _coverage(communities, trial),
                    risk_lambda=risk_lambda, community_weight=community_weight,
                    use_risk_lower_bound=use_risk_lower_bound,
                )
                if bound < incumbent[0]:
                    statuses[node] = {"status": "pruned", "observed_worlds": len(values), "upper_micro": bound, "structural_upper": structural_upper}
                    break
                if len(values) == len(worlds):
                    score = exact_score_micro(values, _coverage(communities, trial), risk_lambda=risk_lambda, community_weight=community_weight)
                    statuses[node] = {"status": "promoted_full", "observed_worlds": len(values), "score_micro": score, "upper_micro": bound, "structural_upper": structural_upper}
                    if _better((score, node), incumbent):
                        incumbent = (score, node)
                    break
                next_worlds = worlds[len(values): len(values) + batch_size]
                values.extend(evaluator.values(trial, next_worlds))
        selected.append(incumbent[1])
        rounds.append({"winner": incumbent[1], "score_micro": incumbent[0], "candidates": statuses})
    return {"selected": selected, "rounds": rounds, "cache": evaluator.cache, "world_evaluations": evaluator.calls}
