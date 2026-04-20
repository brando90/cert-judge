/* Sort only the elements at indices divisible by three, leave rest unchanged. */
#include <stdio.h>
#include <stdlib.h>
#include <assert.h>
#include <stdint.h>

static int cmp_int64(const void *a, const void *b) {
    int64_t va = *(const int64_t *)a;
    int64_t vb = *(const int64_t *)b;
    return (va > vb) - (va < vb);
}

void sort_third(int64_t *l, int n, int64_t *out) {
    /* Collect elements at indices divisible by 3 */
    int count3 = 0;
    for (int i = 0; i < n; i += 3) count3++;
    int64_t *thirds = malloc(count3 * sizeof(int64_t));
    int idx = 0;
    for (int i = 0; i < n; i += 3) thirds[idx++] = l[i];
    qsort(thirds, count3, sizeof(int64_t), cmp_int64);

    /* Build result */
    idx = 0;
    for (int i = 0; i < n; i++) {
        if (i % 3 == 0) {
            out[i] = thirds[idx++];
        } else {
            out[i] = l[i];
        }
    }
    free(thirds);
}

void check(void) {
    int64_t out[20];

    {
        int64_t a[] = {1, 2, 3};
        int64_t e[] = {1, 2, 3};
        sort_third(a, 3, out);
        for (int i = 0; i < 3; i++) assert(out[i] == e[i]);
    }
    {
        int64_t a[] = {5, 6, 3, 4, 8, 9, 2};
        int64_t e[] = {2, 6, 3, 4, 8, 9, 5};
        sort_third(a, 7, out);
        for (int i = 0; i < 7; i++) assert(out[i] == e[i]);
    }
    {
        int64_t a[] = {5, 8, 3, 4, 6, 9, 2};
        int64_t e[] = {2, 8, 3, 4, 6, 9, 5};
        sort_third(a, 7, out);
        for (int i = 0; i < 7; i++) assert(out[i] == e[i]);
    }
    {
        int64_t a[] = {5, 6, 9, 4, 8, 3, 2};
        int64_t e[] = {2, 6, 9, 4, 8, 3, 5};
        sort_third(a, 7, out);
        for (int i = 0; i < 7; i++) assert(out[i] == e[i]);
    }
    {
        int64_t a[] = {5, 6, 3, 4, 8, 9, 2, 1};
        int64_t e[] = {2, 6, 3, 4, 8, 9, 5, 1};
        sort_third(a, 8, out);
        for (int i = 0; i < 8; i++) assert(out[i] == e[i]);
    }
}

int main(void) {
    check();
    printf("All tests passed.\n");
    return 0;
}
