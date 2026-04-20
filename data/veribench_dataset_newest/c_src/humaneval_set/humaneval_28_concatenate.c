/* Concatenate list of strings into a single string. */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <assert.h>

/* Caller must free result. */
char *concatenate(const char **strings, int n) {
    int total_len = 0;
    for (int i = 0; i < n; i++) {
        total_len += strlen(strings[i]);
    }
    char *result = malloc(total_len + 1);
    int pos = 0;
    for (int i = 0; i < n; i++) {
        int slen = strlen(strings[i]);
        memcpy(result + pos, strings[i], slen);
        pos += slen;
    }
    result[pos] = '\0';
    return result;
}

void check(void) {
    char *r;

    r = concatenate(NULL, 0);
    assert(strcmp(r, "") == 0);
    free(r);

    {
        const char *a[] = {"x", "y", "z"};
        r = concatenate(a, 3);
        assert(strcmp(r, "xyz") == 0);
        free(r);
    }

    {
        const char *a[] = {"x", "y", "z", "w", "k"};
        r = concatenate(a, 5);
        assert(strcmp(r, "xyzwk") == 0);
        free(r);
    }
}

int main(void) {
    check();
    printf("All tests passed.\n");
    return 0;
}
