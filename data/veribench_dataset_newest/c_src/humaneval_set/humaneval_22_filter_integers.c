/* Filter given list of any values only for integers.
   In C, we simulate with a tagged union. */
#include <stdio.h>
#include <assert.h>
#include <stdint.h>

typedef enum { VAL_INT, VAL_FLOAT, VAL_STRING, VAL_OTHER } ValType;

typedef struct {
    ValType type;
    int64_t int_val;
} Value;

/* Returns count of integers found. Results in out array. */
int filter_integers(Value *values, int n, int64_t *out) {
    int count = 0;
    for (int i = 0; i < n; i++) {
        if (values[i].type == VAL_INT) {
            out[count++] = values[i].int_val;
        }
    }
    return count;
}

void check(void) {
    int64_t out[20];
    int n;

    n = filter_integers(NULL, 0, out);
    assert(n == 0);

    {
        /* [4, {}, [], 23.2, 9, 'adasd'] */
        Value a[] = {
            {VAL_INT, 4}, {VAL_OTHER, 0}, {VAL_OTHER, 0},
            {VAL_FLOAT, 0}, {VAL_INT, 9}, {VAL_STRING, 0}
        };
        n = filter_integers(a, 6, out);
        assert(n == 2);
        assert(out[0] == 4 && out[1] == 9);
    }

    {
        /* [3, 'c', 3, 3, 'a', 'b'] */
        Value a[] = {
            {VAL_INT, 3}, {VAL_STRING, 0}, {VAL_INT, 3},
            {VAL_INT, 3}, {VAL_STRING, 0}, {VAL_STRING, 0}
        };
        n = filter_integers(a, 6, out);
        assert(n == 3);
        assert(out[0] == 3 && out[1] == 3 && out[2] == 3);
    }
}

int main(void) {
    check();
    printf("All tests passed.\n");
    return 0;
}
