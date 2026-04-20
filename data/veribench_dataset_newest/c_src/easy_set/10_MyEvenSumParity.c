/* Return the parity (0 or 1) of the sum of all elements in a list of even integers.
 *
 * Edge cases:
 * - Sum of even numbers is always even (parity 0).
 * - Empty list sums to 0 (parity 0).
 * - Returns -1 if input contains non-even integers.
 */

#include <stdio.h>
#include <assert.h>
#include <stdint.h>

/* Pre: all elements are even */
int pre_prog(const int64_t *xs, int n) {
    if (n < 0) return 0;
    for (int i = 0; i < n; i++) {
        if (xs[i] % 2 != 0) return 0;
    }
    return 1;
}

int64_t prog(const int64_t *xs, int n) {
    if (!pre_prog(xs, n)) return -1;
    int64_t sum = 0;
    for (int i = 0; i < n; i++) {
        sum += xs[i];
    }
    int64_t r = sum % 2;
    return (r < 0) ? -r : r;
}

int check(void) {
    {
        int64_t a[] = {2, 4, 6};
        assert(prog(a, 3) == 0);
    }
    /* Empty list */
    assert(prog(NULL, 0) == 0);
    /* Odd elements */
    {
        int64_t a[] = {1, 3, 5};
        assert(pre_prog(a, 3) == 0);
    }
    {
        int64_t a[] = {2, 3, 4};
        assert(pre_prog(a, 3) == 0);
    }
    return 1;
}

int main(void) {
    assert(check());
    printf("All tests passed.\n");
    return 0;
}
