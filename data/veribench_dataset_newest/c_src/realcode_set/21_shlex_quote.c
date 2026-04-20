/* Provides a function for shell-escaping a string.
   Sourced from Python's standard shlex library. */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <assert.h>
#include <stdbool.h>
#include <ctype.h>

/* -- Pre-condition -- */
int pre_quote(const char *s) {
    return s != NULL;
}

/* -- Implementation -- */

static bool is_safe_char(char c) {
    if (isalnum((unsigned char)c)) return true;
    /* _@%+=:,./-  */
    return (c == '_' || c == '@' || c == '%' || c == '+' || c == '=' ||
            c == ':' || c == ',' || c == '.' || c == '/' || c == '-');
}

/* quote: Return a shell-escaped version of string s.
   Result written to out (must be large enough). */
void quote(const char *s, char *out) {
    if (s[0] == '\0') {
        strcpy(out, "''");
        return;
    }
    /* Check if all chars are safe */
    bool all_safe = true;
    for (size_t i = 0; s[i] != '\0'; i++) {
        if (!is_safe_char(s[i])) {
            all_safe = false;
            break;
        }
    }
    if (all_safe) {
        strcpy(out, s);
        return;
    }
    /* Use single quotes, replace ' with '"'"' */
    size_t oi = 0;
    out[oi++] = '\'';
    for (size_t i = 0; s[i] != '\0'; i++) {
        if (s[i] == '\'') {
            out[oi++] = '\'';
            out[oi++] = '"';
            out[oi++] = '\'';
            out[oi++] = '"';
            out[oi++] = '\'';
        } else {
            out[oi++] = s[i];
        }
    }
    out[oi++] = '\'';
    out[oi] = '\0';
}

void benchmark_quote(const char *s, char *out) {
    if (!pre_quote(s)) {
        fprintf(stderr, "TypeError: expected string object\n");
        exit(1);
    }
    quote(s, out);
}

/* -- Tests -- */

int check(void) {
    char out[4096];

    /* 1. Empty string */
    benchmark_quote("", out);
    assert(strcmp(out, "''") == 0);

    /* 2. Safe string */
    benchmark_quote("abc", out);
    assert(strcmp(out, "abc") == 0);

    /* 3. String with spaces */
    benchmark_quote("a b c", out);
    assert(strcmp(out, "'a b c'") == 0);

    /* 4. String with quotes */
    benchmark_quote("a'b", out);
    assert(strcmp(out, "'a'\"'\"'b'") == 0);

    return 1;
}

int main(void) {
    assert(check());
    printf("All tests passed.\n");
    return 0;
}
