/* Check if there are two distinct elements in the list that sum to zero. */
#include <stdio.h>
#include <assert.h>
#include <stdbool.h>
#include <stdint.h>

bool pairs_sum_to_zero(int64_t *l, int n) {
    for (int i = 0; i < n; i++) {
        for (int j = i + 1; j < n; j++) {
            if (l[i] + l[j] == 0) return true;
        }
    }
    return false;
}

void check(void) {
    {
        int64_t a[] = {1, 3, 5, 0};
        assert(pairs_sum_to_zero(a, 4) == false);
    }
    {
        int64_t a[] = {1, 3, -2, 1};
        assert(pairs_sum_to_zero(a, 4) == false);
    }
    {
        int64_t a[] = {1, 2, 3, 7};
        assert(pairs_sum_to_zero(a, 4) == false);
    }
    {
        int64_t a[] = {2, 4, -5, 3, 5, 7};
        assert(pairs_sum_to_zero(a, 6) == true);
    }
    {
        int64_t a[] = {1};
        assert(pairs_sum_to_zero(a, 1) == false);
    }
    {
        int64_t a[] = {-3, 9, -1, 3, 2, 30};
        assert(pairs_sum_to_zero(a, 6) == true);
    }
    {
        int64_t a[] = {-3, 9, -1, 3, 2, 31};
        assert(pairs_sum_to_zero(a, 6) == true);
    }
    {
        int64_t a[] = {-3, 9, -1, 4, 2, 30};
        assert(pairs_sum_to_zero(a, 6) == false);
    }
    {
        int64_t a[] = {-3, 9, -1, 4, 2, 31};
        assert(pairs_sum_to_zero(a, 6) == false);
    }
}

int main(void) {
    check();
    printf("All tests passed.\n");
    return 0;
}
