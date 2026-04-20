/* Product of all elements in a non-empty list of integers.
 *
 * Edge cases:
 * - Single-element list returns that element.
 * - Empty list is invalid (pre returns 0).
 */

#include <stdio.h>
#include <assert.h>
#include <stdint.h>

int pre_product_of_list(const int64_t *xs, int n) {
    (void)xs;
    return (n > 0);
}

int64_t product_of_list(const int64_t *xs, int n) {
    if (!pre_product_of_list(xs, n)) return 0; /* sentinel: 0 for error since product could be anything */
    int64_t result = 1;
    for (int i = 0; i < n; i++) {
        result *= xs[i];
    }
    return result;
}

int check(void) {
    {
        int64_t a[] = {2, 3, 4};
        assert(product_of_list(a, 3) == 24);
    }
    {
        int64_t a[] = {5};
        assert(product_of_list(a, 1) == 5);
    }
    assert(pre_product_of_list(NULL, 0) == 0);
    return 1;
}

int main(void) {
    assert(check());
    printf("All tests passed.\n");
    return 0;
}
