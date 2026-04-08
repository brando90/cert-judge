#include <iostream>
#include <string>
#include <cassert>
#include <algorithm>

// The solve function in C++:
//  - If the string has at least one letter, swap the case of each letter
//    (lower <-> upper) and keep other characters unchanged.
//  - If the string has no letters, return its reverse.
std::string solve(const std::string &s) {
    bool has_letters = false;
    std::string result;

    for (char c : s) {
        if (std::isalpha(static_cast<unsigned char>(c))) {
            has_letters = true;
            // Toggle case:
            if (std::islower(static_cast<unsigned char>(c))) {
                result.push_back(std::toupper(static_cast<unsigned char>(c)));
            } else {
                result.push_back(std::tolower(static_cast<unsigned char>(c)));
            }
        } else {
            result.push_back(c);
        }
    }

    if (!has_letters) {
        // Reverse the string
        std::reverse(result.begin(), result.end());
    }
    return result;
}

// The test function (similar to the Python "check"):
bool check(std::string (*candidate)(const std::string&)) {
    // Original tests
    assert(candidate("AsDf") == "aSdF");
    assert(candidate("1234") == "4321");
    assert(candidate("ab") == "AB");
    assert(candidate("#a@C") == "#A@c");
    assert(candidate("#AsdfW^45") == "#aSDFw^45");
    assert(candidate("#6@2") == "2@6#");

    // Additional edge cases
    assert(candidate("#$a^D") == "#$A^d");  // Mix of symbols and letters
    assert(candidate("#ccc") == "#CCC");    // All lowercase letters
    assert(candidate("") == "");            // Empty string
    assert(candidate("!!!") == "!!!");      // No letters, only symbols -> reversed => "!!!"
    assert(candidate("AAA") == "aaa");      // All uppercase letters
    assert(candidate("a") == "A");          // Single lowercase letter
    assert(candidate("A") == "a");          // Single uppercase letter

    return true;
}

int main() {
    if (check(solve)) {
        std::cout << "Pass!" << std::endl;
    } else {
        std::cout << "Some tests failed." << std::endl;
    }
    return 0;
}
