/* Triple each integer in the input list.
 *
 * Edge cases:
 * - Empty list returns empty list.
 *
 * C convention: caller provides output buffer of size n.
 */

#include <stdio.h>
#include <assert.h>
#include <stdint.h>

int pre_triple_all(const int64_t *lst, int n) {
    (void)lst;
    return (n >= 0);
}

/* Write tripled elements to out[], return n on success, -1 on error. */
int triple_all(const int64_t *lst, int n, int64_t *out) {
    if (!pre_triple_all(lst, n)) return -1;
    for (int i = 0; i < n; i++) {
        out[i] = lst[i] * 3;
    }
    return n;
}

int check(void) {
    {
        int64_t a[] = {1, 2, 3};
        int64_t out[3];
        assert(triple_all(a, 3, out) == 3);
        assert(out[0] == 3 && out[1] == 6 && out[2] == 9);
    }
    {
        int64_t out[1];
        assert(triple_all(NULL, 0, out) == 0);
    }
    return 1;
}

int main(void) {
    assert(check());
    printf("All tests passed.\n");
    return 0;
}
