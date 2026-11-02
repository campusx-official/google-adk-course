"""Radix Sort Algorithm Implementation."""

from typing import List


def _counting_sort_for_radix(arr: List[int], exp: int) -> List[int]:
    n = len(arr)
    output = [0] * n
    count = [0] * 10

    for i in range(n):
        index = (arr[i] // exp) % 10
        count[index] += 1

    for i in range(1, 10):
        count[i] += count[i - 1]

    for i in range(n - 1, -1, -1):
        index = (arr[i] // exp) % 10
        output[count[index] - 1] = arr[i]
        count[index] -= 1

    return output


def radix_sort(arr: List[int]) -> List[int]:
    """Sorts an array of non-negative integers using Radix Sort algorithm.
    
    Time Complexity: O(d * (n + k)) where d is digits count, k is base (10).
    Space Complexity: O(n + k).
    """
    if not arr:
        return []

    arr = arr.copy()
    max_val = max(arr)

    exp = 1
    while max_val // exp > 0:
        arr = _counting_sort_for_radix(arr, exp)
        exp *= 10

    return arr


if __name__ == "__main__":
    sample_data = [170, 45, 75, 90, 802, 24, 2, 66]
    print("Original:", sample_data)
    sorted_data = radix_sort(sample_data)
    print("Sorted:", sorted_data)
