/* Provides topological sorting of a graph.
   Sourced from Python's standard graphlib library. */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <assert.h>
#include <stdbool.h>
#include <stdint.h>

/* -- Implementation -- */

#define MAX_NODES 64
#define MAX_EDGES 256

typedef struct {
    int node;
    int npredecessors;
    int successors[MAX_NODES];
    int nsuccs;
} NodeInfo;

typedef struct {
    NodeInfo nodes[MAX_NODES];
    int nnodes;
    int ready[MAX_NODES];
    int nready;
    int npassedout;
    int nfinished;
    bool prepared;
} TopologicalSorter;

void ts_init(TopologicalSorter *ts) {
    ts->nnodes = 0;
    ts->nready = 0;
    ts->npassedout = 0;
    ts->nfinished = 0;
    ts->prepared = false;
}

static int ts_get_node_idx(TopologicalSorter *ts, int node) {
    for (int i = 0; i < ts->nnodes; i++) {
        if (ts->nodes[i].node == node) return i;
    }
    /* Create new */
    int idx = ts->nnodes++;
    ts->nodes[idx].node = node;
    ts->nodes[idx].npredecessors = 0;
    ts->nodes[idx].nsuccs = 0;
    return idx;
}

void ts_add(TopologicalSorter *ts, int node, int *predecessors, int npred) {
    if (ts->prepared) {
        fprintf(stderr, "ValueError: Nodes cannot be added after prepare()\n");
        exit(1);
    }
    int ni = ts_get_node_idx(ts, node);
    ts->nodes[ni].npredecessors += npred;

    for (int i = 0; i < npred; i++) {
        int pi = ts_get_node_idx(ts, predecessors[i]);
        ts->nodes[pi].successors[ts->nodes[pi].nsuccs++] = node;
    }
}

void ts_prepare(TopologicalSorter *ts) {
    ts->prepared = true;
    ts->nready = 0;
    for (int i = 0; i < ts->nnodes; i++) {
        if (ts->nodes[i].npredecessors == 0) {
            ts->ready[ts->nready++] = ts->nodes[i].node;
        }
    }
}

int ts_get_ready(TopologicalSorter *ts, int *out) {
    if (!ts->prepared) {
        fprintf(stderr, "ValueError: prepare() must be called first\n");
        exit(1);
    }
    int n = ts->nready;
    memcpy(out, ts->ready, (size_t)n * sizeof(int));
    ts->npassedout += n;
    ts->nready = 0;
    return n;
}

bool ts_is_active(TopologicalSorter *ts) {
    return ts->nfinished < ts->npassedout || ts->nready > 0;
}

void ts_done(TopologicalSorter *ts, int *nodes, int count) {
    for (int i = 0; i < count; i++) {
        int ni = ts_get_node_idx(ts, nodes[i]);
        for (int j = 0; j < ts->nodes[ni].nsuccs; j++) {
            int succ = ts->nodes[ni].successors[j];
            int si = ts_get_node_idx(ts, succ);
            ts->nodes[si].npredecessors--;
            if (ts->nodes[si].npredecessors == 0) {
                ts->ready[ts->nready++] = succ;
            }
        }
        ts->nfinished++;
    }
}

/* static_order: returns all nodes in topological order. Returns count, -1 on cycle. */
int ts_static_order(TopologicalSorter *ts, int *out) {
    ts_prepare(ts);
    int total = 0;
    while (ts_is_active(ts)) {
        int group[MAX_NODES];
        int gn = ts_get_ready(ts, group);
        if (gn == 0) break;  /* stuck = cycle */
        memcpy(out + total, group, (size_t)gn * sizeof(int));
        total += gn;
        ts_done(ts, group, gn);
    }
    if (ts->nfinished < ts->nnodes) {
        return -1;  /* CycleError */
    }
    return total;
}

/* -- Tests -- */

static bool set_contains(int *arr, int n, int val) {
    for (int i = 0; i < n; i++) {
        if (arr[i] == val) return true;
    }
    return false;
}

int check(void) {
    /* 1. Basic sorting */
    /* graph: {2: {11}, 9: {11, 8}, 10: {11, 3}, 11: {7, 5}, 8: {7, 3}} */
    TopologicalSorter ts;
    ts_init(&ts);
    int p1[] = {11};       ts_add(&ts, 2, p1, 1);
    int p2[] = {11, 8};    ts_add(&ts, 9, p2, 2);
    int p3[] = {11, 3};    ts_add(&ts, 10, p3, 2);
    int p4[] = {7, 5};     ts_add(&ts, 11, p4, 2);
    int p5[] = {7, 3};     ts_add(&ts, 8, p5, 2);

    int result[MAX_NODES];
    int total = ts_static_order(&ts, result);
    assert(total > 0);

    /* Expected groups: {3, 5, 7}, {8, 11}, {2, 9, 10} */
    /* First 3 should be from {3, 5, 7} */
    assert(total == 8);
    int idx = 0;
    int g1[] = {3, 5, 7};
    for (int i = 0; i < 3; i++) {
        assert(set_contains(g1, 3, result[idx + i]));
    }
    idx += 3;
    int g2[] = {8, 11};
    for (int i = 0; i < 2; i++) {
        assert(set_contains(g2, 2, result[idx + i]));
    }
    idx += 2;
    int g3[] = {2, 9, 10};
    for (int i = 0; i < 3; i++) {
        assert(set_contains(g3, 3, result[idx + i]));
    }

    /* 2. Cycle detection */
    TopologicalSorter ts2;
    ts_init(&ts2);
    int pc1[] = {2}; ts_add(&ts2, 1, pc1, 1);
    int pc2[] = {1}; ts_add(&ts2, 2, pc2, 1);
    total = ts_static_order(&ts2, result);
    assert(total == -1);  /* CycleError */

    return 1;
}

int main(void) {
    assert(check());
    printf("All tests passed.\n");
    return 0;
}
