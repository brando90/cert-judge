/* Return the remainder when non-negative integer a is divided by positive integer b.
 *
 * Edge cases:
 * - remainder(a, a) = 0 for any positive a
 * - remainder(a, b) = a when a < b
 * - The function returns -1 if a is negative or b is not positive.
 */

#include <stdio.h>
#include <assert.h>
#include <stdint.h>

int pre_prog(int64_t a, int64_t b) {
    return (a >= 0) && (b > 0);
}

int64_t prog(int64_t a, int64_t b) {
    if (!pre_prog(a, b)) return -1;
    return a % b;
}

int check(void) {
    assert(prog(7, 3) == 1);
    assert(prog(3, 7) == 3);
    assert(pre_prog(-1, 3) == 0);
    assert(pre_prog(5, 0) == 0);
    return 1;
}

int main(void) {
    assert(check());
    printf("All tests passed.\n");
    return 0;
}
