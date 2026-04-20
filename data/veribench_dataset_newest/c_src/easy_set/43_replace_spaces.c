/* Replace spaces with underscores in a string.
 *
 * Edge cases:
 * - Empty string returns empty string.
 * - NULL input is invalid (pre returns 0).
 *
 * C convention: writes result into caller-provided buffer.
 */

#include <stdio.h>
#include <assert.h>
#include <string.h>

int pre_replace_spaces(const char *s) {
    return (s != NULL);
}

int replace_spaces(const char *s, char *out) {
    if (!pre_replace_spaces(s)) return -1;
    int j = 0;
    for (int i = 0; s[i] != '\0'; i++) {
        out[j++] = (s[i] == ' ') ? '_' : s[i];
    }
    out[j] = '\0';
    return 0;
}

int check(void) {
    char buf[256];
    assert(replace_spaces("hello world", buf) == 0);
    assert(strcmp(buf, "hello_world") == 0);

    assert(replace_spaces("", buf) == 0);
    assert(strcmp(buf, "") == 0);

    assert(pre_replace_spaces(NULL) == 0);
    return 1;
}

int main(void) {
    assert(check());
    printf("All tests passed.\n");
    return 0;
}
