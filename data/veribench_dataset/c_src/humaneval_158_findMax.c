#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>
#include <assert.h>

// We assume that no word exceeds 255 characters, and that
// the function won't be called concurrently from multiple threads.
//
// Returns a pointer to a static buffer containing the best word.
// If length == 0, returns an empty string.
const char* find_max(const char *words[], int length) {
    static char best_word[256];  // We'll store the best result here
    best_word[0] = '\0';

    if (length == 0) {
        // Return an empty string if no words
        return best_word;
    }

    int best_unique_count = -1;

    for (int i = 0; i < length; i++) {
        const char *word = words[i];

        // Build a frequency array or a set for unique chars:
        // Here we'll do a simple boolean array of size 256 to track ASCII usage.
        bool freq[256] = {false};
        int unique_count = 0;

        for (int j = 0; word[j] != '\0'; j++) {
            unsigned char c = (unsigned char)word[j];
            if (!freq[c]) {
                freq[c] = true;
                unique_count++;
            }
        }

        // If more unique characters or if a tie that is lexicographically earlier:
        if (unique_count > best_unique_count) {
            best_unique_count = unique_count;
            strncpy(best_word, word, 255);
            best_word[255] = '\0';
        } else if (unique_count == best_unique_count) {
            // Compare lexicographically
            if (strcmp(word, best_word) < 0) {
                strncpy(best_word, word, 255);
                best_word[255] = '\0';
            }
        }
    }
    return best_word;
}

// A helper to compare function output with an expected string
void assert_string_equal(const char *got, const char *expected, const char *label) {
    if (strcmp(got, expected) != 0) {
        fprintf(stderr, "Assertion failed (%s): expected \"%s\" but got \"%s\"\n", label, expected, got);
        exit(EXIT_FAILURE);
    }
}

// We'll build arrays for each test and pass them into find_max
bool check() {
    {
        const char* arr[] = {"name", "of", "string"};
        assert_string_equal(find_max(arr, 3), "string", "t1");
    }
    {
        const char* arr[] = {"name", "enam", "game"};
        assert_string_equal(find_max(arr, 3), "enam", "t2");
    }
    {
        const char* arr[] = {"aaaaaaa", "bb", "cc"};
        assert_string_equal(find_max(arr, 3), "aaaaaaa", "t3");
    }
    {
        const char* arr[] = {"abc", "cba"};
        assert_string_equal(find_max(arr, 2), "abc", "t4");
    }
    {
        const char* arr[] = {"play", "this", "game", "of", "footbott"};
        assert_string_equal(find_max(arr, 5), "footbott", "t5");
    }
    {
        const char* arr[] = {"we", "are", "gonna", "rock"};
        assert_string_equal(find_max(arr, 4), "gonna", "t6");
    }
    {
        const char* arr[] = {"we", "are", "a", "mad", "nation"};
        assert_string_equal(find_max(arr, 5), "nation", "t7");
    }
    {
        const char* arr[] = {"this", "is", "a", "prrk"};
        assert_string_equal(find_max(arr, 4), "this", "t8");
    }

    // Edge cases
    {
        const char* arr[] = {"b"};
        assert_string_equal(find_max(arr, 1), "b", "t9");
    }
    {
        const char* arr[] = {"play", "play", "play"};
        assert_string_equal(find_max(arr, 3), "play", "t10");
    }

    // Additional edge cases

    // 1. Empty list -> should return an empty string
    {
        const char* arr[] = {};
        assert_string_equal(find_max(arr, 0), "", "Empty list case");
    }

    // 2. Same unique characters, different lexicographical order
    //    "abcd", "abdc", "bacd" -> all have 4 distinct letters
    //    Among them, "abcd" is lexicographically smallest
    {
        const char* arr[] = {"abcd", "abdc", "bacd"};
        assert_string_equal(find_max(arr, 3), "abcd", "t11");
    }

    // 3. Single word with only one unique character
    {
        const char* arr[] = {"aaaaaa"};
        assert_string_equal(find_max(arr, 1), "aaaaaa", "t12");
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
