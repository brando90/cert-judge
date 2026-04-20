/* Find the longest palindromic substring in a string.
 *
 * Edge cases:
 * - Empty string returns empty string.
 * - Non-string (NULL) input is invalid.
 *
 * C convention: writes result into caller-provided buffer.
 */

#include <stdio.h>
#include <assert.h>
#include <string.h>

int pre_longest_palindrome(const char *s) {
    return (s != NULL);
}

/* Writes the longest palindromic substring of s into out. Returns 0 on success, -1 on error. */
int longest_palindrome(const char *s, char *out) {
    if (!pre_longest_palindrome(s)) return -1;
    size_t len = strlen(s);
    if (len == 0) { out[0] = '\0'; return 0; }

    size_t best_start = 0, best_len = 1;

    for (size_t i = 0; i < len; i++) {
        /* Odd-length palindromes */
        size_t l = i, r = i;
        while (r < len && s[l] == s[r]) {
            if (r - l + 1 > best_len) { best_start = l; best_len = r - l + 1; }
            if (l == 0) break;
            l--; r++;
        }
        /* Even-length palindromes */
        if (i + 1 < len) {
            l = i; r = i + 1;
            while (r < len && s[l] == s[r]) {
                if (r - l + 1 > best_len) { best_start = l; best_len = r - l + 1; }
                if (l == 0) break;
                l--; r++;
            }
        }
    }

    memcpy(out, s + best_start, best_len);
    out[best_len] = '\0';
    return 0;
}

int check(void) {
    char buf[256];
    assert(longest_palindrome("babad", buf) == 0);
    assert(strcmp(buf, "bab") == 0 || strcmp(buf, "aba") == 0);

    assert(longest_palindrome("", buf) == 0);
    assert(strcmp(buf, "") == 0);

    assert(pre_longest_palindrome(NULL) == 0);
    return 1;
}

int main(void) {
    assert(check());
    printf("All tests passed.\n");
    return 0;
}
