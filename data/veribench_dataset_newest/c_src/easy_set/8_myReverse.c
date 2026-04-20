/* Return a new list with the elements in reverse order.
 *
 * Edge cases:
 * - Empty list returns empty list.
 * - Single element list returns the same list.
 *
 * C convention: caller provides output buffer of size n.
 */

#include <stdio.h>
#include <assert.h>
#include <stdint.h>

int pre_prog(const int64_t *xs, int n) {
    (void)xs;
    return (n >= 0);
}

/* Write reversed xs into out[], return n on success, -1 on pre-violation */
int prog(const int64_t *xs, int n, int64_t *out) {
    if (!pre_prog(xs, n)) return -1;
    for (int i = 0; i < n; i++) {
        out[i] = xs[n - 1 - i];
    }
    return n;
}

int check(void) {
    {
        int64_t a[] = {1, 2, 3, 4};
        int64_t out[4];
        int r = prog(a, 4, out);
        assert(r == 4);
        assert(out[0] == 4 && out[1] == 3 && out[2] == 2 && out[3] == 1);
    }
    {
        int64_t out[1];
        int r = prog(NULL, 0, out);
        assert(r == 0);
    }
    return 1;
}

int main(void) {
    assert(check());
    printf("All tests passed.\n");
    return 0;
}
