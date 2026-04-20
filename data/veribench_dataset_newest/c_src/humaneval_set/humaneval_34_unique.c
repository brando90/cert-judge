/* Return sorted unique elements in a list. */
#include <stdio.h>
#include <stdlib.h>
#include <assert.h>
#include <stdint.h>

static int cmp_int64(const void *a, const void *b) {
    int64_t va = *(const int64_t *)a;
    int64_t vb = *(const int64_t *)b;
    return (va > vb) - (va < vb);
}

/* Returns count of unique elements. */
int unique(int64_t *l, int n, int64_t *out) {
    if (n == 0) return 0;
    /* Copy and sort */
    int64_t *tmp = malloc(n * sizeof(int64_t));
    for (int i = 0; i < n; i++) tmp[i] = l[i];
    qsort(tmp, n, sizeof(int64_t), cmp_int64);
    int count = 0;
    out[count++] = tmp[0];
    for (int i = 1; i < n; i++) {
        if (tmp[i] != tmp[i-1]) {
            out[count++] = tmp[i];
        }
    }
    free(tmp);
    return count;
}

void check(void) {
    int64_t out[100];
    int n;

    {
        int64_t a[] = {5, 3, 5, 2, 3, 3, 9, 0, 123};
        int64_t expected[] = {0, 2, 3, 5, 9, 123};
        n = unique(a, 9, out);
        assert(n == 6);
        for (int i = 0; i < 6; i++) assert(out[i] == expected[i]);
    }
}

int main(void) {
    check();
    printf("All tests passed.\n");
    return 0;
}
