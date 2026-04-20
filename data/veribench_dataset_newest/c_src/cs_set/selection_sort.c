/* Selection sort for an array of integers.
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

int pre_selection_sort(const int64_t *arr, int n) {
    if (arr == NULL && n != 0) return 0;
    if (n < 0) return 0;
    return 1;
}

void selection_sort(const int64_t *arr, int n, int64_t *out) {
    if (!pre_selection_sort(arr, n)) {
        fprintf(stderr, "pre_selection_sort failed\n");
        exit(1);
    }
    if (n == 0) return;

    memcpy(out, arr, (size_t)n * sizeof(int64_t));

    for (int i = 0; i < n; i++) {
        int min_idx = i;
        for (int j = i + 1; j < n; j++) {
            if (out[j] < out[min_idx]) {
                min_idx = j;
            }
        }
        int64_t tmp = out[i];
        out[i] = out[min_idx];
        out[min_idx] = tmp;
    }
}

static void assert_arrays_equal(const int64_t *a, const int64_t *b, int n) {
    for (int i = 0; i < n; i++) assert(a[i] == b[i]);
}

int check(void) {
    int64_t out[100];

    { int64_t a[] = {3,1,2}; int64_t e[] = {1,2,3}; selection_sort(a,3,out); assert_arrays_equal(out,e,3); }
    { int64_t a[] = {1,2,3}; int64_t e[] = {1,2,3}; selection_sort(a,3,out); assert_arrays_equal(out,e,3); }
    { int64_t a[] = {2,1,3}; int64_t e[] = {1,2,3}; selection_sort(a,3,out); assert_arrays_equal(out,e,3); }

    /* Empty */
    selection_sort(NULL, 0, out);

    /* Single */
    { int64_t a[] = {1}; selection_sort(a,1,out); assert(out[0]==1); }

    /* Larger */
    { int64_t a[] = {5,2,4,6,1,3}; int64_t e[] = {1,2,3,4,5,6}; selection_sort(a,6,out); assert_arrays_equal(out,e,6); }
    { int64_t a[] = {9,8,7,6,5,4,3,2,1}; int64_t e[] = {1,2,3,4,5,6,7,8,9}; selection_sort(a,9,out); assert_arrays_equal(out,e,9); }

    /* Two elements */
    { int64_t a[] = {2,1}; int64_t e[] = {1,2}; selection_sort(a,2,out); assert_arrays_equal(out,e,2); }
    { int64_t a[] = {1,2}; int64_t e[] = {1,2}; selection_sort(a,2,out); assert_arrays_equal(out,e,2); }

    /* Duplicates */
    { int64_t a[] = {3,1,4,1,2,3}; int64_t e[] = {1,1,2,3,3,4}; selection_sort(a,6,out); assert_arrays_equal(out,e,6); }
    { int64_t a[] = {5,5,5,5,5}; int64_t e[] = {5,5,5,5,5}; selection_sort(a,5,out); assert_arrays_equal(out,e,5); }

    /* Already sorted */
    { int64_t a[] = {1,2,3,4,5}; int64_t e[] = {1,2,3,4,5}; selection_sort(a,5,out); assert_arrays_equal(out,e,5); }

    /* Reverse sorted */
    { int64_t a[] = {5,4,3,2,1}; int64_t e[] = {1,2,3,4,5}; selection_sort(a,5,out); assert_arrays_equal(out,e,5); }

    /* Random */
    { int64_t a[] = {3,7,1,9,2,8,4,6,5}; int64_t e[] = {1,2,3,4,5,6,7,8,9}; selection_sort(a,9,out); assert_arrays_equal(out,e,9); }

    return 1;
}

int main(void) {
    assert(check());
    printf("All tests passed.\n");
    return 0;
}
