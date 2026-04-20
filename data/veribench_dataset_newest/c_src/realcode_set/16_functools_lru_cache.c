/* Provides a Least-Recently-Used (LRU) cache.
   Sourced from Python's standard functools library.
   NOTE: simplified from Python version -- implements a simple hash-table cache
   for single int64_t -> int64_t function calls instead of a decorator. */

#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <assert.h>
#include <stdbool.h>
#include <string.h>

/* -- Implementation -- */

#define CACHE_SLOTS 256

typedef int64_t (*CachedFunc)(int64_t);

typedef struct CacheEntry {
    bool occupied;
    int64_t key;
    int64_t result;
    int64_t access_time;  /* for LRU eviction */
} CacheEntry;

typedef struct {
    CacheEntry entries[CACHE_SLOTS];
    int maxsize;      /* 0 = no caching, <0 = unbounded */
    int currsize;
    int64_t hits;
    int64_t misses;
    int64_t time_counter;
    CachedFunc func;
} LRUCache;

void lru_cache_init(LRUCache *c, CachedFunc func, int maxsize) {
    memset(c->entries, 0, sizeof(c->entries));
    c->maxsize = maxsize;
    c->currsize = 0;
    c->hits = 0;
    c->misses = 0;
    c->time_counter = 0;
    c->func = func;
}

void lru_cache_clear(LRUCache *c) {
    CachedFunc f = c->func;
    int ms = c->maxsize;
    memset(c->entries, 0, sizeof(c->entries));
    c->currsize = 0;
    c->hits = 0;
    c->misses = 0;
    c->time_counter = 0;
    c->func = f;
    c->maxsize = ms;
}

static int _hash_key(int64_t key) {
    uint64_t k = (uint64_t)key;
    k = (k ^ (k >> 16)) * 0x45d9f3b;
    k = (k ^ (k >> 16)) * 0x45d9f3b;
    k = k ^ (k >> 16);
    return (int)(k % CACHE_SLOTS);
}

int64_t lru_cache_call(LRUCache *c, int64_t key) {
    /* maxsize == 0: no caching */
    if (c->maxsize == 0) {
        c->misses++;
        return c->func(key);
    }

    /* Look up in cache (linear probing) */
    int h = _hash_key(key);
    for (int i = 0; i < CACHE_SLOTS; i++) {
        int idx = (h + i) % CACHE_SLOTS;
        if (!c->entries[idx].occupied) break;
        if (c->entries[idx].key == key) {
            c->hits++;
            c->entries[idx].access_time = c->time_counter++;
            return c->entries[idx].result;
        }
    }

    /* Cache miss */
    c->misses++;
    int64_t result = c->func(key);

    /* Evict LRU if needed (bounded cache) */
    if (c->maxsize > 0 && c->currsize >= c->maxsize) {
        /* Find LRU entry */
        int lru_idx = -1;
        int64_t min_time = INT64_MAX;
        for (int i = 0; i < CACHE_SLOTS; i++) {
            if (c->entries[i].occupied && c->entries[i].access_time < min_time) {
                min_time = c->entries[i].access_time;
                lru_idx = i;
            }
        }
        if (lru_idx >= 0) {
            c->entries[lru_idx].occupied = false;
            c->currsize--;
        }
    }

    /* Insert */
    h = _hash_key(key);
    for (int i = 0; i < CACHE_SLOTS; i++) {
        int idx = (h + i) % CACHE_SLOTS;
        if (!c->entries[idx].occupied) {
            c->entries[idx].occupied = true;
            c->entries[idx].key = key;
            c->entries[idx].result = result;
            c->entries[idx].access_time = c->time_counter++;
            c->currsize++;
            break;
        }
    }

    return result;
}

/* -- Tests -- */

static int call_count_f = 0;
static int64_t test_f(int64_t x) {
    call_count_f++;
    return x * 10;
}

static int call_count_mul = 0;
static int64_t test_mul(int64_t x) {
    call_count_mul++;
    return x * x;
}

int check(void) {
    /* 1. Test basic caching with maxsize=2 */
    call_count_f = 0;
    LRUCache cache;
    lru_cache_init(&cache, test_f, 2);

    int64_t inputs[] = {7, 9, 7, 9, 7, 9, 8, 8, 8, 9, 9, 9, 8, 8, 8, 7};
    int n = 16;
    for (int i = 0; i < n; i++) {
        assert(lru_cache_call(&cache, inputs[i]) == inputs[i] * 10);
    }
    /* Expected: 4 misses (7, 9, 8, 7) */
    assert(call_count_f == 4);
    assert(cache.hits == 12);
    assert(cache.misses == 4);
    assert(cache.currsize == 2);

    /* 2. Test cache_clear */
    lru_cache_clear(&cache);
    assert(cache.hits == 0 && cache.misses == 0 && cache.currsize == 0);

    /* 3. Test maxsize=0 (no caching) */
    call_count_mul = 0;
    LRUCache cache0;
    lru_cache_init(&cache0, test_mul, 0);
    lru_cache_call(&cache0, 3);
    lru_cache_call(&cache0, 3);
    lru_cache_call(&cache0, 4);
    assert(call_count_mul == 3);
    assert(cache0.hits == 0 && cache0.misses == 3 && cache0.currsize == 0);

    /* 4. Test unbounded (maxsize=-1) */
    call_count_f = 0;
    LRUCache cacheu;
    lru_cache_init(&cacheu, test_f, -1);
    lru_cache_call(&cacheu, 1);
    lru_cache_call(&cacheu, 1);
    lru_cache_call(&cacheu, 2);
    lru_cache_call(&cacheu, 2);
    assert(cacheu.hits == 2 && cacheu.misses == 2 && cacheu.currsize == 2);
    assert(call_count_f == 2);

    return 1;
}

int main(void) {
    assert(check());
    printf("All tests passed.\n");
    return 0;
}
