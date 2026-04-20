/* Return the smallest element in a non-empty list of non-negative integers.
 *
 * Edge cases:
 * - Single-element list returns that element.
 * - Empty list or negative elements are invalid (pre returns 0).
 */

#include <stdio.h>
#include <assert.h>
#include <stdint.h>

int pre_my_min_list(const int64_t *xs, int n) {
    if (n <= 0) return 0;
    for (int i = 0; i < n; i++) {
        if (xs[i] < 0) return 0;
    }
    return 1;
}

int64_t my_min_list(const int64_t *xs, int n) {
    if (!pre_my_min_list(xs, n)) return -1;
    int64_t m = xs[0];
    for (int i = 1; i < n; i++) {
        if (xs[i] < m) m = xs[i];
    }
    return m;
}

int check(void) {
    {
        int64_t a[] = {7, 3, 9, 2};
        assert(my_min_list(a, 4) == 2);
    }
    {
        int64_t a[] = {5};
        assert(my_min_list(a, 1) == 5);
    }
    assert(pre_my_min_list(NULL, 0) == 0);
    return 1;
}

int main(void) {
    assert(check());
    printf("All tests passed.\n");
    return 0;
}
