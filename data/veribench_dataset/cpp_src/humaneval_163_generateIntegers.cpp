#include <iostream>
#include <vector>
#include <algorithm>
#include <cassert>

using namespace std;

/*
 * generate_integers(a, b):
 *   Given two integers a and b, produce a vector of the even integers from 2..8
 *   that lie between min(a,b) and max(a,b), inclusive.
 */
vector<int> generate_integers(int a, int b) {
    int lower = max(2, min(a, b));
    int upper = min(8, max(a, b));
    vector<int> result;
    for (int i = lower; i <= upper; i++) {
        if (i % 2 == 0) {
            result.push_back(i);
        }
    }
    return result;
}

/*
 * check(candidate):
 *   Checks the correctness of the candidate function using various test cases,
 *   mirroring the Python test suite.
 */
bool check(vector<int> (*candidate)(int, int)) {
    // Original tests
    // Test 1
    {
        auto got = candidate(2, 10);
        assert((got == vector<int>{2, 4, 6, 8}) && "Test 1");
    }
    // Test 2
    {
        auto got = candidate(10, 2);
        assert((got == vector<int>{2, 4, 6, 8}) && "Test 2");
    }
    // Test 3
    {
        auto got = candidate(132, 2);
        assert((got == vector<int>{2, 4, 6, 8}) && "Test 3");
    }
    // Test 4
    {
        auto got = candidate(17, 89);
        assert((got == vector<int>{}) && "Test 4");
    }

    // Additional edge cases
    // 1) Both inputs are the same within range (4,4)
    {
        auto got = candidate(4, 4);
        assert((got == vector<int>{4}) && "Edge Case 1");
    }
    // 2) Both inputs are the same outside range (10,10)
    {
        auto got = candidate(10, 10);
        assert((got == vector<int>{}) && "Edge Case 2");
    }
    // 3) Inputs cross the range boundaries (1,9)
    {
        auto got = candidate(1, 9);
        assert((got == vector<int>{2, 4, 6, 8}) && "Edge Case 3");
    }
    // 4) Inputs entirely below the range (0,1)
    {
        auto got = candidate(0, 1);
        assert((got == vector<int>{}) && "Edge Case 4");
    }
    // 5) Inputs entirely above the range (9,12)
    {
        auto got = candidate(9, 12);
        assert((got == vector<int>{}) && "Edge Case 5");
    }

    return true; // If no asserts failed, we're good
}

int main() {
    if (check(generate_integers)) {
        cout << "Pass!" << endl;
    } else {
        cout << "Some tests failed." << endl;
    }
    return 0;
}
