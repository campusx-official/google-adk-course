"""Quick Sort Algorithm Implementation."""

from typing import List


def quick_sort(arr: List[int]) -> List[int]:
    """Sorts an array using the Quick Sort algorithm.
    
    Time Complexity: O(n log n) average/best, O(n^2) worst case.
    Space Complexity: O(log n) auxiliary space.
    """
    if len(arr) <= 1:
        return arr

    pivot = arr[len(arr) // 2]
    left = [x for x in arr if x < pivot]
    middle = [x for x in arr if x == pivot]
    right = [x for x in arr if x > pivot]

    return quick_sort(left) + middle + quick_sort(right)


if __name__ == "__main__":
    sample_data = [10, 7, 8, 9, 1, 5]
    print("Original:", sample_data)
    sorted_data = quick_sort(sample_data)
    print("Sorted:", sorted_data)
