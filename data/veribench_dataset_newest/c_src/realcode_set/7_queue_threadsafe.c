/* Provides Queue, LifoQueue, and PriorityQueue classes.
   Sourced from Python's standard queue library.
   NOTE: simplified from Python version -- threading omitted, single-threaded only. */

#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <assert.h>
#include <stdbool.h>

/* -- Implementation -- */

#define Q_CAPACITY 256

typedef enum { QUEUE_FIFO, QUEUE_LIFO, QUEUE_PRIORITY } QueueType;

typedef struct {
    int64_t data[Q_CAPACITY];
    int size;
    int maxsize;
    int unfinished_tasks;
    bool is_shutdown;
    QueueType type;
    /* For FIFO: circular buffer */
    int head;
    int tail;
} Queue;

void queue_init(Queue *q, int maxsize, QueueType type) {
    q->size = 0;
    q->maxsize = maxsize;
    q->unfinished_tasks = 0;
    q->is_shutdown = false;
    q->type = type;
    q->head = 0;
    q->tail = 0;
}

bool queue_empty(Queue *q) { return q->size == 0; }
bool queue_full(Queue *q) { return q->maxsize > 0 && q->size >= q->maxsize; }
int queue_qsize(Queue *q) { return q->size; }

/* Heap helpers for PriorityQueue */
static void _heap_siftdown(int64_t *h, int startpos, int pos) {
    int64_t newitem = h[pos];
    while (pos > startpos) {
        int pp = (pos - 1) >> 1;
        if (newitem < h[pp]) { h[pos] = h[pp]; pos = pp; continue; }
        break;
    }
    h[pos] = newitem;
}

static void _heap_siftup(int64_t *h, int n, int pos) {
    int startpos = pos;
    int64_t newitem = h[pos];
    int childpos = 2*pos + 1;
    while (childpos < n) {
        int rightpos = childpos + 1;
        if (rightpos < n && !(h[childpos] < h[rightpos])) childpos = rightpos;
        h[pos] = h[childpos];
        pos = childpos;
        childpos = 2*pos + 1;
    }
    h[pos] = newitem;
    _heap_siftdown(h, startpos, pos);
}

/* Returns: 0=ok, 1=Full, 2=ShutDown */
int queue_put(Queue *q, int64_t item, bool block) {
    (void)block;
    if (q->is_shutdown) return 2;
    if (q->maxsize > 0 && q->size >= q->maxsize) return 1;

    switch (q->type) {
        case QUEUE_FIFO:
            q->data[q->tail] = item;
            q->tail = (q->tail + 1) % Q_CAPACITY;
            break;
        case QUEUE_LIFO:
            q->data[q->size] = item;
            break;
        case QUEUE_PRIORITY:
            q->data[q->size] = item;
            _heap_siftdown(q->data, 0, q->size);
            break;
    }
    q->size++;
    q->unfinished_tasks++;
    return 0;
}

/* Returns: 0=ok, 1=Empty, 2=ShutDown */
int queue_get(Queue *q, int64_t *out, bool block) {
    (void)block;
    if (q->is_shutdown && q->size == 0) return 2;
    if (q->size == 0) return 1;

    switch (q->type) {
        case QUEUE_FIFO:
            *out = q->data[q->head];
            q->head = (q->head + 1) % Q_CAPACITY;
            break;
        case QUEUE_LIFO:
            *out = q->data[q->size - 1];
            break;
        case QUEUE_PRIORITY: {
            *out = q->data[0];
            q->size--;
            if (q->size > 0) {
                q->data[0] = q->data[q->size];
                _heap_siftup(q->data, q->size, 0);
            }
            return 0;  /* already decremented */
        }
    }
    q->size--;
    return 0;
}

int queue_put_nowait(Queue *q, int64_t item) { return queue_put(q, item, false); }
int queue_get_nowait(Queue *q, int64_t *out) { return queue_get(q, out, false); }

int queue_task_done(Queue *q) {
    q->unfinished_tasks--;
    if (q->unfinished_tasks < 0) {
        q->unfinished_tasks = 0;
        return -1;  /* ValueError */
    }
    return 0;
}

void queue_shutdown(Queue *q) {
    q->is_shutdown = true;
}

/* -- Tests -- */

int check(void) {
    int rc;
    int64_t val;

    /* 1) Queue (FIFO) */
    Queue q;
    queue_init(&q, 5, QUEUE_FIFO);
    assert(queue_empty(&q) && !queue_full(&q));
    queue_put(&q, 111, true);
    queue_put(&q, 333, true);
    queue_put(&q, 222, true);
    rc = queue_get(&q, &val, true); assert(rc == 0 && val == 111);
    rc = queue_get(&q, &val, true); assert(rc == 0 && val == 333);
    rc = queue_get(&q, &val, true); assert(rc == 0 && val == 222);
    assert(queue_empty(&q));

    /* 2) LifoQueue (LIFO) */
    Queue lq;
    queue_init(&lq, 5, QUEUE_LIFO);
    queue_put(&lq, 111, true);
    queue_put(&lq, 333, true);
    queue_put(&lq, 222, true);
    rc = queue_get(&lq, &val, true); assert(rc == 0 && val == 222);
    rc = queue_get(&lq, &val, true); assert(rc == 0 && val == 333);
    rc = queue_get(&lq, &val, true); assert(rc == 0 && val == 111);

    /* 3) PriorityQueue */
    Queue pq;
    queue_init(&pq, 5, QUEUE_PRIORITY);
    queue_put(&pq, 2, true);
    queue_put(&pq, 1, true);
    queue_put(&pq, 3, true);
    rc = queue_get(&pq, &val, true); assert(rc == 0 && val == 1);
    rc = queue_get(&pq, &val, true); assert(rc == 0 && val == 2);
    rc = queue_get(&pq, &val, true); assert(rc == 0 && val == 3);

    /* 4) Full / Empty */
    Queue qs;
    queue_init(&qs, 1, QUEUE_FIFO);
    rc = queue_put(&qs, 1, true); assert(rc == 0);
    assert(queue_full(&qs));
    rc = queue_put_nowait(&qs, 2); assert(rc == 1);  /* Full */
    rc = queue_get(&qs, &val, true); assert(rc == 0 && val == 1);
    rc = queue_get_nowait(&qs, &val); assert(rc == 1);  /* Empty */

    /* 5) Task Done */
    Queue qj;
    queue_init(&qj, 3, QUEUE_FIFO);
    queue_put(&qj, 100, true);
    queue_get(&qj, &val, true);
    rc = queue_task_done(&qj); assert(rc == 0);
    rc = queue_task_done(&qj); assert(rc == -1);  /* ValueError */

    /* 6) Shutdown */
    Queue qsd;
    queue_init(&qsd, 2, QUEUE_FIFO);
    queue_shutdown(&qsd);
    rc = queue_put(&qsd, 99, true); assert(rc == 2);  /* ShutDown */

    return 1;
}

int main(void) {
    assert(check());
    printf("All tests passed.\n");
    return 0;
}
