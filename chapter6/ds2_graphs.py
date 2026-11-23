"""
DS2 Fall 2026 - Shortest-Path Algorithms (Part D)
Bellman-Ford and Floyd-Warshall, standard library only.

Vertices are numbered 0..n-1, edges are tuples (u, v, w).
"""

import random
import time

INF = float('inf')


def bellman_ford(n, edges, src):
    """Return (dist, pred, has_negative_cycle).

    Single-source shortest paths. Relaxes every edge in the listed order,
    at most n-1 passes, and stops early if a pass changes nothing.
    One extra (n-th) pass detects a negative cycle reachable from src.

    Time : O(V * E) worst case, O(E) best case (early exit after one pass).
    Space: O(V) for dist and pred (the edge list is input, not counted).
    """
    dist = [INF] * n
    pred = [None] * n
    dist[src] = 0

    for _ in range(n - 1):
        changed = False
        for u, v, w in edges:
            
            if dist[u] != INF and dist[u] + w < dist[v]:
                dist[v] = dist[u] + w
                pred[v] = u
                changed = True
        if not changed:          
            return dist, pred, False

    for u, v, w in edges:
        if dist[u] != INF and dist[u] + w < dist[v]:
            return dist, pred, True
    return dist, pred, False


def bf_path(pred, src, target):
    """Return the path src -> target as a list, or None if unreachable.

    Follows predecessor links backwards from target, then reverses.
    A step counter guards against cycles in pred (negative-cycle case).

    Time : O(V) in the worst case (path has at most V vertices).
    Space: O(V) for the returned path.
    """
    if target != src and pred[target] is None:
        return None
    path = [target]
    cur = target
    steps = 0
    while cur != src:
        cur = pred[cur]
        if cur is None:
            return None
        path.append(cur)
        steps += 1
        if steps > len(pred):    
            return None
    path.reverse()
    return path


def floyd_warshall(n, edges):
    """Return (dist, nxt, has_negative_cycle).

    All-pairs shortest paths. k (the intermediate vertex) is the OUTERMOST
    loop. nxt[i][j] is the first vertex after i on a shortest i -> j path.
    A negative cycle exists iff some diagonal entry dist[i][i] < 0.

    Time : Theta(V^3).
    Space: Theta(V^2) for dist and nxt.
    """
    dist = [[INF] * n for _ in range(n)]
    nxt = [[None] * n for _ in range(n)]
    for i in range(n):
        dist[i][i] = 0
        nxt[i][i] = i
    for u, v, w in edges:
        if w < dist[u][v]:       
            dist[u][v] = w
            nxt[u][v] = v

    for k in range(n):
        dk = dist[k]
        for i in range(n):
            dik = dist[i][k]
            if dik == INF:     
                continue
            di = dist[i]
            for j in range(n):
                dkj = dk[j]
                if dkj == INF:
                    continue
                if dik + dkj < di[j]:
                    di[j] = dik + dkj
                    nxt[i][j] = nxt[i][k]

    has_neg = any(dist[i][i] < 0 for i in range(n))
    return dist, nxt, has_neg


def fw_path(nxt, u, v):
    """Return the path u -> v as a list, or None if unreachable.

    Walks the nxt table from u until v is reached.
    Step limit protects against loops when a negative cycle is present.

    Time : O(V) per query.
    Space: O(V) for the returned path.
    """
    if nxt[u][v] is None:
        return None
    path = [u]
    cur = u
    while cur != v:
        cur = nxt[cur][v]
        if cur is None:
            return None
        path.append(cur)
        if len(path) > len(nxt) + 1:  
            return None
    return path


# ----------------------------------------------------------------------
# helpers for the main block
# ----------------------------------------------------------------------

def fmt(x):
    if x == INF:
        return "inf"
    return str(int(x)) if x == int(x) else "%.4f" % x


def names_of(path, names):
    return " -> ".join(names[p] for p in path) if path else "no path"


