#!/usr/bin/env python3
"""Verify the 12-vertex counterexample to WOWII Conjecture 291.

The verifier uses only the Python standard library. It checks that the edge-list
and graph6 files describe the same graph and independently computes all
invariants used in the counterexample certificate.
"""

from __future__ import annotations

import argparse
from itertools import combinations
from pathlib import Path
from typing import Iterable

ROOT = Path(__file__).resolve().parents[1]
EDGE_LIST_PATH = ROOT / "data" / "witness.edgelist"
GRAPH6_PATH = ROOT / "data" / "witness.graph6"
RESULTS_PATH = ROOT / "results" / "verification.txt"

EXPECTED_VERTICES = tuple(range(12))
EXPECTED_ORDER = 12
EXPECTED_SIZE = 25
EXPECTED_GRAPH6 = "Ka??_`xsIhNV"
EXPECTED_TRIANGLE_COUNTS = (1, 10, 1, 11, 1, 0, 1, 1, 12, 7, 6, 12)
EXPECTED_HH_SEQUENCES = (
    (8, 8, 7, 6, 5, 5, 2, 2, 2, 2, 2, 1),
    (7, 6, 5, 4, 4, 2, 2, 1, 1, 1, 1),
    (5, 4, 3, 3, 1, 1, 1, 1, 1, 0),
)
EXPECTED_TOTAL_DOMINATING_SET = frozenset({1, 3, 8, 10})
EXPECTED_TOTAL_DOMINATION_NUMBER = 4
EXPECTED_ZERO_STEP = 2
EXPECTED_MIN_TRIANGLE_FREQUENCY = 1

SPANNING_TREE = frozenset(
    {
        (5, 10),
        (1, 10),
        (10, 11),
        (0, 1),
        (0, 9),
        (1, 3),
        (3, 6),
        (3, 7),
        (3, 8),
        (2, 8),
        (4, 8),
    }
)


class VerificationError(AssertionError):
    """Raised when one of the witness checks fails."""


def canonical_edge(u: int, v: int) -> tuple[int, int]:
    if u == v:
        raise VerificationError(f"Loop found at vertex {u}.")
    return (u, v) if u < v else (v, u)


def read_edgelist(path: Path) -> frozenset[tuple[int, int]]:
    edges: set[tuple[int, int]] = set()
    for line_number, raw_line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        line = raw_line.split("#", 1)[0].strip()
        if not line:
            continue
        fields = line.split()
        if len(fields) != 2:
            raise VerificationError(
                f"{path}:{line_number}: expected two integer endpoints, got {raw_line!r}."
            )
        try:
            u, v = map(int, fields)
        except ValueError as exc:
            raise VerificationError(
                f"{path}:{line_number}: endpoints must be integers."
            ) from exc
        edge = canonical_edge(u, v)
        if edge in edges:
            raise VerificationError(f"{path}:{line_number}: duplicate edge {edge}.")
        edges.add(edge)
    return frozenset(edges)


def decode_graph6(text: str) -> tuple[int, frozenset[tuple[int, int]]]:
    """Decode the graph6 forms for graphs with at most 62 vertices."""

    value = text.strip()
    if value.startswith(">>graph6<<"):
        value = value[len(">>graph6<<") :]
    if not value:
        raise VerificationError("The graph6 file is empty.")

    first = ord(value[0]) - 63
    if not 0 <= first <= 62:
        raise VerificationError("This verifier supports graph6 orders from 0 through 62.")
    order = first

    bits: list[int] = []
    for char in value[1:]:
        encoded = ord(char) - 63
        if not 0 <= encoded <= 63:
            raise VerificationError(f"Invalid graph6 character: {char!r}.")
        bits.extend((encoded >> shift) & 1 for shift in range(5, -1, -1))

    required_bits = order * (order - 1) // 2
    if len(bits) < required_bits:
        raise VerificationError("The graph6 string does not contain enough adjacency bits.")

    edges: set[tuple[int, int]] = set()
    bit_index = 0
    # graph6 stores the strict upper triangle by increasing second endpoint.
    for v in range(1, order):
        for u in range(v):
            if bits[bit_index]:
                edges.add((u, v))
            bit_index += 1
    return order, frozenset(edges)


