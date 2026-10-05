def binary_search(array, key, lowest=0, highest=None):
    if highest is None:
        highest = len(array) - 1

    if lowest > highest:
        return -1

    middle = (lowest + highest) // 2

    if array[middle] == key:
        return middle

    if key < array[middle]:
        return binary_search(array, key, lowest, middle - 1)

    return binary_search(array, key, middle + 1, highest)


array = [10, 20, 30, 40, 50]
key = 30

print(binary_search(array, key))