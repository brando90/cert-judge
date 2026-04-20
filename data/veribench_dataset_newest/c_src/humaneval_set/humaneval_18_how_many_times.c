/* Find how many times a given substring can be found in the original string (overlapping). */
#include <stdio.h>
#include <string.h>
#include <assert.h>

int how_many_times(const char *string, const char *substring) {
    int slen = strlen(string);
    int sublen = strlen(substring);
    if (sublen == 0 || sublen > slen) return 0;

    int times = 0;
    for (int i = 0; i <= slen - sublen; i++) {
        if (strncmp(string + i, substring, sublen) == 0) {
            times++;
        }
    }
    return times;
}

void check(void) {
    assert(how_many_times("", "x") == 0);
    assert(how_many_times("xyxyxyx", "x") == 4);
    assert(how_many_times("cacacacac", "cac") == 4);
    assert(how_many_times("john doe", "john") == 1);
}

int main(void) {
    check();
    printf("All tests passed.\n");
    return 0;
}
