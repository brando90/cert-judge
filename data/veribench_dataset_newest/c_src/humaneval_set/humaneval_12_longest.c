/* Out of list of strings, return the longest one. Return NULL if list is empty. */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <assert.h>

/* Returns pointer into original array (not a copy). Returns NULL if n==0. */
const char *longest(const char **strings, int n) {
    if (n == 0) return NULL;
    int maxlen = 0;
    for (int i = 0; i < n; i++) {
        int l = strlen(strings[i]);
        if (l > maxlen) maxlen = l;
    }
    for (int i = 0; i < n; i++) {
        if ((int)strlen(strings[i]) == maxlen) return strings[i];
    }
    return NULL;
}

void check(void) {
    assert(longest(NULL, 0) == NULL);

    {
        const char *a[] = {"x", "y", "z"};
        assert(strcmp(longest(a, 3), "x") == 0);
    }
    {
        const char *a[] = {"x", "yyy", "zzzz", "www", "kkkk", "abc"};
        assert(strcmp(longest(a, 6), "zzzz") == 0);
    }
}

int main(void) {
    check();
    printf("All tests passed.\n");
    return 0;
}
