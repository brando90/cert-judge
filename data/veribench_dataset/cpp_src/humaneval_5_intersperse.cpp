#include <iostream>
#include <vector>
#include <cassert>

using namespace std;

/**
 * Insert 'delimiter' between every pair of consecutive elements
 * in the vector 'numbers'. If 'numbers' is empty, return an empty vector.
 */
vector<int> intersperse(const vector<int>& numbers, int delimiter) {
    if (numbers.empty()) {
        return {};
    }
    // Pre-size the result to avoid repeated allocations:
    // If there are N elements, the final size is 2*N - 1
    vector<int> result;
    result.reserve(numbers.size() * 2 - 1);

    // Insert element, then delimiter, for all but the last
    for (size_t i = 0; i < numbers.size() - 1; ++i) {
        result.push_back(numbers[i]);
        result.push_back(delimiter);
    }
    // Finally append the last element
    result.push_back(numbers.back());

    return result;
}

/**
 * Helper function to compare two vectors for equality.
 */
bool vectors_equal(const vector<int>& v1, const vector<int>& v2) {
    if (v1.size() != v2.size()) {
        return false;
    }
    for (size_t i = 0; i < v1.size(); i++) {
        if (v1[i] != v2[i]) {
            return false;
        }
    }
    return true;
}

/**
 * A test function (mimicking the Python "check") that
 * uses assert to verify correctness.
 */
bool check(vector<int> (*candidate)(const vector<int>&, int)) {
    // Original tests
    {
        // candidate([], 7) => []
        vector<int> empty_input;
        vector<int> empty_expected;
        assert(vectors_equal(candidate(empty_input, 7), empty_expected));

        // candidate([5, 6, 3, 2], 8) => [5, 8, 6, 8, 3, 8, 2]
        vector<int> input1 = {5, 6, 3, 2};
        vector<int> expected1 = {5, 8, 6, 8, 3, 8, 2};
        assert(vectors_equal(candidate(input1, 8), expected1));

        // candidate([2, 2, 2], 2) => [2, 2, 2, 2, 2]
        vector<int> input2 = {2, 2, 2};
        vector<int> expected2 = {2, 2, 2, 2, 2};
        assert(vectors_equal(candidate(input2, 2), expected2));
    }

    // Additional tests

    // 1. Single element
    {
        vector<int> single_input = {42};
        vector<int> single_expected = {42};
        assert(vectors_equal(candidate(single_input, 9), single_expected));
    }

    // 2. Two elements
    {
        // candidate([1, 2], -1) => [1, -1, 2]
        vector<int> two_input = {1, 2};
        vector<int> two_expected = {1, -1, 2};
        assert(vectors_equal(candidate(two_input, -1), two_expected));
    }

    // 3. Larger list => length check
    {
        //  big_input = [1,2,3,4,5], delimiter=0
        //  The output length should be 2*5 - 1 = 9
        vector<int> big_input = {1, 2, 3, 4, 5};
        vector<int> big_output = candidate(big_input, 0);
        assert(big_output.size() == (big_input.size() * 2 - 1));

        // Also check the pattern is correct:
        // Indices 0,2,4,6,8 => original elements
        // Indices 1,3,5,7 => delimiter
        for (size_t i = 0; i < big_output.size(); ++i) {
            if (i % 2 == 0) {
                // Even index => original element
                assert(big_output[i] == big_input[i / 2]);
            } else {
                // Odd index => delimiter
                assert(big_output[i] == 0);
            }
        }
    }

    return true;
}

int main() {
    if (check(intersperse)) {
        cout << "Pass!" << endl;
    } else {
        cout << "Some tests failed." << endl;
    }
    return 0;
}
