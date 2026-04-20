/* Provides heappop for removing the smallest item from a min-heap.
   Sourced from Python's standard heapq library. */

#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <assert.h>
#include <stdbool.h>

/* -- Pre-condition -- */
int pre_heappop(double *heap, int n) {
    (void)n;
    return heap != NULL;
}

/* -- Implementation -- */

static void _siftdown(double *heap, int startpos, int pos) {
    double newitem = heap[pos];
    while (pos > startpos) {
        int parentpos = (pos - 1) >> 1;
        double parent = heap[parentpos];
        if (newitem < parent) {
            heap[pos] = parent;
            pos = parentpos;
            continue;
        }
        break;
    }
    heap[pos] = newitem;
}

static void _siftup(double *heap, int n, int pos) {
    int endpos = n;
    int startpos = pos;
    double newitem = heap[pos];
    int childpos = 2 * pos + 1;
    while (childpos < endpos) {
        int rightpos = childpos + 1;
        if (rightpos < endpos && !(heap[childpos] < heap[rightpos])) {
            childpos = rightpos;
        }
        heap[pos] = heap[childpos];
        pos = childpos;
        childpos = 2 * pos + 1;
    }
    heap[pos] = newitem;
    _siftdown(heap, startpos, pos);
}

static void heappush(double *heap, int *n, double item) {
    heap[*n] = item;
    (*n)++;
    _siftdown(heap, 0, *n - 1);
}

double heappop(double *heap, int *n) {
    if (*n <= 0) {
        fprintf(stderr, "IndexError: pop from empty heap\n");
        exit(1);
    }
    (*n)--;
    double lastelt = heap[*n];
    if (*n > 0) {
        double returnitem = heap[0];
        heap[0] = lastelt;
        _siftup(heap, *n, 0);
        return returnitem;
    }
    return lastelt;
}

double benchmark_heappop(double *heap, int *n) {
    if (!pre_heappop(heap, *n)) {
        fprintf(stderr, "AttributeError: heap is NULL\n");
        exit(1);
    }
    return heappop(heap, n);
}

/* -- Tests -- */

static void check_invariant(double *heap, int n) {
    for (int pos = 1; pos < n; pos++) {
        int parentpos = (pos - 1) >> 1;
        assert(heap[parentpos] <= heap[pos]);
    }
}

static int double_cmp(const void *a, const void *b) {
    double da = *(const double *)a;
    double db = *(const double *)b;
    if (da < db) return -1;
    if (da > db) return 1;
    return 0;
}

int check(void) {
    /* Basic unit tests */
    double h[] = {1, 2, 3};  /* already a valid heap */
    int n = 3;
    double popped = benchmark_heappop(h, &n);
    check_invariant(h, n);
    assert(popped == 1.0);

    /* Edge: pop single-element heap */
    double h2[] = {5.0};
    int n2 = 1;
    popped = benchmark_heappop(h2, &n2);
    assert(popped == 5.0 && n2 == 0);

    /* Property check: push 256 numbers then pop all in sorted order */
    double h3[512];
    int n3 = 0;
    double data[256];
    unsigned int seed = 42;
    for (int i = 0; i < 256; i++) {
        seed = seed * 1103515245 + 12345;
        data[i] = (double)(seed % 100000) / 100.0;
        heappush(h3, &n3, data[i]);
        check_invariant(h3, n3);
    }

    double results[256];
    int ri = 0;
    while (n3 > 0) {
        results[ri++] = benchmark_heappop(h3, &n3);
        if (n3 > 0) check_invariant(h3, n3);
    }

    /* results should be sorted */
    qsort(data, 256, sizeof(double), double_cmp);
    for (int i = 0; i < 256; i++) {
        assert(results[i] == data[i]);
    }

    return 1;
}

int main(void) {
    assert(check());
    printf("All tests passed.\n");
    return 0;
}
