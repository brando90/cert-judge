/* Return length of given string. */
#include <stdio.h>
#include <string.h>
#include <assert.h>

int my_strlen(const char *string) {
    return (int)strlen(string);
}

void check(void) {
    assert(my_strlen("") == 0);
    assert(my_strlen("x") == 1);
    assert(my_strlen("asdasnakj") == 9);
}

int main(void) {
    check();
    printf("All tests passed.\n");
    return 0;
}
