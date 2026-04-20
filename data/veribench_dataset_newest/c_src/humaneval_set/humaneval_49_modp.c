/* Return 2^n modulo p. */
#include <stdio.h>
#include <assert.h>
#include <stdint.h>

int64_t modp(int64_t n, int64_t p) {
    int64_t ret = 1;
    for (int64_t i = 0; i < n; i++) {
        ret = (2 * ret) % p;
    }
    return ret;
}

void check(void) {
    assert(modp(3, 5) == 3);
    assert(modp(1101, 101) == 2);
    assert(modp(0, 101) == 1);
    assert(modp(3, 11) == 8);
    assert(modp(100, 101) == 1);
    assert(modp(30, 5) == 4);
    assert(modp(31, 5) == 3);
}

int main(void) {
    check();
    printf("All tests passed.\n");
    return 0;
}
