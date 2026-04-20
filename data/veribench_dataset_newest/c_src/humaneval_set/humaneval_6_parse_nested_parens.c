/* For each group of nested parentheses separated by spaces, output the deepest nesting level. */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <assert.h>

static int parse_paren_group(const char *s, int len) {
    int depth = 0, max_depth = 0;
    for (int i = 0; i < len; i++) {
        if (s[i] == '(') {
            depth++;
            if (depth > max_depth) max_depth = depth;
        } else if (s[i] == ')') {
            depth--;
        }
    }
    return max_depth;
}

/* Returns count of groups. Results stored in result array. */
int parse_nested_parens(const char *paren_string, int *result, int max_results) {
    int count = 0;
    int len = strlen(paren_string);
    int i = 0;
    while (i < len && count < max_results) {
        /* skip spaces */
        while (i < len && paren_string[i] == ' ') i++;
        if (i >= len) break;
        int start = i;
        /* find end of group (next space or end) */
        while (i < len && paren_string[i] != ' ') i++;
        int group_len = i - start;
        if (group_len > 0) {
            result[count++] = parse_paren_group(paren_string + start, group_len);
        }
    }
    return count;
}

void check(void) {
    int result[20];
    int n;

    n = parse_nested_parens("(()()) ((())) () ((())()())", result, 20);
    assert(n == 4);
    assert(result[0] == 2);
    assert(result[1] == 3);
    assert(result[2] == 1);
    assert(result[3] == 3);

    n = parse_nested_parens("() (()) ((())) (((())))", result, 20);
    assert(n == 4);
    assert(result[0] == 1);
    assert(result[1] == 2);
    assert(result[2] == 3);
    assert(result[3] == 4);

    {
        const char *input3 = "(()(())((())))";
        n = parse_nested_parens(input3, result, 20);
        assert(n == 1);
        assert(result[0] == 4);
    }
}

int main(void) {
    check();
    printf("All tests passed.\n");
    return 0;
}
