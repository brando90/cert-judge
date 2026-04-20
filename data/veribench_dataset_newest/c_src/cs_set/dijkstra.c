/* Dijkstra's Algorithm for shortest path in a weighted graph.
 *
 * Edge cases:
 * - Negative weights cause pre to fail (exit).
 * - Disconnected target returns NOT_FOUND (INT64_MIN sentinel).
 * - Start equals target returns 0.
 *
 * Graph representation: weighted adjacency list stored as flat arrays.
 *   adj_offsets[i] = start index in adj_dest/adj_weight for node i's edges
 *   adj_offsets[num_nodes] = total number of edges (sentinel)
 *   adj_dest[k], adj_weight[k] = destination and weight of edge k
 */

#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>
#include <assert.h>

#define NOT_FOUND INT64_MIN

int pre_dijkstra(const int *adj_offsets, const int *adj_dest, const int64_t *adj_weight,
                 int num_nodes, int start, int target) {
    if (adj_offsets == NULL || num_nodes <= 0) return 0;
    if (start < 0 || start >= num_nodes) return 0;
    if (target < 0 || target >= num_nodes) return 0;
    int total_edges = adj_offsets[num_nodes];
    if ((adj_dest == NULL || adj_weight == NULL) && total_edges > 0) return 0;
    for (int i = 0; i < total_edges; i++) {
        if (adj_dest[i] < 0 || adj_dest[i] >= num_nodes) return 0;
        if (adj_weight[i] < 0) return 0;
    }
    return 1;
}

/* Simple min-heap for (distance, node) pairs */
typedef struct {
    int64_t dist;
    int node;
} HeapEntry;

typedef struct {
    HeapEntry *data;
    int size;
    int capacity;
} MinHeap;

static void heap_init(MinHeap *h, int cap) {
    h->data = (HeapEntry *)malloc((size_t)cap * sizeof(HeapEntry));
    assert(h->data);
    h->size = 0;
    h->capacity = cap;
}

static void heap_push(MinHeap *h, int64_t dist, int node) {
    if (h->size == h->capacity) {
        h->capacity *= 2;
        h->data = (HeapEntry *)realloc(h->data, (size_t)h->capacity * sizeof(HeapEntry));
        assert(h->data);
    }
    int i = h->size++;
    h->data[i].dist = dist;
    h->data[i].node = node;
    /* Bubble up */
    while (i > 0) {
        int parent = (i - 1) / 2;
        if (h->data[parent].dist > h->data[i].dist) {
            HeapEntry tmp = h->data[parent];
            h->data[parent] = h->data[i];
            h->data[i] = tmp;
            i = parent;
        } else {
            break;
        }
    }
}

static HeapEntry heap_pop(MinHeap *h) {
    assert(h->size > 0);
    HeapEntry top = h->data[0];
    h->size--;
    if (h->size > 0) {
        h->data[0] = h->data[h->size];
        /* Bubble down */
        int i = 0;
        while (1) {
            int left = 2 * i + 1, right = 2 * i + 2, smallest = i;
            if (left < h->size && h->data[left].dist < h->data[smallest].dist)
                smallest = left;
            if (right < h->size && h->data[right].dist < h->data[smallest].dist)
                smallest = right;
            if (smallest != i) {
                HeapEntry tmp = h->data[i];
                h->data[i] = h->data[smallest];
                h->data[smallest] = tmp;
                i = smallest;
            } else {
                break;
            }
        }
    }
    return top;
}

static void heap_free(MinHeap *h) {
    free(h->data);
}

int64_t dijkstra(const int *adj_offsets, const int *adj_dest, const int64_t *adj_weight,
                 int num_nodes, int start, int target) {
    if (!pre_dijkstra(adj_offsets, adj_dest, adj_weight, num_nodes, start, target)) {
        fprintf(stderr, "pre_dijkstra failed\n");
        exit(1);
    }

    if (start == target) return 0;

    int64_t *min_dists = (int64_t *)malloc((size_t)num_nodes * sizeof(int64_t));
    assert(min_dists);
    for (int i = 0; i < num_nodes; i++) min_dists[i] = INT64_MAX;
    min_dists[start] = 0;

    MinHeap pq;
    heap_init(&pq, num_nodes);
    heap_push(&pq, 0, start);

    int64_t result = NOT_FOUND;

    while (pq.size > 0) {
        HeapEntry entry = heap_pop(&pq);
        int64_t d = entry.dist;
        int u = entry.node;

        if (u == target) {
            result = d;
            break;
        }

        if (d > min_dists[u]) continue;

        for (int e = adj_offsets[u]; e < adj_offsets[u + 1]; e++) {
            int v = adj_dest[e];
            int64_t w = adj_weight[e];
            int64_t new_dist = d + w;
            if (new_dist < min_dists[v]) {
                min_dists[v] = new_dist;
                heap_push(&pq, new_dist, v);
            }
        }
    }

    heap_free(&pq);
    free(min_dists);
    return result;
}

int check(void) {
    /* g1: 0->(1,1), 0->(2,4), 1->(2,2) */
    {
        int offsets[] = {0, 2, 3, 3};
        int dest[] = {1, 2, 2};
        int64_t weight[] = {1, 4, 2};
        assert(dijkstra(offsets, dest, weight, 3, 0, 2) == 3);
        assert(dijkstra(offsets, dest, weight, 3, 0, 1) == 1);
    }

    /* g2: 0->(1,5), 2->(3,1); disconnected */
    {
        int offsets[] = {0, 1, 1, 2, 2};
        int dest[] = {1, 3};
        int64_t weight[] = {5, 1};
        assert(dijkstra(offsets, dest, weight, 4, 0, 2) == NOT_FOUND);
        assert(dijkstra(offsets, dest, weight, 4, 0, 0) == 0);
    }

    /* g3: 0->(1,1), 0->(2,5), 1->(3,1), 2->(3,1) => shortest 0->1->3 = 2 */
    {
        int offsets[] = {0, 2, 3, 4, 4};
        int dest[] = {1, 2, 3, 3};
        int64_t weight[] = {1, 5, 1, 1};
        assert(dijkstra(offsets, dest, weight, 4, 0, 3) == 2);
    }

    /* Negative weight test -- pre should return 0 */
    {
        int offsets[] = {0, 1, 1};
        int dest[] = {1};
        int64_t weight[] = {-5};
        assert(pre_dijkstra(offsets, dest, weight, 2, 0, 1) == 0);
    }

    return 1;
}

int main(void) {
    assert(check());
    printf("All tests passed.\n");
    return 0;
}
