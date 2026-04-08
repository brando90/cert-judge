#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <assert.h>

/*
 * generate_integers(a, b, out, out_size):
 *   Fills 'out' with the even integers from 2..8 that lie between min(a,b) and max(a,b).
 *   The number of elements placed in out is stored in *out_size.
 *
 * We assume 'out' has enough capacity for all possible answers (max 4 even numbers).
 */
void generate_integers(int a, int b, int *out, int *out_size) {
    int lower = (a < b) ? a : b;
    int upper = (a > b) ? a : b;
    if (lower < 2) lower = 2;
    if (upper > 8) upper = 8;

    int count = 0;
    for (int i = lower; i <= upper; i++) {
        if (i % 2 == 0) {
            out[count++] = i;
        }
    }
    *out_size = count;
}

/*
 * A helper to compare the output of generate_integers(...) with an expected array of integers.
 */
static void assert_array_equal(const int *got, int got_size, const int *expected, int expected_size, const char* msg) {
    if (got_size != expected_size) {
        fprintf(stderr, "Assertion failed (%s): size mismatch. Expected %d, got %d.\n",
                msg, expected_size, got_size);
        exit(EXIT_FAILURE);
    }
    for (int i = 0; i < got_size; i++) {
        if (got[i] != expected[i]) {
            fprintf(stderr, "Assertion failed (%s): at index %d, expected %d, got %d.\n",
                    msg, i, expected[i], got[i]);
            exit(EXIT_FAILURE);
        }
    }
}

/*
 * check():
 *   Runs generate_integers with various test inputs, verifying correctness with the expected outputs.
 */
bool check() {
    int out[10];   // Enough space for the results
    int size;

    // Original tests
    // Test 1
    generate_integers(2, 10, out, &size);
    int exp1[] = {2, 4, 6, 8};
    assert_array_equal(out, size, exp1, 4, "Test 1");

    // Test 2
    generate_integers(10, 2, out, &size);
    int exp2[] = {2, 4, 6, 8};
    assert_array_equal(out, size, exp2, 4, "Test 2");

    // Test 3
    generate_integers(132, 2, out, &size);
    int exp3[] = {2, 4, 6, 8};
    assert_array_equal(out, size, exp3, 4, "Test 3");

    // Test 4
    generate_integers(17, 89, out, &size);
    int exp4[] = {};
    assert_array_equal(out, size, exp4, 0, "Test 4");

    // Additional edge cases
    // 1) Both inputs are the same within range (4,4)
    generate_integers(4, 4, out, &size);
    int expEdge1[] = {4};
    assert_array_equal(out, size, expEdge1, 1, "Edge Case 1");

    // 2) Both inputs are the same outside range (10,10)
    generate_integers(10, 10, out, &size);
    int expEdge2[] = {};
    assert_array_equal(out, size, expEdge2, 0, "Edge Case 2");

    // 3) Inputs cross the range boundaries (1,9)
    generate_integers(1, 9, out, &size);
    int expEdge3[] = {2, 4, 6, 8};
    assert_array_equal(out, size, expEdge3, 4, "Edge Case 3");

    // 4) Inputs entirely below the range (0,1)
    generate_integers(0, 1, out, &size);
    int expEdge4[] = {};
    assert_array_equal(out, size, expEdge4, 0, "Edge Case 4");

    // 5) Inputs entirely above the range (9,12)
    generate_integers(9, 12, out, &size);
    int expEdge5[] = {};
    assert_array_equal(out, size, expEdge5, 0, "Edge Case 5");

    // If we got here, all tests have passed.
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
