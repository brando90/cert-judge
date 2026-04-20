/* Length of the longest valid parentheses substring.
 *
 * Edge cases:
 * - Empty string returns 0.
 * - NULL input is invalid (pre returns 0).
 */

#include <stdio.h>
#include <assert.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>

int pre_lvp(const char *s) {
    return (s != NULL);
}

int64_t longest_valid_parentheses(const char *s) {
    if (!pre_lvp(s)) return -1;
    size_t len = strlen(s);
    if (len == 0) return 0;

    /* Stack-based approach */
    int *stack = malloc((len + 1) * sizeof(int));
    if (!stack) return -1;
    int top = 0;
    stack[top] = -1; /* base */

    int64_t max_len = 0;
    for (size_t i = 0; i < len; i++) {
        if (s[i] == '(') {
            stack[++top] = (int)i;
        } else {
            if (top > 0) {
                top--;
                int64_t cur = (int64_t)i - stack[top];
                if (cur > max_len) max_len = cur;
            } else {
                stack[top] = (int)i;
            }
        }
    }
    free(stack);
    return max_len;
}

int check(void) {
    assert(longest_valid_parentheses(")()())") == 4);
    assert(longest_valid_parentheses("") == 0);
    assert(pre_lvp(NULL) == 0);
    return 1;
}

int main(void) {
    assert(check());
    printf("All tests passed.\n");
    return 0;
}
