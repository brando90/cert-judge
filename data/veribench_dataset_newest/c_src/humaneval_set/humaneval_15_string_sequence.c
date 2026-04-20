/* Return a string containing space-delimited numbers starting from 0 up to n inclusive. */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <assert.h>
#include <stdint.h>

/* Caller must free result. */
char *string_sequence(int64_t n) {
    /* Estimate max size: each number up to ~20 digits + space */
    int buf_size = (n + 1) * 22;
    char *result = malloc(buf_size);
    result[0] = '\0';
    int pos = 0;
    for (int64_t i = 0; i <= n; i++) {
        if (i > 0) {
            pos += sprintf(result + pos, " ");
        }
        pos += sprintf(result + pos, "%ld", (long)i);
    }
    return result;
}

void check(void) {
    char *r;

    r = string_sequence(0);
    assert(strcmp(r, "0") == 0);
    free(r);

    r = string_sequence(3);
    assert(strcmp(r, "0 1 2 3") == 0);
    free(r);

    r = string_sequence(10);
    assert(strcmp(r, "0 1 2 3 4 5 6 7 8 9 10") == 0);
    free(r);
}

int main(void) {
    check();
    printf("All tests passed.\n");
    return 0;
}
