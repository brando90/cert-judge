#include <stdio.h>
#include <stdlib.h>
#include <ctype.h>   // for tolower
#include <string.h>  // for strcpy, strcat
#include <assert.h>

/**
 * Convert an integer in [1..1000] to Roman numeral (lowercase).
 * We store the result in 'output' and return output as well.
 * Assume 'output' has enough space (say at least 20 chars).
 */
char* int_to_mini_roman(int number, char *output) {
    // Values and symbols in ascending order
    // (like the Python arrays), but we will index from the top (i=12).
    static int num[] = {1, 4, 5, 9, 10, 40, 50, 90, 100, 400, 500, 900, 1000};
    static const char* sym[] = {
        "I", "IV", "V", "IX", "X", "XL", "L", "XC",
        "C", "CD", "D", "CM", "M"
    };
    
    // We'll build the result in uppercase first,
    // then convert to lowercase.
    char buffer[50] = "";  // temporary
    int i = 12;
    
    while (number > 0) {
        int div = number / num[i];
        number %= num[i];
        while (div > 0) {
            strcat(buffer, sym[i]);
            div--;
        }
        i--;
    }
    // Convert buffer to lowercase
    for (int j = 0; buffer[j] != '\0'; j++) {
        buffer[j] = (char)tolower((unsigned char)buffer[j]);
    }
    strcpy(output, buffer);
    return output;
}

/**
 * We'll define a check function that calls int_to_mini_roman
 * with test data, verifying correctness with assert.
 */
int check() {
    char result[50];

    // Original tests
    assert(strcmp(int_to_mini_roman(19,   result), "xix")     == 0);
    assert(strcmp(int_to_mini_roman(152,  result), "clii")    == 0);
    assert(strcmp(int_to_mini_roman(251,  result), "ccli")    == 0);
    assert(strcmp(int_to_mini_roman(426,  result), "cdxxvi")  == 0);
    assert(strcmp(int_to_mini_roman(500,  result), "d")       == 0);
    assert(strcmp(int_to_mini_roman(1,    result), "i")       == 0);
    assert(strcmp(int_to_mini_roman(4,    result), "iv")      == 0);
    assert(strcmp(int_to_mini_roman(43,   result), "xliii")   == 0);
    assert(strcmp(int_to_mini_roman(90,   result), "xc")      == 0);
    assert(strcmp(int_to_mini_roman(94,   result), "xciv")    == 0);
    assert(strcmp(int_to_mini_roman(532,  result), "dxxxii")  == 0);
    assert(strcmp(int_to_mini_roman(900,  result), "cm")      == 0);
    assert(strcmp(int_to_mini_roman(994,  result), "cmxciv")  == 0);
    assert(strcmp(int_to_mini_roman(1000, result), "m")       == 0);

    // Additional or edge tests are effectively covered by these.

    return 1; // All tests passed
}

int main() {
    if (check()) {
        printf("Pass!\n");
    } else {
        printf("Some tests failed.\n");
    }
    return 0;
}
