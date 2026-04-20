/* Return the greatest common divisor of two integers a and b. */
#include <stdio.h>
#include <assert.h>
#include <stdint.h>

int64_t greatest_common_divisor(int64_t a, int64_t b) {
    while (b) {
        int64_t tmp = b;
        b = a % b;
        a = tmp;
    }
    return a;
}

void check(void) {
    assert(greatest_common_divisor(0, 1) == 1);
    assert(greatest_common_divisor(2, 0) == 2);
    assert(greatest_common_divisor(0, 0) == 0);
    assert(greatest_common_divisor(3, 7) == 1);
    assert(greatest_common_divisor(10, 15) == 5);
    assert(greatest_common_divisor(49, 14) == 7);
    assert(greatest_common_divisor(144, 60) == 12);
}

int main(void) {
    check();
    printf("All tests passed.\n");
    return 0;
}
