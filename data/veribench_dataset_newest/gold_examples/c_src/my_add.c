/* Return the sum of two natural numbers (non-negative integers).
 *
 * Edge cases:
 * - 0 + n = n
 * - The function returns -1 if a or b is not a natural number.
 */

#include <stdio.h>
#include <assert.h>
#include <stdint.h>

/* -- Pre-condition -- */

int pre(int64_t a, int64_t b) {
    return (a >= 0) && (b >= 0);
}

/* -- Implementation -- */

int64_t my_add_non_negative(int64_t a, int64_t b) {
    if (!pre(a, b)) return -1;
    return a + b;
}

/* -- Tests -- */

int check(void) {
    /* Basic unit tests */
    assert(my_add_non_negative(1, 2) == 3);

    /* Edge unit tests */
    assert(my_add_non_negative(0, 0) == 0);

    /* Negative (pre-violations must return -1) */
    assert(my_add_non_negative(-1, 0) == -1);
    assert(my_add_non_negative(0, -2) == -1);

    return 1;
}

int main(void) {
    assert(check());
    printf("All tests passed.\n");
    return 0;
}
