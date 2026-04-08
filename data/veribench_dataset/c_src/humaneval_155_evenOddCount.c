#include <stdio.h>
#include <stdlib.h>
#include <assert.h>
#include <math.h>   // for fabs (though we'll cast to int so abs is enough)
#include <string.h> // for sprintf

// We'll define a struct to hold the two counts
typedef struct {
    int even_count;
    int odd_count;
} EvenOddResult;

/**
 * Given an integer, return a struct containing (#even_digits, #odd_digits)
 * in the absolute value of that integer.
 *
 * Example:
 *   even_odd_count(-12) => (1,1)
 *   even_odd_count(123) => (1,2)
 */
EvenOddResult even_odd_count(int num) {
    EvenOddResult result;
    result.even_count = 0;
    result.odd_count  = 0;

    // Convert absolute value of num to string
    // We'll store it in a local buffer:
    char buffer[50];
    int abs_value = (num < 0) ? -num : num;
    sprintf(buffer, "%d", abs_value);

    // Iterate over each character
    for (int i = 0; buffer[i] != '\0'; i++) {
        int digit = buffer[i] - '0';
        if (digit % 2 == 0) {
            result.even_count++;
        } else {
            result.odd_count++;
        }
    }
    return result;
}

/**
 * We'll define a check function that calls even_odd_count
 * with the test data, verifying correctness via asserts.
 */
int check() {
    {
        // Original tests
        {
            EvenOddResult r = even_odd_count(7);     // => (0,1)
            assert(r.even_count == 0 && r.odd_count == 1);

            r = even_odd_count(-78);                 // => (1,1)
            assert(r.even_count == 1 && r.odd_count == 1);

            r = even_odd_count(3452);                // => (2,2)
            assert(r.even_count == 2 && r.odd_count == 2);

            r = even_odd_count(346211);              // => (3,3)
            assert(r.even_count == 3 && r.odd_count == 3);

            r = even_odd_count(-345821);             // => (3,3)
            assert(r.even_count == 3 && r.odd_count == 3);

            r = even_odd_count(-2);                  // => (1,0)
            assert(r.even_count == 1 && r.odd_count == 0);

            r = even_odd_count(-45347);              // => (2,3)
            assert(r.even_count == 2 && r.odd_count == 3);

            r = even_odd_count(0);                   // => (1,0)
            assert(r.even_count == 1 && r.odd_count == 0);
        }
        // Additional tests
        {
            // 1. All digits even => 24680 => (5,0)
            EvenOddResult r = even_odd_count(24680);
            assert(r.even_count == 5 && r.odd_count == 0);

            // 2. All digits odd => 13579 => (0,5)
            r = even_odd_count(13579);
            assert(r.even_count == 0 && r.odd_count == 5);
        }
    }
    return 1;  // All tests passed
}

int main() {
    if (check()) {
        printf("Pass!\n");
    } else {
        printf("Some tests failed.\n");
    }
    return 0;
}
