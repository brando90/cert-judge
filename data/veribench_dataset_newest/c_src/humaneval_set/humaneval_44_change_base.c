/* Change numerical base of input number x to base (base < 10). */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <assert.h>
#include <stdint.h>

/* Caller must free result. */
char *change_base(int64_t x, int base) {
    if (x == 0) {
        char *r = malloc(2);
        r[0] = '0';
        r[1] = '\0';
        return r;
    }
    char buf[128];
    int pos = 0;
    while (x > 0) {
        buf[pos++] = '0' + (int)(x % base);
        x /= base;
    }
    char *result = malloc(pos + 1);
    for (int i = 0; i < pos; i++) {
        result[i] = buf[pos - 1 - i];
    }
    result[pos] = '\0';
    return result;
}

void check(void) {
    char *r;

    r = change_base(8, 3);
    assert(strcmp(r, "22") == 0);
    free(r);

    r = change_base(9, 3);
    assert(strcmp(r, "100") == 0);
    free(r);

    r = change_base(234, 2);
    assert(strcmp(r, "11101010") == 0);
    free(r);

    r = change_base(16, 2);
    assert(strcmp(r, "10000") == 0);
    free(r);

    r = change_base(8, 2);
    assert(strcmp(r, "1000") == 0);
    free(r);

    r = change_base(7, 2);
    assert(strcmp(r, "111") == 0);
    free(r);

    for (int x = 2; x < 8; x++) {
        char expected[4];
        sprintf(expected, "%d", x);
        r = change_base(x, x + 1);
        assert(strcmp(r, expected) == 0);
        free(r);
    }
}

int main(void) {
    check();
    printf("All tests passed.\n");
    return 0;
}
