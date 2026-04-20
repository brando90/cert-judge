/* For a given list of integers, return sum and product of all the integers. */
#include <stdio.h>
#include <assert.h>
#include <stdint.h>

void sum_product(int64_t *numbers, int n, int64_t *out_sum, int64_t *out_product) {
    *out_sum = 0;
    *out_product = 1;
    for (int i = 0; i < n; i++) {
        *out_sum += numbers[i];
        *out_product *= numbers[i];
    }
}

void check(void) {
    int64_t s, p;

    sum_product(NULL, 0, &s, &p);
    assert(s == 0 && p == 1);

    {
        int64_t a[] = {1, 1, 1};
        sum_product(a, 3, &s, &p);
        assert(s == 3 && p == 1);
    }

    {
        int64_t a[] = {100, 0};
        sum_product(a, 2, &s, &p);
        assert(s == 100 && p == 0);
    }

    {
        int64_t a[] = {3, 5, 7};
        sum_product(a, 3, &s, &p);
        assert(s == 15 && p == 105);
    }

    {
        int64_t a[] = {10};
        sum_product(a, 1, &s, &p);
        assert(s == 10 && p == 10);
    }
}

int main(void) {
    check();
    printf("All tests passed.\n");
    return 0;
}
