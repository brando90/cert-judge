/* Find the shortest palindrome that begins with a supplied string. */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <assert.h>
#include <stdbool.h>

bool is_palindrome(const char *s, int len) {
    for (int i = 0; i < len / 2; i++) {
        if (s[i] != s[len - 1 - i]) return false;
    }
    return true;
}

/* Caller must free the result. */
char *make_palindrome(const char *string) {
    int len = strlen(string);
    if (len == 0) {
        char *r = malloc(1);
        r[0] = '\0';
        return r;
    }

    int beginning_of_suffix = 0;
    while (!is_palindrome(string + beginning_of_suffix, len - beginning_of_suffix)) {
        beginning_of_suffix++;
    }

    /* result = string + reverse(string[:beginning_of_suffix]) */
    int result_len = len + beginning_of_suffix;
    char *result = malloc(result_len + 1);
    memcpy(result, string, len);
    for (int i = 0; i < beginning_of_suffix; i++) {
        result[len + i] = string[beginning_of_suffix - 1 - i];
    }
    result[result_len] = '\0';
    return result;
}

void check(void) {
    char *r;

    r = make_palindrome("");
    assert(strcmp(r, "") == 0);
    free(r);

    r = make_palindrome("x");
    assert(strcmp(r, "x") == 0);
    free(r);

    r = make_palindrome("xyz");
    assert(strcmp(r, "xyzyx") == 0);
    free(r);

    r = make_palindrome("xyx");
    assert(strcmp(r, "xyx") == 0);
    free(r);

    r = make_palindrome("jerry");
    assert(strcmp(r, "jerryrrej") == 0);
    free(r);
}

int main(void) {
    check();
    printf("All tests passed.\n");
    return 0;
}
