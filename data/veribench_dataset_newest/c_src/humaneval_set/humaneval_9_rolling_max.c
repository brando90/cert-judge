/* From a given list of integers, generate a list of rolling maximum. */
#include <stdio.h>
#include <stdlib.h>
#include <assert.h>
#include <stdint.h>

/* Returns length of result. Caller must free *out. */
int rolling_max(int64_t *numbers, int n, int64_t **out) {
    if (n == 0) {
        *out = NULL;
        return 0;
    }
    *out = malloc(n * sizeof(int64_t));
    int64_t running_max = numbers[0];
    (*out)[0] = running_max;
    for (int i = 1; i < n; i++) {
        if (numbers[i] > running_max) {
            running_max = numbers[i];
        }
        (*out)[i] = running_max;
    }
    return n;
}

void check(void) {
    int64_t *out;
    int len;

    len = rolling_max(NULL, 0, &out);
    assert(len == 0);

    {
        int64_t a[] = {1, 2, 3, 4};
        int64_t expected[] = {1, 2, 3, 4};
        len = rolling_max(a, 4, &out);
        assert(len == 4);
        for (int i = 0; i < 4; i++) assert(out[i] == expected[i]);
        free(out);
    }

    {
        int64_t a[] = {4, 3, 2, 1};
        int64_t expected[] = {4, 4, 4, 4};
        len = rolling_max(a, 4, &out);
        assert(len == 4);
        for (int i = 0; i < 4; i++) assert(out[i] == expected[i]);
        free(out);
    }

    {
        int64_t a[] = {3, 2, 3, 100, 3};
        int64_t expected[] = {3, 3, 3, 100, 100};
        len = rolling_max(a, 5, &out);
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
