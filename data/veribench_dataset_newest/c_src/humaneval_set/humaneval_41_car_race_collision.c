/* Return the number of collisions: n^2. */
#include <stdio.h>
#include <assert.h>
#include <stdint.h>

int64_t car_race_collision(int64_t n) {
    return n * n;
}

void check(void) {
    assert(car_race_collision(2) == 4);
    assert(car_race_collision(3) == 9);
    assert(car_race_collision(4) == 16);
    assert(car_race_collision(8) == 64);
    assert(car_race_collision(10) == 100);
}

int main(void) {
    check();
    printf("All tests passed.\n");
    return 0;
}
