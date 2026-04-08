// Filename: humaneval_0_hasCloseElements.cpp

#include <iostream>
#include <vector>
#include <cmath>
#include <cassert>

using namespace std;

bool has_close_elements(const vector<double>& numbers, double threshold) {
    /**
     * Check if in given list of numbers, any two numbers are closer to each other
     * than the given threshold.
     */
    for (size_t i = 0; i < numbers.size(); ++i) {
        for (size_t j = 0; j < numbers.size(); ++j) {
            if (i != j) {
                double distance = fabs(numbers[i] - numbers[j]);
                if (distance < threshold) {
                    return true;
                }
            }
        }
    }
    return false;
}

bool check(bool (*candidate)(const vector<double>&, double)) {
    // Original tests
    assert(candidate({1.0, 2.0, 3.9, 4.0, 5.0, 2.2}, 0.3) == true);
    assert(candidate({1.0, 2.0, 3.9, 4.0, 5.0, 2.2}, 0.05) == false);
    assert(candidate({1.0, 2.0, 5.9, 4.0, 5.0}, 0.95) == true);
    assert(candidate({1.0, 2.0, 5.9, 4.0, 5.0}, 0.8) == false);
    assert(candidate({1.0, 2.0, 3.0, 4.0, 5.0, 2.0}, 0.1) == true);
    assert(candidate({1.1, 2.2, 3.1, 4.1, 5.1}, 1.0) == true);
    assert(candidate({1.1, 2.2, 3.1, 4.1, 5.1}, 0.5) == false);

    // Additional tests
    assert(candidate({}, 0.1) == false);                           // Empty list
    assert(candidate({1.5}, 0.1) == false);                        // Single element
    assert(candidate({3.14, 3.14}, 0.1) == true);                  // Identical elements, threshold > 0
    assert(candidate({3.14, 3.14}, 0.0) == false);                 // Identical elements, threshold == 0
    assert(candidate({100, 200}, 999.9) == true);                  // Large threshold
    assert(candidate({1.0, 1.00000001}, 1e-5) == true);            // Close distinct elements
    assert(candidate({1.0, 1.0002}, 1e-5) == false);               // Not close distinct elements

    return true;
}

int main() {
    if (check(has_close_elements)) {
        cout << "Pass!" << endl;
    } else {
        cout << "Some tests failed." << endl;
    }
    return 0;
}
