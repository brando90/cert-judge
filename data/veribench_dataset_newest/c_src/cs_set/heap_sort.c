/* Heap sort for an array of integers.
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

int pre_heap_sort(const int64_t *arr, int n) {
    if (arr == NULL && n != 0) return 0;
    if (n < 0) return 0;
    return 1;
}

static void heapify(int64_t *arr, int n, int i) {
    int largest = i;
    int left = 2 * i + 1;
    int right = 2 * i + 2;

    if (left < n && arr[left] > arr[largest])
        largest = left;
    if (right < n && arr[right] > arr[largest])
        largest = right;

    if (largest != i) {
        int64_t tmp = arr[i];
        arr[i] = arr[largest];
        arr[largest] = tmp;
        heapify(arr, n, largest);
    }
}

void heap_sort(const int64_t *arr, int n, int64_t *out) {
    if (!pre_heap_sort(arr, n)) {
        fprintf(stderr, "pre_heap_sort failed\n");
        exit(1);
    }
    if (n <= 0) return;
    if (n == 1) { out[0] = arr[0]; return; }

    memcpy(out, arr, (size_t)n * sizeof(int64_t));

    /* Build max heap */
    for (int i = n / 2 - 1; i >= 0; i--) {
        heapify(out, n, i);
    }

    /* Extract elements one by one */
    for (int i = n - 1; i > 0; i--) {
        int64_t tmp = out[0];
        out[0] = out[i];
        out[i] = tmp;
        heapify(out, i, 0);
    }
}

static void assert_arrays_equal(const int64_t *a, const int64_t *b, int n) {
    for (int i = 0; i < n; i++) assert(a[i] == b[i]);
}

int check(void) {
    int64_t out[100];

    { int64_t a[] = {3,1,2}; int64_t e[] = {1,2,3}; heap_sort(a,3,out); assert_arrays_equal(out,e,3); }
    { int64_t a[] = {1,2,3}; int64_t e[] = {1,2,3}; heap_sort(a,3,out); assert_arrays_equal(out,e,3); }
    { int64_t a[] = {2,1,3}; int64_t e[] = {1,2,3}; heap_sort(a,3,out); assert_arrays_equal(out,e,3); }

    /* Empty */
    heap_sort(NULL, 0, out);

    /* Single */
    { int64_t a[] = {1}; heap_sort(a,1,out); assert(out[0]==1); }

    /* Larger */
    { int64_t a[] = {5,2,4,6,1,3}; int64_t e[] = {1,2,3,4,5,6}; heap_sort(a,6,out); assert_arrays_equal(out,e,6); }
    { int64_t a[] = {9,8,7,6,5,4,3,2,1}; int64_t e[] = {1,2,3,4,5,6,7,8,9}; heap_sort(a,9,out); assert_arrays_equal(out,e,9); }
    { int64_t a[] = {2,6,4,3,1,5}; int64_t e[] = {1,2,3,4,5,6}; heap_sort(a,6,out); assert_arrays_equal(out,e,6); }

    /* Two elements */
    { int64_t a[] = {2,1}; int64_t e[] = {1,2}; heap_sort(a,2,out); assert_arrays_equal(out,e,2); }
    { int64_t a[] = {1,2}; int64_t e[] = {1,2}; heap_sort(a,2,out); assert_arrays_equal(out,e,2); }

    /* Duplicates */
    { int64_t a[] = {3,1,4,1,2,3}; int64_t e[] = {1,1,2,3,3,4}; heap_sort(a,6,out); assert_arrays_equal(out,e,6); }
    { int64_t a[] = {5,5,5,5,5}; int64_t e[] = {5,5,5,5,5}; heap_sort(a,5,out); assert_arrays_equal(out,e,5); }

    /* Already sorted */
    { int64_t a[] = {1,2,3,4,5}; int64_t e[] = {1,2,3,4,5}; heap_sort(a,5,out); assert_arrays_equal(out,e,5); }

    /* Reverse sorted */
    { int64_t a[] = {5,4,3,2,1}; int64_t e[] = {1,2,3,4,5}; heap_sort(a,5,out); assert_arrays_equal(out,e,5); }

    /* Random */
    { int64_t a[] = {3,7,1,9,2,8,4,6,5}; int64_t e[] = {1,2,3,4,5,6,7,8,9}; heap_sort(a,9,out); assert_arrays_equal(out,e,9); }

    /* Larger test */
    {
        int64_t a[] = {64,34,25,12,22,11,90,88,76,50,42};
        int64_t e[] = {11,12,22,25,34,42,50,64,76,88,90};
        heap_sort(a,11,out);
        assert_arrays_equal(out,e,11);
    }

    return 1;
}

int main(void) {
    assert(check());
    printf("All tests passed.\n");
    return 0;
}
