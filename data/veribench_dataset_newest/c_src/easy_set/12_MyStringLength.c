/* Return the number of characters in a string.
 *
 * Edge cases:
 * - Empty string has length 0.
 * - Returns -1 if input is NULL.
 */

#include <stdio.h>
#include <assert.h>
#include <stdint.h>
#include <string.h>

int pre_prog(const char *s) {
    return (s != NULL);
}

int64_t prog(const char *s) {
    if (!pre_prog(s)) return -1;
    return (int64_t)strlen(s);
}

int check(void) {
    assert(prog("hello") == 5);
    assert(prog("") == 0);
    assert(pre_prog(NULL) == 0);
    return 1;
}

int main(void) {
    assert(check());
    printf("All tests passed.\n");
    return 0;
}
