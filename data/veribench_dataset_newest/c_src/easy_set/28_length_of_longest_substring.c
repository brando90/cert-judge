/* Length of longest substring without repeating characters.
 *
 * Edge cases:
 * - Empty string returns 0.
 * - NULL input is invalid (pre returns 0).
 */

#include <stdio.h>
#include <assert.h>
#include <stdint.h>
#include <string.h>

int pre_lols(const char *s) {
    return (s != NULL);
}

int64_t length_of_longest_substring(const char *s) {
    if (!pre_lols(s)) return -1;
    size_t len = strlen(s);
    if (len == 0) return 0;

    /* char_pos[c] = last index where c was seen, -1 means not seen */
    int char_pos[256];
    memset(char_pos, -1, sizeof(char_pos));

    int64_t max_len = 0;
    size_t start = 0;
    for (size_t end = 0; end < len; end++) {
        unsigned char c = (unsigned char)s[end];
        if (char_pos[c] >= 0 && (size_t)char_pos[c] >= start) {
            start = (size_t)char_pos[c] + 1;
        } else {
            int64_t cur = (int64_t)(end - start + 1);
            if (cur > max_len) max_len = cur;
        }
        char_pos[c] = (int)end;
    }
    return max_len;
}

int check(void) {
    assert(length_of_longest_substring("abcabcbb") == 3);
    assert(length_of_longest_substring("") == 0);
    assert(pre_lols(NULL) == 0);
    return 1;
}

int main(void) {
    assert(check());
    printf("All tests passed.\n");
    return 0;
}
