"""Insertion Sort Algorithm Implementation."""

from typing import List


def insertion_sort(arr: List[int]) -> List[int]:
    """Sorts an array using the Insertion Sort algorithm.
    
    Time Complexity: O(n^2) worst/average, O(n) best case.
    Space Complexity: O(1).
    """
    arr = arr.copy()
    for i in range(1, len(arr)):
        key = arr[i]
        j = i - 1
        while j >= 0 and arr[j] > key:
            arr[j + 1] = arr[j]
            j -= 1
        arr[j + 1] = key
    return arr


if __name__ == "__main__":
    sample_data = [12, 11, 13, 5, 6]
    print("Original:", sample_data)
    sorted_data = insertion_sort(sample_data)
    print("Sorted:", sorted_data)