def adjacency(vertices: Iterable[int], edges: Iterable[tuple[int, int]]) -> dict[int, set[int]]:
    adj = {vertex: set() for vertex in vertices}
    for u, v in edges:
        if u not in adj or v not in adj:
            raise VerificationError(f"Edge {(u, v)} has an endpoint outside the vertex set.")
        adj[u].add(v)
        adj[v].add(u)
    return adj


def is_connected(vertices: tuple[int, ...], adj: dict[int, set[int]]) -> bool:
    if not vertices:
        return True
    reached = {vertices[0]}
    stack = [vertices[0]]
    while stack:
        current = stack.pop()
        for neighbor in adj[current] - reached:
            reached.add(neighbor)
            stack.append(neighbor)
    return reached == set(vertices)


def verify_spanning_tree(
    vertices: tuple[int, ...],
    graph_edges: frozenset[tuple[int, int]],
) -> None:
    tree_edges = frozenset(canonical_edge(*edge) for edge in SPANNING_TREE)
    if not tree_edges <= graph_edges:
        missing = sorted(tree_edges - graph_edges)
        raise VerificationError(f"Spanning-tree certificate uses missing edges: {missing}.")
    if len(tree_edges) != len(vertices) - 1:
        raise VerificationError("Spanning-tree certificate has the wrong number of edges.")
    tree_adj = adjacency(vertices, tree_edges)
    if not is_connected(vertices, tree_adj):
        raise VerificationError("Spanning-tree certificate is not connected.")
    # A connected graph on n vertices with n-1 edges is a tree.


def triangle_counts(vertices: tuple[int, ...], adj: dict[int, set[int]]) -> tuple[int, ...]:
    counts: list[int] = []
    for vertex in vertices:
        count = sum(
            1
            for u, v in combinations(sorted(adj[vertex]), 2)
            if v in adj[u]
        )
        counts.append(count)
    return tuple(counts)


def havel_hakimi_step(sequence: tuple[int, ...]) -> tuple[int, ...]:
    if not sequence:
        return ()
    work = sorted(sequence, reverse=True)
    degree = work.pop(0)
    if degree > len(work):
        raise VerificationError("Havel-Hakimi sequence is not graphical.")
    for index in range(degree):
        work[index] -= 1
        if work[index] < 0:
            raise VerificationError("Havel-Hakimi reduction produced a negative entry.")
    return tuple(sorted(work, reverse=True))


def first_havel_hakimi_zero_step(
    degrees: tuple[int, ...],
) -> tuple[int, tuple[tuple[int, ...], ...]]:
    sequence = tuple(sorted(degrees, reverse=True))
    history = [sequence]
    step = 0
    while sequence and 0 not in sequence:
        sequence = havel_hakimi_step(sequence)
        step += 1
        history.append(sequence)
    return step, tuple(history)


def is_total_dominating_set(
    candidate: frozenset[int],
    vertices: tuple[int, ...],
    adj: dict[int, set[int]],
) -> bool:
    return all(bool(adj[vertex] & candidate) for vertex in vertices)


def total_domination_number(
    vertices: tuple[int, ...],
    adj: dict[int, set[int]],
) -> tuple[int, frozenset[int]]:
    for size in range(1, len(vertices) + 1):
        for candidate_tuple in combinations(vertices, size):
            candidate = frozenset(candidate_tuple)
            if is_total_dominating_set(candidate, vertices, adj):
                return size, candidate
    raise VerificationError("No total dominating set exists.")


