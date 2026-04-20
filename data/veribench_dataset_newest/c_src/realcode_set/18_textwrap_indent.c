/* Provides a function for indenting lines in a string.
   Sourced from Python's standard textwrap library. */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <assert.h>
#include <stdbool.h>
#include <ctype.h>

/* -- Pre-condition -- */
int pre_indent(const char *text, const char *prefix) {
    return text != NULL && prefix != NULL;
}

/* -- Implementation -- */

/* Predicate type: returns true if line should be indented */
typedef bool (*Predicate)(const char *line);

static bool default_predicate(const char *line) {
    /* Return true if line has any non-whitespace */
    for (size_t i = 0; line[i] != '\0' && line[i] != '\n'; i++) {
        if (!isspace((unsigned char)line[i])) return true;
    }
    return false;
}

static bool pred_all(const char *line) { (void)line; return true; }
static bool pred_none(const char *line) { (void)line; return false; }

/* indent: Adds prefix to beginning of selected lines in text.
   Result written to out (must be large enough). */
void indent(const char *text, const char *prefix, Predicate pred, char *out) {
    if (pred == NULL) pred = default_predicate;

    size_t prefix_len = strlen(prefix);
    size_t out_idx = 0;
    const char *p = text;

    while (*p != '\0') {
        /* Find end of line (including the newline char if present) */
        const char *eol = p;
        while (*eol != '\0' && *eol != '\n') eol++;
        bool has_newline = (*eol == '\n');
        size_t line_len = (size_t)(eol - p) + (has_newline ? 1 : 0);

        /* Copy line to temp buffer for predicate */
        char line_buf[4096];
        memcpy(line_buf, p, line_len);
        line_buf[line_len] = '\0';

        if (pred(line_buf)) {
            memcpy(out + out_idx, prefix, prefix_len);
            out_idx += prefix_len;
        }
        memcpy(out + out_idx, p, line_len);
        out_idx += line_len;

        p += line_len;
    }
    out[out_idx] = '\0';
}

void benchmark_indent(const char *text, const char *prefix, Predicate pred, char *out) {
    if (!pre_indent(text, prefix)) {
        fprintf(stderr, "TypeError: text and prefix must be strings\n");
        exit(1);
    }
    indent(text, prefix, pred, out);
}

/* -- Tests -- */

int check(void) {
    const char *cases[] = {
        "Hi.\nThis is a test.\nTesting.",
        "Hi.\nThis is a test.\n\nTesting.",
        "\nHi.\nThis is a test.\nTesting.\n",
    };
    const char *prefix = "  ";
    char out[4096];

    /* 1. Default predicate */
    const char *expected_default[] = {
        "  Hi.\n  This is a test.\n  Testing.",
        "  Hi.\n  This is a test.\n\n  Testing.",
        "\n  Hi.\n  This is a test.\n  Testing.\n",
    };
    for (int i = 0; i < 3; i++) {
        benchmark_indent(cases[i], prefix, NULL, out);
        assert(strcmp(out, expected_default[i]) == 0);
    }

    /* 2. Predicate=True (indent all lines) */
    const char *expected_all[] = {
        "  Hi.\n  This is a test.\n  Testing.",
        "  Hi.\n  This is a test.\n  \n  Testing.",
        "  \n  Hi.\n  This is a test.\n  Testing.\n",
    };
    for (int i = 0; i < 3; i++) {
        benchmark_indent(cases[i], prefix, pred_all, out);
        assert(strcmp(out, expected_all[i]) == 0);
    }

    /* 3. Predicate=False (no indentation) */
    for (int i = 0; i < 3; i++) {
        benchmark_indent(cases[i], prefix, pred_none, out);
        assert(strcmp(out, cases[i]) == 0);
    }

    return 1;
}

int main(void) {
    assert(check());
    printf("All tests passed.\n");
    return 0;
}
