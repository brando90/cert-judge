/* Return the larger of two natural numbers (non-negative integers).
 *
 * Edge cases:
 * - max(0, 0) = 0
 * - The function returns -1 if either input is not a natural number.
 */

#include <stdio.h>
#include <assert.h>
#include <stdint.h>

int pre_prog(int64_t a, int64_t b) {
    return (a >= 0) && (b >= 0);
}

int64_t prog(int64_t a, int64_t b) {
    if (!pre_prog(a, b)) return -1;
    return (a <= b) ? b : a;
}

int check(void) {
    assert(prog(7, 3) == 7);
    assert(prog(0, 0) == 0);
    assert(pre_prog(-1, 0) == 0);
    assert(pre_prog(0, -2) == 0);
    return 1;
}

int main(void) {
    assert(check());
    printf("All tests passed.\n");
    return 0;
}