def count_total_dominating_sets_of_size(
    size: int,
    vertices: tuple[int, ...],
    adj: dict[int, set[int]],
) -> int:
    return sum(
        is_total_dominating_set(frozenset(candidate), vertices, adj)
        for candidate in combinations(vertices, size)
    )


def verify_hand_lower_bound(adj: dict[int, set[int]]) -> None:
    # Vertex 5 is a leaf and therefore forces vertex 10 into every total
    # dominating set.
    if adj[5] != {10}:
        raise VerificationError(f"Expected N(5)={{10}}, found {sorted(adj[5])}.")

    required_neighborhoods = ({1, 9}, {8, 11}, {3, 11}, {3, 8})
    actual_neighborhoods = (adj[0], adj[2], adj[6], adj[7])
    if actual_neighborhoods != required_neighborhoods:
        raise VerificationError(
            "The four-neighborhood lower-bound certificate does not match the graph."
        )

    first = required_neighborhoods[0]
    remaining = required_neighborhoods[1:]
    if any(first & neighborhood for neighborhood in remaining):
        raise VerificationError("The first forcing neighborhood is not disjoint as claimed.")
    intersection = set.intersection(*(set(neighborhood) for neighborhood in remaining))
    if intersection:
        raise VerificationError(
            f"Expected the final three-neighborhood intersection to be empty, got {intersection}."
        )


def format_tuple(values: Iterable[int]) -> str:
    return "(" + ", ".join(str(value) for value in values) + ")"


