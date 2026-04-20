/* Remove lowercase letters a-e from a string.
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

int pre_remove_abcde(const char *s) {
    return (s != NULL);
}

int remove_abcde(const char *s, char *out) {
    if (!pre_remove_abcde(s)) return -1;
    int j = 0;
    for (int i = 0; s[i] != '\0'; i++) {
        if (s[i] != 'a' && s[i] != 'b' && s[i] != 'c' && s[i] != 'd' && s[i] != 'e') {
            out[j++] = s[i];
        }
    }
    out[j] = '\0';
    return 0;
}

int check(void) {
    char buf[256];
    assert(remove_abcde("alphabet", buf) == 0);
    assert(strcmp(buf, "lpht") == 0);

    assert(remove_abcde("", buf) == 0);
    assert(strcmp(buf, "") == 0);

    assert(pre_remove_abcde(NULL) == 0);
    return 1;
}

int main(void) {
    assert(check());
    printf("All tests passed.\n");
    return 0;
}
