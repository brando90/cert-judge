/* Return list of prime factors of given integer in order from smallest to largest. */
#include <stdio.h>
#include <stdlib.h>
#include <assert.h>
#include <stdint.h>
#include <math.h>

/* Returns count of factors. Factors stored in result array. */
int factorize(int64_t n, int64_t *result, int max_results) {
    int count = 0;
    int64_t i = 2;
    while (i <= (int64_t)(sqrt((double)n) + 1) && count < max_results) {
        if (n % i == 0) {
            result[count++] = i;
            n /= i;
        } else {
            i++;
        }
    }
    if (n > 1 && count < max_results) {
        result[count++] = n;
    }
    return count;
}

void check(void) {
    int64_t result[100];
    int n;

    n = factorize(2, result, 100);
    assert(n == 1 && result[0] == 2);

    n = factorize(4, result, 100);
    assert(n == 2 && result[0] == 2 && result[1] == 2);

    n = factorize(8, result, 100);
    assert(n == 3 && result[0] == 2 && result[1] == 2 && result[2] == 2);

    n = factorize(3 * 19, result, 100);
    assert(n == 2 && result[0] == 3 && result[1] == 19);

    n = factorize(3 * 19 * 3 * 19, result, 100);
    assert(n == 4);
    assert(result[0] == 3 && result[1] == 3 && result[2] == 19 && result[3] == 19);

    n = factorize(3 * 19 * 3 * 19 * 3 * 19, result, 100);
    assert(n == 6);

    n = factorize(3 * 19 * 19 * 19, result, 100);
    assert(n == 4 && result[0] == 3 && result[1] == 19 && result[2] == 19 && result[3] == 19);

    n = factorize(3 * 2 * 3, result, 100);
    assert(n == 3 && result[0] == 2 && result[1] == 3 && result[2] == 3);
}

int main(void) {
    check();
    printf("All tests passed.\n");
    return 0;
}
