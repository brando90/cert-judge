/* Longest common subsequence (LCS) for two strings.
 *
 * Edge cases:
 * - Empty inputs yield empty LCS.
 * - NULL inputs are invalid (pre returns 0).
 *
 * C convention: writes result into caller-provided buffer.
 */

#include <stdio.h>
#include <assert.h>
#include <stdlib.h>
#include <string.h>

int pre_lcs(const char *s1, const char *s2) {
    return (s1 != NULL) && (s2 != NULL);
}

/* Writes LCS of s1,s2 into out. Returns 0 on success, -1 on error. */
int longest_common_subsequence(const char *s1, const char *s2, char *out) {
    if (!pre_lcs(s1, s2)) return -1;
    size_t m = strlen(s1), n = strlen(s2);
    if (m == 0 || n == 0) { out[0] = '\0'; return 0; }

    /* Allocate DP table */
    int *dp = calloc((m + 1) * (n + 1), sizeof(int));
    int *dir = calloc((m + 1) * (n + 1), sizeof(int));
    if (!dp || !dir) { free(dp); free(dir); return -1; }

    #define DP(i,j) dp[(i)*(n+1)+(j)]
    #define DIR(i,j) dir[(i)*(n+1)+(j)]

    for (size_t i = 1; i <= m; i++) {
        for (size_t j = 1; j <= n; j++) {
            if (s1[i-1] == s2[j-1]) {
                DP(i,j) = DP(i-1,j-1) + 1;
                DIR(i,j) = 0; /* diagonal */
            } else if (DP(i-1,j) >= DP(i,j-1)) {
                DP(i,j) = DP(i-1,j);
                DIR(i,j) = 1; /* up */
            } else {
                DP(i,j) = DP(i,j-1);
                DIR(i,j) = 2; /* left */
            }
        }
    }

    /* Reconstruct */
    int lcs_len = DP(m, n);
    out[lcs_len] = '\0';
    {
        size_t i = m, j = n;
        int pos = lcs_len - 1;
        while (i > 0 && j > 0) {
            if (DIR(i,j) == 0) {
                out[pos--] = s1[i-1];
                i--; j--;
            } else if (DIR(i,j) == 1) {
                i--;
            } else {
                j--;
            }
        }
    }

    #undef DP
    #undef DIR
    free(dp);
    free(dir);
    return 0;
}

int check(void) {
    char buf[256];
    assert(longest_common_subsequence("abcde", "ace", buf) == 0);
    assert(strcmp(buf, "ace") == 0);

    assert(longest_common_subsequence("", "", buf) == 0);
    assert(strcmp(buf, "") == 0);

    assert(pre_lcs(NULL, "abc") == 0);
    return 1;
}

int main(void) {
    assert(check());
    printf("All tests passed.\n");
    return 0;
}
