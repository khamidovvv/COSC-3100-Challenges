"""Week 3B Lab - B-Trees: STARTER CODE.

Complete every method marked TODO. Run this file to test your work:
    python lab3b_starter.py
Each test prints PASS, FAIL or TODO. Do not change the test functions.
"""
import bisect
import random
import time


class BNode:
    __slots__ = ("keys", "children", "leaf")

    def __init__(self, leaf=True):
        self.keys = []
        self.children = []
        self.leaf = leaf


class BTree:
    def __init__(self, t=2):
        if t < 2:
            raise ValueError("minimum degree t must be at least 2")
        self.t = t
        self.root = BNode(True)
        self.reads = 0  # node visits (simulated disk reads)
        self.writes = 0  # nodes created or modified by splits / merges
        self.splits = 0
        self.merges = 0

    # ------------------------------------------------------------ search
    def search(self, key):
        """TODO B1: walk down from the root; use bisect_left in each node; add 1 to
                self.reads per node."""
        node = self.root

        while True:
            self.reads += 1

            i = bisect.bisect_left(node.keys, key)

            if i < len(node.keys) and node.keys[i] == key:
                return True

            if node.leaf:
                return False

            node = node.children[i]

    # ------------------------------------------------------------ insert

    def insert(self, key):
        # Ignore duplicate keys
        if self.search(key):
            return

        # Split the root if it is full
        if len(self.root.keys) == 2 * self.t - 1:
            new_root = BNode(False)
            new_root.children.append(self.root)

            self._split_child(new_root, 0)
            self.root = new_root

        self._insert_nonfull(self.root, key)


    def _split_child(self, parent, i):
        t = self.t
        child = parent.children[i]
        new_child = BNode(child.leaf)

        median = child.keys[t - 1]

        new_child.keys = child.keys[t:]
        child.keys = child.keys[:t - 1]

        if not child.leaf:
            new_child.children = child.children[t:]
            child.children = child.children[:t]

        parent.keys.insert(i, median)
        parent.children.insert(i + 1, new_child)

        self.splits += 1
        self.writes += 3


    def _insert_nonfull(self, node, key):
        while True:
            i = bisect.bisect_left(node.keys, key)

            if node.leaf:
                node.keys.insert(i, key)
                self.writes += 1
                return

            # Split a full child before descending
            if len(node.children[i].keys) == 2 * self.t - 1:
                self._split_child(node, i)

                if key > node.keys[i]:
                    i += 1

            node = node.children[i]

    # ------------------------------------------------------------ delete (PROVIDED)
    # Part D2: replace every "# CASE ?" with the case number (1, 2a, 2b, 2c, 3a or 3b)
    # from the deletion decision table, and explain each branch in one comment line.
    def delete(self, key):
        self._delete(self.root, key)
        if not self.root.keys and not self.root.leaf:  # tree shrinks at the ROOT
            self.root = self.root.children[0]

    def _delete(self, node, key):
        t = self.t
        self.reads += 1
        i = bisect.bisect_left(node.keys, key)
        found = i < len(node.keys) and node.keys[i] == key
        if node.leaf:  # CASE 1: Delete the key directly from a leaf
            if found:
                node.keys.pop(i)
                self.writes += 1
            return
        if found:
            left, right = node.children[i], node.children[i + 1]
            if len(left.keys) >= t:  # CASE 2a	Replace the key with its predecessor
                pred = self._max_key(left)
                node.keys[i] = pred
                self._delete(left, pred)
            elif len(right.keys) >= t:  # CASE 2b Replace the key with its successor
                succ = self._min_key(right)
                node.keys[i] = succ
                self._delete(right, succ)
            else:  # CASE 2c	Merge both children with the separator key
                self._merge(node, i)
                self._delete(left, key)
            return
        child = node.children[i]  # CASE 3	Key is not in this node; prepare child before descending
        if len(child.keys) == t - 1:
            i = self._fill(node, i)
        self._delete(node.children[i], key)

    def _max_key(self, node):
        while not node.leaf:
            self.reads += 1
            node = node.children[-1]
        return node.keys[-1]

    def _min_key(self, node):
        while not node.leaf:
            self.reads += 1
            node = node.children[0]
        return node.keys[0]

    def _fill(self, node, i):
        """Give child i at least t keys; return the index of the child to descend into."""
        t = self.t
        if i > 0 and len(node.children[i - 1].keys) >= t:  # CASE 3a	Borrow from the left sibling
            child, sib = node.children[i], node.children[i - 1]
            child.keys.insert(0, node.keys[i - 1])
            node.keys[i - 1] = sib.keys.pop()
            if not sib.leaf:
                child.children.insert(0, sib.children.pop())
            self.writes += 3
            return i
        if i < len(node.children) - 1 and len(node.children[i + 1].keys) >= t:  # CASE 3a	Borrow from the right sibling
            child, sib = node.children[i], node.children[i + 1]
            child.keys.append(node.keys[i])
            node.keys[i] = sib.keys.pop(0)
            if not sib.leaf:
                child.children.append(sib.children.pop(0))
            self.writes += 3
            return i
        if i < len(node.children) - 1:  # CASE 3b	Merge child with right sibling
            self._merge(node, i)
            return i
        self._merge(node, i - 1)  # CASE 3b	Merge child with left sibling
        return i - 1

    def _merge(self, node, i):
        """Merge child i, separator key i and child i+1 into child i."""
        left, right = node.children[i], node.children[i + 1]
        left.keys.append(node.keys.pop(i))
        left.keys.extend(right.keys)
        left.children.extend(right.children)
        node.children.pop(i + 1)
        self.merges += 1
        self.writes += 2

    # ------------------------------------------------------------ queries and stats

    def range(self, lo, hi):
        """TODO B2: return all keys lo <= k <= hi in order; skip children that cannot
                contain keys in range."""
        result = []

        if lo > hi:
            return result

        def traverse(node):
            self.reads += 1

            for i, key in enumerate(node.keys):
                if key >= lo and not node.leaf:
                    traverse(node.children[i])

                if lo <= key <= hi:
                    result.append(key)

                if key > hi:
                    return

            if not node.leaf:
                traverse(node.children[-1])

        traverse(self.root)
        return result


    def inorder(self):
        out = []

        def go(node):
            for j, k in enumerate(node.keys):
                if not node.leaf:
                    go(node.children[j])
                out.append(k)
            if not node.leaf:
                go(node.children[-1])

        go(self.root)
        return out

    def height(self):
        """Edges from root to a leaf (a single leaf root has height 0)."""
        h, node = 0, self.root
        while not node.leaf:
            node = node.children[0]
            h += 1
        return h

    def node_count(self):
        def go(n):
            return 1 + sum(go(c) for c in n.children)

        return go(self.root)


    def fill_factor(self):
        """Average keys per node as a fraction of the maximum 2t-1."""
        nodes, keys = 0, 0
        stack = [self.root]
        while stack:
            n = stack.pop()
            nodes += 1
            keys += len(n.keys)
            stack.extend(n.children)
        return keys / (nodes * (2 * self.t - 1))


    def to_tuple(self, node=None):
        node = node or self.root
        return (tuple(node.keys), tuple(self.to_tuple(c) for c in node.children))


    def is_valid(self):
        t = self.t
        leaf_depths = set()

        def check(node, low, high, depth, is_root=False):
            keys = node.keys
            n = len(keys)

            # Check number of keys
            if is_root:
                assert n <= 2 * t - 1, "Root has too many keys"
                if not node.leaf:
                    assert n >= 1, "Internal root is empty"
            else:
                assert t - 1 <= n <= 2 * t - 1, "Invalid node size"

            # Check sorted keys
            assert keys == sorted(keys), "Keys are not sorted"
            assert len(keys) == len(set(keys)), "Duplicate keys found"

            # Check separator bounds
            for key in keys:
                if low is not None:
                    assert key > low, "Key below lower bound"
                if high is not None:
                    assert key < high, "Key above upper bound"

            if node.leaf:
                assert len(node.children) == 0, "Leaf has children"
                leaf_depths.add(depth)
            else:
                assert len(node.children) == n + 1, "Wrong child count"

                for i, child in enumerate(node.children):
                    child_low = low if i == 0 else keys[i - 1]
                    child_high = high if i == n else keys[i]

                    check(child, child_low, child_high, depth + 1)

        check(self.root, None, None, 0, True)

        assert len(leaf_depths) == 1, "Leaves have different depths"

        return True


