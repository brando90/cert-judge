/* Encode/decode strings by shifting every character by 5 in the alphabet. */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <assert.h>

char *encode_shift(const char *s) {
    int len = strlen(s);
    char *result = malloc(len + 1);
    for (int i = 0; i < len; i++) {
        result[i] = (char)(((s[i] - 'a' + 5) % 26) + 'a');
    }
    result[len] = '\0';
    return result;
}

char *decode_shift(const char *s) {
    int len = strlen(s);
    char *result = malloc(len + 1);
    for (int i = 0; i < len; i++) {
        result[i] = (char)((((s[i] - 'a' - 5) % 26 + 26) % 26) + 'a');
    }
    result[len] = '\0';
    return result;
}

void check(void) {
    const char *tests[] = {
        "hello", "abcdefghijklmnopqrstuvwxyz", "a", "zzzzz",
        "teststring", "programming", "verification"
    };
    int n = sizeof(tests) / sizeof(tests[0]);
    for (int i = 0; i < n; i++) {
        char *encoded = encode_shift(tests[i]);
        char *decoded = decode_shift(encoded);
        assert(strcmp(decoded, tests[i]) == 0);
        free(encoded);
        free(decoded);
    }
}

int main(void) {
    check();
    printf("All tests passed.\n");
    return 0;
}
