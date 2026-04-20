/* Return true if the string length is a prime number. */
#include <stdio.h>
#include <string.h>
#include <assert.h>
#include <stdbool.h>

bool prime_length(const char *string) {
    int l = strlen(string);
    if (l == 0 || l == 1) return false;
    for (int i = 2; i < l; i++) {
        if (l % i == 0) return false;
    }
    return true;
}

void check(void) {
    assert(prime_length("Hello") == true);
    assert(prime_length("abcdcba") == true);
    assert(prime_length("kittens") == true);
    assert(prime_length("orange") == false);
    assert(prime_length("wow") == true);
    assert(prime_length("world") == true);
    assert(prime_length("MadaM") == true);
    assert(prime_length("Wow") == true);
    assert(prime_length("") == false);
    assert(prime_length("HI") == true);
    assert(prime_length("go") == true);
    assert(prime_length("gogo") == false);
    assert(prime_length("aaaaaaaaaaaaaaa") == false);
    assert(prime_length("Madam") == true);
    assert(prime_length("M") == false);
    assert(prime_length("0") == false);
}

int main(void) {
    check();
    printf("All tests passed.\n");
    return 0;
}
