#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <assert.h>

/*
 * eat(number, need, remaining, result):
 *   If need <= remaining, result[0] = number + need, result[1] = remaining - need.
 *   Else, result[0] = number + remaining, result[1] = 0.
 *
 * We store the output in the integer array result[2].
 */
void eat(int number, int need, int remaining, int result[2]) {
    if (need <= remaining) {
        result[0] = number + need;
        result[1] = remaining - need;
    } else {
        result[0] = number + remaining;
        result[1] = 0;
    }
}

/*
 * A helper function to check that we got the expected array of two ints.
 */
static void assert_eat_output(int got[2], int expected0, int expected1, const char* test_label) {
    if (got[0] != expected0 || got[1] != expected1) {
        fprintf(stderr, "Assertion failed on %s. Expected [%d, %d], got [%d, %d].\n",
                test_label, expected0, expected1, got[0], got[1]);
        exit(EXIT_FAILURE);
    }
}

/*
 * check():
 *   Calls eat(...) with multiple test cases and verifies the results.
 *   Returns true if all tests pass.
 */
bool check(void) {
    int out[2];

    // Original tests
    // 1) eat(5, 6, 10) -> [11, 4]
    eat(5, 6, 10, out);
    assert_eat_output(out, 11, 4, "Test 1");

    // 2) eat(4, 8, 9) -> [12, 1]
    eat(4, 8, 9, out);
    assert_eat_output(out, 12, 1, "Test 2");

    // 3) eat(1, 10, 10) -> [11, 0]
    eat(1, 10, 10, out);
    assert_eat_output(out, 11, 0, "Test 3");

    // 4) eat(2, 11, 5) -> [7, 0]
    eat(2, 11, 5, out);
    assert_eat_output(out, 7, 0, "Test 4");

    // Additional tests
    // 5) eat(4, 5, 7) -> [9, 2]
    eat(4, 5, 7, out);
    assert_eat_output(out, 9, 2, "Test 5");

    // 6) eat(4, 5, 1) -> [5, 0]
    eat(4, 5, 1, out);
    assert_eat_output(out, 5, 0, "Test 6");

    // If we reach here, all tests have passed
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
