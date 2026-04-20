/* Provides a simple, unbounded FIFO queue.
   Sourced from Python's standard queue library. */

#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <assert.h>
#include <stdbool.h>

/* -- Implementation -- */

#define QUEUE_CAPACITY 1024

typedef struct {
    int64_t data[QUEUE_CAPACITY];
    int head;
    int tail;
    int count;
} SimpleQueue;

void queue_init(SimpleQueue *q) {
    q->head = 0;
    q->tail = 0;
    q->count = 0;
}

bool queue_empty(SimpleQueue *q) {
    return q->count == 0;
}

int queue_qsize(SimpleQueue *q) {
    return q->count;
}

void queue_put(SimpleQueue *q, int64_t item) {
    if (q->count >= QUEUE_CAPACITY) {
        fprintf(stderr, "Queue overflow\n");
        exit(1);
    }
    q->data[q->tail] = item;
    q->tail = (q->tail + 1) % QUEUE_CAPACITY;
    q->count++;
}

/* Returns 0 on success, -1 on empty (non-blocking) */
int queue_get(SimpleQueue *q, int64_t *out, bool block, double timeout) {
    if (timeout < 0 && timeout != -1.0) {
        fprintf(stderr, "ValueError: 'timeout' must be a non-negative number\n");
        exit(1);
    }
    if (q->count == 0) {
        if (!block) return -1;  /* Empty */
        return -1;  /* In single-threaded C, blocking would deadlock */
    }
    *out = q->data[q->head];
    q->head = (q->head + 1) % QUEUE_CAPACITY;
    q->count--;
    return 0;
}

void queue_put_nowait(SimpleQueue *q, int64_t item) {
    queue_put(q, item);
}

int queue_get_nowait(SimpleQueue *q, int64_t *out) {
    return queue_get(q, out, false, -1.0);
}

/* -- Tests -- */

int check(void) {
    SimpleQueue q;
    int64_t val;
    int rc;

    /* 1. Basics */
    queue_init(&q);
    assert(queue_empty(&q) && queue_qsize(&q) == 0);

    queue_put(&q, 1);
    queue_put_nowait(&q, 2);
    assert(!queue_empty(&q) && queue_qsize(&q) == 2);

    rc = queue_get(&q, &val, true, -1.0);
    assert(rc == 0 && val == 1);
    rc = queue_get_nowait(&q, &val);
    assert(rc == 0 && val == 2);
    assert(queue_empty(&q) && queue_qsize(&q) == 0);

    /* 2. Empty exception equivalent */
    rc = queue_get_nowait(&q, &val);
    assert(rc == -1);

    /* 3. FIFO property */
    SimpleQueue q_fifo;
    queue_init(&q_fifo);
    for (int i = 0; i < 10; i++) {
        queue_put(&q_fifo, (int64_t)i);
    }
    for (int i = 0; i < 10; i++) {
        rc = queue_get(&q_fifo, &val, true, -1.0);
        assert(rc == 0 && val == (int64_t)i);
    }

    return 1;
}

int main(void) {
    assert(check());
    printf("All tests passed.\n");
    return 0;
}
