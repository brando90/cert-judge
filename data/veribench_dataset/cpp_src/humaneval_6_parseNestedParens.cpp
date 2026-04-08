#include <iostream>
#include <string>
#include <vector>
#include <sstream>
#include <cassert>
#include <algorithm>

using namespace std;

/**
 * Given a single group of parentheses (e.g. "(()())"),
 * return the maximum nesting depth of that group.
 */
int parse_paren_group(const string& s) {
    int depth = 0;
    int max_depth = 0;
    for (char c : s) {
        if (c == '(') {
            depth++;
            max_depth = max(max_depth, depth);
        } else if (c == ')') {
            depth--;
        }
    }
    return max_depth;
}

/**
 * Given a string that may contain multiple groups of parentheses separated
 * by spaces, parse each group and return a vector of integer depths.
 *
 * Example:
 *   parse_nested_parens("(()()) ((())) () ((())()())") => [2, 3, 1, 3]
 */
vector<int> parse_nested_parens(const string& paren_string) {
    vector<int> result;
    // We'll split the string on spaces
    // and ignore any empty segments
    istringstream iss(paren_string);
    string group;
    while (iss >> group) {
        // For each non-empty group, compute max depth
        if (!group.empty()) {
            result.push_back(parse_paren_group(group));
        }
    }
    return result;
}

/**
 * Helper function to check if two integer vectors are equal
 */
bool vectors_equal(const vector<int>& a, const vector<int>& b) {
    if (a.size() != b.size()) return false;
    for (size_t i = 0; i < a.size(); i++) {
        if (a[i] != b[i]) return false;
    }
    return true;
}

/**
 * Test function (replicates the Python "check" function).
 */
bool check(vector<int> (*candidate)(const string&)) {
    // Original tests
    {
        vector<int> r = candidate("(()()) ((())) () ((())()())");
        assert(vectors_equal(r, {2, 3, 1, 3}));

        r = candidate("() (()) ((())) (((())))");
        assert(vectors_equal(r, {1, 2, 3, 4}));

        r = candidate("(()(())((())))");
        // There's only one group here => max nesting depth=4
        assert(vectors_equal(r, {4}));
    }

    // Additional tests

    // 1. Empty string => no groups => []
    {
        vector<int> r = candidate("");
        assert(vectors_equal(r, {}));
    }

    // 2. Single group with no nesting => "()"
    {
        vector<int> r = candidate("()");
        // "()" => max depth=1
        assert(vectors_equal(r, {1}));
    }

    // 3. Single group, deeply nested => "(((())))"
    {
        vector<int> r = candidate("(((())))");
        // max depth=4
        assert(vectors_equal(r, {4}));
    }

    // 4. Multiple groups with varying depths => "(()) ((()))"
    {
        vector<int> r = candidate("(()) ((()))");
        // first => depth=2, second => depth=3
        assert(vectors_equal(r, {2, 3}));
    }

    return true;
}

int main() {
    if (check(parse_nested_parens)) {
        cout << "Pass!" << endl;
    } else {
        cout << "Some tests failed." << endl;
    }
    return 0;
}
