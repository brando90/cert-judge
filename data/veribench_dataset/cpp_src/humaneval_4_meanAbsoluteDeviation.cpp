#include <iostream>
#include <vector>
#include <cmath>
#include <cassert>

double mean_absolute_deviation(const std::vector<double>& numbers) {
    /**
     * For a given list of input numbers, calculate Mean Absolute Deviation around
     * the mean of this dataset:
     *
     *   MAD = average of | x - mean(x) |
     *
     * numbers is assumed non-empty in this context.
     */
    double sum = 0.0;
    for (double val : numbers) {
        sum += val;
    }
    double mean_val = sum / numbers.size();

    double total_dev = 0.0;
    for (double val : numbers) {
        total_dev += std::fabs(val - mean_val);
    }
    return total_dev / numbers.size();
}

bool check(double (*candidate)(const std::vector<double>&)) {
    // Helper lambda to check closeness
    auto almost_equal = [](double a, double b, double tol) {
        return std::fabs(a - b) < tol;
    };

    // Original tests
    assert(almost_equal(candidate({1.0, 2.0, 3.0}), 2.0 / 3.0, 1e-6));
    assert(almost_equal(candidate({1.0, 2.0, 3.0, 4.0}), 1.0, 1e-6));
    assert(almost_equal(candidate({1.0, 2.0, 3.0, 4.0, 5.0}), 6.0 / 5.0, 1e-6));

    // Additional tests:

    // 1. Single element -> MAD = 0
    assert(almost_equal(candidate({42.0}), 0.0, 1e-9));

    // 2. All elements the same -> MAD = 0
    assert(almost_equal(candidate({5.0, 5.0, 5.0, 5.0}), 0.0, 1e-9));

    // 3. Larger dataset => [10, 20, 30, 40, 50]
    //    mean = 30 => deviations=[20,10,0,10,20] => average=12
    assert(almost_equal(candidate({10.0, 20.0, 30.0, 40.0, 50.0}), 12.0, 1e-6));

    // 4. Very small differences
    //    nums_small = [1.000001, 1.000002, 1.000003]
    //    mean ~ 1.000002 => deviations ~ [1e-6, 0, 1e-6] => sum=2e-6 => avg= ~6.6667e-7
    //    We'll compare with 0.0000006666667 within 1e-9
    std::vector<double> nums_small = {1.000001, 1.000002, 1.000003};
    double expected_small = 0.0000006666667; // ~6.666667e-7
    assert(almost_equal(candidate(nums_small), expected_small, 1e-9));

    return true;
}

int main() {
    if (check(mean_absolute_deviation)) {
        std::cout << "Pass!" << std::endl;
    } else {
        std::cout << "Some tests failed." << std::endl;
    }
    return 0;
}
