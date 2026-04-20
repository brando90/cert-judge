/* Given a positive floating point number, return the decimal part. */
#include <stdio.h>
#include <assert.h>
#include <math.h>

double truncate_number(double number) {
    return fmod(number, 1.0);
}

void check(void) {
    assert(truncate_number(3.5) == 0.5);
    assert(fabs(truncate_number(1.33) - 0.33) < 1e-6);
    assert(fabs(truncate_number(123.456) - 0.456) < 1e-6);
}

int main(void) {
    check();
    printf("All tests passed.\n");
    return 0;
}
