/* Depth-First Search (DFS) for reachability in a directed graph.
 *
 * Edge cases:
 * - Start equals target returns true.
 * - Cycles handled without infinite loops (visited set).
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

int pre_dfs(const int *adj_offsets, const int *adj_list, int num_nodes, int start, int target) {
    if (adj_offsets == NULL || num_nodes <= 0) return 0;
    if (start < 0 || start >= num_nodes) return 0;
    if (target < 0 || target >= num_nodes) return 0;
    int total_edges = adj_offsets[num_nodes];
    if (adj_list == NULL && total_edges > 0) return 0;
    for (int i = 0; i < total_edges; i++) {
        if (adj_list[i] < 0 || adj_list[i] >= num_nodes) return 0;
    }
    return 1;
}

bool dfs(const int *adj_offsets, const int *adj_list, int num_nodes, int start, int target) {
    if (!pre_dfs(adj_offsets, adj_list, num_nodes, start, target)) {
        fprintf(stderr, "pre_dfs failed\n");
        exit(1);
    }

    /* Iterative DFS using a stack */
    int *stack = (int *)malloc((size_t)num_nodes * sizeof(int));
    bool *visited = (bool *)calloc((size_t)num_nodes, sizeof(bool));
    assert(stack && visited);

    int top = 0;
    stack[top++] = start;
    visited[start] = true;

    bool result = false;

    while (top > 0) {
        int curr = stack[--top];

        if (curr == target) {
            result = true;
            break;
        }

        for (int e = adj_offsets[curr]; e < adj_offsets[curr + 1]; e++) {
            int neighbor = adj_list[e];
            if (!visited[neighbor]) {
                visited[neighbor] = true;
                stack[top++] = neighbor;
            }
        }
    }

    free(stack);
    free(visited);
    return result;
}

int check(void) {
    /* g1: 0->1->2 */
    {
        int offsets[] = {0, 1, 2, 2};
        int adj[] = {1, 2};
        assert(dfs(offsets, adj, 3, 0, 2) == true);
        assert(dfs(offsets, adj, 3, 0, 1) == true);
        assert(dfs(offsets, adj, 3, 0, 0) == true);
        assert(dfs(offsets, adj, 3, 2, 0) == false);
    }

    /* g2: Disconnected: 0->1, 2->3 */
    {
        int offsets[] = {0, 1, 1, 2, 2};
        int adj[] = {1, 3};
        assert(dfs(offsets, adj, 4, 0, 1) == true);
        assert(dfs(offsets, adj, 4, 2, 3) == true);
        assert(dfs(offsets, adj, 4, 0, 2) == false);
    }

    /* g3: Cycle 0 <-> 1 */
    {
        int offsets[] = {0, 1, 2};
        int adj[] = {1, 0};
        assert(dfs(offsets, adj, 2, 0, 1) == true);
        assert(dfs(offsets, adj, 2, 1, 0) == true);
    }

    /* g4: 0->1, 1->{2,3}, 2->0 */
    {
        int offsets[] = {0, 1, 3, 4, 4};
        int adj[] = {1, 2, 3, 0};
        assert(dfs(offsets, adj, 4, 0, 3) == true);   /* 0->1->3 */
        assert(dfs(offsets, adj, 4, 2, 3) == true);   /* 2->0->1->3 */
        assert(dfs(offsets, adj, 4, 3, 0) == false);
    }

    /* g5: chain 0->1->2->...->9 */
    {
        int offsets[11];
        int adj[10];
        for (int i = 0; i < 10; i++) {
            offsets[i] = i;
            adj[i] = i + 1;
        }
        offsets[10] = 10; /* node 9 has 0 neighbors but we set sentinel */
        /* Actually node 9 has no neighbors. adj[0..8] = {1,2,...,9} */
        /* offsets: 0:0, 1:1, 2:2, ..., 9:9, sentinel:10 but we only have 9 edges for nodes 0..8 */
        /* Let me redo: node i (0..8) has 1 neighbor (i+1), node 9 has 0 neighbors */
        for (int i = 0; i <= 9; i++) offsets[i] = i;
        offsets[10] = 9;  /* 9 edges total */
        for (int i = 0; i < 9; i++) adj[i] = i + 1;

        assert(dfs(offsets, adj, 10, 0, 9) == true);
        assert(dfs(offsets, adj, 10, 5, 4) == false);
    }

    return 1;
}

int main(void) {
    assert(check());
    printf("All tests passed.\n");
    return 0;
}
