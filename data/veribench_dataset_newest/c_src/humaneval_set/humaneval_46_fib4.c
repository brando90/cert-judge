/* Compute the n-th element of the fib4 number sequence. */
#include <stdio.h>
#include <assert.h>
#include <stdint.h>

int64_t fib4(int n) {
    int64_t results[4] = {0, 0, 2, 0};
    if (n < 4) return results[n];

    for (int i = 4; i <= n; i++) {
        int64_t next = results[0] + results[1] + results[2] + results[3];
        results[0] = results[1];
        results[1] = results[2];
        results[2] = results[3];
        results[3] = next;
    }
    return results[3];
}

void check(void) {
    assert(fib4(5) == 4);
    assert(fib4(8) == 28);
    assert(fib4(10) == 104);
    assert(fib4(12) == 386);
}

int main(void) {
    check();
    printf("All tests passed.\n");
    return 0;
}
