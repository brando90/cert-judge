/* Thread-safe counter using a mutex to avoid race conditions.
 * In this C translation, we use pthread_mutex for synchronization.
 */

#include <stdio.h>
#include <stdlib.h>
#include <assert.h>
#include <stdint.h>
#include <pthread.h>

typedef struct SafeCounter {
    int64_t value;
    pthread_mutex_t lock;
} SafeCounter;

SafeCounter *counter_new(int64_t initial_value) {
    SafeCounter *c = (SafeCounter *)malloc(sizeof(SafeCounter));
    if (!c) { perror("malloc"); exit(1); }
    c->value = initial_value;
    pthread_mutex_init(&c->lock, NULL);
    return c;
}

int64_t counter_increment(SafeCounter *c) {
    pthread_mutex_lock(&c->lock);
    c->value += 1;
    int64_t val = c->value;
    pthread_mutex_unlock(&c->lock);
    return val;
}

int64_t counter_decrement(SafeCounter *c) {
    pthread_mutex_lock(&c->lock);
    c->value -= 1;
    int64_t val = c->value;
    pthread_mutex_unlock(&c->lock);
    return val;
}

int64_t counter_get_value(SafeCounter *c) {
    pthread_mutex_lock(&c->lock);
    int64_t val = c->value;
    pthread_mutex_unlock(&c->lock);
    return val;
}

void counter_free(SafeCounter *c) {
    pthread_mutex_destroy(&c->lock);
    free(c);
}

/* Thread worker functions */
typedef struct {
    SafeCounter *counter;
    int iterations;
} WorkerArgs;

void *inc_worker(void *arg) {
    WorkerArgs *wa = (WorkerArgs *)arg;
    for (int i = 0; i < wa->iterations; i++) {
        counter_increment(wa->counter);
    }
    return NULL;
}

void *dec_worker(void *arg) {
    WorkerArgs *wa = (WorkerArgs *)arg;
    for (int i = 0; i < wa->iterations; i++) {
        counter_decrement(wa->counter);
    }
    return NULL;
}

void check(void) {
    /* 1) Single-thread operations */
    SafeCounter *c1 = counter_new(10);
    assert(counter_increment(c1) == 11);
    assert(counter_decrement(c1) == 10);
    assert(counter_get_value(c1) == 10);
    counter_free(c1);

    /* 2) Multiple increments in sequence */
    SafeCounter *c2 = counter_new(0);
    for (int i = 0; i < 5; i++) {
        counter_increment(c2);
    }
    assert(counter_get_value(c2) == 5);
    counter_free(c2);

    /* 3) Concurrent increments: should reach exactly 500 */
    SafeCounter *c3 = counter_new(0);
    pthread_t threads[5];
    WorkerArgs wa3 = {c3, 100};
    for (int i = 0; i < 5; i++) {
        pthread_create(&threads[i], NULL, inc_worker, &wa3);
    }
    for (int i = 0; i < 5; i++) {
        pthread_join(threads[i], NULL);
    }
    assert(counter_get_value(c3) == 500);
    counter_free(c3);

    /* 4) Mixed increment/decrement: should end at 0 */
    SafeCounter *c4 = counter_new(0);
    pthread_t mixed_threads[6];
    WorkerArgs wa4_inc = {c4, 50};
    WorkerArgs wa4_dec = {c4, 50};
    for (int i = 0; i < 3; i++) {
        pthread_create(&mixed_threads[i], NULL, inc_worker, &wa4_inc);
    }
    for (int i = 0; i < 3; i++) {
        pthread_create(&mixed_threads[3 + i], NULL, dec_worker, &wa4_dec);
    }
    for (int i = 0; i < 6; i++) {
        pthread_join(mixed_threads[i], NULL);
    }
    assert(counter_get_value(c4) == 0);
    counter_free(c4);
}

int main(void) {
    check();
    printf("All tests passed.\n");
    return 0;
}
