/* Return the string s repeated n times.
 *
 * Edge cases:
 * - Repeating 0 times returns empty string.
 * - Repeating empty string returns empty string.
 * - Returns -1 if s is NULL or n < 0.
 *
 * C convention: writes result into caller-provided buffer.
 */

#include <stdio.h>
#include <assert.h>
#include <string.h>
#include <stdint.h>

int pre_prog(const char *s, int64_t n) {
    return (s != NULL) && (n >= 0);
}

int prog(const char *s, int64_t n, char *out) {
    if (!pre_prog(s, n)) return -1;
    size_t len = strlen(s);
    int pos = 0;
    for (int64_t i = 0; i < n; i++) {
        for (size_t j = 0; j < len; j++) {
            out[pos++] = s[j];
        }
    }
    out[pos] = '\0';
    return 0;
}

int check(void) {
    char buf[1024];
    assert(prog("abc", 3, buf) == 0);
    assert(strcmp(buf, "abcabcabc") == 0);

    assert(prog("hello", 0, buf) == 0);
    assert(strcmp(buf, "") == 0);

    assert(pre_prog("test", -1) == 0);
    assert(pre_prog(NULL, 3) == 0);
    return 1;
}

int main(void) {
    assert(check());
    printf("All tests passed.\n");
    return 0;
}
