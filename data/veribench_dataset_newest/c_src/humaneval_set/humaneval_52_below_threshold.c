/* Return true if all numbers in the list are below threshold t. */
#include <stdio.h>
#include <assert.h>
#include <stdbool.h>
#include <stdint.h>

bool below_threshold(int64_t *l, int n, int64_t t) {
    for (int i = 0; i < n; i++) {
        if (l[i] >= t) return false;
    }
    return true;
}

void check(void) {
    {
        int64_t a[] = {1, 2, 4, 10};
        assert(below_threshold(a, 4, 100) == true);
    }
    {
        int64_t a[] = {1, 20, 4, 10};
        assert(below_threshold(a, 4, 5) == false);
    }
    {
        int64_t a[] = {1, 20, 4, 10};
        assert(below_threshold(a, 4, 21) == true);
    }
    {
        int64_t a[] = {1, 20, 4, 10};
        assert(below_threshold(a, 4, 22) == true);
    }
    {
        int64_t a[] = {1, 8, 4, 10};
        assert(below_threshold(a, 4, 11) == true);
    }
    {
        int64_t a[] = {1, 8, 4, 10};
        assert(below_threshold(a, 4, 10) == false);
    }
}

int main(void) {
    check();
    printf("All tests passed.\n");
    return 0;
}
