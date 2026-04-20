/* Merge sort for an array of integers.
 *
 * Edge cases:
 * - Empty or single-element array returns copy.
 */

#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>
#include <assert.h>

int pre_merge_sort(const int64_t *arr, int n) {
    if (arr == NULL && n != 0) return 0;
    if (n < 0) return 0;
    return 1;
}

static void merge(int64_t *arr, int left, int mid, int right) {
    int n1 = mid - left + 1;
    int n2 = right - mid;

    int64_t *L = (int64_t *)malloc((size_t)n1 * sizeof(int64_t));
    int64_t *R = (int64_t *)malloc((size_t)n2 * sizeof(int64_t));
    assert(L && R);

    memcpy(L, arr + left, (size_t)n1 * sizeof(int64_t));
    memcpy(R, arr + mid + 1, (size_t)n2 * sizeof(int64_t));

    int i = 0, j = 0, k = left;
    while (i < n1 && j < n2) {
        if (L[i] <= R[j]) {
            arr[k++] = L[i++];
        } else {
            arr[k++] = R[j++];
        }
    }
    while (i < n1) arr[k++] = L[i++];
    while (j < n2) arr[k++] = R[j++];

    free(L);
    free(R);
}

static void merge_sort_helper(int64_t *arr, int left, int right) {
    if (left < right) {
        int mid = left + (right - left) / 2;
        merge_sort_helper(arr, left, mid);
        merge_sort_helper(arr, mid + 1, right);
        merge(arr, left, mid, right);
    }
}

void merge_sort(const int64_t *arr, int n, int64_t *out) {
    if (!pre_merge_sort(arr, n)) {
        fprintf(stderr, "pre_merge_sort failed\n");
        exit(1);
    }
    if (n <= 0) return;

    memcpy(out, arr, (size_t)n * sizeof(int64_t));
    if (n == 1) return;

    merge_sort_helper(out, 0, n - 1);
}

static void assert_arrays_equal(const int64_t *a, const int64_t *b, int n) {
    for (int i = 0; i < n; i++) assert(a[i] == b[i]);
}

int check(void) {
    int64_t out[100];

    { int64_t a[] = {3,1,2}; int64_t e[] = {1,2,3}; merge_sort(a,3,out); assert_arrays_equal(out,e,3); }
    { int64_t a[] = {1,2,3}; int64_t e[] = {1,2,3}; merge_sort(a,3,out); assert_arrays_equal(out,e,3); }
    { int64_t a[] = {2,1,3}; int64_t e[] = {1,2,3}; merge_sort(a,3,out); assert_arrays_equal(out,e,3); }

    /* Empty */
    merge_sort(NULL, 0, out);

    /* Single */
    { int64_t a[] = {1}; merge_sort(a,1,out); assert(out[0]==1); }

    /* Larger */
    { int64_t a[] = {5,2,4,6,1,3}; int64_t e[] = {1,2,3,4,5,6}; merge_sort(a,6,out); assert_arrays_equal(out,e,6); }
    { int64_t a[] = {9,8,7,6,5,4,3,2,1}; int64_t e[] = {1,2,3,4,5,6,7,8,9}; merge_sort(a,9,out); assert_arrays_equal(out,e,9); }
    { int64_t a[] = {2,6,4,3,1,5}; int64_t e[] = {1,2,3,4,5,6}; merge_sort(a,6,out); assert_arrays_equal(out,e,6); }

    /* Two elements */
    { int64_t a[] = {2,1}; int64_t e[] = {1,2}; merge_sort(a,2,out); assert_arrays_equal(out,e,2); }
    { int64_t a[] = {1,2}; int64_t e[] = {1,2}; merge_sort(a,2,out); assert_arrays_equal(out,e,2); }

    /* Duplicates */
    { int64_t a[] = {3,1,4,1,2,3}; int64_t e[] = {1,1,2,3,3,4}; merge_sort(a,6,out); assert_arrays_equal(out,e,6); }
    { int64_t a[] = {5,5,5,5,5}; int64_t e[] = {5,5,5,5,5}; merge_sort(a,5,out); assert_arrays_equal(out,e,5); }

    /* Already sorted */
    { int64_t a[] = {1,2,3,4,5}; int64_t e[] = {1,2,3,4,5}; merge_sort(a,5,out); assert_arrays_equal(out,e,5); }

    /* Reverse sorted */
    { int64_t a[] = {5,4,3,2,1}; int64_t e[] = {1,2,3,4,5}; merge_sort(a,5,out); assert_arrays_equal(out,e,5); }

    /* Random */
    { int64_t a[] = {3,7,1,9,2,8,4,6,5}; int64_t e[] = {1,2,3,4,5,6,7,8,9}; merge_sort(a,9,out); assert_arrays_equal(out,e,9); }

    /* Larger test */
    {
        int64_t a[] = {64,34,25,12,22,11,90,88,76,50,42};
        int64_t e[] = {11,12,22,25,34,42,50,64,76,88,90};
        merge_sort(a,11,out);
        assert_arrays_equal(out,e,11);
    }

    return 1;
}

int main(void) {
    assert(check());
    printf("All tests passed.\n");
    return 0;
}
