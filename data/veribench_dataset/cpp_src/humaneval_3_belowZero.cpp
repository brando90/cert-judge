#include <iostream>
#include <vector>
#include <cassert>

bool below_zero(const std::vector<int>& operations) {
    /**
     * You're given a list of deposit and withdrawal operations on a bank account
     * that starts with zero balance.
     * Detect if at any point the balance falls below zero => return true.
     * Otherwise return false.
     */
    int balance = 0;
    for (int op : operations) {
        balance += op;
        if (balance < 0) {
            return true;
        }
    }
    return false;
}

bool check(bool (*candidate)(const std::vector<int>&)) {
    // Original tests
    assert(candidate({}) == false);
    assert(candidate({1, 2, -3, 1, 2, -3}) == false);
    assert(candidate({1, 2, -4, 5, 6}) == true);
    assert(candidate({1, -1, 2, -2, 5, -5, 4, -4}) == false);
    assert(candidate({1, -1, 2, -2, 5, -5, 4, -5}) == true);
    assert(candidate({1, -2, 2, -2, 5, -5, 4, -4}) == true);

    // Additional tests
    // 1. Single negative operation
    assert(candidate({-5}) == true);
    // 2. Single positive operation
    assert(candidate({5}) == false);
    // 3. Balanced deposits => never below zero
    assert(candidate({1, -1}) == false);
    // 4. Goes below zero at the last operation
    assert(candidate({5, -3, -3}) == true);

    return true;
}

int main() {
    if (check(below_zero)) {
        std::cout << "Pass!" << std::endl;
    } else {
        std::cout << "Some tests failed." << std::endl;
    }
    return 0;
}
