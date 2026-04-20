/* Insert a number between every two consecutive elements of input list. */
#include <stdio.h>
#include <stdlib.h>
#include <assert.h>
#include <stdint.h>
#include <string.h>

/* Returns length of result. Caller must free *out. */
int intersperse(int64_t *numbers, int n, int64_t delimeter, int64_t **out) {
    if (n == 0) {
        *out = NULL;
        return 0;
    }
    int result_len = 2 * n - 1;
    *out = malloc(result_len * sizeof(int64_t));
    int idx = 0;
    for (int i = 0; i < n - 1; i++) {
        (*out)[idx++] = numbers[i];
        (*out)[idx++] = delimeter;
    }
    (*out)[idx++] = numbers[n - 1];
    return result_len;
}

void check(void) {
    int64_t *out;
    int len;

    len = intersperse(NULL, 0, 7, &out);
    assert(len == 0);
    assert(out == NULL);

    {
        int64_t a[] = {5, 6, 3, 2};
        int64_t expected[] = {5, 8, 6, 8, 3, 8, 2};
        len = intersperse(a, 4, 8, &out);
        assert(len == 7);
        for (int i = 0; i < 7; i++) assert(out[i] == expected[i]);
        free(out);
    }

    {
        int64_t a[] = {2, 2, 2};
        int64_t expected[] = {2, 2, 2, 2, 2};
        len = intersperse(a, 3, 2, &out);
        assert(len == 5);
        for (int i = 0; i < 5; i++) assert(out[i] == expected[i]);
        free(out);
    }
}

int main(void) {
    check();
    printf("All tests passed.\n");
    return 0;
}
