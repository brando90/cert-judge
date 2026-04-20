/* Remove vowels from a string (case-insensitive). */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <assert.h>
#include <ctype.h>

static int is_vowel(char c) {
    char lower = tolower((unsigned char)c);
    return (lower == 'a' || lower == 'e' || lower == 'i' || lower == 'o' || lower == 'u');
}

/* Caller must free result. */
char *remove_vowels(const char *text) {
    int len = strlen(text);
    char *result = malloc(len + 1);
    int pos = 0;
    for (int i = 0; i < len; i++) {
        if (!is_vowel(text[i])) {
            result[pos++] = text[i];
        }
    }
    result[pos] = '\0';
    return result;
}

void check(void) {
    char *r;

    r = remove_vowels("");
    assert(strcmp(r, "") == 0);
    free(r);

    r = remove_vowels("abcdef\nghijklm");
    assert(strcmp(r, "bcdf\nghjklm") == 0);
    free(r);

    r = remove_vowels("fedcba");
    assert(strcmp(r, "fdcb") == 0);
    free(r);

    r = remove_vowels("eeeee");
    assert(strcmp(r, "") == 0);
    free(r);

    r = remove_vowels("acBAA");
    assert(strcmp(r, "cB") == 0);
    free(r);

    r = remove_vowels("EcBOO");
    assert(strcmp(r, "cB") == 0);
    free(r);

    r = remove_vowels("ybcd");
    assert(strcmp(r, "ybcd") == 0);
    free(r);
}

int main(void) {
    check();
    printf("All tests passed.\n");
    return 0;
}
