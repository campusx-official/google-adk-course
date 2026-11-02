"""Selection Sort Algorithm Implementation."""

from typing import List


def selection_sort(arr: List[int]) -> List[int]:
    """Sorts an array using the Selection Sort algorithm.
    
    Time Complexity: O(n^2) for all cases.
    Space Complexity: O(1).
    """
    n = len(arr)
    arr = arr.copy()
    for i in range(n):
        min_idx = i
        for j in range(i + 1, n):
            if arr[j] < arr[min_idx]:
                min_idx = j
        arr[i], arr[min_idx] = arr[min_idx], arr[i]
    return arr


if __name__ == "__main__":
    sample_data = [64, 25, 12, 22, 11]
    print("Original:", sample_data)
    sorted_data = selection_sort(sample_data)
    print("Sorted:", sorted_data)
