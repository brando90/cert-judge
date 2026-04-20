/* Multiplies two integers without checking for 32-bit signed overflow.
 * This simulates C-style overflow where values silently wrap around.
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <assert.h>
#include <stdint.h>

int32_t unsafeMultiply(int32_t a, int32_t b) {
    /* Multiply without checking for overflow.
     * In C, signed overflow is undefined behavior, but on most platforms
     * with two's complement, it wraps. We use unsigned arithmetic to get
     * defined wrapping behavior, then reinterpret as signed. */
    uint32_t ua = (uint32_t)a;
    uint32_t ub = (uint32_t)b;
    uint32_t result = ua * ub;
    return (int32_t)result;
}

void check(void) {
    /* 1) Normal small inputs */
    assert(unsafeMultiply(1000, 1000) == 1000000);

    /* 2) Exact upper limit: should return 2^31 - 1 */
    int32_t max_int = 2147483647; /* 2^31 - 1 */
    assert(unsafeMultiply(1, max_int) == max_int);

    /* 3) Overflow case: 65536 * 65536 = 2^32 -> wraps to 0 */
    assert(unsafeMultiply(65536, 65536) == 0);

    /* 4) Negative input overflow simulation: -65536 * 65536 = -2^32 -> wraps to 0 */
    assert(unsafeMultiply(-65536, 65536) == 0);

    /* 5) Overflow with sign flip: 300000 * 300000 should be negative */
    assert(unsafeMultiply(300000, 300000) < 0);
}

int main(void) {
    check();
    printf("All tests passed.\n");
    return 0;
}
