"""Week 3 Lab - Mini challenge: order-statistic AVL leaderboard.

Keys are tuples (-score, player_id), so position 1 = highest score and ties
are broken by player id.  Every node stores height AND size (nodes in its
subtree), which lets select(k) and rank(key) run in O(log n).

Run:  python leaderboard.py
"""

import bisect
import gc
import random
import sys
import time

sys.setrecursionlimit(10000)


# ------------------------------------------------------------------ AVL with sizes
class OSNode:
    __slots__ = ("key", "left", "right", "height", "size")

    def __init__(self, key):
        self.key = key
        self.left = None
        self.right = None
        self.height = 0
        self.size = 1


def h(n):
    return n.height if n else -1


def sz(n):
    return n.size if n else 0


def update(n):
    n.height = 1 + max(h(n.left), h(n.right))
    n.size = 1 + sz(n.left) + sz(n.right)       


def balance(n):
    return h(n.left) - h(n.right)               


def rot_left(x):
    y = x.right
    x.right = y.left
    y.left = x
    update(x)                                   
    update(y)
    return y


def rot_right(y):
    x = y.left
    y.left = x.right
    x.right = y
    update(y)
    update(x)
    return x


def rebalance(n):
    update(n)
    bf = balance(n)
    if bf > 1:
        if balance(n.left) < 0:                 
            n.left = rot_left(n.left)
        return rot_right(n)                     
    if bf < -1:
        if balance(n.right) > 0:                
            n.right = rot_right(n.right)
        return rot_left(n)                      
    return n


class OSTree:
    def __init__(self):
        self.root = None

    def __len__(self):
        return sz(self.root)

    # ---- insert
    def insert(self, key):
        self.root = self._insert(self.root, key)

    def _insert(self, n, key):
        if n is None:
            return OSNode(key)
        if key < n.key:
            n.left = self._insert(n.left, key)
        elif key > n.key:
            n.right = self._insert(n.right, key)
        else:
            return n
        return rebalance(n)

    # ---- delete
    def delete(self, key):
        self.root = self._delete(self.root, key)

    def _delete(self, n, key):
        if n is None:
            return None                         
        if key < n.key:
            n.left = self._delete(n.left, key)
        elif key > n.key:
            n.right = self._delete(n.right, key)
        else:
            if n.left is None:
                return n.right
            if n.right is None:
                return n.left
            succ = n.right                      
            while succ.left:
                succ = succ.left
            n.key = succ.key
            n.right = self._delete(n.right, succ.key)
        return rebalance(n)

    # ---- order statistics
    def select(self, k):
        """k-th smallest key, 0-based, O(log n)."""
        if not 0 <= k < sz(self.root):
            raise IndexError(k)
        cur = self.root
        while True:
            ls = sz(cur.left)
            if k < ls:
                cur = cur.left
            elif k == ls:
                return cur.key
            else:
                k -= ls + 1
                cur = cur.right

    def rank(self, key):
        """number of keys smaller than key, O(log n)."""
        r = 0
        cur = self.root
        while cur:
            if key <= cur.key:
                cur = cur.left
            else:
                r += sz(cur.left) + 1
                cur = cur.right
        return r

    def first(self, k):
        """k smallest keys in order: O(log n + k) with an explicit stack."""
        out, stack, cur = [], [], self.root
        while (cur or stack) and len(out) < k:
            while cur:
                stack.append(cur)
                cur = cur.left
            cur = stack.pop()
            out.append(cur.key)
            cur = cur.right
        return out

    def is_valid(self):
        def check(n, lo, hi):
            if n is None:
                return True
            if (lo is not None and n.key <= lo) or (hi is not None and n.key >= hi):
                return False
            if n.height != 1 + max(h(n.left), h(n.right)):
                return False
            if n.size != 1 + sz(n.left) + sz(n.right):
                return False
            if balance(n) not in (-1, 0, 1):
                return False
            return check(n.left, lo, n.key) and check(n.right, n.key, hi)
        return check(self.root, None, None)

    @classmethod
    def from_sorted(cls, keys):
        """Perfectly balanced tree from a sorted list in O(n).  Only used to
        set up the 1M / 2M scaling runs quickly (inserting 2M keys one by one
        takes minutes in pure Python)."""
        t = cls()

        def build(lo, hi):
            if lo >= hi:
                return None
            mid = (lo + hi) // 2
            n = OSNode(keys[mid])
            n.left = build(lo, mid)
            n.right = build(mid + 1, hi)
            update(n)
            return n
        t.root = build(0, len(keys))
        return t


# ------------------------------------------------------------------ the two leaderboards
class Leaderboard:
    """AVL version."""

    def __init__(self):
        self.tree = OSTree()
        self.score = {}

    def set_score(self, player, score):
        if player in self.score:
            self.tree.delete((-self.score[player], player))
        self.score[player] = score
        self.tree.insert((-score, player))

    def rank_of(self, player):                  
        return self.tree.rank((-self.score[player], player)) + 1

    def at(self, position):                     
        neg, player = self.tree.select(position - 1)
        return player, -neg

    def top(self, k):
        return [(p, -s) for s, p in self.tree.first(k)]


