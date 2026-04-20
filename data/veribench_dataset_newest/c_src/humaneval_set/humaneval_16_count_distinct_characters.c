/* Given a string, find out how many distinct characters (case-insensitive) it consists of. */
#include <stdio.h>
#include <string.h>
#include <assert.h>
#include <ctype.h>
#include <stdbool.h>

int count_distinct_characters(const char *string) {
    bool seen[256] = {false};
    int count = 0;
    for (int i = 0; string[i] != '\0'; i++) {
        unsigned char c = (unsigned char)tolower((unsigned char)string[i]);
        if (!seen[c]) {
            seen[c] = true;
            count++;
        }
    }
    return count;
}

void check(void) {
    assert(count_distinct_characters("") == 0);
    assert(count_distinct_characters("abcde") == 5);
    assert(count_distinct_characters("abcdecadeCADE") == 5);
    assert(count_distinct_characters("aaaaAAAAaaaa") == 1);
    assert(count_distinct_characters("Jerry jERRY JeRRRY") == 5);
}

int main(void) {
    check();
    printf("All tests passed.\n");
    return 0;
}
