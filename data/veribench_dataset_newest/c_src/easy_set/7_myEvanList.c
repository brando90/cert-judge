/* Return a new list containing only the even numbers from the input list.
 *
 * Edge cases:
 * - Empty list returns empty list.
 * - List with no even numbers returns empty list.
 *
 * C convention: caller provides output buffer; function returns count of even elements written.
 */

#include <stdio.h>
#include <assert.h>
#include <stdint.h>
#include <string.h>

int pre_prog(const int64_t *xs, int n) {
    (void)xs; /* xs is a valid list of integers (n >= 0) */
    return (n >= 0);
}

/* Write even elements to out[], return count */
int prog(const int64_t *xs, int n, int64_t *out) {
    if (!pre_prog(xs, n)) return -1;
    int count = 0;
    for (int i = 0; i < n; i++) {
        if (xs[i] % 2 == 0) {
            out[count++] = xs[i];
        }
    }
    return count;
}

int check(void) {
    {
        int64_t a[] = {1, 2, 3, 4, 5, 6};
        int64_t out[6];
        int c = prog(a, 6, out);
        assert(c == 3);
        assert(out[0] == 2 && out[1] == 4 && out[2] == 6);
    }
    {
        int64_t out[1];
        int c = prog(NULL, 0, out);
        assert(c == 0);
    }
    return 1;
}

int main(void) {
    assert(check());
    printf("All tests passed.\n");
    return 0;
}