def verify() -> str:
    edges = read_edgelist(EDGE_LIST_PATH)
    vertices = EXPECTED_VERTICES
    if len(vertices) != EXPECTED_ORDER:
        raise VerificationError("Internal expected-order mismatch.")
    if len(edges) != EXPECTED_SIZE:
        raise VerificationError(f"Expected {EXPECTED_SIZE} edges, found {len(edges)}.")

    graph6_text = GRAPH6_PATH.read_text(encoding="utf-8").strip()
    if graph6_text != EXPECTED_GRAPH6:
        raise VerificationError(
            f"Expected graph6 {EXPECTED_GRAPH6!r}, found {graph6_text!r}."
        )
    graph6_order, graph6_edges = decode_graph6(graph6_text)
    if graph6_order != EXPECTED_ORDER:
        raise VerificationError(
            f"graph6 order is {graph6_order}, expected {EXPECTED_ORDER}."
        )
    if graph6_edges != edges:
        only_edgelist = sorted(edges - graph6_edges)
        only_graph6 = sorted(graph6_edges - edges)
        raise VerificationError(
            "Edge-list and graph6 data disagree: "
            f"only in edge list={only_edgelist}, only in graph6={only_graph6}."
        )

    adj = adjacency(vertices, edges)
    if not is_connected(vertices, adj):
        raise VerificationError("The witness graph is disconnected.")
    verify_spanning_tree(vertices, edges)

    counts = triangle_counts(vertices, adj)
    if counts != EXPECTED_TRIANGLE_COUNTS:
        raise VerificationError(
            f"Triangle counts are {counts}, expected {EXPECTED_TRIANGLE_COUNTS}."
        )
    minimum_triangle_count = min(counts)
    min_triangle_frequency = counts.count(minimum_triangle_count)
    if min_triangle_frequency != EXPECTED_MIN_TRIANGLE_FREQUENCY:
        raise VerificationError(
            "Minimum-triangle frequency mismatch: "
            f"expected {EXPECTED_MIN_TRIANGLE_FREQUENCY}, got {min_triangle_frequency}."
        )
    minimum_vertices = tuple(
        vertex for vertex, count in zip(vertices, counts) if count == minimum_triangle_count
    )
    if minimum_vertices != (5,):
        raise VerificationError(f"Expected vertex 5 to be the unique minimum, got {minimum_vertices}.")

    degree_sequence = tuple(sorted((len(adj[v]) for v in vertices), reverse=True))
    zero_step, hh_history = first_havel_hakimi_zero_step(degree_sequence)
    if hh_history[:3] != EXPECTED_HH_SEQUENCES:
        raise VerificationError(
            f"Havel-Hakimi history is {hh_history[:3]}, expected {EXPECTED_HH_SEQUENCES}."
        )
    if zero_step != EXPECTED_ZERO_STEP:
        raise VerificationError(
            f"Expected first zero at step {EXPECTED_ZERO_STEP}, got step {zero_step}."
        )

    if not is_total_dominating_set(EXPECTED_TOTAL_DOMINATING_SET, vertices, adj):
        raise VerificationError("The set {1, 3, 8, 10} is not total dominating.")
    tds3_count = count_total_dominating_sets_of_size(3, vertices, adj)
    if tds3_count != 0:
        raise VerificationError(f"Found {tds3_count} total dominating sets of size 3.")
    gamma_t, minimum_tds = total_domination_number(vertices, adj)
    if gamma_t != EXPECTED_TOTAL_DOMINATION_NUMBER:
        raise VerificationError(
            f"Expected total domination number {EXPECTED_TOTAL_DOMINATION_NUMBER}, got {gamma_t}."
        )
    verify_hand_lower_bound(adj)

    conjectured_upper_bound = zero_step + min_triangle_frequency
    if not gamma_t > conjectured_upper_bound:
        raise VerificationError(
            "The computed values do not contradict Conjecture 291: "
            f"gamma_t={gamma_t}, upper bound={conjectured_upper_bound}."
        )

    report = f"""WOWII Conjecture 291 witness verification
==========================================

Data
----
edge-list file: data/witness.edgelist
graph6 file: data/witness.graph6
graph6: {graph6_text}
edge-list/graph6 agreement: yes

Graph
-----
order: {len(vertices)}
size: {len(edges)}
connected: yes
spanning-tree certificate: valid

Triangle calculation
--------------------
per-vertex counts (vertices 0 through 11):
{format_tuple(counts)}
minimum incident-triangle count: {minimum_triangle_count}
vertices attaining the minimum: {{{', '.join(map(str, minimum_vertices))}}}
minimum-triangle frequency: {min_triangle_frequency}

Havel-Hakimi calculation
------------------------
step 0: {format_tuple(hh_history[0])}
step 1: {format_tuple(hh_history[1])}
step 2: {format_tuple(hh_history[2])}
first zero step h(G): {zero_step}

Total domination calculation
----------------------------
certified total dominating set: {{1, 3, 8, 10}}
total dominating sets of size 3: {tds3_count}
first minimum total dominating set found exhaustively: {{{', '.join(map(str, sorted(minimum_tds)))}}}
total domination number gamma_t(G): {gamma_t}
hand lower-bound certificate: valid

Conjecture 291 contradiction
----------------------------
h(G) + freq(min T): {zero_step} + {min_triangle_frequency} = {conjectured_upper_bound}
gamma_t(G): {gamma_t}
contradiction: {gamma_t} > {conjectured_upper_bound}

RESULT: PASS - the supplied graph is a counterexample to WOWII Conjecture 291.
"""
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--write-results",
        action="store_true",
        help="write the deterministic verification report to results/verification.txt",
    )
    args = parser.parse_args()

    try:
        report = verify()
        if args.write_results:
            RESULTS_PATH.parent.mkdir(parents=True, exist_ok=True)
            RESULTS_PATH.write_text(report, encoding="utf-8")
        elif RESULTS_PATH.exists():
            committed = RESULTS_PATH.read_text(encoding="utf-8")
            if committed != report:
                raise VerificationError(
                    "results/verification.txt is stale; run "
                    "'python scripts/verify.py --write-results' and commit the change."
                )
        print(report, end="")
        return 0
    except (OSError, VerificationError) as exc:
        print(f"RESULT: FAIL - {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
