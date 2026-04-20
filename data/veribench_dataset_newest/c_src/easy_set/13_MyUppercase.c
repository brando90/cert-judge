/* Convert all lowercase letters in a string to uppercase.
 *
 * Edge cases:
 * - Empty string returns empty string.
 * - Non-alphabetic characters remain unchanged.
 * - Returns NULL if input is NULL.
 *
 * C convention: writes result into caller-provided buffer.
 */

#include <stdio.h>
#include <assert.h>
#include <string.h>
#include <ctype.h>

int pre_prog(const char *s) {
    return (s != NULL);
}

/* Write uppercase version of s into out (must be large enough). Returns 0 on success, -1 on error. */
int prog(const char *s, char *out) {
    if (!pre_prog(s)) return -1;
    size_t len = strlen(s);
    for (size_t i = 0; i < len; i++) {
        out[i] = (char)toupper((unsigned char)s[i]);
    }
    out[len] = '\0';
    return 0;
}

int check(void) {
    char buf[256];
    assert(prog("hello", buf) == 0);
    assert(strcmp(buf, "HELLO") == 0);

    assert(prog("", buf) == 0);
    assert(strcmp(buf, "") == 0);

    assert(pre_prog(NULL) == 0);
    return 1;
}

int main(void) {
    assert(check());
    printf("All tests passed.\n");
    return 0;
}
