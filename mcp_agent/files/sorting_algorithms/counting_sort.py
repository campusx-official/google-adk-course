"""Counting Sort Algorithm Implementation."""

from typing import List


def counting_sort(arr: List[int]) -> List[int]:
    """Sorts an array of non-negative integers using Counting Sort algorithm.
    
    Time Complexity: O(n + k) where k is the maximum element.
    Space Complexity: O(k).
    """
    if not arr:
        return []

    max_val = max(arr)
    min_val = min(arr)
    range_val = max_val - min_val + 1

    count = [0] * range_val
    output = [0] * len(arr)

    for num in arr:
        count[num - min_val] += 1

    for i in range(1, len(count)):
        count[i] += count[i - 1]

    for num in reversed(arr):
        output[count[num - min_val] - 1] = num
        count[num - min_val] -= 1

    return output


if __name__ == "__main__":
    sample_data = [4, 2, 2, 8, 3, 3, 1]
    print("Original:", sample_data)
    sorted_data = counting_sort(sample_data)
    print("Sorted:", sorted_data)
