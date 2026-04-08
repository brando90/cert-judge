#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <assert.h>

/* We'll assume no more than 100 input elements. If an input can have N elements,
   the output can have up to 2*N-1 elements. */
#define MAX_INPUT_SIZE 100
#define MAX_OUTPUT_SIZE (2*MAX_INPUT_SIZE - 1)

/**
 * Insert 'delimiter' between every pair of consecutive elements in 'numbers' (length=n).
 * The resulting array is stored in 'out_array'. The number of elements in the
 * result is placed in '*out_length'.
 *
 * If 'n' is 0, 'out_length' will be 0 => no output.
 */
void intersperse(const int *numbers, int n, int delimiter,
                 int *out_array, int *out_length) {
    if (n == 0) {
        *out_length = 0;
        return;
    }

    // We'll fill out_array, inserting 'delimiter' between elements
    int idx_out = 0;

    for (int i = 0; i < n - 1; i++) {
        out_array[idx_out++] = numbers[i];
        out_array[idx_out++] = delimiter;
    }
    // Finally, append the last element
    out_array[idx_out++] = numbers[n - 1];

    *out_length = idx_out;
}

/* Helper to compare two arrays for equality of length and elements */
bool arrays_equal(const int *arr1, int len1, const int *arr2, int len2) {
    if (len1 != len2) return false;
    for (int i = 0; i < len1; i++) {
        if (arr1[i] != arr2[i]) return false;
    }
    return true;
}

/* We'll define a check function that replicates the Python tests. */
bool check() {
    {
        // candidate([], 7) => []
        int input1[] = {};
        int output[MAX_OUTPUT_SIZE];
        int out_len = 0;

        intersperse(input1, 0, 7, output, &out_len);
        assert(arrays_equal(output, out_len, NULL, 0)); // both length=0
    }
    {
        // candidate([5, 6, 3, 2], 8) => [5,8,6,8,3,8,2]
        int input2[] = {5, 6, 3, 2};
        int expected2[] = {5, 8, 6, 8, 3, 8, 2};
        int output[MAX_OUTPUT_SIZE];
        int out_len;

        intersperse(input2, 4, 8, output, &out_len);
        assert(arrays_equal(output, out_len, expected2, 7));
    }
    {
        // candidate([2,2,2], 2) => [2,2,2,2,2]
        int input3[] = {2, 2, 2};
        int expected3[] = {2, 2, 2, 2, 2};
        int output[MAX_OUTPUT_SIZE];
        int out_len;

        intersperse(input3, 3, 2, output, &out_len);
        assert(arrays_equal(output, out_len, expected3, 5));
    }

    // Additional tests

    // 1. Single element -> no place to insert => same as input
    {
        int single_input[] = {42};
        int single_output[MAX_OUTPUT_SIZE];
        int out_len;
        intersperse(single_input, 1, 9, single_output, &out_len);

        // Expect [42]
        int expected[] = {42};
        assert(arrays_equal(single_output, out_len, expected, 1));
    }

    // 2. Two elements => exactly one delimiter in between
    {
        int input4[] = {1, 2};
        int expected4[] = {1, -1, 2};
        int output[MAX_OUTPUT_SIZE];
        int out_len;

        intersperse(input4, 2, -1, output, &out_len);
        assert(arrays_equal(output, out_len, expected4, 3));
    }

    // 3. Larger list => length check
    {
        // [1,2,3,4,5], delimiter=0 => length = 9 => pattern check
        int big_input[] = {1, 2, 3, 4, 5};
        int out_len;
        int out_array[MAX_OUTPUT_SIZE];

        intersperse(big_input, 5, 0, out_array, &out_len);
        // We expect length=2*5 -1 = 9
        assert(out_len == 9);

        // Also check the pattern:
        // Even indices: original numbers, Odd indices: 0 (delimiter)
        // out_array[0]=1, [1]=0, [2]=2, [3]=0, [4]=3, [5]=0, [6]=4, [7]=0, [8]=5
        for (int i = 0; i < out_len; i++) {
            if (i % 2 == 0) {
                // even => an original element
                int original_index = i / 2;
                assert(out_array[i] == big_input[original_index]);
            } else {
                // odd => delimiter
                assert(out_array[i] == 0);
            }
        }
    }

    return true;
}

int main() {
    if (check()) {
        printf("Pass!\n");
    } else {
        printf("Some tests failed.\n");
    }
    return 0;
}
