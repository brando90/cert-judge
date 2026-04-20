/* Filter an input list of strings only for ones that contain a given substring. */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <assert.h>

/* Returns count of matching strings. result[i] points into original strings array (not copied). */
int filter_by_substring(const char **strings, int n, const char *substring, const char **result) {
    int count = 0;
    for (int i = 0; i < n; i++) {
        if (strstr(strings[i], substring) != NULL) {
            result[count++] = strings[i];
        }
    }
    return count;
}

void check(void) {
    const char *result[20];
    int n;

    n = filter_by_substring(NULL, 0, "john", result);
    assert(n == 0);

    {
        const char *a[] = {"xxx", "asd", "xxy", "john doe", "xxxAAA", "xxx"};
        n = filter_by_substring(a, 6, "xxx", result);
        assert(n == 3);
        assert(strcmp(result[0], "xxx") == 0);
        assert(strcmp(result[1], "xxxAAA") == 0);
        assert(strcmp(result[2], "xxx") == 0);
    }

    {
        const char *a[] = {"xxx", "asd", "aaaxxy", "john doe", "xxxAAA", "xxx"};
        n = filter_by_substring(a, 6, "xx", result);
        assert(n == 4);
        assert(strcmp(result[0], "xxx") == 0);
        assert(strcmp(result[1], "aaaxxy") == 0);
        assert(strcmp(result[2], "xxxAAA") == 0);
        assert(strcmp(result[3], "xxx") == 0);
    }

    {
        const char *a[] = {"grunt", "trumpet", "prune", "gruesome"};
        n = filter_by_substring(a, 4, "run", result);
        assert(n == 2);
        assert(strcmp(result[0], "grunt") == 0);
        assert(strcmp(result[1], "prune") == 0);
    }
}

int main(void) {
    check();
    printf("All tests passed.\n");
    return 0;
}
