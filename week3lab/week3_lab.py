"""Week 3 Lab - Advanced Trees: starter code.

Fill in every function marked TODO. Run this file to test your work:
    python week3_lab_starter.py
Each test prints PASS, FAIL or TODO. Do not change the test functions.
"""
import bisect
import random
import sys
import time

sys.setrecursionlimit(10000)


# ======================================================== Part A: plain BST
class BSTNode:
    def __init__(self, key):
        self.key = key
        self.left = None
        self.right = None


class BST:
    def __init__(self):
        self.root = None

    def insert(self, key):
        new_node = BSTNode(key)

        if self.root is None:
            self.root = new_node
            return

        current = self.root

        while True:
            if key < current.key:
                if current.left is None:
                    current.left = new_node
                    return
                current = current.left

            elif key > current.key:
                if current.right is None:
                    current.right = new_node
                    return
                current = current.right

            else:
                return

    def search(self, key):
        current = self.root

        while current:
            if key == current.key:
                return True

            if key < current.key:
                current = current.left
            else:
                current = current.right

        return False

    def height(self):
        if self.root is None:
            return -1

        stack = [(self.root, 0)]
        max_height = 0

        while stack:
            node, depth = stack.pop()
            max_height = max(max_height, depth)

            if node.left:
                stack.append((node.left, depth + 1))

            if node.right:
                stack.append((node.right, depth + 1))

        return max_height


# ======================================================== Part B: rotations
def rotate_left(x):
    y = x.right
    t2 = y.left

    y.left = x
    x.right = t2

    return y


def rotate_right(y):
    x = y.left
    t2 = x.right

    x.right = y
    y.left = t2

    return x


# ======================================================== Part C: AVL tree
class AVLNode:
    def __init__(self, key):
        self.key = key
        self.left = None
        self.right = None
        self.height = 0


def h(node):
    return node.height if node else -1


def update(node):
    node.height = 1 + max(h(node.left), h(node.right))


def balance(node):
    return h(node.left) - h(node.right)


class AVLTree:
    def __init__(self):
        self.root = None
        self.rotations = 0

    def rotate_left(self, x):
        y = x.right
        t2 = y.left

        y.left = x
        x.right = t2

        update(x)
        update(y)

        self.rotations += 1
        return y

    def rotate_right(self, y):
        x = y.left
        t2 = x.right

        x.right = y
        y.left = t2

        update(y)
        update(x)

        self.rotations += 1
        return x

    def rebalance(self, node):
        update(node)

        bf = balance(node)

        # LL
        if bf > 1 and balance(node.left) >= 0:
            return self.rotate_right(node)

        # LR
        if bf > 1 and balance(node.left) < 0:
            node.left = self.rotate_left(node.left)
            return self.rotate_right(node)

        # RR
        if bf < -1 and balance(node.right) <= 0:
            return self.rotate_left(node)

        # RL
        if bf < -1 and balance(node.right) > 0:
            node.right = self.rotate_right(node.right)
            return self.rotate_left(node)

        return node

    def insert(self, key):
        self.root = self._insert(self.root, key)

    def _insert(self, node, key):
        if node is None:
            return AVLNode(key)

        if key < node.key:
            node.left = self._insert(node.left, key)

        elif key > node.key:
            node.right = self._insert(node.right, key)

        else:
            return node

        return self.rebalance(node)

    def search(self, key):
        cur = self.root

        while cur:
            if key == cur.key:
                return True

            cur = cur.left if key < cur.key else cur.right

        return False

    def height(self):
        return h(self.root)

    def is_valid(self):
        def check(node, low, high):
            if node is None:
                return True, -1

            if low is not None and node.key <= low:
                return False, 0

            if high is not None and node.key >= high:
                return False, 0

            left_valid, left_height = check(
                node.left,
                low,
                node.key
            )

            if not left_valid:
                return False, 0

            right_valid, right_height = check(
                node.right,
                node.key,
                high
            )

            if not right_valid:
                return False, 0

            expected_height = 1 + max(
                left_height,
                right_height
            )

            if node.height != expected_height:
                return False, 0

            bf = left_height - right_height

            if bf < -1 or bf > 1:
                return False, 0

            return True, expected_height

        valid, _ = check(self.root, None, None)
        return valid
# ======================================================== Part D: Red-Black validator
# A Red-Black tree is given as nested tuples: (key, colour, left, right)
# where colour is "R" or "B" and an empty child (NIL) is None.
def is_valid_rb(t):
    if t is None:
        return True, 1

    if t[1] != "B":
        return False, "root must be black"

    def check(node, low, high):
        if node is None:
            return 1

        key, color, left, right = node

        if color not in ("R", "B"):
            raise ValueError("invalid colour")

        if low is not None and key <= low:
            raise ValueError("BST order broken")

        if high is not None and key >= high:
            raise ValueError("BST order broken")

        if color == "R":
            if left is not None and left[1] == "R":
                raise ValueError(f"red node {key} has red child")

            if right is not None and right[1] == "R":
                raise ValueError(f"red node {key} has red child")

        left_bh = check(left, low, key)
        right_bh = check(right, key, high)

        if left_bh != right_bh:
            raise ValueError(f"black-height mismatch at {key}")

        return left_bh + (1 if color == "B" else 0)

    try:
        black_height = check(t, None, None)
        return True, black_height

    except ValueError as e:
        return False, str(e)

# ======================================================== tests (do not edit)
def run(name, fn):
    try:
        fn()
        print(f"PASS  {name}")
    except NotImplementedError:
        print(f"TODO  {name}")
    except AssertionError as e:
        print(f"FAIL  {name}  {e}")


def inorder(n, out):
    if n:
        inorder(n.left, out)
        out.append(n.key)
        inorder(n.right, out)
    return out


def test_bst():
    t = BST()
    for k in range(2000):
        t.insert(k)
    assert t.height() == 1999, "sorted input should give a chain"
    assert t.search(1234) and not t.search(5000)


def test_rotations():
    rng = random.Random(0)
    for _ in range(100):
        t = BST()
        for k in rng.sample(range(500), 40):
            t.insert(k)
        before = inorder(t.root, [])
        t.root = rotate_left(t.root) if t.root.right else rotate_right(t.root)
        assert inorder(t.root, []) == before, "rotation changed the in-order sequence"


def test_avl():
    rng = random.Random(1)
    for order in ("sorted", "random"):
        keys = list(range(3000))
        if order == "random":
            rng.shuffle(keys)
        t = AVLTree()
        for k in keys:
            t.insert(k)
        assert t.is_valid(), f"invalid AVL tree ({order} input)"
        assert t.height() <= 1.44 * 11.56 + 1, "AVL tree too tall"


def test_rb():
    good = (13, "B", (8, "R", (1, "B", None, None), (11, "B", None, None)),
            (17, "R", (15, "B", None, None), (25, "B", None, None)))
    red_red = (20, "B", (10, "B", None, None), (30, "B", (25, "R", None, (27, "R", None, None)), None))
    assert is_valid_rb(good) == (True, 3), "tree 1 is valid with black-height 3 (counting NIL)"
    assert is_valid_rb(red_red)[0] is False, "tree 2 has a red node with a red child"


if __name__ == "__main__":
    run("Part A  BST on 2,000 sorted keys", test_bst)
    run("Part B  rotations keep in-order", test_rotations)
    run("Part C  AVL insert + validator", test_avl)
    run("Part D  Red-Black validator", test_rb)