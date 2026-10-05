# Validate a Binary Search Tree

class Node:
    def __init__(self, data):
        self.data = data
        self.left = None
        self.right = None


def is_valid_bst(root, minimum=float('-inf'), maximum=float('inf')):
    if root is None:
        return True

    if root.data <= minimum or root.data >= maximum:
        return False

    return (
        is_valid_bst(root.left, minimum, root.data)
        and
        is_valid_bst(root.right, root.data, maximum)
    )


root = Node(10)
root.left = Node(5)
root.right = Node(15)
root.left.left = Node(2)
root.left.right = Node(7)

print(is_valid_bst(root))