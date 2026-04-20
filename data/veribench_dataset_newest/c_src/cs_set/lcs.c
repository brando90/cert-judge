/* Longest common subsequence (LCS) for strings.
 *
 * Edge cases:
 * - Empty inputs handled.
 * - Returns both the LCS string and its length.
 *
 * In C we support char* strings. The LCS result is written into a caller-allocated buffer.
 */

#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>
#include <assert.h>

int pre_lcs(const char *s1, const char *s2) {
    return (s1 != NULL && s2 != NULL) ? 1 : 0;
}

/* Returns length of LCS. If out_buf is non-NULL, writes the LCS string into it (must be large enough).
 * out_buf will be null-terminated. */
int64_t longest_common_subsequence(const char *s1, const char *s2, char *out_buf) {
    if (!pre_lcs(s1, s2)) {
        fprintf(stderr, "pre_lcs failed\n");
        exit(1);
    }

    int m = (int)strlen(s1);
    int n = (int)strlen(s2);

    /* DP table for lengths */
    int *dp = (int *)calloc((size_t)(m + 1) * (size_t)(n + 1), sizeof(int));
    assert(dp != NULL);

    #define DP(i, j) dp[(i) * (n + 1) + (j)]

    for (int i = 1; i <= m; i++) {
        for (int j = 1; j <= n; j++) {
            if (s1[i - 1] == s2[j - 1]) {
                DP(i, j) = DP(i - 1, j - 1) + 1;
            } else {
                DP(i, j) = DP(i - 1, j) > DP(i, j - 1) ? DP(i - 1, j) : DP(i, j - 1);
            }
        }
    }

    int64_t lcs_len = DP(m, n);

    /* Backtrack to find the actual LCS */
    if (out_buf != NULL) {
        int idx = (int)lcs_len;
        out_buf[idx] = '\0';
        int i = m, j = n;
        while (i > 0 && j > 0) {
            if (s1[i - 1] == s2[j - 1]) {
                idx--;
                out_buf[idx] = s1[i - 1];
                i--;
                j--;
            } else if (DP(i - 1, j) >= DP(i, j - 1)) {
                i--;
            } else {
                j--;
            }
        }
    }

    free(dp);
    #undef DP
    return lcs_len;
}

/* Convenience: returns just the length */
int64_t lcs_length(const char *s1, const char *s2) {
    return longest_common_subsequence(s1, s2, NULL);
}

int check(void) {
    char buf[256];

    /* Basic functionality tests with strings */
    longest_common_subsequence("ABCDGH", "AEDFHR", buf);
    assert(strcmp(buf, "ADH") == 0);

    longest_common_subsequence("AGGTAB", "GXTXAYB", buf);
    assert(strcmp(buf, "GTAB") == 0);

    /* Edge cases */
    longest_common_subsequence("", "", buf);
    assert(strcmp(buf, "") == 0);

    longest_common_subsequence("", "abc", buf);
    assert(strcmp(buf, "") == 0);

    longest_common_subsequence("abc", "", buf);
    assert(strcmp(buf, "") == 0);

    /* Identical sequences */
    longest_common_subsequence("abc", "abc", buf);
    assert(strcmp(buf, "abc") == 0);

    /* One is subsequence of another */
    longest_common_subsequence("abc", "aabbcc", buf);
    assert(strcmp(buf, "abc") == 0);

    /* No common elements */
    longest_common_subsequence("abc", "def", buf);
    assert(strcmp(buf, "") == 0);

    /* Single character */
    longest_common_subsequence("a", "a", buf);
    assert(strcmp(buf, "a") == 0);

    longest_common_subsequence("a", "ab", buf);
    assert(strcmp(buf, "a") == 0);

    longest_common_subsequence("ab", "a", buf);
    assert(strcmp(buf, "a") == 0);

    /* Longer sequences */
    longest_common_subsequence("ABCDEFG", "ACEG", buf);
    assert(strcmp(buf, "ACEG") == 0);

    longest_common_subsequence("programming", "grading", buf);
    assert(strcmp(buf, "graing") == 0);

    /* Length-only tests */
    assert(lcs_length("ABCDGH", "AEDFHR") == 3);
    assert(lcs_length("AGGTAB", "GXTXAYB") == 4);
    assert(lcs_length("", "") == 0);
    assert(lcs_length("", "abc") == 0);
    assert(lcs_length("abc", "abc") == 3);
    assert(lcs_length("abc", "def") == 0);

    return 1;
}

int main(void) {
    assert(check());
    printf("All tests passed.\n");
    return 0;
}
