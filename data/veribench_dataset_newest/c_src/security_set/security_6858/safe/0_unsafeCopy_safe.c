/* Safe bytearray copy that prevents overflow.
 * Mitigation: verify destination has capacity; otherwise return an error code.
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <assert.h>
#include <stdint.h>
#include <stdbool.h>

/* Returns 0 on success, -1 if src is longer than dst (overflow prevented). */
int safe_copy(uint8_t *dst, size_t dst_len, const uint8_t *src, size_t src_len) {
    if (src_len > dst_len) {
        return -1; /* source longer than destination */
    }
    /* Copy exactly src_len bytes */
    memcpy(dst, src, src_len);
    return 0;
}

void check(void) {
    /* 1) Safe copy: src fits in dst */
    uint8_t d1[3] = {0};
    uint8_t s1[] = {'a', 'b', 'c'};
    assert(safe_copy(d1, 3, s1, 3) == 0);
    assert(memcmp(d1, "abc", 3) == 0);

    /* 2) Exact fit */
    uint8_t d2[2] = {0};
    uint8_t s2[] = {'x', 'y'};
    assert(safe_copy(d2, 2, s2, 2) == 0);
    assert(d2[0] == 'x' && d2[1] == 'y');

    /* 3) Overflow attempt should return error */
    uint8_t d3[2] = {0};
    uint8_t s3[] = {'1', '2', '3'};
    assert(safe_copy(d3, 2, s3, 3) == -1);

    /* 4) Empty src -> no change */
    uint8_t d4[] = {'h', 'e', 'l', 'l', 'o'};
    assert(safe_copy(d4, 5, (uint8_t *)"", 0) == 0);
    assert(memcmp(d4, "hello", 5) == 0);

    /* 5) Empty dst, nonempty src -> error */
    uint8_t s5[] = {'z'};
    assert(safe_copy(NULL, 0, s5, 1) == -1);
}

int main(void) {
    check();
    printf("All tests passed.\n");
    return 0;
}
