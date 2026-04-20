/* Detect if at any point the balance of a bank account falls below zero. */
#include <stdio.h>
#include <assert.h>
#include <stdbool.h>
#include <stdint.h>

bool below_zero(int64_t *operations, int n) {
    int64_t balance = 0;
    for (int i = 0; i < n; i++) {
        balance += operations[i];
        if (balance < 0) {
            return true;
        }
    }
    return false;
}

void check(void) {
    assert(below_zero(NULL, 0) == false);
    {
        int64_t a[] = {1, 2, -3, 1, 2, -3};
        assert(below_zero(a, 6) == false);
    }
    {
        int64_t a[] = {1, 2, -4, 5, 6};
        assert(below_zero(a, 5) == true);
    }
    {
        int64_t a[] = {1, -1, 2, -2, 5, -5, 4, -4};
        assert(below_zero(a, 8) == false);
    }
    {
        int64_t a[] = {1, -1, 2, -2, 5, -5, 4, -5};
        assert(below_zero(a, 8) == true);
    }
    {
        int64_t a[] = {1, -2, 2, -2, 5, -5, 4, -4};
        assert(below_zero(a, 8) == true);
    }
}

int main(void) {
    check();
    printf("All tests passed.\n");
    return 0;
}
