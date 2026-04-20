/* Provides a function to join shell arguments.
   Sourced from Python's standard shlex library. */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <assert.h>
#include <stdbool.h>
#include <ctype.h>

/* -- Pre-condition -- */
int pre_join(const char **args, int n) {
    if (args == NULL && n > 0) return 0;
    for (int i = 0; i < n; i++) {
        if (args[i] == NULL) return 0;
    }
    return 1;
}

/* -- Implementation -- */

static bool is_safe_char(char c) {
    if (isalnum((unsigned char)c)) return true;
    return (c == '_' || c == '@' || c == '%' || c == '+' || c == '=' ||
            c == ':' || c == ',' || c == '.' || c == '/' || c == '-');
}

static size_t quote_to(const char *s, char *out) {
    if (s[0] == '\0') {
        memcpy(out, "''", 2);
        return 2;
    }
    bool all_safe = true;
    size_t slen = strlen(s);
    for (size_t i = 0; i < slen; i++) {
        if (!is_safe_char(s[i])) { all_safe = false; break; }
    }
    if (all_safe) {
        memcpy(out, s, slen);
        return slen;
    }
    size_t oi = 0;
    out[oi++] = '\'';
    for (size_t i = 0; i < slen; i++) {
        if (s[i] == '\'') {
            out[oi++] = '\''; out[oi++] = '"'; out[oi++] = '\'';
            out[oi++] = '"'; out[oi++] = '\'';
        } else {
            out[oi++] = s[i];
        }
    }
    out[oi++] = '\'';
    return oi;
}

void join(const char **args, int n, char *out) {
    size_t oi = 0;
    for (int i = 0; i < n; i++) {
        if (i > 0) out[oi++] = ' ';
        oi += quote_to(args[i], out + oi);
    }
    out[oi] = '\0';
}

void benchmark_join(const char **args, int n, char *out) {
    if (!pre_join(args, n)) {
        fprintf(stderr, "TypeError: expected list of strings\n");
        exit(1);
    }
    join(args, n, out);
}

/* -- Tests -- */

int check(void) {
    char out[4096];

    /* 1. Basic join */
    const char *a1[] = {"ls", "-l"};
    benchmark_join(a1, 2, out);
    assert(strcmp(out, "ls -l") == 0);

    /* 2. Join with spaces */
    const char *a2[] = {"echo", "hello world"};
    benchmark_join(a2, 2, out);
    assert(strcmp(out, "echo 'hello world'") == 0);

    /* 3. Join with empty string */
    const char *a3[] = {"cp", "", "dest"};
    benchmark_join(a3, 3, out);
    assert(strcmp(out, "cp '' dest") == 0);

    /* 4. Join empty list */
    benchmark_join(NULL, 0, out);
    assert(strcmp(out, "") == 0);

    /* 5. Complex nesting */
    const char *a5[] = {"grep", "foo'bar"};
    benchmark_join(a5, 2, out);
    assert(strcmp(out, "grep 'foo'\"'\"'bar'") == 0);

    return 1;
}

int main(void) {
    assert(check());
    printf("All tests passed.\n");
    return 0;
}
