/* Return maximum element in the list. */
#include <stdio.h>
#include <assert.h>
#include <stdint.h>

int64_t max_element(int64_t *l, int n) {
    int64_t m = l[0];
    for (int i = 1; i < n; i++) {
        if (l[i] > m) m = l[i];
    }
    return m;
}

void check(void) {
    {
        int64_t a[] = {1, 2, 3};
        assert(max_element(a, 3) == 3);
    }
    {
        int64_t a[] = {5, 3, -5, 2, -3, 3, 9, 0, 124, 1, -10};
        assert(max_element(a, 11) == 124);
    }
}

int main(void) {
    check();
    printf("All tests passed.\n");
    return 0;
}
