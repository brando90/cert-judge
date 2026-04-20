/* For a given number n, find the largest number that divides n evenly, smaller than n. */
#include <stdio.h>
#include <assert.h>
#include <stdint.h>

int64_t largest_divisor(int64_t n) {
    for (int64_t i = n - 1; i >= 1; i--) {
        if (n % i == 0) {
            return i;
        }
    }
    return 1;
}

void check(void) {
    assert(largest_divisor(3) == 1);
    assert(largest_divisor(7) == 1);
    assert(largest_divisor(10) == 5);
    assert(largest_divisor(100) == 50);
    assert(largest_divisor(49) == 7);
}

int main(void) {
    check();
    printf("All tests passed.\n");
    return 0;
}
