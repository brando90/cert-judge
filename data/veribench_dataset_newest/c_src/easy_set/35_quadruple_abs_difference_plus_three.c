/* Return 4*|a - b| + 3 for integers a and b.
 *
 * Edge cases:
 * - Works for equal numbers (returns 3).
 */

#include <stdio.h>
#include <assert.h>
#include <stdint.h>
#include <stdlib.h>

int pre_quadruple(int64_t a, int64_t b) {
    /* Integers only -- in C all int64_t are integers, so always true */
    (void)a; (void)b;
    return 1;
}

int64_t quadruple_abs_diff_plus_three(int64_t a, int64_t b) {
    if (!pre_quadruple(a, b)) return -1;
    int64_t diff = a - b;
    if (diff < 0) diff = -diff;
    return 4 * diff + 3;
}

int check(void) {
    assert(quadruple_abs_diff_plus_three(7, 2) == 23);
    assert(quadruple_abs_diff_plus_three(5, 5) == 3);
    return 1;
}

int main(void) {
    assert(check());
    printf("All tests passed.\n");
    return 0;
}
