/* From a list of integers, remove all elements that occur more than once. */
#include <stdio.h>
#include <stdlib.h>
#include <assert.h>
#include <stdint.h>

/* Returns count of elements kept. Results in out array. */
int remove_duplicates(int64_t *numbers, int n, int64_t *out) {
    /* Count occurrences */
    int count = 0;
    for (int i = 0; i < n; i++) {
        int freq = 0;
        for (int j = 0; j < n; j++) {
            if (numbers[j] == numbers[i]) freq++;
        }
        if (freq <= 1) {
            out[count++] = numbers[i];
        }
    }
    return count;
}

void check(void) {
    int64_t out[100];
    int n;

    n = remove_duplicates(NULL, 0, out);
    assert(n == 0);

    {
        int64_t a[] = {1, 2, 3, 4};
        n = remove_duplicates(a, 4, out);
        assert(n == 4);
        assert(out[0] == 1 && out[1] == 2 && out[2] == 3 && out[3] == 4);
    }

    {
        int64_t a[] = {1, 2, 3, 2, 4, 3, 5};
        n = remove_duplicates(a, 7, out);
        assert(n == 3);
        assert(out[0] == 1 && out[1] == 4 && out[2] == 5);
    }
}

int main(void) {
    check();
    printf("All tests passed.\n");
    return 0;
}
