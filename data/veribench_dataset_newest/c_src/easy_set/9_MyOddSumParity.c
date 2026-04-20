/* Return the parity (0 or 1) of the sum of all elements in a list of odd integers.
 *
 * Edge cases:
 * - Single odd number has parity 1.
 * - Sum of even count of odd numbers has parity 0.
 * - Returns -1 if input is not a non-empty list of odd integers.
 */

#include <stdio.h>
#include <assert.h>
#include <stdint.h>

/* Pre: xs is non-empty and all elements are odd */
int pre_prog(const int64_t *xs, int n) {
    if (n <= 0) return 0;
    for (int i = 0; i < n; i++) {
        if (xs[i] % 2 == 0) return 0;
    }
    return 1;
}

int64_t prog(const int64_t *xs, int n) {
    if (!pre_prog(xs, n)) return -1;
    int64_t sum = 0;
    for (int i = 0; i < n; i++) {
        sum += xs[i];
    }
    /* Parity: need to handle negative sums correctly */
    int64_t r = sum % 2;
    return (r < 0) ? -r : r;
}

int check(void) {
    {
        int64_t a[] = {1, 3, 5};
        assert(prog(a, 3) == 1);
    }
    {
        int64_t a[] = {1};
        assert(prog(a, 1) == 1);
    }
    /* Empty list */
    assert(pre_prog(NULL, 0) == 0);
    /* Even elements */
    {
        int64_t a[] = {2, 4, 6};
        assert(pre_prog(a, 3) == 0);
    }
    return 1;
}

int main(void) {
    assert(check());
    printf("All tests passed.\n");
    return 0;
}
