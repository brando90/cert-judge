/* Duplicate each character in the input string.
 *
 * Edge cases:
 * - Empty string returns empty string.
 * - NULL input is invalid (pre returns 0).
 *
 * C convention: writes result into caller-provided buffer (must be at least 2*strlen(s)+1).
 */

#include <stdio.h>
#include <assert.h>
#include <string.h>

int pre_duplicate_chars(const char *s) {
    return (s != NULL);
}

int duplicate_chars(const char *s, char *out) {
    if (!pre_duplicate_chars(s)) return -1;
    int j = 0;
    for (int i = 0; s[i] != '\0'; i++) {
        out[j++] = s[i];
        out[j++] = s[i];
    }
    out[j] = '\0';
    return 0;
}

int check(void) {
    char buf[256];
    assert(duplicate_chars("abc", buf) == 0);
    assert(strcmp(buf, "aabbcc") == 0);

    assert(duplicate_chars("", buf) == 0);
    assert(strcmp(buf, "") == 0);

    assert(pre_duplicate_chars(NULL) == 0);
    return 1;
}

int main(void) {
    assert(check());
    printf("All tests passed.\n");
    return 0;
}
