#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>
#include <assert.h>

// We'll assume no more than 100 input strings, each up to length 999
#define MAX_STRINGS 100
#define MAX_LENGTH 1000

/**
 * Returns 1 (true) if 'substring' occurs within 'str', else 0 (false).
 * This duplicates Python's "substring in str" logic, including:
 * - if substring is "", we return true.
 */
bool string_contains(const char *str, const char *substring) {
    // The standard library function strstr(...) returns pointer if found, else NULL.
    // If substring is an empty string, strstr returns (char*)str (non-NULL).
    return (strstr(str, substring) != NULL);
}

/**
 * Filter an input array of strings by 'substring'.
 * The results are stored in 'out_array'. The length of the result array is stored in '*out_count'.
 *
 * strings: array of input strings
 * count: number of input strings
 * substring: the substring we filter on
 * out_array: user-provided array for results
 * out_count: will store how many strings matched
 */
void filter_by_substring(const char strings[MAX_STRINGS][MAX_LENGTH], int count,
                         const char *substring,
                         char out_array[MAX_STRINGS][MAX_LENGTH], int *out_count) {
    *out_count = 0;

    for (int i = 0; i < count; i++) {
        if (string_contains(strings[i], substring)) {
            // copy strings[i] to out_array[*out_count]
            strcpy(out_array[*out_count], strings[i]);
            (*out_count)++;
        }
    }
}

/**
 * Compare two arrays of strings for equality:
 * 1) They must have the same length
 * 2) Each corresponding element must match
 */
bool string_arrays_equal(const char arr1[MAX_STRINGS][MAX_LENGTH], int len1,
                         const char arr2[MAX_STRINGS][MAX_LENGTH], int len2) {
    if (len1 != len2) {
        return false;
    }
    for (int i = 0; i < len1; i++) {
        if (strcmp(arr1[i], arr2[i]) != 0) {
            return false;
        }
    }
    return true;
}

/**
 * This function (mimicking the "check" in Python) tests 'filter_by_substring' with various inputs
 * and verifies correctness using assert.
 */
bool check() {
    {
        // candidate([], 'john') => []
        char input[MAX_STRINGS][MAX_LENGTH];
        int input_count = 0; // no strings
        char output[MAX_STRINGS][MAX_LENGTH];
        int out_count = 0;

        filter_by_substring(input, input_count, "john", output, &out_count);
        // Expect an empty result
        assert(out_count == 0);
    }
    {
        // input = ['xxx','asd','xxy','john doe','xxxAAA','xxx'], substring='xxx'
        char input[MAX_STRINGS][MAX_LENGTH] = {
            "xxx", "asd", "xxy", "john doe", "xxxAAA", "xxx"
        };
        int input_count = 6;
        char output[MAX_STRINGS][MAX_LENGTH];
        int out_count = 0;

        filter_by_substring(input, input_count, "xxx", output, &out_count);

        char expected[MAX_STRINGS][MAX_LENGTH] = {
            "xxx", "xxxAAA", "xxx"
        };
        int expected_count = 3;

        assert(string_arrays_equal(output, out_count, expected, expected_count));
    }
    {
        // input = ['xxx','asd','aaaxxy','john doe','xxxAAA','xxx'], substring='xx'
        char input[MAX_STRINGS][MAX_LENGTH] = {
            "xxx", "asd", "aaaxxy", "john doe", "xxxAAA", "xxx"
        };
        int input_count = 6;
        char output[MAX_STRINGS][MAX_LENGTH];
        int out_count = 0;

        filter_by_substring(input, input_count, "xx", output, &out_count);

        char expected[MAX_STRINGS][MAX_LENGTH] = {
            "xxx", "aaaxxy", "xxxAAA", "xxx"
        };
        int expected_count = 4;

        assert(string_arrays_equal(output, out_count, expected, expected_count));
    }
    {
        // input = ['grunt','trumpet','prune','gruesome'], substring='run'
        char input[MAX_STRINGS][MAX_LENGTH] = {
            "grunt", "trumpet", "prune", "gruesome"
        };
        int input_count = 4;
        char output[MAX_STRINGS][MAX_LENGTH];
        int out_count = 0;

        filter_by_substring(input, input_count, "run", output, &out_count);

        char expected[MAX_STRINGS][MAX_LENGTH] = {
            "grunt", "prune"
        };
        int expected_count = 2;

        assert(string_arrays_equal(output, out_count, expected, expected_count));
    }

    // Additional tests

    // 1. Substring is empty => everything matches
    {
        char input[MAX_STRINGS][MAX_LENGTH] = {"abc", "def"};
        int input_count = 2;
        char output[MAX_STRINGS][MAX_LENGTH];
        int out_count = 0;

        filter_by_substring(input, input_count, "", output, &out_count);

        // Expect the same as input
        assert(out_count == 2);
        char expected[MAX_STRINGS][MAX_LENGTH] = {"abc", "def"};
        int expected_count = 2;
        assert(string_arrays_equal(output, out_count, expected, expected_count));
    }

    // 2. Substring not present
    {
        char input[MAX_STRINGS][MAX_LENGTH] = {"abc", "def"};
        int input_count = 2;
        char output[MAX_STRINGS][MAX_LENGTH];
        int out_count = 0;

        filter_by_substring(input, input_count, "zzz", output, &out_count);

        // Expect empty
        assert(out_count == 0);
    }

    // 3. Mixed presence
    {
        // 'test' only in 'unittest' and 'contest'
        char input[MAX_STRINGS][MAX_LENGTH] = {"unittest", "productive", "contest", "random"};
        int input_count = 4;
        char output[MAX_STRINGS][MAX_LENGTH];
        int out_count = 0;

        filter_by_substring(input, input_count, "test", output, &out_count);

        char expected[MAX_STRINGS][MAX_LENGTH] = {"unittest", "contest"};
        int expected_count = 2;

        assert(string_arrays_equal(output, out_count, expected, expected_count));
    }

    // 4. Substring at the start
    {
        // 'hel' => in "hello world" and "help me"
        char input[MAX_STRINGS][MAX_LENGTH] = {"hello world", "bye world", "help me"};
        int input_count = 3;
        char output[MAX_STRINGS][MAX_LENGTH];
        int out_count = 0;

        filter_by_substring(input, input_count, "hel", output, &out_count);

        char expected[MAX_STRINGS][MAX_LENGTH] = {"hello world", "help me"};
        int expected_count = 2;
        assert(string_arrays_equal(output, out_count, expected, expected_count));
    }

    // 5. Substring at the end
    {
        // 'world' => in "hello world", "small world"
        char input[MAX_STRINGS][MAX_LENGTH] = {"hello world", "small world", "test"};
        int input_count = 3;
        char output[MAX_STRINGS][MAX_LENGTH];
        int out_count = 0;

        filter_by_substring(input, input_count, "world", output, &out_count);

        char expected[MAX_STRINGS][MAX_LENGTH] = {"hello world", "small world"};
        int expected_count = 2;
        assert(string_arrays_equal(output, out_count, expected, expected_count));
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
