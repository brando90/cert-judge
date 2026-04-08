// Filename: humaneval_1_separateParenGroups.cpp

#include <iostream>
#include <vector>
#include <string>
#include <cassert>

using namespace std;

vector<string> separate_paren_groups(const string& paren_string) {
    vector<string> result;
    string current_string;
    int current_depth = 0;
    
    for (char c : paren_string) {
        if (c == '(') {
            current_depth++;
            current_string += c;
        } else if (c == ')') {
            current_depth--;
            current_string += c;
            if (current_depth == 0) {
                result.push_back(current_string);
                current_string.clear();
            }
        }
    }
    return result;
}

bool check(vector<string> (*candidate)(const string&)) {
    // Original tests
    assert((candidate("(()()) ((())) () ((())()())") == vector<string>{"(()())", "((()))", "()", "((())()())"}));
    assert((candidate("() (()) ((())) (((())))") == vector<string>{"()", "(())", "((()))", "(((())))"}));
    assert((candidate("(()(())((())))") == vector<string>{"(()(())((())))"}));
    assert((candidate("( ) (( )) (( )( ))") == vector<string>{"()", "(())", "(()())"}));

    // Additional tests
    assert((candidate("") == vector<string>{}));                           // Empty string
    assert((candidate("   ") == vector<string>{}));                        // Spaces only
    assert((candidate("()") == vector<string>{"()"}));                     // Single balanced group
    assert((candidate("(") == vector<string>{}));                          // Single unbalanced open
    assert((candidate(")") == vector<string>{}));                          // Single unbalanced close
    assert((candidate("()(())") == vector<string>{"()", "(())"}));         // Multiple consecutive groups
    assert((candidate("  () (())  ") == vector<string>{"()", "(())"}));    // Leading/trailing spaces
    assert((candidate("(  ) ((   )) (( )(   ))") == vector<string>{"()", "(())", "(()())"})); // Spaces within parentheses
    
    return true;
}

int main() {
    if (check(separate_paren_groups)) {
        cout << "Pass!" << endl;
    } else {
        cout << "Some tests failed." << endl;
    }
    return 0;
}