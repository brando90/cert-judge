/* For a given string, flip lowercase characters to uppercase and vice versa. */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <assert.h>
#include <ctype.h>

/* Caller must free result. */
char *flip_case(const char *string) {
    int len = strlen(string);
    char *result = malloc(len + 1);
    for (int i = 0; i < len; i++) {
        unsigned char c = (unsigned char)string[i];
        if (islower(c)) {
            result[i] = toupper(c);
        } else if (isupper(c)) {
            result[i] = tolower(c);
        } else {
            result[i] = c;
        }
    }
    result[len] = '\0';
    return result;
}

void check(void) {
    char *r;

    r = flip_case("");
    assert(strcmp(r, "") == 0);
    free(r);

    r = flip_case("Hello!");
    assert(strcmp(r, "hELLO!") == 0);
    free(r);

    r = flip_case("These violent delights have violent ends");
    assert(strcmp(r, "tHESE VIOLENT DELIGHTS HAVE VIOLENT ENDS") == 0);
    free(r);
}

int main(void) {
    check();
    printf("All tests passed.\n");
    return 0;
}
