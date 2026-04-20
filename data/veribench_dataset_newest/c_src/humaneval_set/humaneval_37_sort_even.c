/* Sort elements at even indices, leave odd indices unchanged. */
#include <stdio.h>
#include <stdlib.h>
#include <assert.h>
#include <stdint.h>

static int cmp_int64(const void *a, const void *b) {
    int64_t va = *(const int64_t *)a;
    int64_t vb = *(const int64_t *)b;
    return (va > vb) - (va < vb);
}

void sort_even(int64_t *l, int n, int64_t *out) {
    /* Collect even-indexed elements */
    int n_evens = (n + 1) / 2;
    int64_t *evens = malloc(n_evens * sizeof(int64_t));
    for (int i = 0; i < n_evens; i++) {
        evens[i] = l[i * 2];
    }
    qsort(evens, n_evens, sizeof(int64_t), cmp_int64);

    /* Build result */
    int ei = 0;
    for (int i = 0; i < n; i++) {
        if (i % 2 == 0) {
            out[i] = evens[ei++];
        } else {
            out[i] = l[i];
        }
    }
    free(evens);
}

void check(void) {
    int64_t out[20];

    {
        int64_t a[] = {1, 2, 3};
        int64_t e[] = {1, 2, 3};
        sort_even(a, 3, out);
        for (int i = 0; i < 3; i++) assert(out[i] == e[i]);
    }
    {
        int64_t a[] = {5, 3, -5, 2, -3, 3, 9, 0, 123, 1, -10};
        int64_t e[] = {-10, 3, -5, 2, -3, 3, 5, 0, 9, 1, 123};
        sort_even(a, 11, out);
        for (int i = 0; i < 11; i++) assert(out[i] == e[i]);
    }
    {
        int64_t a[] = {5, 8, -12, 4, 23, 2, 3, 11, 12, -10};
        int64_t e[] = {-12, 8, 3, 4, 5, 2, 12, 11, 23, -10};
        sort_even(a, 10, out);
        for (int i = 0; i < 10; i++) assert(out[i] == e[i]);
    }
}

int main(void) {
    check();
    printf("All tests passed.\n");
    return 0;
}
