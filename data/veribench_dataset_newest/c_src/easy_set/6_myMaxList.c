/* Return the largest element in a non-empty list of natural numbers.
 *
 * Edge cases:
 * - Single element list returns that element.
 * - The function returns -1 if the list is empty or contains non-natural numbers.
 */

#include <stdio.h>
#include <assert.h>
#include <stdint.h>

/* Pre: xs is non-empty (n > 0) and all elements >= 0 */
int pre_prog(const int64_t *xs, int n) {
    if (n <= 0) return 0;
    for (int i = 0; i < n; i++) {
        if (xs[i] < 0) return 0;
    }
    return 1;
}

/* Returns max element, or -1 on pre-violation */
int64_t prog(const int64_t *xs, int n) {
    if (!pre_prog(xs, n)) return -1;
    int64_t m = xs[0];
    for (int i = 1; i < n; i++) {
        if (xs[i] > m) m = xs[i];
    }
    return m;
}

int check(void) {
    {
        int64_t a[] = {7, 3, 9, 2};
        assert(prog(a, 4) == 9);
    }
    {
        int64_t a[] = {5};
        assert(prog(a, 1) == 5);
    }
    /* Empty list */
    assert(pre_prog(NULL, 0) == 0);
    /* List with negative */
    {
        int64_t a[] = {-1, 2, 3};
        assert(pre_prog(a, 3) == 0);
    }
    return 1;
}

int main(void) {
    assert(check());
    printf("All tests passed.\n");
    return 0;
}
