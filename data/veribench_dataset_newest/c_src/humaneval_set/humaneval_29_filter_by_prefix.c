/* Filter an input list of strings only for ones that start with a given prefix. */
#include <stdio.h>
#include <string.h>
#include <assert.h>

/* Returns count of matches. result[i] points into original array. */
int filter_by_prefix(const char **strings, int n, const char *prefix, const char **result) {
    int count = 0;
    int plen = strlen(prefix);
    for (int i = 0; i < n; i++) {
        if (strncmp(strings[i], prefix, plen) == 0) {
            result[count++] = strings[i];
        }
    }
    return count;
}

void check(void) {
    const char *result[20];
    int n;

    n = filter_by_prefix(NULL, 0, "john", result);
    assert(n == 0);

    {
        const char *a[] = {"xxx", "asd", "xxy", "john doe", "xxxAAA", "xxx"};
        n = filter_by_prefix(a, 6, "xxx", result);
        assert(n == 3);
        assert(strcmp(result[0], "xxx") == 0);
        assert(strcmp(result[1], "xxxAAA") == 0);
        assert(strcmp(result[2], "xxx") == 0);
    }
}

int main(void) {
    check();
    printf("All tests passed.\n");
    return 0;
}
