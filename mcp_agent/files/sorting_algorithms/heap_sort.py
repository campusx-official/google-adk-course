"""Heap Sort Algorithm Implementation."""

from typing import List


def heapify(arr: List[int], n: int, i: int) -> None:
    largest = i
    left = 2 * i + 1
    right = 2 * i + 2

    if left < n and arr[left] > arr[largest]:
        largest = left

    if right < n and arr[right] > arr[largest]:
        largest = right

    if largest != i:
        arr[i], arr[largest] = arr[largest], arr[i]
        heapify(arr, n, largest)


def heap_sort(arr: List[int]) -> List[int]:
    """Sorts an array using Heap Sort algorithm.
    
    Time Complexity: O(n log n) in all cases.
    Space Complexity: O(1) auxiliary space.
    """
    arr = arr.copy()
    n = len(arr)

    # Build max heap
    for i in range(n // 2 - 1, -1, -1):
        heapify(arr, n, i)

    # Extract elements one by one
    for i in range(n - 1, 0, -1):
        arr[i], arr[0] = arr[0], arr[i]
        heapify(arr, i, 0)

    return arr


if __name__ == "__main__":
    sample_data = [12, 11, 13, 5, 6, 7]
    print("Original:", sample_data)
    sorted_data = heap_sort(sample_data)
    print("Sorted:", sorted_data)
