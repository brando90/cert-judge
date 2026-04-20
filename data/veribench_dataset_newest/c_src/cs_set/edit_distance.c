/* Levenshtein edit distance between two strings.
 *
 * Edge cases:
 * - Empty strings handled.
 * - In C we only support char* strings (not generic lists).
 */

#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>
#include <assert.h>

int pre_edit_distance(const char *s1, const char *s2) {
    return (s1 != NULL && s2 != NULL) ? 1 : 0;
}

static int64_t min3(int64_t a, int64_t b, int64_t c) {
    int64_t m = a;
    if (b < m) m = b;
    if (c < m) m = c;
    return m;
}

int64_t edit_distance(const char *s1, const char *s2) {
    if (!pre_edit_distance(s1, s2)) {
        fprintf(stderr, "pre_edit_distance failed\n");
        exit(1);
    }

    int m = (int)strlen(s1);
    int n = (int)strlen(s2);

    /* Allocate DP table */
    int64_t *dp = (int64_t *)malloc((size_t)(m + 1) * (size_t)(n + 1) * sizeof(int64_t));
    assert(dp != NULL);

    #define DP(i, j) dp[(i) * (n + 1) + (j)]

    for (int i = 0; i <= m; i++) DP(i, 0) = i;
    for (int j = 0; j <= n; j++) DP(0, j) = j;

    for (int i = 1; i <= m; i++) {
        for (int j = 1; j <= n; j++) {
            if (s1[i - 1] == s2[j - 1]) {
                DP(i, j) = DP(i - 1, j - 1);
            } else {
                DP(i, j) = 1 + min3(
                    DP(i - 1, j),       /* deletion */
                    DP(i, j - 1),       /* insertion */
                    DP(i - 1, j - 1)    /* substitution */
                );
            }
        }
    }

    int64_t result = DP(m, n);
    free(dp);
    #undef DP
    return result;
}

int check(void) {
    /* Basic functionality tests with strings */
    assert(edit_distance("hello", "hello") == 0);
    assert(edit_distance("cat", "bat") == 1);
    assert(edit_distance("cat", "cats") == 1);
    assert(edit_distance("cats", "cat") == 1);
    assert(edit_distance("cat", "dog") == 3);
    assert(edit_distance("kitten", "sitting") == 3);

    /* Edge cases */
    assert(edit_distance("", "") == 0);
    assert(edit_distance("", "abc") == 3);
    assert(edit_distance("ab", "") == 2);
    assert(edit_distance("a", "b") == 1);

    /* Longer sequences */
    assert(edit_distance("intention", "execution") == 5);
    assert(edit_distance("saturday", "sunday") == 3);

    /* Same length, all different */
    assert(edit_distance("abc", "def") == 3);
    assert(edit_distance("xyz", "abc") == 3);

    /* One character strings */
    assert(edit_distance("a", "a") == 0);
    assert(edit_distance("a", "b") == 1);
    assert(edit_distance("a", "") == 1);
    assert(edit_distance("", "a") == 1);

    /* Repeated characters */
    assert(edit_distance("aaa", "aa") == 1);
    assert(edit_distance("aa", "aaa") == 1);
    assert(edit_distance("aaaa", "bbbb") == 4);

    return 1;
}

int main(void) {
    assert(check());
    printf("All tests passed.\n");
    return 0;
}
