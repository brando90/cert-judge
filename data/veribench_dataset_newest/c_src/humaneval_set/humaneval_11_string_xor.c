/* Perform binary XOR on two binary strings and return result as a string. */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <assert.h>

/* Caller must free result. */
char *string_xor(const char *a, const char *b) {
    int len = strlen(a);
    char *result = malloc(len + 1);
    for (int i = 0; i < len; i++) {
        result[i] = (a[i] == b[i]) ? '0' : '1';
    }
    result[len] = '\0';
    return result;
}

void check(void) {
    char *r;

    r = string_xor("111000", "101010");
    assert(strcmp(r, "010010") == 0);
    free(r);

    r = string_xor("1", "1");
    assert(strcmp(r, "0") == 0);
    free(r);

    r = string_xor("0101", "0000");
    assert(strcmp(r, "0101") == 0);
    free(r);
}

int main(void) {
    check();
    printf("All tests passed.\n");
    return 0;
}
