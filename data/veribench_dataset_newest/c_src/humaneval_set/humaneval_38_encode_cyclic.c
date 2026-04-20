/* Encode/decode strings by cycling groups of three characters. */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <assert.h>

/* Caller must free result. */
char *encode_cyclic(const char *s) {
    int len = strlen(s);
    char *result = malloc(len + 1);
    for (int i = 0; i < len; i += 3) {
        int group_len = len - i;
        if (group_len > 3) group_len = 3;
        if (group_len == 3) {
            result[i] = s[i + 1];
            result[i + 1] = s[i + 2];
            result[i + 2] = s[i];
        } else {
            for (int j = 0; j < group_len; j++) {
                result[i + j] = s[i + j];
            }
        }
    }
    result[len] = '\0';
    return result;
}

char *decode_cyclic(const char *s) {
    char *once = encode_cyclic(s);
    char *twice = encode_cyclic(once);
    free(once);
    return twice;
}

void check(void) {
    /* Test encode then decode on known strings */
    const char *tests[] = {
        "abc", "abcdef", "abcdefghij", "hello world!", "a", "ab", "",
        "xyzabcdefgh", "programming", "teststring!!"
    };
    int ntests = sizeof(tests) / sizeof(tests[0]);
    for (int i = 0; i < ntests; i++) {
        char *encoded = encode_cyclic(tests[i]);
        char *decoded = decode_cyclic(encoded);
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
