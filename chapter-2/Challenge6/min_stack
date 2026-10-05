class MinStack:
    def __init__(self):
        self.stack = []
        self.min_stack = []

    def push(self, x) -> None:
        self.stack.append(x)
        current_min = x if not self.min_stack else min(x, self.min_stack[-1])
        self.min_stack.append(current_min)

    def pop(self) -> None:
        if not self.stack:
            raise IndexError("pop from empty stack")
        self.stack.pop()
        self.min_stack.pop()

    def top(self):
        if not self.stack:
            raise IndexError("top from empty stack")
        return self.stack[-1]

    def get_min(self):
        if not self.min_stack:
            raise IndexError("get_min from empty stack")
        return self.min_stack[-1]


if __name__ == "__main__":
    ms = MinStack()
    ms.push(3)
    ms.push(5)
    ms.push(2)
    assert ms.get_min() == 2
    ms.pop()
    assert ms.get_min() == 3
    assert ms.top() == 5
    empty_ms = MinStack()
    try:
        empty_ms.pop()
        assert False, "expected IndexError"
    except IndexError:
        pass
    print("All tests passed.")