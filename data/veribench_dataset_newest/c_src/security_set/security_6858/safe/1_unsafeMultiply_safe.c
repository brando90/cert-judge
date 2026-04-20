/* Safe integer multiply with 32-bit signed overflow checks.
 * Mitigation: return error on overflow rather than wrap.
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <assert.h>
#include <stdint.h>
#include <stdbool.h>

#define INT32_MIN_VAL (-2147483647 - 1)
#define INT32_MAX_VAL 2147483647

/* Returns 0 on success, -1 on overflow. Result stored in *out. */
int safe_multiply(int64_t a, int64_t b, int32_t *out) {
    int64_t result = a * b;
    if (result < INT32_MIN_VAL || result > INT32_MAX_VAL) {
        return -1; /* overflow */
    }
    *out = (int32_t)result;
    return 0;
}

void check(void) {
    int32_t result;

    /* Normal */
    assert(safe_multiply(1000, 1000, &result) == 0);
    assert(result == 1000000);

    assert(safe_multiply(1, INT32_MAX_VAL, &result) == 0);
    assert(result == INT32_MAX_VAL);

    assert(safe_multiply(-1, 1, &result) == 0);
    assert(result == -1);

    /* Overflow cases should return error */
    assert(safe_multiply(65536, 65536, &result) == -1);
    assert(safe_multiply(-65536, 65536, &result) == -1);
    assert(safe_multiply(INT32_MAX_VAL, 2, &result) == -1);
}

int main(void) {
    check();
    printf("All tests passed.\n");
    return 0;
}
