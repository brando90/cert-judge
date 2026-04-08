#include <iostream>
#include <vector>
#include <string>
#include <set>
#include <cassert>
#include <algorithm>

// Translated function: find_max
// Returns the word with the maximum number of unique characters.
// If there's a tie, return the lexicographically smallest word.
// If the list is empty, return an empty string.
std::string find_max(const std::vector<std::string>& words) {
    if (words.empty()) {
        return "";
    }

    std::string best_word = "";
    int best_unique_count = -1;

    for (const auto &word : words) {
        // Count unique characters:
        std::set<char> unique_chars(word.begin(), word.end());
        int count = static_cast<int>(unique_chars.size());

        if (count > best_unique_count) {
            best_unique_count = count;
            best_word = word;
        } else if (count == best_unique_count) {
            // Tie-breaking by lexicographical order:
            if (word < best_word) {
                best_word = word;
            }
        }
    }
    return best_word;
}

// Test function (similar to the Python check)
bool check(std::string (*candidate)(const std::vector<std::string>&)) {
    // Original tests
    assert(candidate({"name", "of", "string"}) == "string"); // t1
    assert(candidate({"name", "enam", "game"}) == "enam");   // t2
    assert(candidate({"aaaaaaa", "bb", "cc"}) == "aaaaaaa"); // t3
    assert(candidate({"abc", "cba"}) == "abc");              // t4
    assert(candidate({"play", "this", "game", "of", "footbott"}) == "footbott"); // t5
    assert(candidate({"we", "are", "gonna", "rock"}) == "gonna");                // t6
    assert(candidate({"we", "are", "a", "mad", "nation"}) == "nation");          // t7
    assert(candidate({"this", "is", "a", "prrk"}) == "this");                    // t8

    // Edge cases
    assert(candidate({"b"}) == "b"); // t9
    assert(candidate({"play", "play", "play"}) == "play"); // t10

    // Additional edge cases
    // 1. Empty list -> should return an empty string
    assert(candidate({}) == "");

    // 2. Words with the same unique characters but different lexicographical order
    //    "abcd", "abdc", "bacd" all have 4 unique chars, "abcd" < "abdc" < "bacd"
    assert(candidate({"abcd", "abdc", "bacd"}) == "abcd"); // t11

    // 3. Single word with only one unique character
    assert(candidate({"aaaaaa"}) == "aaaaaa"); // t12

    return true;
}

int main() {
    if (check(find_max)) {
        std::cout << "Pass!" << std::endl;
    } else {
        std::cout << "Some tests failed." << std::endl;
    }
    return 0;
}
