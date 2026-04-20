/* Safe linked-list traversal with NULL checks.
 */

#include <stdio.h>
#include <stdlib.h>
#include <assert.h>
#include <stdbool.h>

typedef struct Node {
    int value;
    struct Node *next;
} Node;

Node *node_new(int value, Node *next) {
    Node *n = (Node *)malloc(sizeof(Node));
    if (!n) { perror("malloc"); exit(1); }
    n->value = value;
    n->next = next;
    return n;
}

/* Safe find last: returns 0 on success with result in *out, -1 if empty. */
int safe_find_last(Node *node, int *out) {
    if (node == NULL) {
        return -1; /* empty list */
    }
    Node *current = node;
    while (current->next != NULL) {
        current = current->next;
    }
    *out = current->value;
    return 0;
}

void free_list(Node *head) {
    while (head) {
        Node *tmp = head;
        head = head->next;
        free(tmp);
    }
}

void check(void) {
    int result;

    Node *n3 = node_new(3, NULL);
    Node *n2 = node_new(2, n3);
    Node *n1 = node_new(1, n2);
    assert(safe_find_last(n1, &result) == 0);
    assert(result == 3);
    free_list(n1);

    Node *single = node_new(42, NULL);
    assert(safe_find_last(single, &result) == 0);
    assert(result == 42);
    free_list(single);

    /* Empty list should return error */
    assert(safe_find_last(NULL, &result) == -1);

    /* Long list */
    Node *head = NULL;
    for (int i = 9; i >= 0; i--) {
        head = node_new(i, head);
    }
    assert(safe_find_last(head, &result) == 0);
    assert(result == 9);
    free_list(head);
}

int main(void) {
    check();
    printf("All tests passed.\n");
    return 0;
}
