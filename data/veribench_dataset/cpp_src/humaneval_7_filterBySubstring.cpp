#include <iostream>
#include <vector>
#include <string>
#include <cassert>

using namespace std;

/**
 * Returns all strings in 'strings' that contain 'substring'.
 * If 'substring' is empty, all strings match (same as Python logic).
 */
vector<string> filter_by_substring(const vector<string>& strings, const string& substring) {
    vector<string> result;
    for (const auto& s : strings) {
        // Check if 'substring' occurs in 's'
        // string::find returns npos if not found
        if (s.find(substring) != string::npos) {
            result.push_back(s);
        }
    }
    return result;
}

/**
 * Helper function to compare two vectors of std::string for equality
 */
bool vectors_equal(const vector<string>& v1, const vector<string>& v2) {
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
 * Test function (mimics the Python 'check' function).
 */
bool check(vector<string> (*candidate)(const vector<string>&, const string&)) {
    // Original tests
    {
        // candidate([], 'john') => []
        vector<string> empty_vec;
        vector<string> r = candidate(empty_vec, "john");
        assert(vectors_equal(r, {}));
    }
    {
        // candidate(['xxx','asd','xxy','john doe','xxxAAA','xxx'], 'xxx')
        vector<string> input = {"xxx", "asd", "xxy", "john doe", "xxxAAA", "xxx"};
        vector<string> expected = {"xxx", "xxxAAA", "xxx"};
        auto r = candidate(input, "xxx");
        assert(vectors_equal(r, expected));
    }
    {
        // candidate(['xxx','asd','aaaxxy','john doe','xxxAAA','xxx'], 'xx')
        vector<string> input = {"xxx", "asd", "aaaxxy", "john doe", "xxxAAA", "xxx"};
        vector<string> expected = {"xxx", "aaaxxy", "xxxAAA", "xxx"};
        auto r = candidate(input, "xx");
        assert(vectors_equal(r, expected));
    }
    {
        // candidate(['grunt','trumpet','prune','gruesome'], 'run')
        vector<string> input = {"grunt", "trumpet", "prune", "gruesome"};
        vector<string> expected = {"grunt", "prune"};
        auto r = candidate(input, "run");
        assert(vectors_equal(r, expected));
    }

    // Additional tests

    // 1. Substring is empty => everything matches
    {
        vector<string> input = {"abc", "def"};
        vector<string> expected = {"abc", "def"}; // everything is returned
        auto r = candidate(input, "");
        assert(vectors_equal(r, expected));
    }

    // 2. Substring not present
    {
        vector<string> input = {"abc", "def"};
        vector<string> expected = {};
        auto r = candidate(input, "zzz");
        assert(vectors_equal(r, expected));
    }

    // 3. Mixed presence
    {
        // "test" only in 'unittest' and 'contest'
        vector<string> input = {"unittest", "productive", "contest", "random"};
        vector<string> expected = {"unittest", "contest"};
        auto r = candidate(input, "test");
        assert(vectors_equal(r, expected));
    }

    // 4. Substring at the start
    {
        // substring "hel" => matches "hello world" and "help me"
        vector<string> input = {"hello world", "bye world", "help me"};
        vector<string> expected = {"hello world", "help me"};
        auto r = candidate(input, "hel");
        assert(vectors_equal(r, expected));
    }

    // 5. Substring at the end
    {
        // substring "world" => matches "hello world", "small world"
        vector<string> input = {"hello world", "small world", "test"};
        vector<string> expected = {"hello world", "small world"};
        auto r = candidate(input, "world");
        assert(vectors_equal(r, expected));
    }

    return true;
}

int main() {
    if (check(filter_by_substring)) {
        cout << "Pass!" << endl;
    } else {
        cout << "Some tests failed." << endl;
    }
    return 0;
}
