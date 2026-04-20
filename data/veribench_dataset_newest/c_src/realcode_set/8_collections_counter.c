/* Provides a simple counter for counting characters in strings.
   Sourced from Python's standard collections library.
   NOTE: simplified from Python version -- only supports counting chars in strings
   and dict-like update/subtract with char keys. */

#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <assert.h>
#include <stdbool.h>

/* -- Implementation -- */

/* Simple counter: 256 slots for each byte value */
typedef struct {
    int64_t counts[256];
} Counter;

void counter_init(Counter *c) {
    memset(c->counts, 0, sizeof(c->counts));
}

void counter_init_from_string(Counter *c, const char *s) {
    counter_init(c);
    if (s == NULL) return;
    for (size_t i = 0; s[i] != '\0'; i++) {
        c->counts[(unsigned char)s[i]]++;
    }
}

int64_t counter_get(Counter *c, char key) {
    return c->counts[(unsigned char)key];
}

/* most_common: fill out array of (char, count) pairs sorted by count desc, then char asc.
   Returns number of entries filled. */
typedef struct { char ch; int64_t count; } CountPair;

static int countpair_cmp(const void *a, const void *b) {
    const CountPair *pa = (const CountPair *)a;
    const CountPair *pb = (const CountPair *)b;
    if (pb->count != pa->count) return (pb->count > pa->count) ? 1 : -1;
    return (pa->ch > pb->ch) ? 1 : (pa->ch < pb->ch) ? -1 : 0;
}

int counter_most_common(Counter *c, CountPair *out, int n) {
    CountPair all[256];
    int total = 0;
    for (int i = 0; i < 256; i++) {
        if (c->counts[i] != 0) {
            all[total].ch = (char)i;
            all[total].count = c->counts[i];
            total++;
        }
    }
    qsort(all, (size_t)total, sizeof(CountPair), countpair_cmp);
    int limit = (n <= 0 || n > total) ? total : n;
    memcpy(out, all, (size_t)limit * sizeof(CountPair));
    return limit;
}

/* elements: fill sorted array of chars, each repeated count times. Returns length. */
int counter_elements(Counter *c, char *out, int capacity) {
    int idx = 0;
    for (int i = 0; i < 256; i++) {
        for (int64_t j = 0; j < c->counts[i] && idx < capacity - 1; j++) {
            out[idx++] = (char)i;
        }
    }
    out[idx] = '\0';
    return idx;
}

void counter_update_string(Counter *c, const char *s) {
    for (size_t i = 0; s[i] != '\0'; i++) {
        c->counts[(unsigned char)s[i]]++;
    }
}

void counter_update_char(Counter *c, char key, int64_t delta) {
    c->counts[(unsigned char)key] += delta;
}

void counter_subtract_string(Counter *c, const char *s) {
    for (size_t i = 0; s[i] != '\0'; i++) {
        c->counts[(unsigned char)s[i]]--;
    }
}

/* -- Tests -- */

int check(void) {
    /* 1. Basic counting (string) */
    Counter c;
    counter_init_from_string(&c, "abracadabra");
    assert(counter_get(&c, 'a') == 5);
    assert(counter_get(&c, 'b') == 2);
    assert(counter_get(&c, 'r') == 2);
    assert(counter_get(&c, 'd') == 1);

    /* 2. most_common */
    CountPair mc[3];
    int nmc = counter_most_common(&c, mc, 3);
    assert(nmc == 3);
    /* Sort by count desc, then key asc for deterministic check */
    assert(mc[0].ch == 'a' && mc[0].count == 5);
    assert(mc[1].ch == 'b' && mc[1].count == 2);
    assert(mc[2].ch == 'r' && mc[2].count == 2);

    /* 3. elements */
    char elems[128];
    int ne = counter_elements(&c, elems, 128);
    assert(ne == 11);
    assert(strcmp(elems, "aaaaabbcdrr") == 0);

    /* 4. Update (string) */
    counter_update_string(&c, "aa");
    assert(counter_get(&c, 'a') == 7);

    /* 5. Update (mapping-like) */
    counter_update_char(&c, 'c', 3);
    counter_update_char(&c, 'd', -1);
    assert(counter_get(&c, 'c') == 4);
    assert(counter_get(&c, 'd') == 0);

    /* 6. Subtract */
    counter_subtract_string(&c, "aab");
    assert(counter_get(&c, 'a') == 5);
    assert(counter_get(&c, 'b') == 1);

    return 1;
}

int main(void) {
    assert(check());
    printf("All tests passed.\n");
    return 0;
}
