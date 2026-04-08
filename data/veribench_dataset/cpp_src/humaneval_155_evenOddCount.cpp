#include <iostream>
#include <utility>   // For std::pair
#include <cmath>     // For std::abs
#include <string>    // For std::to_string
#include <cassert>

/**
 * Given an integer, return a pair <#evens, #odds> that counts
 * how many digits are even vs. odd in the absolute value of `num`.
 *
 * Example:
 *   even_odd_count(-12) => (1,1)  (1 even, 1 odd)
 *   even_odd_count(123) => (1,2)
 */
std::pair<int,int> even_odd_count(int num) {
    int even_count = 0;
    int odd_count  = 0;

    // Convert absolute value of num to string
    std::string s = std::to_string(std::abs(num));

    // For each character (digit), check if it is even or odd
    for (char c : s) {
        int digit = c - '0';  // convert character to integer
        if (digit % 2 == 0) {
            even_count++;
        } else {
            odd_count++;
        }
    }
    return std::make_pair(even_count, odd_count);
}

/**
 * We replicate the "check" function from Python,
 * verifying that 'candidate' passes all the given tests.
 */
bool check(std::pair<int,int> (*candidate)(int)) {
    // Original tests
    {
        auto r = candidate(7);       // => (0,1)
        assert(r.first == 0 && r.second == 1);

        r = candidate(-78);          // => (1,1)
        assert(r.first == 1 && r.second == 1);

        r = candidate(3452);         // => (2,2)
        assert(r.first == 2 && r.second == 2);

        r = candidate(346211);       // => (3,3)
        assert(r.first == 3 && r.second == 3);

        r = candidate(-345821);      // => (3,3)
        assert(r.first == 3 && r.second == 3);

        r = candidate(-2);           // => (1,0)
        assert(r.first == 1 && r.second == 0);

        r = candidate(-45347);       // => (2,3)
        assert(r.first == 2 && r.second == 3);

        r = candidate(0);            // => (1,0)
        assert(r.first == 1 && r.second == 0);
    }

    // Additional tests
    // 1. All digits even => 24680 => (5,0)
    {
        auto r = candidate(24680);
        assert(r.first == 5 && r.second == 0);
    }
    // 2. All digits odd => 13579 => (0,5)
    {
        auto r = candidate(13579);
        assert(r.first == 0 && r.second == 5);
    }
    return true;
}

int main() {
    if (check(even_odd_count)) {
        std::cout << "Pass!" << std::endl;
    } else {
        std::cout << "Some tests failed." << std::endl;
    }
    return 0;
}
