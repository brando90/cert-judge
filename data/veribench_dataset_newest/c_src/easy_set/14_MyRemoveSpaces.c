/* Remove all space characters from a string.
 *
 * Edge cases:
 * - Empty string returns empty string.
 * - String with only spaces returns empty string.
 * - Returns -1 if input is NULL.
 *
 * C convention: writes result into caller-provided buffer.
 */

#include <stdio.h>
#include <assert.h>
#include <string.h>

int pre_prog(const char *s) {
    return (s != NULL);
}

int prog(const char *s, char *out) {
    if (!pre_prog(s)) return -1;
    int j = 0;
    for (int i = 0; s[i] != '\0'; i++) {
        if (s[i] != ' ') {
            out[j++] = s[i];
        }
    }
    out[j] = '\0';
    return 0;
}

int check(void) {
    char buf[256];
    assert(prog("hello world", buf) == 0);
    assert(strcmp(buf, "helloworld") == 0);

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