class ListLeaderboard:
    """Same interface, sorted Python list + bisect."""

    def __init__(self):
        self.data = []
        self.score = {}

    def set_score(self, player, score):
        if player in self.score:
            i = bisect.bisect_left(self.data, (-self.score[player], player))
            del self.data[i]
        self.score[player] = score
        bisect.insort(self.data, (-score, player))

    def rank_of(self, player):
        return bisect.bisect_left(self.data, (-self.score[player], player)) + 1

    def at(self, position):
        neg, player = self.data[position - 1]
        return player, -neg

    def top(self, k):
        return [(p, -s) for s, p in self.data[:k]]


# ------------------------------------------------------------------ experiments
def timed(fn):
    gc.collect()
    gc.disable()
    t0 = time.perf_counter()
    out = fn()
    dt = time.perf_counter() - t0
    gc.enable()
    return dt, out


def self_test():
    """small randomised check: both boards agree, validator stays True, sizes right"""
    rng = random.Random(5)
    a, b = Leaderboard(), ListLeaderboard()
    for step in range(4000):
        p, s = rng.randrange(300), rng.randrange(50) 
        a.set_score(p, s)
        b.set_score(p, s)
        if step % 400 == 0:
            assert a.tree.is_valid()
    assert a.tree.is_valid() and len(a.tree) == len(b.data)
    for pos in range(1, len(b.data) + 1):
        assert a.at(pos) == b.at(pos)
    for p in a.score:
        assert a.rank_of(p) == b.rank_of(p)
    assert a.top(25) == b.top(25)
    # delete the whole tree key by key
    t = OSTree()
    ks = rng.sample(range(5000), 1000)
    for k in ks:
        t.insert(k)
    rng.shuffle(ks)
    for i, k in enumerate(ks):
        t.delete(k)
        if i % 100 == 0:
            assert t.is_valid()
    assert t.root is None


def main_experiment(n=200_000, updates=100_000, queries=2000, seed=1):
    rng = random.Random(seed)
    scores = [rng.randrange(1_000_000) for _ in range(n)]
    ups = [(rng.randrange(n), rng.randrange(1_000_000)) for _ in range(updates)]
    qpos = [rng.randrange(1, n + 1) for _ in range(queries // 2)]
    qpl = [rng.randrange(n) for _ in range(queries // 2)]

    res = {}
    boards = {}
    for name, cls in (("AVL", Leaderboard), ("List", ListLeaderboard)):
        b = cls()

        def load():
            for p in range(n):
                b.set_score(p, scores[p])
        t_load, _ = timed(load)

        def upd():
            for p, s in ups:
                b.set_score(p, s)
        t_up, _ = timed(upd)

        def qry():
            return ([b.at(k) for k in qpos], [b.rank_of(p) for p in qpl])
        t_q, answers = timed(qry)
        res[name] = dict(load=t_load, update=t_up, query=t_q, answers=answers)
        boards[name] = b
        print(f"{name:5} load {t_load:7.2f} s | {updates} updates {t_up:7.2f} s | {queries} queries {t_q*1000:7.2f} ms")
    assert res["AVL"]["answers"] == res["List"]["answers"], "leaderboards disagree!"
    assert boards["AVL"].top(50) == boards["List"].top(50)
    assert boards["AVL"].tree.is_valid()
    print("both leaderboards give identical answers; AVL tree valid, height",
          boards["AVL"].tree.root.height)
    return res


def scaling(sizes=(200_000, 1_000_000, 2_000_000), updates=2000, seed=3):
    rows = []
    for n in sizes:
        rng = random.Random(seed)
        pairs = sorted((-rng.randrange(10_000_000), p) for p in range(n))
        score = {p: -neg for neg, p in pairs}
        ups = [(rng.randrange(n), rng.randrange(10_000_000)) for _ in range(updates)]
        row = {"n": n}

        # AVL (built balanced in O(n) to save time)
        b = Leaderboard()
        b.tree = OSTree.from_sorted(pairs)
        b.score = dict(score)
        dt, _ = timed(lambda: [b.set_score(p, s) for p, s in ups])
        row["avl_us"] = dt / updates * 1e6
        del b
        gc.collect()

        # sorted list
        b = ListLeaderboard()
        b.data = list(pairs)
        b.score = dict(score)
        dt, _ = timed(lambda: [b.set_score(p, s) for p, s in ups])
        row["list_us"] = dt / updates * 1e6
        del b, pairs, score
        gc.collect()
        rows.append(row)
        print(f"n={n:>9,}  AVL {row['avl_us']:9.1f} us/update   list {row['list_us']:9.1f} us/update")
    return rows


if __name__ == "__main__":
    import json
    self_test()
    print("self test passed")
    main = main_experiment()
    out = {k: {kk: vv for kk, vv in v.items() if kk != "answers"} for k, v in main.items()}
    sc = scaling()
    with open("leaderboard_results.json", "w") as f:
        json.dump({"main": out, "scaling": sc}, f, indent=1)
