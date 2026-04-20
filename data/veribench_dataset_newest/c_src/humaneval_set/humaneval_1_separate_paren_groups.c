/* Separate groups of balanced parentheses from a string into individual strings. */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <assert.h>

/* Returns number of groups found. Groups written into result array (pre-allocated). */
int separate_paren_groups(const char *paren_string, char **result, int max_groups) {
    int count = 0;
    char current[1024];
    int cur_len = 0;
    int current_depth = 0;

    for (int i = 0; paren_string[i] != '\0'; i++) {
        char c = paren_string[i];
        if (c == '(') {
            current_depth++;
            current[cur_len++] = c;
        } else if (c == ')') {
            current_depth--;
            current[cur_len++] = c;
            if (current_depth == 0) {
                current[cur_len] = '\0';
                if (count < max_groups) {
                    result[count] = malloc(cur_len + 1);
                    strcpy(result[count], current);
                    count++;
                }
                cur_len = 0;
            }
        }
        /* ignore spaces and other chars */
    }
    return count;
}

void check(void) {
    char *result[20];
    int n;

    n = separate_paren_groups("(()()) ((())) () ((())()())", result, 20);
    assert(n == 4);
    assert(strcmp(result[0], "(()())") == 0);
    assert(strcmp(result[1], "((()))") == 0);
    assert(strcmp(result[2], "()") == 0);
    assert(strcmp(result[3], "((())()())") == 0);
    for (int i = 0; i < n; i++) free(result[i]);

    n = separate_paren_groups("() (()) ((())) (((())))", result, 20);
    assert(n == 4);
    assert(strcmp(result[0], "()") == 0);
    assert(strcmp(result[1], "(())") == 0);
    assert(strcmp(result[2], "((()))") == 0);
    assert(strcmp(result[3], "(((())))") == 0);
    for (int i = 0; i < n; i++) free(result[i]);

    {
        const char *input3 = "(()(())((())))";
        n = separate_paren_groups(input3, result, 20);
        assert(n == 1);
        assert(strcmp(result[0], input3) == 0);
    }
    for (int i = 0; i < n; i++) free(result[i]);

    n = separate_paren_groups("( ) (( )) (( )( ))", result, 20);
    assert(n == 3);
    assert(strcmp(result[0], "()") == 0);
    assert(strcmp(result[1], "(())") == 0);
    assert(strcmp(result[2], "(()())") == 0);
    for (int i = 0; i < n; i++) free(result[i]);
}

int main(void) {
    check();
    printf("All tests passed.\n");
    return 0;
}
