/* Return the nth Fibonacci number for natural number indices.
 *
 * Edge cases:
 * - fibonacci(0) = 0
 * - fibonacci(1) = 1
 * - fibonacci(n) = fibonacci(n-1) + fibonacci(n-2) for n > 1
 * - Returns -1 if input is not a natural number.
 */

#include <stdio.h>
#include <assert.h>
#include <stdint.h>

int pre_prog(int64_t n) {
    return (n >= 0);
}

int64_t prog(int64_t n) {
    if (!pre_prog(n)) return -1;
    if (n <= 1) return n;
    int64_t a = 0, b = 1;
    for (int64_t i = 2; i <= n; i++) {
        int64_t tmp = a + b;
        a = b;
        b = tmp;
    }
    return b;
}

int check(void) {
    assert(prog(6) == 8);
    assert(prog(0) == 0);
    assert(pre_prog(-1) == 0);
    return 1;
}

int main(void) {
    assert(check());
    printf("All tests passed.\n");
    return 0;
}
