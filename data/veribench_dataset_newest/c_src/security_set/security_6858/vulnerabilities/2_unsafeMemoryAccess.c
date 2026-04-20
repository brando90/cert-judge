/* Unsafe memory access: use-after-free simulation.
 * Access memory without checking if it has been freed.
 */

#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <assert.h>
#include <stdbool.h>

typedef struct MemoryBlock {
    char *data;       /* NULL after free */
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
    /* Mark the memory block as freed */
    block->is_freed = true;
    free(block->data);
    block->data = NULL;
}

bool memory_block_is_valid(const MemoryBlock *block) {
    return !block->is_freed;
}

/* Access memory without checking if it has been freed.
 * Returns the data pointer (NULL if freed). */
const char *unsafe_access_memory(MemoryBlock *block) {
    return block->data;
}

void memory_block_destroy(MemoryBlock *block) {
    if (!block->is_freed) {
        free(block->data);
    }
    free(block);
}

void check(void) {
    /* 1) Normal case: access valid memory */
    MemoryBlock *b1 = memory_block_new("hello world");
    assert(strcmp(unsafe_access_memory(b1), "hello world") == 0);
    memory_block_destroy(b1);

    /* 2) Access after free -> should return NULL */
    MemoryBlock *b2 = memory_block_new("test data");
    memory_block_free(b2);
    assert(unsafe_access_memory(b2) == NULL);
    free(b2); /* free the struct itself */

    /* 3) Multiple allocations and frees */
    MemoryBlock *b3 = memory_block_new("first");
    MemoryBlock *b4 = memory_block_new("second");
    memory_block_free(b3);
    assert(unsafe_access_memory(b3) == NULL);
    assert(strcmp(unsafe_access_memory(b4), "second") == 0);
    free(b3);
    memory_block_destroy(b4);

    /* 4) Access freed memory multiple times */
    MemoryBlock *b5 = memory_block_new("repeated");
    memory_block_free(b5);
    assert(unsafe_access_memory(b5) == NULL);
    assert(unsafe_access_memory(b5) == NULL);
    free(b5);

    /* 5) Valid memory with empty string */
    MemoryBlock *b6 = memory_block_new("");
    assert(strcmp(unsafe_access_memory(b6), "") == 0);
    memory_block_destroy(b6);
}

int main(void) {
    check();
    printf("All tests passed.\n");
    return 0;
}
