/* Check if all elements in the list are even integers.
 *
 * Edge cases:
 * - Empty list returns true (1).
 *
 * Returns 1 if all even, 0 if not, -1 on pre-violation.
 */

#include <stdio.h>
#include <assert.h>
#include <stdint.h>

int pre_all_even(const int64_t *xs, int n) {
    (void)xs;
    return (n >= 0);
}

int all_even(const int64_t *xs, int n) {
    if (!pre_all_even(xs, n)) return -1;
    for (int i = 0; i < n; i++) {
        if (xs[i] % 2 != 0) return 0;
    }
    return 1;
}

int check(void) {
    {
        int64_t a[] = {2, 4, 6};
        assert(all_even(a, 3) == 1);
    }
    assert(all_even(NULL, 0) == 1);
    {
        int64_t a[] = {1, 2, 4};
        assert(all_even(a, 3) == 0);
    }
    return 1;
}

int main(void) {
    assert(check());
    printf("All tests passed.\n");
    return 0;
}
