/* Return list of all prefixes from shortest to longest of the input string. */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <assert.h>

/* Returns count of prefixes. result[i] is malloc'd, caller must free. */
int all_prefixes(const char *string, char **result, int max_results) {
    int len = strlen(string);
    int count = 0;
    for (int i = 0; i < len && count < max_results; i++) {
        result[count] = malloc(i + 2);
        memcpy(result[count], string, i + 1);
        result[count][i + 1] = '\0';
        count++;
    }
    return count;
}

void check(void) {
    char *result[100];
    int n;

    n = all_prefixes("", result, 100);
    assert(n == 0);

    n = all_prefixes("asdfgh", result, 100);
    assert(n == 6);
    assert(strcmp(result[0], "a") == 0);
    assert(strcmp(result[1], "as") == 0);
    assert(strcmp(result[2], "asd") == 0);
    assert(strcmp(result[3], "asdf") == 0);
    assert(strcmp(result[4], "asdfg") == 0);
    assert(strcmp(result[5], "asdfgh") == 0);
    for (int i = 0; i < n; i++) free(result[i]);

    n = all_prefixes("WWW", result, 100);
    assert(n == 3);
    assert(strcmp(result[0], "W") == 0);
    assert(strcmp(result[1], "WW") == 0);
    assert(strcmp(result[2], "WWW") == 0);
    for (int i = 0; i < n; i++) free(result[i]);
}

int main(void) {
    check();
    printf("All tests passed.\n");
    return 0;
}
