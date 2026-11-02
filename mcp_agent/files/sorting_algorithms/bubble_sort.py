"""Bubble Sort Algorithm Implementation."""

from typing import List


def bubble_sort(arr: List[int]) -> List[int]:
    """Sorts an array using the Bubble Sort algorithm.
    
    Time Complexity: O(n^2) worst/average, O(n) best case (with optimization).
    Space Complexity: O(1).
    """
    n = len(arr)
    arr = arr.copy()
    for i in range(n):
        swapped = False
        for j in range(0, n - i - 1):
            if arr[j] > arr[j + 1]:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
                swapped = True
        if not swapped:
            break
    return arr


if __name__ == "__main__":
    sample_data = [64, 34, 25, 12, 22, 11, 90]
    print("Original:", sample_data)
    sorted_data = bubble_sort(sample_data)
    print("Sorted:", sorted_data)
