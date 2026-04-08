#include <iostream>
#include <string>
#include <vector>
#include <cassert>
#include <algorithm> // for std::transform

/**
 * Given an integer between 1 and 1000, return its Roman numeral representation
 * (in lowercase).
 *
 * Examples:
 *   int_to_mini_roman(19)  -> "xix"
 *   int_to_mini_roman(152) -> "clii"
 *   int_to_mini_roman(426) -> "cdxxvi"
 */
std::string int_to_mini_roman(int number) {
    // Values and symbols in decreasing order
    // (matching the Python logic, just reversed indexing)
    static const int    num[] = {1, 4, 5, 9, 10, 40, 50, 90,
                                 100, 400, 500, 900, 1000};
    static const char*  sym[] = {"I", "IV", "V", "IX", "X", "XL", "L", "XC",
                                 "C", "CD", "D", "CM", "M"};

    std::string result;
    int i = 12; // Start from the largest (1000)
    while (number > 0) {
        int div = number / num[i];
        number %= num[i];
        while (div > 0) {
            result += sym[i];
            div--;
        }
        i--;
    }
    // Convert result to lowercase
    std::string lower_result(result);
    std::transform(lower_result.begin(), lower_result.end(), lower_result.begin(),
                   [](unsigned char c){ return std::tolower(c); });
    return lower_result;
}

/**
 * We replicate the "check" function from Python, verifying
 * that int_to_mini_roman() passes the given tests.
 */
bool check(std::string (*candidate)(int)) {
    // Original tests
    assert(candidate(19)   == "xix");
    assert(candidate(152)  == "clii");
    assert(candidate(251)  == "ccli");
    assert(candidate(426)  == "cdxxvi");
    assert(candidate(500)  == "d");
    assert(candidate(1)    == "i");
    assert(candidate(4)    == "iv");
    assert(candidate(43)   == "xliii");
    assert(candidate(90)   == "xc");
    assert(candidate(94)   == "xciv");
    assert(candidate(532)  == "dxxxii");
    assert(candidate(900)  == "cm");
    assert(candidate(994)  == "cmxciv");
    assert(candidate(1000) == "m");

    // Additional or edge tests
    // (We've effectively tested min=1 and max=1000.)
    return true;
}

int main() {
    if (check(int_to_mini_roman)) {
        std::cout << "Pass!" << std::endl;
    } else {
        std::cout << "Some tests failed." << std::endl;
    }
    return 0;
}
