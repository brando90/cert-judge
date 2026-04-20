/* Check if there are three distinct elements in the list that sum to zero. */
#include <stdio.h>
#include <assert.h>
#include <stdbool.h>
#include <stdint.h>

bool triples_sum_to_zero(int64_t *l, int n) {
    for (int i = 0; i < n; i++) {
        for (int j = i + 1; j < n; j++) {
            for (int k = j + 1; k < n; k++) {
                if (l[i] + l[j] + l[k] == 0) return true;
            }
        }
    }
    return false;
}

void check(void) {
    {
        int64_t a[] = {1, 3, 5, 0};
        assert(triples_sum_to_zero(a, 4) == false);
    }
    {
        int64_t a[] = {1, 3, 5, -1};
        assert(triples_sum_to_zero(a, 4) == false);
    }
    {
        int64_t a[] = {1, 3, -2, 1};
        assert(triples_sum_to_zero(a, 4) == true);
    }
    {
        int64_t a[] = {1, 2, 3, 7};
        assert(triples_sum_to_zero(a, 4) == false);
    }
    {
        int64_t a[] = {1, 2, 5, 7};
        assert(triples_sum_to_zero(a, 4) == false);
    }
    {
        int64_t a[] = {2, 4, -5, 3, 9, 7};
        assert(triples_sum_to_zero(a, 6) == true);
    }
    {
        int64_t a[] = {1};
        assert(triples_sum_to_zero(a, 1) == false);
    }
    {
        int64_t a[] = {1, 3, 5, -100};
        assert(triples_sum_to_zero(a, 4) == false);
    }
    {
        int64_t a[] = {100, 3, 5, -100};
        assert(triples_sum_to_zero(a, 4) == false);
    }
}

int main(void) {
    check();
    printf("All tests passed.\n");
    return 0;
}
