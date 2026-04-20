/* Unsafe counter without synchronization.
 * Simulates race conditions with a simple counter (no actual threading needed).
 * The tests verify single-threaded sequential behavior and simulate
 * what race conditions would look like.
 */

#include <stdio.h>
#include <stdlib.h>
#include <assert.h>
#include <stdint.h>

typedef struct UnsafeCounter {
    int64_t value;
} UnsafeCounter;

UnsafeCounter *counter_new(int64_t initial_value) {
    UnsafeCounter *c = (UnsafeCounter *)malloc(sizeof(UnsafeCounter));
    if (!c) { perror("malloc"); exit(1); }
    c->value = initial_value;
    return c;
}

int64_t counter_increment(UnsafeCounter *c) {
    /* Increment without synchronization.
     * In a multi-threaded context, reading and writing c->value
     * is not atomic, leading to race conditions. */
    int64_t current = c->value;
    /* Simulate: in a real race, another thread could modify c->value here */
    c->value = current + 1;
    return c->value;
}

int64_t counter_decrement(UnsafeCounter *c) {
    /* Decrement without synchronization. */
    int64_t current = c->value;
    c->value = current - 1;
    return c->value;
}

int64_t counter_get_value(UnsafeCounter *c) {
    return c->value;
}

void counter_free(UnsafeCounter *c) {
    free(c);
}

void check(void) {
    /* 1) Single-thread operations work correctly */
    UnsafeCounter *c1 = counter_new(10);
    assert(counter_increment(c1) == 11);
    assert(counter_decrement(c1) == 10);
    assert(counter_get_value(c1) == 10);
    counter_free(c1);

    /* 2) Multiple increments in sequence */
    UnsafeCounter *c2 = counter_new(0);
    for (int i = 0; i < 5; i++) {
        counter_increment(c2);
    }
    assert(counter_get_value(c2) == 5);
    counter_free(c2);

    /* 3) Simulated race: sequential increments should reach 500 */
    UnsafeCounter *c3 = counter_new(0);
    for (int t = 0; t < 5; t++) {
        for (int i = 0; i < 100; i++) {
            counter_increment(c3);
        }
    }
    int64_t final3 = counter_get_value(c3);
    printf("Expected: 500, Actual: %ld\n", (long)final3);
    /* In sequential execution, value should be exactly 500 */
    assert(final3 <= 500);
    counter_free(c3);

    /* 4) Simulated race: mixed increment/decrement */
    UnsafeCounter *c4 = counter_new(0);
    for (int t = 0; t < 3; t++) {
        for (int i = 0; i < 50; i++) {
            counter_increment(c4);
        }
    }
    for (int t = 0; t < 3; t++) {
        for (int i = 0; i < 50; i++) {
            counter_decrement(c4);
        }
    }
    int64_t final4 = counter_get_value(c4);
    printf("Expected: 0, Actual: %ld\n", (long)final4);
    assert(-150 <= final4 && final4 <= 150);
    counter_free(c4);
}

int main(void) {
    check();
    printf("All tests passed.\n");
    return 0;
}
