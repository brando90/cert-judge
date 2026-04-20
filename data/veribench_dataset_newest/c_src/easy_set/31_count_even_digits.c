/* Count even digits in a non-negative integer.
 *
 * Edge cases:
 * - 0 has one even digit (0).
 * - Negative inputs are invalid (pre returns 0).
 */

#include <stdio.h>
#include <assert.h>
#include <stdint.h>

int pre_count_even_digits(int64_t n) {
    return (n >= 0);
}

int64_t count_even_digits(int64_t n) {
    if (!pre_count_even_digits(n)) return -1;
    if (n == 0) return 1; /* digit 0 is even */
    int64_t count = 0;
    while (n > 0) {
        if ((n % 10) % 2 == 0) count++;
        n /= 10;
    }
    return count;
}

int check(void) {
    assert(count_even_digits(24863) == 4);
    assert(count_even_digits(0) == 1);
    assert(pre_count_even_digits(-1) == 0);
    return 1;
}

int main(void) {
    assert(check());
    printf("All tests passed.\n");
    return 0;
}
