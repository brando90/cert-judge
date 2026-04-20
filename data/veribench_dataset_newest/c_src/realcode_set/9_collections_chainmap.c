/* Provides a dict-like structure for creating a single view of multiple mappings.
   Sourced from Python's standard collections library.
   NOTE: simplified from Python version -- uses string keys and int64_t values. */

#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <assert.h>
#include <stdbool.h>

/* -- Implementation -- */

#define MAP_CAPACITY 64
#define MAX_MAPS 8

typedef struct {
    char keys[MAP_CAPACITY][64];
    int64_t values[MAP_CAPACITY];
    int size;
} SimpleMap;

void map_init(SimpleMap *m) { m->size = 0; }

void map_set(SimpleMap *m, const char *key, int64_t val) {
    for (int i = 0; i < m->size; i++) {
        if (strcmp(m->keys[i], key) == 0) {
            m->values[i] = val;
            return;
        }
    }
    strncpy(m->keys[m->size], key, 63);
    m->keys[m->size][63] = '\0';
    m->values[m->size] = val;
    m->size++;
}

bool map_get(SimpleMap *m, const char *key, int64_t *out) {
    for (int i = 0; i < m->size; i++) {
        if (strcmp(m->keys[i], key) == 0) {
            *out = m->values[i];
            return true;
        }
    }
    return false;
}

bool map_contains(SimpleMap *m, const char *key) {
    for (int i = 0; i < m->size; i++) {
        if (strcmp(m->keys[i], key) == 0) return true;
    }
    return false;
}

bool map_del(SimpleMap *m, const char *key) {
    for (int i = 0; i < m->size; i++) {
        if (strcmp(m->keys[i], key) == 0) {
            /* Shift last element into gap */
            m->size--;
            if (i < m->size) {
                strcpy(m->keys[i], m->keys[m->size]);
                m->values[i] = m->values[m->size];
            }
            return true;
        }
    }
    return false;
}

typedef struct {
    SimpleMap *maps[MAX_MAPS];
    int nmaps;
} ChainMap;

void chainmap_init(ChainMap *cm, SimpleMap **maps, int nmaps) {
    cm->nmaps = nmaps;
    for (int i = 0; i < nmaps; i++) cm->maps[i] = maps[i];
}

bool chainmap_get(ChainMap *cm, const char *key, int64_t *out) {
    for (int i = 0; i < cm->nmaps; i++) {
        if (map_get(cm->maps[i], key, out)) return true;
    }
    return false;
}

bool chainmap_contains(ChainMap *cm, const char *key) {
    for (int i = 0; i < cm->nmaps; i++) {
        if (map_contains(cm->maps[i], key)) return true;
    }
    return false;
}

void chainmap_set(ChainMap *cm, const char *key, int64_t val) {
    map_set(cm->maps[0], key, val);
}

bool chainmap_del(ChainMap *cm, const char *key) {
    return map_del(cm->maps[0], key);
}

/* new_child: creates a new ChainMap with m prepended */
void chainmap_new_child(ChainMap *cm, SimpleMap *m, ChainMap *out) {
    out->maps[0] = m;
    for (int i = 0; i < cm->nmaps && i + 1 < MAX_MAPS; i++) {
        out->maps[i + 1] = cm->maps[i];
    }
    out->nmaps = (cm->nmaps + 1 < MAX_MAPS) ? cm->nmaps + 1 : MAX_MAPS;
}

/* parents: creates a new ChainMap from maps[1:] */
void chainmap_parents(ChainMap *cm, ChainMap *out) {
    out->nmaps = cm->nmaps - 1;
    for (int i = 0; i < out->nmaps; i++) {
        out->maps[i] = cm->maps[i + 1];
    }
}

/* -- Tests -- */

int check(void) {
    SimpleMap d1, d2;
    int64_t val;
    map_init(&d1);
    map_init(&d2);
    map_set(&d1, "a", 1);
    map_set(&d1, "b", 2);
    map_set(&d2, "b", 3);
    map_set(&d2, "c", 4);

    SimpleMap *maps[] = {&d1, &d2};
    ChainMap cm;
    chainmap_init(&cm, maps, 2);

    /* 1. Basic lookup */
    assert(chainmap_get(&cm, "a", &val) && val == 1);
    assert(chainmap_get(&cm, "c", &val) && val == 4);

    /* 2. Shadowing (first map wins) */
    assert(chainmap_get(&cm, "b", &val) && val == 2);

    /* 3. Writes affect first map only */
    chainmap_set(&cm, "c", 5);
    assert(map_get(&d1, "c", &val) && val == 5);
    assert(map_get(&d2, "c", &val) && val == 4);  /* d2 unchanged */

    /* 4. new_child */
    SimpleMap d3;
    map_init(&d3);
    map_set(&d3, "d", 6);
    ChainMap cm2;
    chainmap_new_child(&cm, &d3, &cm2);
    assert(chainmap_get(&cm2, "a", &val) && val == 1);
    assert(chainmap_get(&cm2, "d", &val) && val == 6);
    assert(cm2.maps[0] == &d3);
    assert(cm2.maps[1] == &d1);

    /* 5. parents */
    ChainMap p;
    chainmap_parents(&cm, &p);
    assert(chainmap_get(&p, "b", &val) && val == 3);
    assert(!chainmap_contains(&p, "a"));

    return 1;
}

int main(void) {
    assert(check());
    printf("All tests passed.\n");
    return 0;
}
