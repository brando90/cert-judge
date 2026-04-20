/* Return list with elements incremented by 1. */
#include <stdio.h>
#include <assert.h>
#include <stdint.h>

void incr_list(int64_t *l, int n, int64_t *out) {
    for (int i = 0; i < n; i++) {
        out[i] = l[i] + 1;
    }
}

void check(void) {
    int64_t out[20];

    {
        int n = 0;
        incr_list(NULL, n, out);
        /* empty, nothing to check */
    }
    {
        int64_t a[] = {3, 2, 1};
        int64_t e[] = {4, 3, 2};
        incr_list(a, 3, out);
        for (int i = 0; i < 3; i++) assert(out[i] == e[i]);
    }
    {
        int64_t a[] = {5, 2, 5, 2, 3, 3, 9, 0, 123};
        int64_t e[] = {6, 3, 6, 3, 4, 4, 10, 1, 124};
        incr_list(a, 9, out);
        for (int i = 0; i < 9; i++) assert(out[i] == e[i]);
    }
}

int main(void) {
    check();
    printf("All tests passed.\n");
    return 0;
}
