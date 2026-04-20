/* Return median of elements in the list. */
#include <stdio.h>
#include <stdlib.h>
#include <assert.h>
#include <math.h>
#include <stdint.h>

static int cmp_int64(const void *a, const void *b) {
    int64_t va = *(const int64_t *)a;
    int64_t vb = *(const int64_t *)b;
    return (va > vb) - (va < vb);
}

double median(int64_t *l, int n) {
    int64_t *sorted = malloc(n * sizeof(int64_t));
    for (int i = 0; i < n; i++) sorted[i] = l[i];
    qsort(sorted, n, sizeof(int64_t), cmp_int64);

    double result;
    if (n % 2 == 1) {
        result = (double)sorted[n / 2];
    } else {
        result = (sorted[n / 2 - 1] + sorted[n / 2]) / 2.0;
    }
    free(sorted);
    return result;
}

void check(void) {
    {
        int64_t a[] = {3, 1, 2, 4, 5};
        assert(median(a, 5) == 3.0);
    }
    {
        int64_t a[] = {-10, 4, 6, 1000, 10, 20};
        assert(fabs(median(a, 6) - 8.0) < 1e-9);
    }
    {
        int64_t a[] = {5};
        assert(median(a, 1) == 5.0);
    }
    {
        int64_t a[] = {6, 5};
        assert(fabs(median(a, 2) - 5.5) < 1e-9);
    }
    {
        int64_t a[] = {8, 1, 3, 9, 9, 2, 7};
        assert(median(a, 7) == 7.0);
    }
}

int main(void) {
    check();
    printf("All tests passed.\n");
    return 0;
}
