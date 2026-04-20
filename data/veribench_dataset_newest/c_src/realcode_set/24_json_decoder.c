/* Implementation of a simple JSON decoder.
   Sourced from Python's standard json.decoder library.
   NOTE: simplified from Python version -- supports primitives, numbers,
   strings, empty arrays, and empty objects. */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <assert.h>
#include <stdbool.h>
#include <ctype.h>
#include <math.h>
#include <stdint.h>

/* -- Pre-condition -- */
int pre_decode(const char *s) {
    return s != NULL;
}

/* -- Implementation -- */

typedef enum {
    JSON_NULL, JSON_BOOL, JSON_INT, JSON_FLOAT, JSON_STRING,
    JSON_ARRAY, JSON_OBJECT
} JsonType;

typedef struct {
    JsonType type;
    union {
        bool bool_val;
        int64_t int_val;
        double float_val;
        char str_val[4096];
    };
} JsonValue;

/* Forward declaration */
static int scan_once(const char *s, int idx, JsonValue *out);

/* scanstring: parse a JSON string starting after the opening " */
static int scanstring(const char *s, int end, char *out) {
    int oi = 0;
    while (1) {
        char c = s[end];
        if (c == '\0') {
            fprintf(stderr, "JSONDecodeError: Unterminated string\n");
            exit(1);
        }
        if (c == '"') {
            out[oi] = '\0';
            return end + 1;
        }
        if (c == '\\') {
            end++;
            char esc = s[end];
            switch (esc) {
                case '"':  out[oi++] = '"'; break;
                case '\\': out[oi++] = '\\'; break;
                case '/':  out[oi++] = '/'; break;
                case 'b':  out[oi++] = '\b'; break;
                case 'f':  out[oi++] = '\f'; break;
                case 'n':  out[oi++] = '\n'; break;
                case 'r':  out[oi++] = '\r'; break;
                case 't':  out[oi++] = '\t'; break;
                case 'u':  out[oi++] = '?'; end += 4; break;  /* placeholder */
                default:
                    fprintf(stderr, "JSONDecodeError: Invalid \\escape\n");
                    exit(1);
            }
            end++;
        } else {
            out[oi++] = c;
            end++;
        }
    }
}

static int scan_once(const char *s, int idx, JsonValue *out) {
    char c = s[idx];

    if (c == '"') {
        out->type = JSON_STRING;
        return scanstring(s, idx + 1, out->str_val);
    }
    if (c == '{') {
        /* Only support empty objects */
        if (s[idx + 1] == '}') {
            out->type = JSON_OBJECT;
            return idx + 2;
        }
        fprintf(stderr, "JSONDecodeError: Non-empty objects not supported\n");
        exit(1);
    }
    if (c == '[') {
        /* Only support empty arrays */
        if (s[idx + 1] == ']') {
            out->type = JSON_ARRAY;
            return idx + 2;
        }
        fprintf(stderr, "JSONDecodeError: Non-empty arrays not supported\n");
        exit(1);
    }
    if (c == 'n' && strncmp(s + idx, "null", 4) == 0) {
        out->type = JSON_NULL;
        return idx + 4;
    }
    if (c == 't' && strncmp(s + idx, "true", 4) == 0) {
        out->type = JSON_BOOL;
        out->bool_val = true;
        return idx + 4;
    }
    if (c == 'f' && strncmp(s + idx, "false", 5) == 0) {
        out->type = JSON_BOOL;
        out->bool_val = false;
        return idx + 5;
    }

    /* Number */
    if (c == '-' || isdigit((unsigned char)c)) {
        char numbuf[256];
        int ni = 0;
        bool is_float = false;
        if (s[idx] == '-') numbuf[ni++] = s[idx++];
        while (isdigit((unsigned char)s[idx])) numbuf[ni++] = s[idx++];
        if (s[idx] == '.') {
            is_float = true;
            numbuf[ni++] = s[idx++];
            while (isdigit((unsigned char)s[idx])) numbuf[ni++] = s[idx++];
        }
        if (s[idx] == 'e' || s[idx] == 'E') {
            is_float = true;
            numbuf[ni++] = s[idx++];
            if (s[idx] == '+' || s[idx] == '-') numbuf[ni++] = s[idx++];
            while (isdigit((unsigned char)s[idx])) numbuf[ni++] = s[idx++];
        }
        numbuf[ni] = '\0';

        if (is_float) {
            out->type = JSON_FLOAT;
            out->float_val = strtod(numbuf, NULL);
        } else {
            out->type = JSON_INT;
            out->int_val = strtoll(numbuf, NULL, 10);
        }
        return idx;
    }

    fprintf(stderr, "JSONDecodeError: unexpected character at position %d\n", idx);
    exit(1);
}

JsonValue benchmark_loads(const char *s) {
    if (!pre_decode(s)) {
        fprintf(stderr, "TypeError: expected string\n");
        exit(1);
    }
    JsonValue val;
    scan_once(s, 0, &val);
    return val;
}

/* -- Tests -- */

int check(void) {
    JsonValue v;

    /* 1. Primitives */
    v = benchmark_loads("true");
    assert(v.type == JSON_BOOL && v.bool_val == true);

    v = benchmark_loads("false");
    assert(v.type == JSON_BOOL && v.bool_val == false);

    v = benchmark_loads("null");
    assert(v.type == JSON_NULL);

    /* 2. Integers */
    v = benchmark_loads("123");
    assert(v.type == JSON_INT && v.int_val == 123);

    v = benchmark_loads("-7");
    assert(v.type == JSON_INT && v.int_val == -7);

    /* 3. Empty structures */
    v = benchmark_loads("[]");
    assert(v.type == JSON_ARRAY);

    v = benchmark_loads("{}");
    assert(v.type == JSON_OBJECT);

    /* 4. String */
    v = benchmark_loads("\"hi\"");
    assert(v.type == JSON_STRING && strcmp(v.str_val, "hi") == 0);

    return 1;
}

int main(void) {
    assert(check());
    printf("All tests passed.\n");
    return 0;
}
