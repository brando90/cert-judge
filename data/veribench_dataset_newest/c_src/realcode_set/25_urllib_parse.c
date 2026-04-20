/* Provides URL quoting and unquoting functions.
   Sourced from Python's standard urllib.parse library. */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <assert.h>
#include <stdbool.h>
#include <ctype.h>
#include <stdint.h>

/* -- Implementation -- */

static bool is_always_safe(unsigned char c) {
    if (isalnum(c)) return true;
    return (c == '_' || c == '.' || c == '-' || c == '~');
}

static bool is_in_safe(unsigned char c, const char *safe) {
    for (size_t i = 0; safe[i] != '\0'; i++) {
        if ((unsigned char)safe[i] == c) return true;
    }
    return false;
}

/* quote: percent-encode a string. safe chars are not encoded. */
void url_quote(const char *s, const char *safe, char *out) {
    if (safe == NULL) safe = "/";
    size_t oi = 0;
    for (size_t i = 0; s[i] != '\0'; i++) {
        unsigned char c = (unsigned char)s[i];
        if (is_always_safe(c) || is_in_safe(c, safe)) {
            out[oi++] = (char)c;
        } else {
            snprintf(out + oi, 4, "%%%02X", c);
            oi += 3;
        }
    }
    out[oi] = '\0';
}

/* Also support quoting bytes (raw uint8_t data) */
void url_quote_bytes(const uint8_t *s, int slen, const char *safe, char *out) {
    if (safe == NULL) safe = "/";
    size_t oi = 0;
    for (int i = 0; i < slen; i++) {
        unsigned char c = s[i];
        if (is_always_safe(c) || is_in_safe(c, safe)) {
            out[oi++] = (char)c;
        } else {
            snprintf(out + oi, 4, "%%%02X", c);
            oi += 3;
        }
    }
    out[oi] = '\0';
}

static int hex_val(char c) {
    if (c >= '0' && c <= '9') return c - '0';
    if (c >= 'A' && c <= 'F') return c - 'A' + 10;
    if (c >= 'a' && c <= 'f') return c - 'a' + 10;
    return -1;
}

/* unquote_to_bytes: decode percent-encoded string to raw bytes.
   Returns length of decoded output. */
int url_unquote_to_bytes(const char *s, uint8_t *out) {
    int oi = 0;
    size_t slen = strlen(s);
    for (size_t i = 0; i < slen; i++) {
        if (s[i] == '%' && i + 2 < slen) {
            int h = hex_val(s[i + 1]);
            int l = hex_val(s[i + 2]);
            if (h >= 0 && l >= 0) {
                out[oi++] = (uint8_t)(h * 16 + l);
                i += 2;
                continue;
            }
        }
        out[oi++] = (uint8_t)s[i];
    }
    return oi;
}

/* -- Tests -- */

int check(void) {
    char enc[4096];
    uint8_t dec[4096];
    int dlen;

    /* 1. Test quote (string) */
    url_quote("abc def", "/", enc);
    assert(strcmp(enc, "abc%20def") == 0);

    /* quote bytes */
    url_quote_bytes((const uint8_t *)"abc def", 7, "/", enc);
    assert(strcmp(enc, "abc%20def") == 0);

    url_quote("~@:/", "/", enc);
    assert(strcmp(enc, "~%40%3A/") == 0);

    url_quote("~@:/", "", enc);
    assert(strcmp(enc, "~%40%3A%2F") == 0);

    /* 2. Test unquote_to_bytes */
    dlen = url_unquote_to_bytes("abc%20def", dec);
    assert(dlen == 7 && memcmp(dec, "abc def", 7) == 0);

    dlen = url_unquote_to_bytes("%7E%40%3A%2F", dec);
    assert(dlen == 4 && memcmp(dec, "~@:/", 4) == 0);

    dlen = url_unquote_to_bytes("a%25b", dec);
    assert(dlen == 3 && memcmp(dec, "a%b", 3) == 0);

    /* Invalid percent encoding: %b is not valid hex pair, pass through */
    dlen = url_unquote_to_bytes("a%b", dec);
    assert(dlen == 3 && memcmp(dec, "a%b", 3) == 0);

    /* Mixed case hex */
    dlen = url_unquote_to_bytes("%Ab%eA", dec);
    assert(dlen == 2 && dec[0] == 0xAB && dec[1] == 0xEA);

    return 1;
}

int main(void) {
    assert(check());
    printf("All tests passed.\n");
    return 0;
}
