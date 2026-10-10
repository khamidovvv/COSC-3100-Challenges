
import bisect
import random
import time

from lab3b import BTree
from rbtree import RBTree


def run(make, keys, probe):
    tree = make()

    start = time.perf_counter()

    for key in keys:
        tree.insert(key)

    build_s = time.perf_counter() - start

    if isinstance(tree, BTree):
        tree.reads = 0

    start = time.perf_counter()

    for key in probe:
        tree.search(key)

    search_us = (
        time.perf_counter() - start
    ) * 1_000_000 / len(probe)

    if isinstance(tree, BTree):
        reads_per_search = tree.reads / len(probe)
    else:
        reads_per_search = None

    return (
        build_s,
        search_us,
        reads_per_search,
        tree.height()
    )


def run_sorted_list(keys, probe):
    data = []

    start = time.perf_counter()

    for key in keys:
        bisect.insort(data, key)

    build_s = time.perf_counter() - start

    start = time.perf_counter()

    for key in probe:
        i = bisect.bisect_left(data, key)
        found = i < len(data) and data[i] == key

    search_us = (
        time.perf_counter() - start
    ) * 1_000_000 / len(probe)

    return build_s, search_us, None, None


random.seed(42)

keys = random.sample(range(1_000_000), 100_000)
probe = random.sample(keys, 5_000)

print(f"{'Structure':<20} {'Build(s)':>10} {'Search(us)':>12} {'Reads':>10} {'Height':>8}")

results = {}

for degree in [2, 4, 16, 64, 256]:
    name = f"B-tree t={degree}"
    result = run(lambda d=degree: BTree(d), keys, probe)
    results[name] = result

result = run(RBTree, keys, probe)
results["Red-Black"] = result

results["Sorted list"] = run_sorted_list(keys, probe)

for name, (build, search, reads, height) in results.items():
    reads_text = f"{reads:.2f}" if reads is not None else "N/A"
    height_text = str(height) if height is not None else "N/A"

    print(
        f"{name:<20} "
        f"{build:>10.3f} "
        f"{search:>12.3f} "
        f"{reads_text:>10} "
        f"{height_text:>8}"
    )



import matplotlib.pyplot as plt

degrees = [2, 4, 16, 64, 256]

heights = [
    results[f"B-tree t={t}"][3]
    for t in degrees
]

reads = [
    results[f"B-tree t={t}"][2]
    for t in degrees
]

search_times = [
    results[f"B-tree t={t}"][1]
    for t in degrees
]

rb_height = results["Red-Black"][3]

# Plot 1: Height comparison
plt.figure(figsize=(8, 5))
plt.plot(degrees, heights, marker="o", label="B-Tree")
plt.axhline(
    y=rb_height,
    linestyle="--",
    label="Red-Black Tree"
)
plt.xscale("log", base=2)
plt.xticks(degrees, degrees)
plt.xlabel("Minimum Degree (t)")
plt.ylabel("Tree Height")
plt.title("B-Tree Height vs Minimum Degree")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.savefig("height_plot.png", dpi=300)
plt.close()

# Plot 2: Reads and search time
fig, ax1 = plt.subplots(figsize=(8, 5))

ax1.plot(
    degrees, reads,
    marker="o", label="Page Reads"
)
ax1.set_xlabel("Minimum Degree (t)")
ax1.set_ylabel("Average Page Reads")
ax1.set_xscale("log", base=2)
ax1.set_xticks(degrees, degrees)

ax2 = ax1.twinx()
ax2.plot(
    degrees, search_times,
    marker="s", linestyle="--",
    label="Search Time"
)
ax2.set_ylabel("Search Time (microseconds)")

plt.title("B-Tree Search Performance")
fig.tight_layout()
plt.savefig("search_plot.png", dpi=300)
plt.close()

print("Both plots saved successfully!")