/* Sort a space-delimited string of number words from smallest to largest. */
#define _POSIX_C_SOURCE 200809L
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <assert.h>

static int word_value(const char *word) {
    if (strcmp(word, "zero") == 0) return 0;
    if (strcmp(word, "one") == 0) return 1;
    if (strcmp(word, "two") == 0) return 2;
    if (strcmp(word, "three") == 0) return 3;
    if (strcmp(word, "four") == 0) return 4;
    if (strcmp(word, "five") == 0) return 5;
    if (strcmp(word, "six") == 0) return 6;
    if (strcmp(word, "seven") == 0) return 7;
    if (strcmp(word, "eight") == 0) return 8;
    if (strcmp(word, "nine") == 0) return 9;
    return -1;
}

static int cmp_words(const void *a, const void *b) {
    const char *wa = *(const char **)a;
    const char *wb = *(const char **)b;
    return word_value(wa) - word_value(wb);
}

/* Caller must free result. */
char *sort_numbers(const char *numbers) {
    if (numbers[0] == '\0') {
        char *r = malloc(1);
        r[0] = '\0';
        return r;
    }

    /* Split into words */
    char *copy = strdup(numbers);
    char *words[100];
    int count = 0;
    char *tok = strtok(copy, " ");
    while (tok != NULL) {
        words[count++] = tok;
        tok = strtok(NULL, " ");
    }

    /* Sort */
    qsort(words, count, sizeof(char *), cmp_words);

    /* Join */
    int total_len = 0;
    for (int i = 0; i < count; i++) {
        total_len += strlen(words[i]);
        if (i > 0) total_len++; /* space */
    }
    char *result = malloc(total_len + 1);
    int pos = 0;
    for (int i = 0; i < count; i++) {
        if (i > 0) result[pos++] = ' ';
        int wlen = strlen(words[i]);
        memcpy(result + pos, words[i], wlen);
        pos += wlen;
    }
    result[pos] = '\0';

    free(copy);
    return result;
}

void check(void) {
    char *r;

    r = sort_numbers("");
    assert(strcmp(r, "") == 0);
    free(r);

    r = sort_numbers("three");
    assert(strcmp(r, "three") == 0);
    free(r);

    r = sort_numbers("three five nine");
    assert(strcmp(r, "three five nine") == 0);
    free(r);

    r = sort_numbers("five zero four seven nine eight");
    assert(strcmp(r, "zero four five seven eight nine") == 0);
    free(r);

    r = sort_numbers("six five four three two one zero");
    assert(strcmp(r, "zero one two three four five six") == 0);
    free(r);
}

int main(void) {
    check();
    printf("All tests passed.\n");
    return 0;
}
