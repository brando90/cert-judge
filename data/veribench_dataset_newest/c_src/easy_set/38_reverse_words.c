/* Reverse each word in the string but preserve word order.
 *
 * Edge cases:
 * - Empty string returns empty string.
 * - NULL input is invalid (pre returns 0).
 *
 * C convention: writes result into caller-provided buffer.
 * Words are separated by spaces; consecutive spaces are collapsed (matching Python split()).
 */

#include <stdio.h>
#include <assert.h>
#include <string.h>

int pre_reverse_words(const char *s) {
    return (s != NULL);
}

int reverse_words(const char *s, char *out) {
    if (!pre_reverse_words(s)) return -1;
    size_t len = strlen(s);
    if (len == 0) { out[0] = '\0'; return 0; }

    int out_pos = 0;
    int first_word = 1;
    size_t i = 0;
    while (i < len) {
        /* Skip spaces */
        while (i < len && s[i] == ' ') i++;
        if (i >= len) break;
        /* Find end of word */
        size_t start = i;
        while (i < len && s[i] != ' ') i++;
        size_t end = i; /* exclusive */
        /* Write separator */
        if (!first_word) out[out_pos++] = ' ';
        first_word = 0;
        /* Write word reversed */
        for (size_t j = end; j > start; j--) {
            out[out_pos++] = s[j - 1];
        }
    }
    out[out_pos] = '\0';
    return 0;
}

int check(void) {
    char buf[256];
    assert(reverse_words("hello world", buf) == 0);
    assert(strcmp(buf, "olleh dlrow") == 0);

    assert(reverse_words("", buf) == 0);
    assert(strcmp(buf, "") == 0);

    assert(pre_reverse_words(NULL) == 0);
    return 1;
}

int main(void) {
    assert(check());
    printf("All tests passed.\n");
    return 0;
}