# ======================================================== tests (do not edit)
def run(name, fn):
    try:
        fn()
        print(f"PASS  {name}")
    except NotImplementedError:
        print(f"TODO  {name}")
    except AssertionError as e:
        print(f"FAIL  {name}  {e}")


def test_search():
    b = BTree(2)
    b.root = BNode(False)
    b.root.keys = [20]
    l, r = BNode(True), BNode(True)
    l.keys, r.keys = [5, 10], [30, 40, 50]
    b.root.children = [l, r]
    assert b.search(40) and not b.search(35), "search gives wrong answer"
    b.reads = 0
    b.search(50)
    assert b.reads == 2, "a search for 50 should read exactly 2 nodes"
    assert b.range(8, 40) == [10, 20, 30, 40], "range(8, 40) is wrong"


def test_split():
    b = BTree(3)
    parent, child = BNode(False), BNode(True)
    parent.keys, child.keys = [100], [10, 20, 30, 40, 50]
    parent.children = [child, BNode(True)]
    parent.children[1].keys = [110, 120]
    b._split_child(parent, 0)
    assert parent.keys == [30, 100], "median must move up into the parent"
    halves = [c.keys for c in parent.children]
    assert halves == [[10, 20], [40, 50], [110, 120]], "split halves are wrong"


def test_insert():
    rng = random.Random(7)
    for t in (2, 3, 5):
        b = BTree(t)
        keys = rng.sample(range(10000), 3000)
        for k in keys:
            b.insert(k)
        assert b.is_valid(), f"invalid tree for t = {t}"
        assert b.inorder() == sorted(keys), f"keys lost or out of order for t = {t}"
    b = BTree(2)
    for k in range(1, 8):
        b.insert(k)
    expected = ((2, 4), (((1,), ()), ((3,), ()), ((5, 6, 7), ())))
    assert b.to_tuple() == expected, "t = 2, keys 1..7 gives the wrong shape"


def test_validator():
    b = BTree(2)
    for k in range(20):
        b.insert(k)
    assert b.is_valid() is True
    b.root.children[0].keys.append(999)  # break the order
    try:
        b.is_valid()
        raise AssertionError("validator accepted a tree with a key out of order")
    except AssertionError as e:
        if "accepted" in str(e):
            raise


def test_delete():
    rng = random.Random(3)
    b, ref = BTree(3), set()
    for _ in range(4000):
        k = rng.randrange(800)
        if rng.random() < 0.55:
            b.insert(k);
            ref.add(k)
        else:
            b.delete(k);
            ref.discard(k)
    assert b.is_valid() and b.inorder() == sorted(ref), "delete broke the tree"


if __name__ == "__main__":
    run("Part B  search, read counter and range", test_search)
    run("Part C  split_child", test_split)
    run("Part C  insert (t = 2, 3, 5)", test_insert)
    run("Part C  validator detects a broken tree", test_validator)
    run("Part D  provided delete still works", test_delete)