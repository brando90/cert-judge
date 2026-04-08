#include <iostream>
#include <vector>
#include <cassert>

using namespace std;

/*
 * eat(number, need, remaining):
 *   If need <= remaining, return [number + need, remaining - need].
 *   Else, return [number + remaining, 0].
 */
vector<int> eat(int number, int need, int remaining) {
    if (need <= remaining) {
        return {number + need, remaining - need};
    } else {
        return {number + remaining, 0};
    }
}

/*
 * check(candidate):
 *   Uses assert to test candidate function with multiple test cases.
 *   Returns true if all tests pass successfully.
 */
bool check(vector<int> (*candidate)(int, int, int)) {
    // Original tests
    // 1) eat(5, 6, 10) -> [11, 4]
    {
        auto got = candidate(5, 6, 10);
        assert(got.size() == 2);
        assert(got[0] == 11 && got[1] == 4);
    }
    // 2) eat(4, 8, 9) -> [12, 1]
    {
        auto got = candidate(4, 8, 9);
        assert(got.size() == 2);
        assert(got[0] == 12 && got[1] == 1);
    }
    // 3) eat(1, 10, 10) -> [11, 0]
    {
        auto got = candidate(1, 10, 10);
        assert(got.size() == 2);
        assert(got[0] == 11 && got[1] == 0);
    }
    // 4) eat(2, 11, 5) -> [7, 0]
    {
        auto got = candidate(2, 11, 5);
        assert(got.size() == 2);
        assert(got[0] == 7 && got[1] == 0);
    }

    // Additional tests
    // 5) eat(4, 5, 7) -> [9, 2]
    {
        auto got = candidate(4, 5, 7);
        assert(got.size() == 2);
        assert(got[0] == 9 && got[1] == 2);
    }
    // 6) eat(4, 5, 1) -> [5, 0]
    {
        auto got = candidate(4, 5, 1);
        assert(got.size() == 2);
        assert(got[0] == 5 && got[1] == 0);
    }

    // If we reach here, all tests have passed
    return true;
}

int main() {
    if (check(eat)) {
        cout << "Pass!" << endl;
    } else {
        cout << "Some tests failed." << endl;
    }
    return 0;
}
