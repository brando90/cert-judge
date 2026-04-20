/* Return true if a given number is prime, and false otherwise. */
#include <stdio.h>
#include <assert.h>
#include <stdbool.h>
#include <stdint.h>

bool is_prime(int64_t n) {
    if (n < 2) return false;
    for (int64_t k = 2; k < n - 1; k++) {
        if (n % k == 0) return false;
    }
    return true;
}

void check(void) {
    assert(is_prime(0) == false);
    assert(is_prime(6) == false);
    assert(is_prime(101) == true);
    assert(is_prime(11) == true);
    assert(is_prime(13441) == true);
    assert(is_prime(61) == true);
    assert(is_prime(4) == false);
    assert(is_prime(1) == false);
    assert(is_prime(5) == true);
    assert(is_prime(17) == true);
    assert(is_prime(5 * 17) == false);
    assert(is_prime(11 * 7) == false);
    assert(is_prime(13441L * 19) == false);
}

int main(void) {
    check();
    printf("All tests passed.\n");
    return 0;
}
