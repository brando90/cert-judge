/* Return the n-th number that is both a Fibonacci number and prime. */
#include <stdio.h>
#include <assert.h>
#include <stdint.h>
#include <stdbool.h>
#include <math.h>

static bool is_prime(int64_t p) {
    if (p < 2) return false;
    if (p == 2) return true;
    if (p % 2 == 0) return false;
    for (int64_t k = 3; k <= (int64_t)sqrt((double)p); k += 2) {
        if (p % k == 0) return false;
    }
    return true;
}

int64_t prime_fib(int n) {
    int64_t a = 0, b = 1;
    int count = 0;
    while (1) {
        int64_t next = a + b;
        a = b;
        b = next;
        if (is_prime(b)) {
            count++;
            if (count == n) return b;
        }
    }
}

void check(void) {
    assert(prime_fib(1) == 2);
    assert(prime_fib(2) == 3);
    assert(prime_fib(3) == 5);
    assert(prime_fib(4) == 13);
    assert(prime_fib(5) == 89);
    assert(prime_fib(6) == 233);
    assert(prime_fib(7) == 1597);
    assert(prime_fib(8) == 28657);
    assert(prime_fib(9) == 514229);
    assert(prime_fib(10) == 433494437);
}

int main(void) {
    check();
    printf("All tests passed.\n");
    return 0;
}
