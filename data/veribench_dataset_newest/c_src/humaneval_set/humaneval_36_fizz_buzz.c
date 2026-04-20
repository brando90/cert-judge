/* Return the number of times digit 7 appears in integers less than n divisible by 11 or 13. */
#include <stdio.h>
#include <assert.h>
#include <stdint.h>

int64_t fizz_buzz(int64_t n) {
    int64_t ans = 0;
    for (int64_t i = 0; i < n; i++) {
        if (i % 11 == 0 || i % 13 == 0) {
            /* Count digit 7 in i */
            int64_t val = i;
            if (val == 0) continue;
            while (val > 0) {
                if (val % 10 == 7) ans++;
                val /= 10;
            }
        }
    }
    return ans;
}

void check(void) {
    assert(fizz_buzz(50) == 0);
    assert(fizz_buzz(78) == 2);
    assert(fizz_buzz(79) == 3);
    assert(fizz_buzz(100) == 3);
    assert(fizz_buzz(200) == 6);
    assert(fizz_buzz(4000) == 192);
    assert(fizz_buzz(10000) == 639);
    assert(fizz_buzz(100000) == 8026);
}

int main(void) {
    check();
    printf("All tests passed.\n");
    return 0;
}
