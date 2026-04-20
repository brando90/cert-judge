/* Check if a non-negative integer is a palindrome.
 *
 * Edge cases:
 * - Single digits are palindromes.
 * - Negative inputs are invalid (pre returns 0).
 * - Returns -1 on pre-violation.
 */

#include <stdio.h>
#include <assert.h>
#include <stdint.h>
#include <string.h>

int pre_is_palindrome(int64_t n) {
    return (n >= 0);
}

/* Returns 1 if palindrome, 0 if not, -1 on pre-violation */
int is_palindrome(int64_t n) {
    if (!pre_is_palindrome(n)) return -1;
    if (n < 10) return 1;
    /* Convert to string and check */
    char buf[32];
    snprintf(buf, sizeof(buf), "%ld", (long)n);
    size_t len = strlen(buf);
    for (size_t i = 0; i < len / 2; i++) {
        if (buf[i] != buf[len - 1 - i]) return 0;
    }
    return 1;
}

int check(void) {
    assert(is_palindrome(121) == 1);
    assert(is_palindrome(0) == 1);
    assert(pre_is_palindrome(-1) == 0);
    return 1;
}

int main(void) {
    assert(check());
    printf("All tests passed.\n");
    return 0;
}
