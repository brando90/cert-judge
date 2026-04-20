/* Return only positive numbers in the list. */
#include <stdio.h>
#include <assert.h>
#include <stdint.h>

int get_positive(int64_t *l, int n, int64_t *out) {
    int count = 0;
    for (int i = 0; i < n; i++) {
        if (l[i] > 0) {
            out[count++] = l[i];
        }
    }
    return count;
}

void check(void) {
    int64_t out[100];
    int n;

    {
        int64_t a[] = {-1, -2, 4, 5, 6};
        n = get_positive(a, 5, out);
        assert(n == 3 && out[0] == 4 && out[1] == 5 && out[2] == 6);
    }
    {
        int64_t a[] = {5, 3, -5, 2, 3, 3, 9, 0, 123, 1, -10};
        int64_t expected[] = {5, 3, 2, 3, 3, 9, 123, 1};
        n = get_positive(a, 11, out);
        assert(n == 8);
        for (int i = 0; i < 8; i++) assert(out[i] == expected[i]);
    }
    {
        int64_t a[] = {-1, -2};
        n = get_positive(a, 2, out);
        assert(n == 0);
    }
    {
        n = get_positive(NULL, 0, out);
        assert(n == 0);
    }
}

int main(void) {
    check();
    printf("All tests passed.\n");
    return 0;
}
