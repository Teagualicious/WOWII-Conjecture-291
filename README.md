# An Independent Counterexample to WOWII Conjecture 291

> **Priority and attribution notice**
>
> This repository does not claim the first counterexample to WOWII Conjecture 291. An earlier public counterexample and infinite family were posted in [`google-deepmind/formal-conjectures` issue #4562](https://github.com/google-deepmind/formal-conjectures/issues/4562). The graph documented here was reached independently and provides a different 12-vertex witness to the same conclusion.

This repository records an alternative, independently obtained finite witness to the falsity of Written on the Wall II (WOWII) Conjecture 291. It makes no claim of novelty, first discovery, or publication priority.

## Conjecture statement

Conjecture 291 asserts that every finite simple connected graph satisfies

\[
\gamma_t(G) \le h(G) + \operatorname{freq}\!\left(\min_{v \in V(G)} T(v)\right),
\]

where:

- \(\gamma_t(G)\) is the total domination number;
- \(h(G)\) is the first Havel-Hakimi reduction step at which a zero appears;
- \(T(v)\) is the number of triangles containing vertex \(v\);
- \(\operatorname{freq}(\min T)\) is the number of vertices attaining the minimum triangle count.

The repository follows the interpretation and formalized statement discussed in the [Formal Conjectures project](https://github.com/google-deepmind/formal-conjectures/blob/main/FormalConjectures/WrittenOnTheWallII/GraphConjecture291.lean).

## Counterexample summary

| Invariant | Value |
|---|---:|
| Order | 12 |
| Size | 25 |
| Total domination number | 4 |
| Havel-Hakimi zero step | 2 |
| Minimum triangle frequency | 1 |
| Conjectured upper bound | 3 |

## Graph specification

The vertex set is

\[
V(G)=\{0,1,\ldots,11\}.
\]

The edge set is given below, one undirected edge per line:

```text
0 1
0 9
1 3
1 8
1 9
1 10
1 11
2 8
2 11
3 6
3 7
3 8
3 9
3 10
3 11
4 8
4 11
5 10
6 11
7 8
8 9
8 10
8 11
9 11
10 11
```

The same graph is stored in [`data/witness.edgelist`](data/witness.edgelist). Its graph6 representation, stored in [`data/witness.graph6`](data/witness.graph6), is

```text
Ka??_`xsIhNV
```

## Connectivity certificate

The following 11 edges form a spanning tree:

```text
{5-10, 10-1, 10-11, 1-0, 0-9, 1-3, 3-6, 3-7, 3-8, 8-2, 8-4}
```

Hence the graph is connected.

## Triangle calculation

The numbers of triangles containing vertices \(0,1,\ldots,11\), respectively, are

\[
(1,10,1,11,1,0,1,1,12,7,6,12).
\]

Vertex \(5\) is the unique vertex contained in no triangle. Therefore

\[
\min_v T(v)=0
\quad\text{and}\quad
\operatorname{freq}(\min T)=1.
\]

The verification script recomputes these values directly from the edge list.

## Havel-Hakimi calculation

The descending degree sequence and its first two Havel-Hakimi reductions are

\[
(8,8,7,6,5,5,2,2,2,2,2,1)
\]

\[
\longrightarrow (7,6,5,4,4,2,2,1,1,1,1)
\]

\[
\longrightarrow (5,4,3,3,1,1,1,1,1,0).
\]

The initial sequence and the first reduction contain no zero, while the second reduction does. Thus

\[
h(G)=2.
\]

## Total domination calculation

The set

\[
\{1,3,8,10\}
\]

is a total dominating set: every vertex has at least one neighbor in this set. Hence \(\gamma_t(G)\le 4\).

No three-vertex total dominating set exists:

1. Vertex \(5\) has the unique neighbor \(10\), so vertex \(10\) belongs to every total dominating set.
2. The other two vertices would need to meet all four neighborhoods
   \[
   \{1,9\},\qquad \{8,11\},\qquad \{3,11\},\qquad \{3,8\}.
   \]
3. One of the two vertices must meet \(\{1,9\}\). Neither \(1\) nor \(9\) belongs to any of the other three neighborhoods.
4. The remaining vertex would therefore have to lie in
   \[
   \{8,11\}\cap\{3,11\}\cap\{3,8\}=\varnothing,
   \]
   which is impossible.

Therefore

\[
\gamma_t(G)=4.
\]

The script also confirms this lower bound by exhaustively checking every three-vertex subset and computes the total domination number by exhaustive enumeration.

## Contradiction

For this graph,

\[
4=\gamma_t(G)>2+1=3
  =h(G)+\operatorname{freq}(\min T).
\]

Thus the graph violates the proposed upper bound and is a counterexample to WOWII Conjecture 291.

## Reproducibility

The verifier requires Python 3.9 or later and uses only the standard library. From the repository root, run

```bash
python scripts/verify.py
```

The script checks:

- agreement between the edge-list and graph6 encodings;
- order, size, connectivity, and the stated spanning tree;
- all per-vertex triangle counts;
- the Havel-Hakimi reductions and first zero step;
- the exhibited total dominating set;
- the absence of any three-vertex total dominating set;
- the total domination number by exhaustive enumeration;
- the final strict inequality \(4>3\).

A deterministic reference run is stored in [`results/verification.txt`](results/verification.txt). To regenerate it, run

```bash
python scripts/verify.py --write-results
```

## Relationship to the earlier counterexample

- Both finite witnesses have 12 vertices.
- The earlier posted witness in [issue #4562](https://github.com/google-deepmind/formal-conjectures/issues/4562) has 21 edges and is the smallest member \(G_6\) of an infinite family \(G_m\), \(m\ge 6\).
- The witness documented here has 25 edges and is presented only as an alternative, independently obtained finite witness.
- Since the two 12-vertex witnesses have different numbers of edges, they are not isomorphic. No relationship beyond refuting the same conjecture is claimed.
- The earlier public posting predates this repository. This repository makes no competing priority claim, and it does not address worldwide historical priority.

## Files

```text
.
├── README.md
├── data
│   ├── witness.edgelist
│   └── witness.graph6
├── scripts
│   └── verify.py
├── results
│   └── verification.txt
├── CITATION.cff
└── LICENSE
```

## AI assistance disclosure

The finite witness search, independent calculations, verification-script preparation, and repository write-up were developed with assistance from OpenAI ChatGPT under the repository owner's direction. All numerical claims in this repository are reproducible with the included standard-library verifier and should receive normal independent review.

## License

The code and documentation in this repository are available under the [MIT License](LICENSE).
