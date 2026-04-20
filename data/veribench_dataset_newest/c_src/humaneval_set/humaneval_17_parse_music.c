/* Parse a string of musical notes and return beat counts. */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <assert.h>

/* Returns count of notes parsed. Results in result array. */
int parse_music(const char *music_string, int *result, int max_results) {
    int count = 0;
    int len = strlen(music_string);
    int i = 0;
    while (i < len && count < max_results) {
        /* skip spaces */
        while (i < len && music_string[i] == ' ') i++;
        if (i >= len) break;

        if (music_string[i] == '.' && i + 1 < len && music_string[i+1] == '|') {
            result[count++] = 1; /* quarter note */
            i += 2;
        } else if (music_string[i] == 'o' && i + 1 < len && music_string[i+1] == '|') {
            result[count++] = 2; /* half note */
            i += 2;
        } else if (music_string[i] == 'o') {
            result[count++] = 4; /* whole note */
            i += 1;
        } else {
            i++;
        }
    }
    return count;
}

void check(void) {
    int result[100];
    int n;

    n = parse_music("", result, 100);
    assert(n == 0);

    n = parse_music("o o o o", result, 100);
    assert(n == 4);
    for (int i = 0; i < 4; i++) assert(result[i] == 4);

    n = parse_music(".| .| .| .|", result, 100);
    assert(n == 4);
    for (int i = 0; i < 4; i++) assert(result[i] == 1);

    {
        int expected[] = {2, 2, 1, 1, 4, 4, 4, 4};
        n = parse_music("o| o| .| .| o o o o", result, 100);
        assert(n == 8);
        for (int i = 0; i < 8; i++) assert(result[i] == expected[i]);
    }

    {
        int expected[] = {2, 1, 2, 1, 4, 2, 4, 2};
        n = parse_music("o| .| o| .| o o| o o|", result, 100);
        assert(n == 8);
        for (int i = 0; i < 8; i++) assert(result[i] == expected[i]);
    }
}

int main(void) {
    check();
    printf("All tests passed.\n");
    return 0;
}
