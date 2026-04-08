#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <assert.h>

/**
 * You're given a list of deposit and withdrawal operations on a bank account
 * that starts with zero balance.
 * Detect if at any point the balance falls below zero => return true.
 * Otherwise return false.
 */
bool below_zero(const int* operations, int length) {
    int balance = 0;
    for (int i = 0; i < length; i++) {
        balance += operations[i];
        if (balance < 0) {
            return true;
        }
    }
    return false;
}

/* Helper function to run tests */
bool check() {
    // 1) Original tests
    {
        int arr1[] = {};                          // empty
        assert(below_zero(arr1, 0) == false);
        
        int arr2[] = {1, 2, -3, 1, 2, -3};         // sum is 0 but never below 0
        assert(below_zero(arr2, 6) == false);
        
        int arr3[] = {1, 2, -4, 5, 6};
        assert(below_zero(arr3, 5) == true);
        
        int arr4[] = {1, -1, 2, -2, 5, -5, 4, -4};
        assert(below_zero(arr4, 8) == false);
        
        int arr5[] = {1, -1, 2, -2, 5, -5, 4, -5};
        assert(below_zero(arr5, 8) == true);
        
        int arr6[] = {1, -2, 2, -2, 5, -5, 4, -4};
        assert(below_zero(arr6, 8) == true);
    }

    // 2) Additional tests
    
    // Single negative operation => should be below zero immediately
    {
        int arr[] = {-5};
        assert(below_zero(arr, 1) == true);
    }
    
    // Single positive operation => never below zero
    {
        int arr[] = {5};
        assert(below_zero(arr, 1) == false);
    }
    
    // Balanced deposits => sum can be zero or positive, never below zero
    {
        int arr[] = {1, -1};
        assert(below_zero(arr, 2) == false);
    }
    
    // Goes below zero at the last operation
    {
        int arr[] = {5, -3, -3}; // final is -1
        assert(below_zero(arr, 3) == true);
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
