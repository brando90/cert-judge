/* Secure Token Generation and Comparison.
   Sourced from Python's standard secrets library.
   NOTE: simplified from Python version -- uses deterministic stub (0xAB bytes)
   matching the Python benchmark behavior. */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <assert.h>
#include <stdbool.h>
#include <stdint.h>
#include <ctype.h>

/* -- Implementation -- */

#define DEFAULT_ENTROPY 32

/* compare_digest: constant-time string comparison.
   Returns true if a == b, false otherwise. */
bool compare_digest(const char *a, const char *b) {
    size_t la = strlen(a);
    size_t lb = strlen(b);
    if (la != lb) return false;

    int result = 0;
    for (size_t i = 0; i < la; i++) {
        result |= (unsigned char)a[i] ^ (unsigned char)b[i];
    }
    return result == 0;
}

/* compare_digest for byte arrays */
bool compare_digest_bytes(const uint8_t *a, size_t la, const uint8_t *b, size_t lb) {
    if (la != lb) return false;
    int result = 0;
    for (size_t i = 0; i < la; i++) {
        result |= a[i] ^ b[i];
    }
    return result == 0;
}

/* token_bytes: deterministic stub -- returns 0xAB repeated nbytes times */
void token_bytes(int nbytes, uint8_t *out) {
    if (nbytes < 0) nbytes = DEFAULT_ENTROPY;
    memset(out, 0xAB, (size_t)nbytes);
}

/* token_hex: returns hex representation of token_bytes */
void token_hex(int nbytes, char *out) {
    if (nbytes < 0) nbytes = DEFAULT_ENTROPY;
    uint8_t buf[256];
    token_bytes(nbytes, buf);
    for (int i = 0; i < nbytes; i++) {
        sprintf(out + 2 * i, "%02x", buf[i]);
    }
    out[2 * nbytes] = '\0';
}

/* -- Tests -- */

static bool is_hexdigit(char c) {
    return (c >= '0' && c <= '9') || (c >= 'a' && c <= 'f') || (c >= 'A' && c <= 'F');
}

int check(void) {
    char hex[1024];

    /* 1. Token Hex */
    int sizes[] = {1, 8, 16, 32};
    for (int i = 0; i < 4; i++) {
        int n = sizes[i];
        token_hex(n, hex);
        assert((int)strlen(hex) == 2 * n);
        for (int j = 0; hex[j] != '\0'; j++) {
            assert(is_hexdigit(hex[j]));
        }
    }
    /* Default */
    token_hex(-1, hex);
    assert((int)strlen(hex) == 2 * DEFAULT_ENTROPY);

    /* 2. Compare Digest */
    assert(compare_digest("abc", "abc") == true);
    assert(compare_digest("abc", "abcd") == false);

    uint8_t b1[] = {'x', 'y', 'z'};
    uint8_t b2[] = {'x', 'y', 'z'};
    uint8_t b3[] = {'a', 'b', 'c'};
    assert(compare_digest_bytes(b1, 3, b2, 3) == true);
    assert(compare_digest_bytes(b1, 3, b3, 3) == false);

    /* 3. Constant-time logic check */
    assert(compare_digest("aaaaa", "aaaab") == false);

    return 1;
}

int main(void) {
    assert(check());
    printf("All tests passed.\n");
    return 0;
}
