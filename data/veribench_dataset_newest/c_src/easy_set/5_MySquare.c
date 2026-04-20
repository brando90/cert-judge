/* Return the square of a natural number (non-negative integer).
 *
 * Edge cases:
 * - square(0) = 0
 * - square(1) = 1
 * - The function returns -1 if input is not a natural number.
 */

#include <stdio.h>
#include <assert.h>
#include <stdint.h>

int pre_prog(int64_t n) {
    return (n >= 0);
}

int64_t prog(int64_t n) {
    if (!pre_prog(n)) return -1;
    return n * n;
}

int check(void) {
    assert(prog(3) == 9);
    assert(prog(0) == 0);
    assert(pre_prog(-1) == 0);
    return 1;
}

int main(void) {
    assert(check());
    printf("All tests passed.\n");
    return 0;
}
