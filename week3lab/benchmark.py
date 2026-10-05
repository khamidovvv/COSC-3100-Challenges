import random
import time
from week3_lab import BST, AVLTree
from rbtree import RBTree
import matplotlib.pyplot as plt
import math

import bisect


class SortedList:
    def __init__(self):
        self.data = []

    def insert(self, key):
        bisect.insort(self.data, key)

    def search(self, key):
        i = bisect.bisect_left(self.data, key)
        return i < len(self.data) and self.data[i] == key

    def height(self):
        return 0

def run(cls, keys):
    t = cls()

    start = time.perf_counter()

    for key in keys:
        t.insert(key)

    insert_ms = (time.perf_counter() - start) * 1000

    probe = random.sample(keys, 1000)

    start = time.perf_counter()

    for key in probe:
        t.search(key)

    search_ms = (time.perf_counter() - start) * 1000

    return insert_ms, search_ms, t.height()

sizes = [1000, 2000, 4000, 8000]

for n in sizes:
    print(f"\n--- n = {n} ---")

    sorted_keys = list(range(n))

    random_keys = list(range(n))
    random.shuffle(random_keys)

    print("List random:", run(SortedList, random_keys))
    print("List sorted:", run(SortedList, sorted_keys))

    print("BST random:", run(BST, random_keys))
    print("BST sorted:", run(BST, sorted_keys))

    print("AVL random:", run(AVLTree, random_keys))
    print("AVL sorted:", run(AVLTree, sorted_keys))

    print("RB random:", run(RBTree, random_keys))
    print("RB sorted:", run(RBTree, sorted_keys))




random_bst_heights = []
random_avl_heights = []
random_rb_heights = []

sorted_bst_heights = []
sorted_avl_heights = []
sorted_rb_heights = []

for n in sizes:
    sorted_keys = list(range(n))

    random_keys = list(range(n))
    random.shuffle(random_keys)

    random_bst_heights.append(run(BST, random_keys)[2])
    random_avl_heights.append(run(AVLTree, random_keys)[2])
    random_rb_heights.append(run(RBTree, random_keys)[2])

    sorted_bst_heights.append(run(BST, sorted_keys)[2])
    sorted_avl_heights.append(run(AVLTree, sorted_keys)[2])
    sorted_rb_heights.append(run(RBTree, sorted_keys)[2])


log_values = [math.log2(n) for n in sizes]

plt.figure()

plt.plot(
    sizes,
    random_bst_heights,
    marker="o",
    label="BST"
)

plt.plot(
    sizes,
    random_avl_heights,
    marker="o",
    label="AVL"
)

plt.plot(
    sizes,
    random_rb_heights,
    marker="o",
    label="Red-Black"
)

plt.plot(
    sizes,
    log_values,
    linestyle="--",
    label="log2(n)"
)

plt.xlabel("Number of keys (n)")
plt.ylabel("Tree height")
plt.title("Tree Height with Random Input")
plt.legend()
plt.grid()

plt.savefig("random_height.png")
plt.close()



plt.figure()

plt.plot(
    sizes,
    sorted_bst_heights,
    marker="o",
    label="BST"
)

plt.plot(
    sizes,
    sorted_avl_heights,
    marker="o",
    label="AVL"
)

plt.plot(
    sizes,
    sorted_rb_heights,
    marker="o",
    label="Red-Black"
)

plt.xlabel("Number of keys (n)")
plt.ylabel("Tree height")
plt.title("Tree Height with Sorted Input")

plt.yscale("log")

plt.legend()
plt.grid()

plt.savefig("sorted_height.png")
plt.close()

print("\nPlots saved:")
print("random_height.png")
print("sorted_height.png")