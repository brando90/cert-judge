#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <ctype.h>
#include <string.h>
#include <assert.h>

/*
 * solve(input, output):
 *   - If the string has at least one letter, swap the case of each letter.
 *   - If the string has no letters, reverse it.
 * 
 * We store the resulting string in 'output'. 
 * We assume 'output' has enough space to hold the result (including null terminator).
 */
void solve(const char *input, char *output) {
    bool has_letters = false;
    size_t len = strlen(input);

    // First, let's do a pass to build the intermediate result in output
    for (size_t i = 0; i < len; i++) {
        unsigned char c = (unsigned char)input[i];
        if (isalpha(c)) {
            has_letters = true;
            if (islower(c)) {
                output[i] = (char)toupper(c);
            } else {
                output[i] = (char)tolower(c);
            }
        } else {
            output[i] = (char)c;
        }
    }
    output[len] = '\0';

    if (!has_letters) {
        // Reverse the string in place
        for (size_t i = 0; i < len / 2; i++) {
            char tmp = output[i];
            output[i] = output[len - 1 - i];
            output[len - 1 - i] = tmp;
        }
    }
}

// Helper function to compare solution with expected result
static void assert_solve(const char* input, const char* expected) {
    char buffer[256];
    solve(input, buffer);

    if (strcmp(buffer, expected) != 0) {
        fprintf(stderr, "Assertion failed for input \"%s\":\n", input);
        fprintf(stderr, "  Expected: \"%s\"\n", expected);
        fprintf(stderr, "  Got:      \"%s\"\n", buffer);
        exit(EXIT_FAILURE);
    }
}

// The check function: calls 'solve(...)' with test inputs and verifies correctness
bool check(void) {
    // Original tests
    assert_solve("AsDf",   "aSdF");
    assert_solve("1234",   "4321");
    assert_solve("ab",     "AB");
    assert_solve("#a@C",   "#A@c");
    assert_solve("#AsdfW^45", "#aSDFw^45");
    assert_solve("#6@2",   "2@6#");

    // Additional tests
    assert_solve("#$a^D", "#$A^d");   // Mix of symbols and letters
    assert_solve("#ccc",  "#CCC");    // All lowercase letters
    assert_solve("",      "");        // Empty string
    assert_solve("!!!",   "!!!");     // No letters -> reversed, but it's symmetrical, so "!!!"
    assert_solve("AAA",   "aaa");     // All uppercase letters
    assert_solve("a",     "A");       // Single lowercase letter
    assert_solve("A",     "a");       // Single uppercase letter

    return true;
}

int main(void) {
    if (check()) {
        printf("Pass!\n");
    } else {
        printf("Some tests failed.\n");
    }
    return 0;
}
