/* Provides heappush for adding items to a min-heap.
   Sourced from Python's standard heapq library. */

#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <assert.h>
#include <stdbool.h>

/* -- Pre-condition -- */
int pre_heappush(double *heap, int n) {
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

void heappush(double *heap, int *n, int capacity, double item) {
    if (*n >= capacity) {
        fprintf(stderr, "heap overflow\n");
        exit(1);
    }
    heap[*n] = item;
    (*n)++;
    _siftdown(heap, 0, *n - 1);
}

void benchmark_heappush(double *heap, int *n, int capacity, double item) {
    if (!pre_heappush(heap, *n)) {
        fprintf(stderr, "AttributeError: heap is NULL\n");
        exit(1);
    }
    heappush(heap, n, capacity, item);
}

/* -- Tests -- */

static void check_invariant(double *heap, int n) {
    for (int pos = 1; pos < n; pos++) {
        int parentpos = (pos - 1) >> 1;
        assert(heap[parentpos] <= heap[pos]);
    }
}

int check(void) {
    /* Basic unit tests */
    double h[512];
    int n = 0;
    benchmark_heappush(h, &n, 512, 3.0);
    check_invariant(h, n);
    benchmark_heappush(h, &n, 512, 1.0);
    check_invariant(h, n);
    benchmark_heappush(h, &n, 512, 2.0);
    check_invariant(h, n);
    assert(h[0] == 1.0);

    /* Edge: push equal elements */
    double h2[16];
    int n2 = 0;
    benchmark_heappush(h2, &n2, 16, 5.0);
    check_invariant(h2, n2);
    benchmark_heappush(h2, &n2, 16, 5.0);
    check_invariant(h2, n2);
    assert(h2[0] == 5.0);

    /* Property check: push 256 numbers, verify invariant and min */
    double h3[512];
    int n3 = 0;
    double data[256];
    /* Use deterministic "random" sequence */
    unsigned int seed = 42;
    double min_val = 1e18;
    for (int i = 0; i < 256; i++) {
        seed = seed * 1103515245 + 12345;
        data[i] = (double)(seed % 100000) / 100.0;
        if (data[i] < min_val) min_val = data[i];
        benchmark_heappush(h3, &n3, 512, data[i]);
        check_invariant(h3, n3);
    }
    assert(n3 == 256);
    assert(h3[0] == min_val);

    return 1;
}

int main(void) {
    assert(check());
    printf("All tests passed.\n");
    return 0;
}
