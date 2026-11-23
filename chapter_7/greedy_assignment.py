"""Greedy algorithms assignment.

Webster University in Tashkent.
Student: Hamidov Muxammadjon, ID 4251674 """


import bisect
import heapq
import itertools
import random
import time


# Part A

def greedy_coins(amount, coins):
    taken = []
    remaining = amount
    
    for c in sorted(coins, reverse=True):
       
        while c <= remaining:
            taken.append(c)
            remaining -= c
    return taken


def min_coins(amount, coins):
    INF = float("inf")
    best = [0] + [INF] * amount         
    for a in range(1, amount + 1):
        for c in coins:
            if c <= a and best[a - c] + 1 < best[a]:
                best[a] = best[a - c] + 1
    return best[amount]


def first_failure(coins, limit):
    
    for a in range(1, limit + 1):
        if len(greedy_coins(a, coins)) > min_coins(a, coins):
            return a
    return None


# Part B

def huffman_codes(freq):
    counter = itertools.count()
    heap = [(w, next(counter), s) for s, w in freq.items()]
    heapq.heapify(heap)

    if len(heap) == 1:                   
        return {heap[0][2]: "0"}

    while len(heap) > 1:
        w1, _, left = heapq.heappop(heap)     
        w2, _, right = heapq.heappop(heap)    
        heapq.heappush(heap, (w1 + w2, next(counter), (left, right)))

    codes = {}

    def walk(tree, prefix):
        if isinstance(tree, tuple):
            walk(tree[0], prefix + "0")
            walk(tree[1], prefix + "1")
        else:
            codes[tree] = prefix

    walk(heap[0][2], "")
    return codes


# Part D

def select_activities(acts):
    chosen = []
    last_finish = float("-inf")
    for act in sorted(acts, key=lambda x: x[2]):      
        if act[1] >= last_finish:                    
            chosen.append(act)
            last_finish = act[2]
    return chosen


# Part E

def kruskal(vertices, edges):
    parent = {v: v for v in vertices}
    size = {v: 1 for v in vertices}

    def find(x):
        
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(a, b):
        ra, rb = find(a), find(b)
        if ra == rb:
            return False                
        if size[ra] < size[rb]:         
            ra, rb = rb, ra
        parent[rb] = ra
        size[ra] += size[rb]
        return True

    tree, total = [], 0
    
    for u, v, w in sorted(edges, key=lambda e: (e[2], e[0] + e[1])):
        if union(u, v):
            tree.append((u, v, w))
            total += w
            if len(tree) == len(parent) - 1:     
                break
    return tree, total


# Bonus

def best_weighted(acts):
    acts = sorted(acts, key=lambda x: x[2])           
    finishes = [a[2] for a in acts]
    n = len(acts)
    best = [0] * (n + 1)                            
    for i in range(1, n + 1):
        name, s, f, value = acts[i - 1]
        
        p = bisect.bisect_right(finishes, s, 0, i - 1)
        best[i] = max(best[i - 1], value + best[p])
    return best[n]




def brute_force_activities(acts):
    for r in range(len(acts), 0, -1):
        for subset in itertools.combinations(acts, r):
            ordered = sorted(subset, key=lambda x: x[1])
            if all(ordered[i][2] <= ordered[i + 1][1] for i in range(len(ordered) - 1)):
                return r
    return 0


def brute_force_mst(vertices, edges):
    n = len(vertices)
    best = None
    for combo in itertools.combinations(edges, n - 1):
        comp = {v: v for v in vertices}

        def find(x):
            while comp[x] != x:
                x = comp[x]
            return x

        ok = True
        for u, v, w in combo:
            ru, rv = find(u), find(v)
            if ru == rv:
                ok = False
                break
            comp[ru] = rv
        if ok:
            cost = sum(e[2] for e in combo)
            if best is None or cost < best:
                best = cost
    return best


def brute_force_weighted(acts):
    top = 0
    for r in range(1, len(acts) + 1):
        for subset in itertools.combinations(acts, r):
            ordered = sorted(subset, key=lambda x: x[1])
            if all(ordered[i][2] <= ordered[i + 1][1] for i in range(len(ordered) - 1)):
                top = max(top, sum(a[3] for a in subset))
    return top


