/* Return base raised to the power of exponent for natural numbers.
 *
 * Edge cases:
 * - power(n, 0) = 1 for any n
 * - power(0, n) = 0 for n > 0
 * - power(0, 0) = 1 by convention
 * - Returns -1 if inputs are not natural numbers.
 */

#include <stdio.h>
#include <assert.h>
#include <stdint.h>

int pre_prog(int64_t base, int64_t exponent) {
    return (base >= 0) && (exponent >= 0);
}

int64_t prog(int64_t base, int64_t exponent) {
    if (!pre_prog(base, exponent)) return -1;
    if (exponent == 0) return 1;
    int64_t result = 1;
    for (int64_t i = 0; i < exponent; i++) {
        result *= base;
    }
    return result;
}

int check(void) {
    assert(prog(2, 3) == 8);
    assert(prog(0, 0) == 1);
    assert(pre_prog(-1, 2) == 0);
    assert(pre_prog(2, -1) == 0);
    return 1;
}

int main(void) {
    assert(check());
    printf("All tests passed.\n");
    return 0;
}
