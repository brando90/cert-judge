/* Check if a non-negative integer is prime.
 *
 * Edge cases:
 * - 0 and 1 are not prime.
 * - Negative inputs are invalid (pre returns 0).
 * - Returns -1 on pre-violation.
 */

#include <stdio.h>
#include <assert.h>
#include <stdint.h>
#include <math.h>

int pre_is_prime(int64_t n) {
    return (n >= 0);
}

/* Returns 1 if prime, 0 if not, -1 on pre-violation */
int is_prime(int64_t n) {
    if (!pre_is_prime(n)) return -1;
    if (n <= 1) return 0;
    if (n <= 3) return 1;
    if (n % 2 == 0 || n % 3 == 0) return 0;
    for (int64_t i = 5; i * i <= n; i += 6) {
        if (n % i == 0 || n % (i + 2) == 0) return 0;
    }
    return 1;
}

int check(void) {
    assert(is_prime(7) == 1);
    assert(is_prime(0) == 0);
    assert(pre_is_prime(-1) == 0);
    return 1;
}

int main(void) {
    assert(check());
    printf("All tests passed.\n");
    return 0;
}
