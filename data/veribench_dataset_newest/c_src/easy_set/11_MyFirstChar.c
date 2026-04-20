/* Return the first character of a non-empty string.
 *
 * Edge cases:
 * - Single character strings return that character.
 * - Returns '\0' if the string is empty or NULL.
 */

#include <stdio.h>
#include <assert.h>
#include <string.h>

int pre_prog(const char *s) {
    return (s != NULL) && (strlen(s) > 0);
}

char prog(const char *s) {
    if (!pre_prog(s)) return '\0';
    return s[0];
}

int check(void) {
    assert(prog("hello") == 'h');
    assert(prog("A") == 'A');
    assert(pre_prog("") == 0);
    assert(pre_prog(NULL) == 0);
    return 1;
}

int main(void) {
    assert(check());
    printf("All tests passed.\n");
    return 0;
}