def run_bf(title, names, edges, src):
    n = len(names)
    print("=" * 60)
    print(title, "(Bellman-Ford, source %s)" % names[src])
    dist, pred, neg = bellman_ford(n, edges, src)
    print("negative cycle:", neg)
    for i in range(n):
        p = pred[i]
        print("  %s: dist=%-4s pred=%s" % (names[i], fmt(dist[i]),
                                          names[p] if p is not None else "-"))
    if not neg:
        for t in range(n):
            if t != src:
                print("  path %s: %s" % (names[t], names_of(bf_path(pred, src, t), names)),
                      "(weight %s)" % fmt(dist[t]) if dist[t] != INF else "")
    return dist, pred, neg


def print_matrix(names, d):
    n = len(names)
    print("      " + "".join("%6s" % names[j] for j in range(n)))
    for i in range(n):
        print("  %-4s" % names[i] + "".join("%6s" % fmt(d[i][j]) for j in range(n)))


def time_fw(v, seed=1):
    rnd = random.Random(seed)
    edges = [(i, j, rnd.randint(1, 100)) for i in range(v) for j in range(v) if i != j]
    t0 = time.perf_counter()
    floyd_warshall(v, edges)
    return time.perf_counter() - t0


if __name__ == "__main__":
    
    n1 = ["S", "A", "B", "C", "D", "E"]
    S, A, B, C, D, E = range(6)
    g1 = [(S, A, 4), (S, B, 5), (A, C, 3), (B, A, -2),
          (B, D, 6), (C, D, -1), (C, E, 5), (D, E, 2)]
    run_bf("Graph 1", n1, g1, S)

   
    n2 = ["W", "X", "Y", "Z"]
    W, X, Y, Z = range(4)
    g2 = [(W, X, 2), (X, Y, 3), (Y, Z, -6), (Z, X, 2)]
    run_bf("Graph 2", n2, g2, W)
    print("  (cycle X -> Y -> Z -> X has weight 3 - 6 + 2 = -1)")

   
    n3 = ["A", "B", "C", "D"]
    a, b, c, d = range(4)
    g3 = [(a, b, 5), (a, d, 10), (b, c, 3), (c, d, 1), (d, b, -2), (c, a, 8)]
    print("=" * 60)
    print("Graph 3 (Floyd-Warshall)")
    dist, nxt, neg = floyd_warshall(4, g3)
    print("negative cycle:", neg)
    print_matrix(n3, dist)
    for (u, v) in [(c, b), (b, a), (a, d)]:
        print("  path %s -> %s: %s (weight %s)" % (n3[u], n3[v],
              names_of(fw_path(nxt, u, v), n3), fmt(dist[u][v])))

    
    g3b = g3 + [(d, a, -12)]
    print("-" * 60)
    print("Graph 3 + edge D->A (-12)")
    dist, nxt, neg = floyd_warshall(4, g3b)
    print("negative cycle:", neg)
    print("  diagonal:", [fmt(dist[i][i]) for i in range(4)])

    
    
    names4 = ["0", "1", "2", "3", "4"]
    g4 = [(0, 1, 4), (0, 2, 1), (2, 1, -2), (2, 3, 7), (4, 0, 1)]
    print("=" * 60)
    print("Extra test: unreachable vertex (vertex 4 cannot be reached from 0)")
    dist, pred, neg = run_bf("Extra graph", names4, g4, 0)
    print("  bf_path to 4:", bf_path(pred, 0, 4))
    dist, nxt, neg = floyd_warshall(5, g4)
    print("Floyd-Warshall on the same graph, negative cycle:", neg)
    print_matrix(names4, dist)
    print("  fw_path 0 -> 4:", fw_path(nxt, 0, 4))
    print("  fw_path 0 -> 3:", names_of(fw_path(nxt, 0, 3), names4))
    print("  fw_path 4 -> 3:", names_of(fw_path(nxt, 4, 3), names4))

    
    print("=" * 60)
    print("Floyd-Warshall timing, complete random graphs")
    print("  %6s %12s %10s" % ("V", "time (s)", "ratio"))
    prev = None
    for v in (50, 100, 200):
        t = min(time_fw(v, seed=s) for s in (1, 2, 3))   # best of 3
        print("  %6d %12.4f %10s" % (v, t, "-" if prev is None else "%.2f" % (t / prev)))
        prev = t
    print("  (doubling V should multiply the time by about 8)")