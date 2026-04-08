// Filename: humaneval_1_separateParenGroups.c

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <assert.h>

#define MAX_GROUPS 100
#define MAX_LENGTH 1000

void separate_paren_groups(const char *paren_string, char result[MAX_GROUPS][MAX_LENGTH], int *group_count) {
    int current_depth = 0, index = 0;
    char current_string[MAX_LENGTH] = {0};
    *group_count = 0;

    while (*paren_string) {
        if (*paren_string == '(') {
            current_depth++;
            current_string[index++] = *paren_string;
        } else if (*paren_string == ')') {
            current_depth--;
            current_string[index++] = *paren_string;
            if (current_depth == 0) {
                current_string[index] = '\0';
                strcpy(result[*group_count], current_string);
                (*group_count)++;
                index = 0;
                current_string[0] = '\0';
            }
        }
        paren_string++;
    }
}

int check() {
    char result[MAX_GROUPS][MAX_LENGTH];
    int group_count;
    
    separate_paren_groups("(()()) ((())) () ((())()())", result, &group_count);
    assert(group_count == 4);
    assert(strcmp(result[0], "(()())") == 0);
    assert(strcmp(result[1], "((()))") == 0);
    assert(strcmp(result[2], "()") == 0);
    assert(strcmp(result[3], "((())()())") == 0);
    
    separate_paren_groups("() (()) ((())) (((())))", result, &group_count);
    assert(group_count == 4);
    assert(strcmp(result[0], "()") == 0);
    assert(strcmp(result[1], "(())") == 0);
    assert(strcmp(result[2], "((()))") == 0);
    assert(strcmp(result[3], "(((())))") == 0);
    
    separate_paren_groups("(()(())((())))", result, &group_count);
    assert(group_count == 1);
    assert(strcmp(result[0], "(()(())((())))") == 0);
    
    separate_paren_groups("( ) (( )) (( )( ))", result, &group_count);
    assert(group_count == 3);
    assert(strcmp(result[0], "()") == 0);
    assert(strcmp(result[1], "(())") == 0);
    assert(strcmp(result[2], "(()())") == 0);
    
    separate_paren_groups("", result, &group_count);
    assert(group_count == 0);
    
    separate_paren_groups("   ", result, &group_count);
    assert(group_count == 0);
    
    separate_paren_groups("()", result, &group_count);
    assert(group_count == 1);
    assert(strcmp(result[0], "()") == 0);
    
    separate_paren_groups("(", result, &group_count);
    assert(group_count == 0);
    
    separate_paren_groups(")", result, &group_count);
    assert(group_count == 0);
    
    separate_paren_groups("()(())", result, &group_count);
    assert(group_count == 2);
    assert(strcmp(result[0], "()") == 0);
    assert(strcmp(result[1], "(())") == 0);
    
    separate_paren_groups("  () (())  ", result, &group_count);
    assert(group_count == 2);
    assert(strcmp(result[0], "()") == 0);
    assert(strcmp(result[1], "(())") == 0);
    
    separate_paren_groups("(  ) ((   )) (( )(   ))", result, &group_count);
    assert(group_count == 3);
    assert(strcmp(result[0], "()") == 0);
    assert(strcmp(result[1], "(())") == 0);
    assert(strcmp(result[2], "(()())") == 0);
    
    return 1;
}

int main() {
    if (check()) {
        printf("Pass!\n");
    } else {
        printf("Some tests failed.\n");
    }
    return 0;
}