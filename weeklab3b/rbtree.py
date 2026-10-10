"""Week 3 Lab - reference Red-Black tree (CLRS insertion, sentinel NIL).

Provided for Part E and the mini challenge. You do not need to modify it.
    from rbtree import RBTree
    t = RBTree(); t.insert(5); t.search(5); t.height(); t.is_valid()
"""

# ------------------------------------------------------------------ Red-Black
RED, BLACK = 0, 1


class RBNode:
    __slots__ = ("key", "color", "left", "right", "parent")

    def __init__(self, key, color, nil):
        self.key = key
        self.color = color
        self.left = nil
        self.right = nil
        self.parent = nil


class RBTree:
    """Red-Black tree following CLRS (sentinel NIL node)."""

    def __init__(self):
        self.NIL = RBNode(None, BLACK, None)
        self.NIL.left = self.NIL.right = self.NIL.parent = self.NIL
        self.root = self.NIL
        self.rotations = 0
        self.recolors = 0

    def rotate_left(self, x):
        y = x.right
        x.right = y.left
        if y.left is not self.NIL:
            y.left.parent = x
        y.parent = x.parent
        if x.parent is self.NIL:
            self.root = y
        elif x is x.parent.left:
            x.parent.left = y
        else:
            x.parent.right = y
        y.left = x
        x.parent = y
        self.rotations += 1

    def rotate_right(self, y):
        x = y.left
        y.left = x.right
        if x.right is not self.NIL:
            x.right.parent = y
        x.parent = y.parent
        if y.parent is self.NIL:
            self.root = x
        elif y is y.parent.right:
            y.parent.right = x
        else:
            y.parent.left = x
        x.right = y
        y.parent = x
        self.rotations += 1

    def insert(self, key):
        parent, cur = self.NIL, self.root
        while cur is not self.NIL:
            parent = cur
            if key < cur.key:
                cur = cur.left
            elif key > cur.key:
                cur = cur.right
            else:
                return  # duplicate
        z = RBNode(key, RED, self.NIL)
        z.parent = parent
        if parent is self.NIL:
            self.root = z
        elif key < parent.key:
            parent.left = z
        else:
            parent.right = z
        self._fix_insert(z)

    def _fix_insert(self, z):
        while z.parent.color == RED:
            gp = z.parent.parent
            if z.parent is gp.left:
                uncle = gp.right
                if uncle.color == RED:  # Case 1: recolor
                    z.parent.color = BLACK
                    uncle.color = BLACK
                    gp.color = RED
                    self.recolors += 3
                    z = gp
                else:
                    if z is z.parent.right:  # Case 2: triangle
                        z = z.parent
                        self.rotate_left(z)
                    z.parent.color = BLACK  # Case 3: line
                    gp.color = RED
                    self.recolors += 2
                    self.rotate_right(gp)
            else:  # mirror image
                uncle = gp.left
                if uncle.color == RED:
                    z.parent.color = BLACK
                    uncle.color = BLACK
                    gp.color = RED
                    self.recolors += 3
                    z = gp
                else:
                    if z is z.parent.left:
                        z = z.parent
                        self.rotate_right(z)
                    z.parent.color = BLACK
                    gp.color = RED
                    self.recolors += 2
                    self.rotate_left(gp)
        if self.root.color == RED:
            self.recolors += 1
        self.root.color = BLACK

    def search(self, key):
        cur = self.root
        while cur is not self.NIL:
            if key == cur.key:
                return True
            cur = cur.left if key < cur.key else cur.right
        return False

    def height(self):
        def go(n):
            if n is self.NIL:
                return -1
            return 1 + max(go(n.left), go(n.right))

        return go(self.root)

    def inorder(self):
        out = []

        def go(n):
            if n is not self.NIL:
                go(n.left)
                out.append(n.key)
                go(n.right)
            go(self.root)
            return out

        def is_valid(self):
            """Checks the 5 red-black properties; returns black-height."""
            if self.root.color != BLACK:
                raise AssertionError("root must be black")

            def check(n, lo, hi):
                if n is self.NIL:
                    return 1
                if (lo is not None and n.key <= lo) or (hi is not None and n.key >= hi):
                    raise AssertionError("BST order broken")
                if n.color == RED and (n.left.color == RED or n.right.color == RED):
                    raise AssertionError(f"red node {n.key} has red child")
                lb = check(n.left, lo, n.key)
                rb = check(n.right, n.key, hi)
                if lb != rb:
                    raise AssertionError(f"black-height mismatch at {n.key}")
                return lb + (1 if n.color == BLACK else 0)

            return check(self.root, None, None)