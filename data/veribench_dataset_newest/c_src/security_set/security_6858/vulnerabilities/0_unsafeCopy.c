/* Unsafe bytearray copy without bounds checking.
 * If src_len > dst_len, this writes past the end of dst (buffer overflow).
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <assert.h>
#include <stdint.h>

void unsafe_copy(uint8_t *dst, size_t dst_len, const uint8_t *src, size_t src_len) {
    /* Copy bytes from src into dst without any bounds checking.
     * If src_len > dst_len, this overflows the dst buffer.
     * We use a separate output buffer to detect the overflow safely. */
    for (size_t i = 0; i < src_len; i++) {
        if (i >= dst_len) {
            /* In real C this would be a silent buffer overflow.
             * We simulate the "IndexError" by aborting. */
            fprintf(stderr, "Buffer overflow at index %zu (dst_len=%zu)\n", i, dst_len);
            exit(1);
        }
        dst[i] = src[i];
    }
}

/* Wrapper that detects overflow via setjmp-like pattern.
 * We fork to detect the exit(1) from overflow. */
#include <sys/wait.h>
#include <unistd.h>

/* Returns 0 if no overflow, 1 if overflow detected. */
int try_unsafe_copy(uint8_t *dst, size_t dst_len, const uint8_t *src, size_t src_len) {
    pid_t pid = fork();
    if (pid == 0) {
        /* Child: attempt the copy. exit(0) on success, exit(1) on overflow. */
        unsafe_copy(dst, dst_len, src, src_len);
        _exit(0);
    }
    int status;
    waitpid(pid, &status, 0);
    if (WIFEXITED(status) && WEXITSTATUS(status) == 0) {
        /* Success in child, but child's memory is separate.
         * Re-do the copy in parent (we know it's safe). */
        unsafe_copy(dst, dst_len, src, src_len);
        return 0;
    }
    return 1; /* overflow */
}

void check(void) {
    /* 1) Safe copy: src fits in dst */
    uint8_t d1[3] = {0};
    uint8_t s1[] = {'a', 'b', 'c'};
    assert(try_unsafe_copy(d1, 3, s1, 3) == 0);
    assert(d1[0] == 'a' && d1[1] == 'b' && d1[2] == 'c');

    /* 2) Exact fit */
    uint8_t d2[2] = {0};
    uint8_t s2[] = {'x', 'y'};
    assert(try_unsafe_copy(d2, 2, s2, 2) == 0);
    assert(d2[0] == 'x' && d2[1] == 'y');

    /* 3) Overflow: src longer than dst */
    uint8_t d3[2] = {0};
    uint8_t s3[] = {'1', '2', '3'};
    assert(try_unsafe_copy(d3, 2, s3, 3) == 1);

    /* 4) Empty src -> no change */
    uint8_t d4[] = {'h', 'e', 'l', 'l', 'o'};
    assert(try_unsafe_copy(d4, 5, (uint8_t*)"", 0) == 0);
    assert(memcmp(d4, "hello", 5) == 0);

    /* 5) Empty dst, nonempty src -> immediate overflow */
    uint8_t s5[] = {'z'};
    assert(try_unsafe_copy(NULL, 0, s5, 1) == 1);
}

int main(void) {
    check();
    printf("All tests passed.\n");
    return 0;
}
