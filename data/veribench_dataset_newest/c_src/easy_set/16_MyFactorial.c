/* Return the factorial of a natural number (non-negative integer).
 *
 * Edge cases:
 * - factorial(0) = 1 by definition
 * - factorial(1) = 1
 * - Returns -1 if input is not a natural number.
 */

#include <stdio.h>
#include <assert.h>
#include <stdint.h>

int pre_prog(int64_t n) {
    return (n >= 0);
}

int64_t prog(int64_t n) {
    if (!pre_prog(n)) return -1;
    if (n == 0) return 1;
    int64_t result = 1;
    for (int64_t i = 1; i <= n; i++) {
        result *= i;
    }
    return result;
}

int check(void) {
    assert(prog(3) == 6);
    assert(prog(0) == 1);
    assert(pre_prog(-1) == 0);
    return 1;
}

int main(void) {
    assert(check());
    printf("All tests passed.\n");
    return 0;
}
