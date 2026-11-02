"""Merge Sort Algorithm Implementation."""

from typing import List


def merge_sort(arr: List[int]) -> List[int]:
    """Sorts an array using the Merge Sort algorithm (Divide and Conquer).
    
    Time Complexity: O(n log n) in all cases.
    Space Complexity: O(n).
    """
    if len(arr) <= 1:
        return arr

    mid = len(arr) // 2
    left = merge_sort(arr[:mid])
    right = merge_sort(arr[mid:])

    return _merge(left, right)


def _merge(left: List[int], right: List[int]) -> List[int]:
    result = []
    i = j = 0

    while i < len(left) and j < len(right):
        if left[i] <= right[j]:
            result.append(left[i])
            i += 1
        else:
            result.append(right[j])
            j += 1

    result.extend(left[i:])
    result.extend(right[j:])
    return result


if __name__ == "__main__":
    sample_data = [38, 27, 43, 3, 9, 82, 10]
    print("Original:", sample_data)
    sorted_data = merge_sort(sample_data)
    print("Sorted:", sorted_data)
