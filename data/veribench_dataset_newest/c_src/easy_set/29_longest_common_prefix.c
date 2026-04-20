/* Longest common prefix among an array of strings.
 *
 * Edge cases:
 * - Empty list returns empty string.
 * - NULL elements are invalid (pre returns 0).
 *
 * C convention: writes result into caller-provided buffer.
 */

#include <stdio.h>
#include <assert.h>
#include <string.h>

int pre_lcp(const char **strs, int n) {
    if (n < 0) return 0;
    for (int i = 0; i < n; i++) {
        if (strs[i] == NULL) return 0;
    }
    return 1;
}

int longest_common_prefix(const char **strs, int n, char *out) {
    if (!pre_lcp(strs, n)) return -1;
    if (n == 0) { out[0] = '\0'; return 0; }

    /* Find min length */
    size_t min_len = strlen(strs[0]);
    for (int i = 1; i < n; i++) {
        size_t l = strlen(strs[i]);
        if (l < min_len) min_len = l;
    }
    if (min_len == 0) { out[0] = '\0'; return 0; }

    size_t prefix_len = 0;
    for (size_t i = 0; i < min_len; i++) {
        char c = strs[0][i];
        int match = 1;
        for (int j = 1; j < n; j++) {
            if (strs[j][i] != c) { match = 0; break; }
        }
        if (!match) break;
        prefix_len++;
    }

    memcpy(out, strs[0], prefix_len);
    out[prefix_len] = '\0';
    return 0;
}

int check(void) {
    char buf[256];
    {
        const char *strs[] = {"flower", "flow", "flight"};
        assert(longest_common_prefix(strs, 3, buf) == 0);
        assert(strcmp(buf, "fl") == 0);
    }
    {
        assert(longest_common_prefix(NULL, 0, buf) == 0);
        assert(strcmp(buf, "") == 0);
    }
    return 1;
}

int main(void) {
    assert(check());
    printf("All tests passed.\n");
    return 0;
}
