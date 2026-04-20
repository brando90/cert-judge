/* Return the sum of digits in a non-negative integer.
 *
 * Edge cases:
 * - Sum of digits of 0 is 0.
 * - Single digit numbers return themselves.
 * - Returns -1 if input is not a non-negative integer.
 */

#include <stdio.h>
#include <assert.h>
#include <stdint.h>

int pre_prog(int64_t n) {
    return (n >= 0);
}

int64_t prog(int64_t n) {
    if (!pre_prog(n)) return -1;
    if (n == 0) return 0;
    int64_t total = 0;
    while (n > 0) {
        total += n % 10;
        n /= 10;
    }
    return total;
}

int check(void) {
    assert(prog(123) == 6);
    assert(prog(0) == 0);
    assert(pre_prog(-1) == 0);
    return 1;
}

int main(void) {
    assert(check());
    printf("All tests passed.\n");
    return 0;
}
