# Challenge 4 - Tower of Hanoi

def hanoi(n, source, spare, target):
    if n == 1:
        print(f"Move disk 1 from {source} to {target}")
        return

    hanoi(n - 1, source, target, spare)

    print(f"Move disk {n} from {source} to {target}")

    hanoi(n - 1, spare, source, target)


hanoi(3, "A", "B", "C")