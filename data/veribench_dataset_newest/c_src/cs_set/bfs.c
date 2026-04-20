/* Breadth-First Search (BFS) to find shortest path distance in an unweighted graph.
 *
 * Edge cases:
 * - Disconnected target returns NOT_FOUND (INT64_MIN sentinel for None).
 * - Start equals target returns 0.
 *
 * Graph representation: adjacency list stored as flat arrays.
 *   adj_offsets[i] = start index in adj_list for node i's neighbors
 *   adj_offsets[num_nodes] = total number of edges (sentinel)
 *   adj_list[adj_offsets[i]..adj_offsets[i+1]) = neighbors of node i
 */

#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>
#include <assert.h>

#define NOT_FOUND INT64_MIN

int pre_bfs(const int *adj_offsets, const int *adj_list, int num_nodes, int start, int target) {
    if (adj_offsets == NULL || num_nodes <= 0) return 0;
    if (start < 0 || start >= num_nodes) return 0;
    if (target < 0 || target >= num_nodes) return 0;
    /* Validate all neighbors are in range */
    int total_edges = adj_offsets[num_nodes];
    if (adj_list == NULL && total_edges > 0) return 0;
    for (int i = 0; i < total_edges; i++) {
        if (adj_list[i] < 0 || adj_list[i] >= num_nodes) return 0;
    }
    return 1;
}

int64_t bfs(const int *adj_offsets, const int *adj_list, int num_nodes, int start, int target) {
    if (!pre_bfs(adj_offsets, adj_list, num_nodes, start, target)) {
        fprintf(stderr, "pre_bfs failed\n");
        exit(1);
    }

    if (start == target) return 0;

    /* BFS queue: stores (node, distance) pairs */
    int *q_node = (int *)malloc((size_t)num_nodes * sizeof(int));
    int64_t *q_dist = (int64_t *)malloc((size_t)num_nodes * sizeof(int64_t));
    bool *visited = (bool *)calloc((size_t)num_nodes, sizeof(bool));
    assert(q_node && q_dist && visited);

    int q_front = 0, q_back = 0;
    q_node[q_back] = start;
    q_dist[q_back] = 0;
    q_back++;
    visited[start] = true;

    int64_t result = NOT_FOUND;

    while (q_front < q_back) {
        int curr = q_node[q_front];
        int64_t dist = q_dist[q_front];
        q_front++;

        if (curr == target) {
            result = dist;
            break;
        }

        for (int e = adj_offsets[curr]; e < adj_offsets[curr + 1]; e++) {
            int neighbor = adj_list[e];
            if (!visited[neighbor]) {
                visited[neighbor] = true;
                q_node[q_back] = neighbor;
                q_dist[q_back] = dist + 1;
                q_back++;
            }
        }
    }

    free(q_node);
    free(q_dist);
    free(visited);
    return result;
}

int check(void) {
    /* g1: 0->1->2 */
    {
        int offsets[] = {0, 1, 2, 2};  /* node 0: [1], node 1: [2], node 2: [] */
        int adj[] = {1, 2};
        assert(bfs(offsets, adj, 3, 0, 2) == 2);
        assert(bfs(offsets, adj, 3, 0, 1) == 1);
        assert(bfs(offsets, adj, 3, 0, 0) == 0);
        assert(bfs(offsets, adj, 3, 2, 0) == NOT_FOUND);  /* Not reachable */
    }

    /* g2: Disconnected: 0->1, 2->3 */
    {
        int offsets[] = {0, 1, 1, 2, 2};  /* node 0: [1], node 1: [], node 2: [3], node 3: [] */
        int adj[] = {1, 3};
        assert(bfs(offsets, adj, 4, 0, 1) == 1);
        assert(bfs(offsets, adj, 4, 2, 3) == 1);
        assert(bfs(offsets, adj, 4, 0, 2) == NOT_FOUND);
        assert(bfs(offsets, adj, 4, 0, 3) == NOT_FOUND);
    }

    /* g3: Cycle 0 <-> 1 */
    {
        int offsets[] = {0, 1, 2};
        int adj[] = {1, 0};
        assert(bfs(offsets, adj, 2, 0, 1) == 1);
        assert(bfs(offsets, adj, 2, 1, 0) == 1);
    }

    /* g4: Fork 0->{1,2} */
    {
        int offsets[] = {0, 2, 2, 2};
        int adj[] = {1, 2};
        assert(bfs(offsets, adj, 3, 0, 1) == 1);
        assert(bfs(offsets, adj, 3, 0, 2) == 1);
    }

    /* g5: Diamond with direct edge 0->{1,2,3}, 1->3, 2->3 */
    {
        int offsets[] = {0, 3, 4, 5, 5};
        int adj[] = {1, 2, 3, 3, 3};
        assert(bfs(offsets, adj, 4, 0, 3) == 1);  /* 0->3 directly */
    }

    /* g6: Diamond forcing 2 steps: 0->{1,2}, 1->3, 2->3 */
    {
        int offsets[] = {0, 2, 3, 4, 4};
        int adj[] = {1, 2, 3, 3};
        assert(bfs(offsets, adj, 4, 0, 3) == 2);
    }

    return 1;
}

int main(void) {
    assert(check());
    printf("All tests passed.\n");
    return 0;
}
