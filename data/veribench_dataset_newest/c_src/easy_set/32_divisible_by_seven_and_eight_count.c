/* Count numbers divisible by both 7 and 8 in a list of integers.
 *
 * Edge cases:
 * - Empty list returns 0.
 * - 0 is divisible by both 7 and 8.
 */

#include <stdio.h>
#include <assert.h>
#include <stdint.h>

int pre_count(const int64_t *xs, int n) {
    (void)xs;
    return (n >= 0);
}

int64_t count_div_by_7_and_8(const int64_t *xs, int n) {
    if (!pre_count(xs, n)) return -1;
    int64_t count = 0;
    for (int i = 0; i < n; i++) {
        if (xs[i] % 7 == 0 && xs[i] % 8 == 0) count++;
    }
    return count;
}

int check(void) {
    {
        int64_t a[] = {56, 14, 28, 112};
        assert(count_div_by_7_and_8(a, 4) == 2);
    }
    assert(count_div_by_7_and_8(NULL, 0) == 0);
    return 1;
}

int main(void) {
    assert(check());
    printf("All tests passed.\n");
    return 0;
}
