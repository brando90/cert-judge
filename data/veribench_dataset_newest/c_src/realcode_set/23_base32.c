/* Provides Base32 encoding and decoding.
   Sourced from Python's standard base64 library. */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <assert.h>
#include <stdint.h>
#include <stdbool.h>
#include <ctype.h>

/* -- Implementation -- */

static const char _b32alphabet[] = "ABCDEFGHIJKLMNOPQRSTUVWXYZ234567";

/* b32encode: Encode bytes s of length slen using Base32.
   Result written to out. Returns length of encoded output. */
int b32encode(const uint8_t *s, int slen, char *out) {
    if (slen == 0) {
        out[0] = '\0';
        return 0;
    }

    int oi = 0;
    for (int i = 0; i < slen; i += 5) {
        uint8_t chunk[5] = {0};
        int chunk_len = (slen - i < 5) ? (slen - i) : 5;
        memcpy(chunk, s + i, (size_t)chunk_len);

        /* Combine into 40-bit value */
        uint64_t val = ((uint64_t)chunk[0] << 32) |
                       ((uint64_t)chunk[1] << 24) |
                       ((uint64_t)chunk[2] << 16) |
                       ((uint64_t)chunk[3] << 8)  |
                       ((uint64_t)chunk[4]);

        out[oi++] = _b32alphabet[(val >> 35) & 0x1F];
        out[oi++] = _b32alphabet[(val >> 30) & 0x1F];
        out[oi++] = _b32alphabet[(val >> 25) & 0x1F];
        out[oi++] = _b32alphabet[(val >> 20) & 0x1F];
        out[oi++] = _b32alphabet[(val >> 15) & 0x1F];
        out[oi++] = _b32alphabet[(val >> 10) & 0x1F];
        out[oi++] = _b32alphabet[(val >> 5) & 0x1F];
        out[oi++] = _b32alphabet[val & 0x1F];
    }

    /* Fix padding */
    int rem = slen % 5;
    if (rem == 1) { memcpy(out + oi - 6, "======", 6); }
    else if (rem == 2) { memcpy(out + oi - 4, "====", 4); }
    else if (rem == 3) { memcpy(out + oi - 3, "===", 3); }
    else if (rem == 4) { memcpy(out + oi - 1, "=", 1); }

    out[oi] = '\0';
    return oi;
}

/* b32decode: Decode Base32 string s into bytes. casefold: uppercase before decode.
   Result written to out. Returns length of decoded output. */
int b32decode(const char *s, bool casefold, uint8_t *out) {
    int slen = (int)strlen(s);
    if (slen == 0) return 0;

    /* Copy and optionally casefold */
    char *buf = (char *)malloc((size_t)(slen + 1));
    memcpy(buf, s, (size_t)(slen + 1));
    if (casefold) {
        for (int i = 0; i < slen; i++) buf[i] = (char)toupper((unsigned char)buf[i]);
    }

    /* Strip padding */
    while (slen > 0 && buf[slen - 1] == '=') slen--;

    /* Build reverse alphabet */
    int rev[256];
    memset(rev, -1, sizeof(rev));
    for (int i = 0; i < 32; i++) rev[(unsigned char)_b32alphabet[i]] = i;

    uint64_t val = 0;
    int bits = 0;
    int oi = 0;

    for (int i = 0; i < slen; i++) {
        int idx = rev[(unsigned char)buf[i]];
        if (idx < 0) {
            fprintf(stderr, "binascii.Error: Non-base32 digit found\n");
            free(buf);
            exit(1);
        }
        val = (val << 5) | (uint64_t)idx;
        bits += 5;
        if (bits >= 8) {
            bits -= 8;
            out[oi++] = (uint8_t)((val >> bits) & 0xFF);
        }
    }

    free(buf);
    return oi;
}

/* -- Tests -- */

int check(void) {
    char enc[256];
    uint8_t dec[256];

    /* b32encode tests */
    b32encode((const uint8_t *)"", 0, enc);
    assert(strcmp(enc, "") == 0);

    b32encode((const uint8_t *)"f", 1, enc);
    assert(strcmp(enc, "MY======") == 0);

    b32encode((const uint8_t *)"fo", 2, enc);
    assert(strcmp(enc, "MZXQ====") == 0);

    b32encode((const uint8_t *)"foo", 3, enc);
    assert(strcmp(enc, "MZXW6===") == 0);

    b32encode((const uint8_t *)"foob", 4, enc);
    assert(strcmp(enc, "MZXW6YQ=") == 0);

    b32encode((const uint8_t *)"fooba", 5, enc);
    assert(strcmp(enc, "MZXW6YTB") == 0);

    b32encode((const uint8_t *)"foobar", 6, enc);
    assert(strcmp(enc, "MZXW6YTBOI======") == 0);

    /* Round-trip */
    const char *msg = "VeriBench";
    b32encode((const uint8_t *)msg, (int)strlen(msg), enc);
    int dlen = b32decode(enc, false, dec);
    dec[dlen] = '\0';
    assert(strcmp((char *)dec, msg) == 0);

    /* Case-folded decode */
    dlen = b32decode("mzxw6ytb", true, dec);
    dec[dlen] = '\0';
    assert(strcmp((char *)dec, "fooba") == 0);

    return 1;
}

int main(void) {
    assert(check());
    printf("All tests passed.\n");
    return 0;
}
