/* Unsafe linked list traversal without null pointer checks.
 * If the list is empty (node is NULL), this dereferences a null pointer.
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <assert.h>
#include <stdbool.h>
#include <sys/wait.h>
#include <unistd.h>

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

/* Find the last value in a linked list without checking for null pointers.
 * If node is NULL, this will segfault (null pointer dereference). */
int unsafe_find_last(Node *node) {
    Node *current = node;
    while (current->next != NULL) {
        current = current->next;
    }
    return current->value;
}

void free_list(Node *head) {
    while (head) {
        Node *tmp = head;
        head = head->next;
        free(tmp);
    }
}

/* Try calling unsafe_find_last in a child process.
 * Returns -1 if the child crashed (e.g., segfault), otherwise the result. */
int try_unsafe_find_last(Node *node, bool *crashed) {
    *crashed = false;
    if (node == NULL) {
        /* We know this will crash. Use fork to detect it. */
        pid_t pid = fork();
        if (pid == 0) {
            unsafe_find_last(node);
            _exit(0);
        }
        int status;
        waitpid(pid, &status, 0);
        if (WIFEXITED(status) && WEXITSTATUS(status) == 0) {
            *crashed = false;
            return 0;
        }
        *crashed = true;
        return -1;
    }
    return unsafe_find_last(node);
}

void check(void) {
    /* 1) Normal case: list with multiple nodes */
    Node *n3 = node_new(3, NULL);
    Node *n2 = node_new(2, n3);
    Node *n1 = node_new(1, n2);
    assert(unsafe_find_last(n1) == 3);
    free_list(n1);

    /* 2) Single node list */
    Node *single = node_new(42, NULL);
    assert(unsafe_find_last(single) == 42);
    free_list(single);

    /* 3) Empty list (NULL) -> should crash (null pointer dereference) */
    bool crashed;
    try_unsafe_find_last(NULL, &crashed);
    assert(crashed);

    /* 4) List with one node that has next=NULL */
    Node *lonely = node_new(99, NULL);
    assert(unsafe_find_last(lonely) == 99);
    free_list(lonely);

    /* 5) Long list */
    Node *head = NULL;
    for (int i = 9; i >= 0; i--) {
        head = node_new(i, head);
    }
    assert(unsafe_find_last(head) == 9);
    free_list(head);
}

int main(void) {
    check();
    printf("All tests passed.\n");
    return 0;
}
