/* Safe memory access: prevent use-after-free by validating block before access.
 */

#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <assert.h>
#include <stdbool.h>

typedef struct MemoryBlock {
    char *data;
    bool is_freed;
} MemoryBlock;

MemoryBlock *memory_block_new(const char *data) {
    MemoryBlock *block = (MemoryBlock *)malloc(sizeof(MemoryBlock));
    if (!block) { perror("malloc"); exit(1); }
    block->is_freed = false;
    if (data) {
        block->data = strdup(data);
    } else {
        block->data = NULL;
    }
    return block;
}

void memory_block_free(MemoryBlock *block) {
    block->is_freed = true;
    free(block->data);
    block->data = NULL;
}

/* Safe access: returns 0 on success with data in *out, -1 if block is freed. */
int safe_access_memory(MemoryBlock *block, const char **out) {
    if (!block || block->is_freed) {
        return -1; /* access after free */
    }
    *out = block->data;
    return 0;
}

void memory_block_destroy(MemoryBlock *block) {
    if (!block->is_freed) {
        free(block->data);
    }
    free(block);
}

void check(void) {
    const char *data;

    /* Normal */
    MemoryBlock *b1 = memory_block_new("hello");
    assert(safe_access_memory(b1, &data) == 0);
    assert(strcmp(data, "hello") == 0);
    memory_block_destroy(b1);

    /* Freed must return error */
    MemoryBlock *b2 = memory_block_new("test");
    memory_block_free(b2);
    assert(safe_access_memory(b2, &data) == -1);
    free(b2);

    /* Empty string ok */
    MemoryBlock *b3 = memory_block_new("");
    assert(safe_access_memory(b3, &data) == 0);
    assert(strcmp(data, "") == 0);
    memory_block_destroy(b3);
}

int main(void) {
    check();
    printf("All tests passed.\n");
    return 0;
}
