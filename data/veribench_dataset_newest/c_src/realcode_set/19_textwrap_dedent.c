/* Provides a function for removing leading whitespace from strings.
   Sourced from Python's standard textwrap library. */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <assert.h>
#include <stdbool.h>
#include <ctype.h>

/* -- Pre-condition -- */
int pre_dedent(const char *text) {
    return text != NULL;
}

/* -- Implementation -- */

static bool line_is_blank_or_space(const char *start, const char *end) {
    for (const char *p = start; p < end; p++) {
        if (*p != ' ' && *p != '\t') return false;
    }
    return true;
}

/* dedent: removes common leading whitespace from every line in text.
   Result written to out buffer. */
void dedent(const char *text, char *out) {
    /* Split on '\n' */
    /* Pass 1: Find common margin */
    int margin = -1;  /* -1 means unset */
    const char *p = text;
    while (*p != '\0') {
        const char *line_start = p;
        while (*p != '\0' && *p != '\n') p++;
        const char *line_end = p;
        if (*p == '\n') p++;

        size_t line_len = (size_t)(line_end - line_start);
        /* Skip blank/whitespace-only lines */
        if (line_len == 0 || line_is_blank_or_space(line_start, line_end)) {
            continue;
        }
        /* Count indent */
        int indent = 0;
        for (const char *c = line_start; c < line_end; c++) {
            if (*c == ' ' || *c == '\t') {
                indent++;
            } else {
                break;
            }
        }
        if (margin == -1 || indent < margin) {
            margin = indent;
        }
    }
    if (margin < 0) margin = 0;

    /* Pass 2: Remove margin */
    p = text;
    size_t out_idx = 0;
    bool first_line = true;
    while (*p != '\0') {
        const char *line_start = p;
        while (*p != '\0' && *p != '\n') p++;
        const char *line_end = p;
        bool has_newline = (*p == '\n');
        if (has_newline) p++;

        size_t line_len = (size_t)(line_end - line_start);

        if (!first_line) {
            out[out_idx++] = '\n';
        }
        first_line = false;

        if (line_len == 0 || line_is_blank_or_space(line_start, line_end)) {
            /* Blank lines become empty */
            /* Don't output anything */
        } else {
            /* Remove margin chars */
            const char *src = line_start + margin;
            size_t copy_len = (size_t)(line_end - src);
            memcpy(out + out_idx, src, copy_len);
            out_idx += copy_len;
        }

        /* If original text ends with \n, preserve it */
        if (has_newline && *p == '\0') {
            out[out_idx++] = '\n';
        }
    }
    out[out_idx] = '\0';
}

void benchmark_dedent(const char *text, char *out) {
    if (!pre_dedent(text)) {
        fprintf(stderr, "TypeError: expected str object\n");
        exit(1);
    }
    dedent(text, out);
}

/* -- Tests -- */

int check(void) {
    char out[4096];

    /* 1. Even indentation */
    benchmark_dedent("  Hello.\n  World.", out);
    assert(strcmp(out, "Hello.\nWorld.") == 0);

    /* 2. Uneven indentation */
    benchmark_dedent("    Line 1.\n  Line 2.", out);
    assert(strcmp(out, "  Line 1.\nLine 2.") == 0);

    /* 3. Tabs preserved inside */
    benchmark_dedent("  col1\tcol2\n  val1\tval2", out);
    assert(strcmp(out, "col1\tcol2\nval1\tval2") == 0);

    /* 4. Whitespace normalization (blank lines become empty) */
    benchmark_dedent("  Text.\n   \n  More.", out);
    assert(strcmp(out, "Text.\n\nMore.") == 0);

    return 1;
}

int main(void) {
    assert(check());
    printf("All tests passed.\n");
    return 0;
}
