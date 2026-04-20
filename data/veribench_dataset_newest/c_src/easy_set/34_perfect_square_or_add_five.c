/* Return n if it's a perfect square, else return n + 5.
 *
 * Edge cases:
 * - 0 and 1 return themselves.
 * - Negative inputs are invalid (pre returns 0).
 */

#include <stdio.h>
#include <assert.h>
#include <stdint.h>
#include <math.h>

int pre_perfect_square_or_add_five(int64_t n) {
    return (n >= 0);
}

int64_t perfect_square_or_add_five(int64_t n) {
    if (!pre_perfect_square_or_add_five(n)) return -1;
    int64_t root = (int64_t)sqrt((double)n);
    /* Adjust for floating point imprecision */
    while (root * root > n) root--;
    while ((root + 1) * (root + 1) <= n) root++;
    return (root * root == n) ? n : n + 5;
}

int check(void) {
    assert(perfect_square_or_add_five(16) == 16);
    assert(perfect_square_or_add_five(2) == 7);
    assert(pre_perfect_square_or_add_five(-1) == 0);
    return 1;
}

int main(void) {
    assert(check());
    printf("All tests passed.\n");
    return 0;
}
