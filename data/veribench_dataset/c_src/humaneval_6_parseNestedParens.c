#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <assert.h>

#define MAX_GROUPS 100   // maximum number of groups
#define MAX_LENGTH 1000  // maximum input string length

/**
 * Given one group of parentheses (e.g. "(()())"),
 * return its maximum nesting depth.
 */
int parse_paren_group(const char *s) {
    int depth = 0;
    int max_depth = 0;
    while (*s) {
        if (*s == '(') {
            depth++;
            if (depth > max_depth) {
                max_depth = depth;
            }
        } else if (*s == ')') {
            depth--;
        }
        s++;
    }
    return max_depth;
}

/**
 * Split `paren_string` on spaces, compute the max nesting depth
 * for each group, and store them in `out_depths`. The number of
 * groups found is stored in `*group_count`.
 *
 * If `paren_string` is empty or only has spaces, then `*group_count=0`.
 */
void parse_nested_parens(const char *paren_string,
                         int *out_depths, int *group_count) {
    *group_count = 0;

    // We'll copy `paren_string` so we can safely tokenize.
    char buffer[MAX_LENGTH + 1];
    strncpy(buffer, paren_string, MAX_LENGTH);
    buffer[MAX_LENGTH] = '\0'; // ensure null termination

    // Split on spaces:
    char *token = strtok(buffer, " ");
    while (token != NULL) {
        if (strlen(token) > 0) {
            // Compute max depth for this token
            int depth = parse_paren_group(token);
            out_depths[*group_count] = depth;
            (*group_count)++;
        }
        token = strtok(NULL, " ");
        if (*group_count >= MAX_GROUPS) {
            // We'll stop if we exceed the group limit
            break;
        }
    }
}

/* Helper function to compare two arrays of int. */
static int arrays_equal(const int *arr1, int len1, const int *arr2, int len2) {
    if (len1 != len2) return 0;  // false
    for (int i = 0; i < len1; i++) {
        if (arr1[i] != arr2[i]) return 0;  // false
    }
    return 1; // true
}

/**
 * We'll define a check function that calls parse_nested_parens with the test data
 * and uses assert to verify correctness.
 */
int check() {
    {
        // candidate("(()()) ((())) () ((())()())") => [2, 3, 1, 3]
        int depths[MAX_GROUPS];
        int group_count;
        parse_nested_parens("(()()) ((())) () ((())()())", depths, &group_count);
        int expected[] = {2, 3, 1, 3};
        assert(arrays_equal(depths, group_count, expected, 4));
    }
    {
        // candidate("() (()) ((())) (((())))") => [1, 2, 3, 4]
        int depths[MAX_GROUPS];
        int group_count;
        parse_nested_parens("() (()) ((())) (((())))", depths, &group_count);
        int expected[] = {1, 2, 3, 4};
        assert(arrays_equal(depths, group_count, expected, 4));
    }
    {
        // candidate("(()(())((())))") => [4]
        int depths[MAX_GROUPS];
        int group_count;
        parse_nested_parens("(()(())((())))", depths, &group_count);
        int expected[] = {4};
        assert(arrays_equal(depths, group_count, expected, 1));
    }

    // Additional tests

    // 1. Empty string => no groups => []
    {
        int depths[MAX_GROUPS];
        int group_count;
        parse_nested_parens("", depths, &group_count);
        assert(group_count == 0);
    }

    // 2. Single group with no nesting => "()"
    {
        int depths[MAX_GROUPS];
        int group_count;
        parse_nested_parens("()", depths, &group_count);
        int expected[] = {1};
        assert(arrays_equal(depths, group_count, expected, 1));
    }

    // 3. Single group, deeply nested => "(((())))"
    {
        int depths[MAX_GROUPS];
        int group_count;
        parse_nested_parens("(((())))", depths, &group_count);
        int expected[] = {4};
        assert(arrays_equal(depths, group_count, expected, 1));
    }

    // 4. Multiple groups => "(()) ((()))" => [2,3]
    {
        int depths[MAX_GROUPS];
        int group_count;
        parse_nested_parens("(()) ((()))", depths, &group_count);
        int expected[] = {2, 3};
        assert(arrays_equal(depths, group_count, expected, 2));
    }

    return 1; // All tests passed
}

int main() {
    if (check()) {
        printf("Pass!\n");
    } else {
        printf("Some tests failed.\n");
    }
    return 0;
}
