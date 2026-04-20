/* Provides an HTML-safe escaping function.
   Sourced from Python's standard html library. */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <assert.h>
#include <stdbool.h>

/* -- Pre-condition -- */
int pre_escape(const char *s) {
    return s != NULL;
}

/* -- Implementation -- */

/* escape: Replace special characters to HTML-safe sequences.
   Result written to out (must be at least 6x len(s) + 1). */
void escape(const char *s, bool quote, char *out) {
    size_t oi = 0;
    for (size_t i = 0; s[i] != '\0'; i++) {
        char c = s[i];
        if (c == '&') {
            memcpy(out + oi, "&amp;", 5); oi += 5;
        } else if (c == '<') {
            memcpy(out + oi, "&lt;", 4); oi += 4;
        } else if (c == '>') {
            memcpy(out + oi, "&gt;", 4); oi += 4;
        } else if (quote && c == '"') {
            memcpy(out + oi, "&quot;", 6); oi += 6;
        } else if (quote && c == '\'') {
            memcpy(out + oi, "&#x27;", 6); oi += 6;
        } else {
            out[oi++] = c;
        }
    }
    out[oi] = '\0';
}

void benchmark_escape(const char *s, bool quote, char *out) {
    if (!pre_escape(s)) {
        fprintf(stderr, "TypeError: expected str object\n");
        exit(1);
    }
    escape(s, quote, out);
}

/* -- Tests -- */

int check(void) {
    char out[4096];

    /* 1. Quote=True (Default) */
    benchmark_escape("<b>\"&'</b>", true, out);
    assert(strcmp(out, "&lt;b&gt;&quot;&amp;&#x27;&lt;/b&gt;") == 0);

    benchmark_escape("", true, out);
    assert(strcmp(out, "") == 0);

    /* 2. Quote=False */
    benchmark_escape("<b>\"&'</b>", false, out);
    assert(strcmp(out, "&lt;b&gt;\"&amp;'&lt;/b&gt;") == 0);

    /* 3. Order check */
    benchmark_escape("&<", true, out);
    assert(strcmp(out, "&amp;&lt;") == 0);

    return 1;
}

int main(void) {
    assert(check());
    printf("All tests passed.\n");
    return 0;
}