def run_tests():
    random.seed(7)
    
    for coins in ([1, 6, 10], [1, 5, 10, 25], [1, 3, 4]):
        for a in range(0, 31):
            fewest = None
            for k in range(0, a + 1):             
                if any(sum(combo) == a
                       for combo in itertools.combinations_with_replacement(coins, k)):
                    fewest = k
                    break
            assert min_coins(a, coins) == fewest
    
    for _ in range(200):
        acts = []
        for i in range(8):
            s = random.randint(0, 12)
            acts.append((i, s, s + random.randint(1, 5)))
        assert len(select_activities(acts)) == brute_force_activities(acts)
    
    names = "ABCDE"
    for _ in range(100):
        edges = [(u, v, random.randint(1, 9)) for u, v in itertools.combinations(names, 2)
                 if random.random() < 0.7]
        # make sure the graph is connected by adding a path
        edges += [(names[i], names[i + 1], random.randint(1, 9)) for i in range(4)]
        edges = list({(u, v): (u, v, w) for u, v, w in edges}.values())
        assert kruskal(names, edges)[1] == brute_force_mst(names, edges)
    
    for _ in range(200):
        acts = []
        for i in range(7):
            s = random.randint(0, 12)
            acts.append((i, s, s + random.randint(1, 6), random.randint(1, 10)))
        assert best_weighted(acts) == brute_force_weighted(acts)
    
    codes = huffman_codes({"P": 35, "Q": 20, "R": 15, "S": 12, "T": 10, "U": 8})
    for x, y in itertools.permutations(codes.values(), 2):
        assert not y.startswith(x)
    print("tests: all brute-force comparisons passed")


if __name__ == "__main__":
    US = [25, 10, 5, 1]
    print("A1", greedy_coins(87, US))
    a = first_failure([1, 6, 10], 100)
    print("A2", a, greedy_coins(a, [1, 6, 10]), min_coins(a, [1, 6, 10]))
    print("A3", [min_coins(a, [1, 6, 10]) for a in range(14)])

    freq = {"P": 35, "Q": 20, "R": 15, "S": 12, "T": 10, "U": 8}
    codes = huffman_codes(freq)
    print("B2", codes, sum(freq[s] * len(codes[s]) for s in freq), "bits")
    msg = "UTSRQPPP"
    bits = "".join(codes[ch] for ch in msg)
    print("B3", msg, "->", bits, f"({len(bits)} bits)")

    acts = [("A", 1, 3), ("B", 2, 5), ("C", 4, 6), ("D", 6, 7),
            ("E", 5, 8), ("F", 8, 10), ("G", 7, 11), ("H", 9, 12),
            ("I", 10, 13), ("J", 12, 14), ("K", 3, 9), ("L", 13, 15)]
    print("D1", [x[0] for x in select_activities(acts)])

    edges = [("A", "B", 7), ("A", "D", 5), ("B", "C", 8), ("B", "D", 9),
             ("B", "E", 7), ("C", "E", 5), ("D", "E", 15), ("D", "F", 6),
             ("E", "F", 8), ("E", "G", 9), ("F", "G", 11)]
    print("E2", kruskal("ABCDEFG", edges))
    cheaper = [e if e[:2] != ("D", "E") else ("D", "E", 4) for e in edges]
    print("E3", kruskal("ABCDEFG", cheaper))

    try:
        example = [("x", 0, 10, 10), ("y", 0, 4, 3), ("z", 5, 10, 3)]
        print("Bonus", best_weighted(example))
        # earliest finish first on example 1 (values of y and z only add up to 6)
        eff = select_activities([(n, s, f) for n, s, f, v in example])
        print("Bonus 1: earliest finish picks", [x[0] for x in eff],
              "value", sum(v for n, s, f, v in example if n in [x[0] for x in eff]))
        example2 = [("a", 0, 10, 5), ("b", 0, 5, 4), ("c", 5, 10, 4)]
        print("Bonus 2: best =", best_weighted(example2), "(highest value first gives 5)")
    except NotImplementedError:
        print("Bonus not attempted")

    run_tests()

    random.seed(2026)
    for n in (10_000, 100_000, 1_000_000):
        acts = []
        for i in range(n):
            s = random.uniform(0, 1e6)
            acts.append((i, s, s + random.uniform(0.5, 50)))
        t = time.perf_counter()
        select_activities(acts)
        print("F2 activities", n, f"{(time.perf_counter() - t) * 1000:.1f} ms")

    for limit in (500, 1000, 2000):
        t = time.perf_counter()
        first_failure(US, limit)
        print("F2 coins", limit, f"{(time.perf_counter() - t) * 1000:.1f} ms")