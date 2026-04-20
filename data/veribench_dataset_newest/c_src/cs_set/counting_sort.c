/* Counting sort for an array of integers (supports negatives via shift).
 *
 * Edge cases:
 * - Empty array (n==0) is valid.
 * - Supports negative numbers by shifting the range.
 */

#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>
#include <assert.h>

int pre_counting_sort(const int64_t *arr, int n) {
    if (arr == NULL && n != 0) return 0;
    if (n < 0) return 0;
    return 1;
}

/* Sorts arr[0..n-1] into out[0..n-1]. Caller must allocate out with n elements. */
void counting_sort(const int64_t *arr, int n, int64_t *out) {
    if (!pre_counting_sort(arr, n)) {
        fprintf(stderr, "pre_counting_sort failed\n");
        exit(1);
    }
    if (n == 0) return;

    /* Find min and max */
    int64_t min_val = arr[0], max_val = arr[0];
    for (int i = 1; i < n; i++) {
        if (arr[i] < min_val) min_val = arr[i];
        if (arr[i] > max_val) max_val = arr[i];
    }

    int64_t range_size = max_val - min_val + 1;
    int64_t *count = (int64_t *)calloc((size_t)range_size, sizeof(int64_t));
    assert(count != NULL);

    /* Count occurrences */
    for (int i = 0; i < n; i++) {
        count[arr[i] - min_val]++;
    }

    /* Build sorted output */
    int idx = 0;
    for (int64_t i = 0; i < range_size; i++) {
        for (int64_t c = 0; c < count[i]; c++) {
            out[idx++] = i + min_val;
        }
    }

    free(count);
}

static void assert_arrays_equal(const int64_t *a, const int64_t *b, int n) {
    for (int i = 0; i < n; i++) assert(a[i] == b[i]);
}

int check(void) {
    int64_t out[100];

    { int64_t a[] = {3,1,2}; int64_t e[] = {1,2,3}; counting_sort(a,3,out); assert_arrays_equal(out,e,3); }
    { int64_t a[] = {1,2,3}; int64_t e[] = {1,2,3}; counting_sort(a,3,out); assert_arrays_equal(out,e,3); }
    { int64_t a[] = {2,1,3}; int64_t e[] = {1,2,3}; counting_sort(a,3,out); assert_arrays_equal(out,e,3); }

    /* Empty */
    counting_sort(NULL, 0, out);

    /* Single */
    { int64_t a[] = {1}; counting_sort(a,1,out); assert(out[0]==1); }

    /* Larger */
    { int64_t a[] = {5,2,4,6,1,3}; int64_t e[] = {1,2,3,4,5,6}; counting_sort(a,6,out); assert_arrays_equal(out,e,6); }
    { int64_t a[] = {9,8,7,6,5,4,3,2,1}; int64_t e[] = {1,2,3,4,5,6,7,8,9}; counting_sort(a,9,out); assert_arrays_equal(out,e,9); }
    { int64_t a[] = {2,6,4,3,1,5}; int64_t e[] = {1,2,3,4,5,6}; counting_sort(a,6,out); assert_arrays_equal(out,e,6); }

    /* Two elements */
    { int64_t a[] = {2,1}; int64_t e[] = {1,2}; counting_sort(a,2,out); assert_arrays_equal(out,e,2); }
    { int64_t a[] = {1,2}; int64_t e[] = {1,2}; counting_sort(a,2,out); assert_arrays_equal(out,e,2); }

    /* Duplicates */
    { int64_t a[] = {3,1,4,1,2,3}; int64_t e[] = {1,1,2,3,3,4}; counting_sort(a,6,out); assert_arrays_equal(out,e,6); }
    { int64_t a[] = {5,5,5,5,5}; int64_t e[] = {5,5,5,5,5}; counting_sort(a,5,out); assert_arrays_equal(out,e,5); }
    { int64_t a[] = {3,1,2,1,3,2}; int64_t e[] = {1,1,2,2,3,3}; counting_sort(a,6,out); assert_arrays_equal(out,e,6); }
    { int64_t a[] = {1,0,2,0,1,0}; int64_t e[] = {0,0,0,1,1,2}; counting_sort(a,6,out); assert_arrays_equal(out,e,6); }

    /* Already sorted */
    { int64_t a[] = {1,2,3,4,5}; int64_t e[] = {1,2,3,4,5}; counting_sort(a,5,out); assert_arrays_equal(out,e,5); }

    /* Reverse sorted */
    { int64_t a[] = {5,4,3,2,1}; int64_t e[] = {1,2,3,4,5}; counting_sort(a,5,out); assert_arrays_equal(out,e,5); }

    /* Random */
    { int64_t a[] = {3,7,1,9,2,8,4,6,5}; int64_t e[] = {1,2,3,4,5,6,7,8,9}; counting_sort(a,9,out); assert_arrays_equal(out,e,9); }

    /* With zeros */
    { int64_t a[] = {0,3,1,0,2}; int64_t e[] = {0,0,1,2,3}; counting_sort(a,5,out); assert_arrays_equal(out,e,5); }

    /* Larger test */
    {
        int64_t a[] = {64,34,25,12,22,11,90,88,76,50,42};
        int64_t e[] = {11,12,22,25,34,42,50,64,76,88,90};
        counting_sort(a,11,out);
        assert_arrays_equal(out,e,11);
    }

    return 1;
}

int main(void) {
    assert(check());
    printf("All tests passed.\n");
    return 0;
}
