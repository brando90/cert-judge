/* Binary search over a sorted array of integers.
 *
 * Edge cases:
 * - Empty array returns INT64_MIN (sentinel for "not found").
 * - Unsorted arrays are invalid (pre fails).
 *
 * Return: index if found, INT64_MIN if not found (sentinel for Optional[int]).
 */

#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>
#include <assert.h>

#define NOT_FOUND INT64_MIN

int pre_binary_search(const int64_t *arr, int n, int64_t target) {
    (void)target;
    if (arr == NULL && n != 0) return 0;
    for (int i = 0; i < n - 1; i++) {
        if (arr[i] > arr[i + 1]) return 0;
    }
    return 1;
}

/* Returns index of target in arr, or NOT_FOUND if not present. */
int64_t binary_search(const int64_t *arr, int n, int64_t target) {
    if (!pre_binary_search(arr, n, target)) {
        fprintf(stderr, "pre_binary_search failed\n");
        exit(1);
    }
    if (n == 0) return NOT_FOUND;

    int left = 0, right = n - 1;
    while (left <= right) {
        int mid = left + (right - left) / 2;
        if (arr[mid] == target) {
            return (int64_t)mid;
        } else if (arr[mid] < target) {
            left = mid + 1;
        } else {
            right = mid - 1;
        }
    }
    return NOT_FOUND;
}

int check(void) {
    /* Basic functionality tests */
    {
        int64_t a[] = {1, 2, 3, 4, 5};
        assert(binary_search(a, 5, 1) == 0);
        assert(binary_search(a, 5, 3) == 2);
        assert(binary_search(a, 5, 5) == 4);
        assert(binary_search(a, 5, 6) == NOT_FOUND);
        assert(binary_search(a, 5, 0) == NOT_FOUND);
    }

    /* Edge cases */
    assert(binary_search(NULL, 0, 1) == NOT_FOUND);
    {
        int64_t a[] = {5};
        assert(binary_search(a, 1, 5) == 0);
        assert(binary_search(a, 1, 3) == NOT_FOUND);
    }

    /* Larger arrays */
    {
        int64_t a[] = {1, 3, 5, 7, 9};
        assert(binary_search(a, 5, 3) == 1);
        assert(binary_search(a, 5, 7) == 3);
        assert(binary_search(a, 5, 4) == NOT_FOUND);
    }
    {
        int64_t a[] = {10, 20, 30, 40, 50, 60};
        assert(binary_search(a, 6, 60) == 5);
        assert(binary_search(a, 6, 10) == 0);
    }

    /* Test with duplicates */
    {
        int64_t a[] = {1, 2, 3, 3, 3, 4, 5};
        int64_t r = binary_search(a, 7, 3);
        assert(r != NOT_FOUND && a[r] == 3 && r >= 2 && r <= 4);
    }

    /* Large sorted array */
    {
        int64_t a[100];
        for (int i = 0; i < 100; i++) a[i] = i;
        assert(binary_search(a, 100, 49) == 49);
        assert(binary_search(a, 100, 99) == 99);
        assert(binary_search(a, 100, 100) == NOT_FOUND);
    }

    /* Two element arrays */
    {
        int64_t a[] = {1, 2};
        assert(binary_search(a, 2, 1) == 0);
        assert(binary_search(a, 2, 2) == 1);
        assert(binary_search(a, 2, 3) == NOT_FOUND);
    }

    return 1;
}

int main(void) {
    assert(check());
    printf("All tests passed.\n");
    return 0;
}
