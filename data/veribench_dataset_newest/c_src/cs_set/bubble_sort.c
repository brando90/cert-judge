/* Bubble sort for an array of integers.
 *
 * Edge cases:
 * - Empty array (n==0) is valid.
 * - Sorts in-place on a copy; returns sorted array via output parameter.
 */

#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>
#include <assert.h>

int pre_bubble_sort(const int64_t *arr, int n) {
    if (arr == NULL && n != 0) return 0;
    if (n < 0) return 0;
    return 1;
}

/* Sorts arr[0..n-1] into out[0..n-1]. Caller must allocate out. */
void bubble_sort(const int64_t *arr, int n, int64_t *out) {
    if (!pre_bubble_sort(arr, n)) {
        fprintf(stderr, "pre_bubble_sort failed\n");
        exit(1);
    }
    if (n == 0) return;

    memcpy(out, arr, (size_t)n * sizeof(int64_t));

    for (int i = 0; i < n; i++) {
        bool swapped = false;
        for (int j = 0; j < n - i - 1; j++) {
            if (out[j] > out[j + 1]) {
                int64_t tmp = out[j];
                out[j] = out[j + 1];
                out[j + 1] = tmp;
                swapped = true;
            }
        }
        if (!swapped) break;
    }
}

static void assert_arrays_equal(const int64_t *a, const int64_t *b, int n) {
    for (int i = 0; i < n; i++) {
        assert(a[i] == b[i]);
    }
}

int check(void) {
    int64_t out[100];

    {
        int64_t a[] = {3, 1, 2};
        int64_t e[] = {1, 2, 3};
        bubble_sort(a, 3, out);
        assert_arrays_equal(out, e, 3);
    }
    {
        int64_t a[] = {1, 2, 3};
        int64_t e[] = {1, 2, 3};
        bubble_sort(a, 3, out);
        assert_arrays_equal(out, e, 3);
    }

    /* Empty */
    bubble_sort(NULL, 0, out);

    /* Single element */
    {
        int64_t a[] = {1};
        bubble_sort(a, 1, out);
        assert(out[0] == 1);
    }

    /* Larger arrays */
    {
        int64_t a[] = {5, 2, 4, 6, 1, 3};
        int64_t e[] = {1, 2, 3, 4, 5, 6};
        bubble_sort(a, 6, out);
        assert_arrays_equal(out, e, 6);
    }
    {
        int64_t a[] = {9, 8, 7, 6, 5, 4, 3, 2, 1};
        int64_t e[] = {1, 2, 3, 4, 5, 6, 7, 8, 9};
        bubble_sort(a, 9, out);
        assert_arrays_equal(out, e, 9);
    }

    /* Two elements */
    {
        int64_t a[] = {2, 1};
        int64_t e[] = {1, 2};
        bubble_sort(a, 2, out);
        assert_arrays_equal(out, e, 2);
    }

    /* Duplicates */
    {
        int64_t a[] = {3, 1, 4, 1, 2, 3};
        int64_t e[] = {1, 1, 2, 3, 3, 4};
        bubble_sort(a, 6, out);
        assert_arrays_equal(out, e, 6);
    }
    {
        int64_t a[] = {5, 5, 5, 5, 5};
        int64_t e[] = {5, 5, 5, 5, 5};
        bubble_sort(a, 5, out);
        assert_arrays_equal(out, e, 5);
    }

    /* Already sorted */
    {
        int64_t a[] = {1, 2, 3, 4, 5};
        int64_t e[] = {1, 2, 3, 4, 5};
        bubble_sort(a, 5, out);
        assert_arrays_equal(out, e, 5);
    }

    /* Reverse sorted */
    {
        int64_t a[] = {5, 4, 3, 2, 1};
        int64_t e[] = {1, 2, 3, 4, 5};
        bubble_sort(a, 5, out);
        assert_arrays_equal(out, e, 5);
    }

    /* Random order */
    {
        int64_t a[] = {3, 7, 1, 9, 2, 8, 4, 6, 5};
        int64_t e[] = {1, 2, 3, 4, 5, 6, 7, 8, 9};
        bubble_sort(a, 9, out);
        assert_arrays_equal(out, e, 9);
    }

    return 1;
}

int main(void) {
    assert(check());
    printf("All tests passed.\n");
    return 0;
}
