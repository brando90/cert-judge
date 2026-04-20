/* Provides a class for rational numbers (Fractions).
   Sourced from Python's standard fractions library. */

#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <assert.h>
#include <stdbool.h>

/* -- Implementation -- */

typedef struct {
    int64_t numerator;
    int64_t denominator;
} Fraction;

static int64_t gcd(int64_t a, int64_t b) {
    if (a < 0) a = -a;
    if (b < 0) b = -b;
    while (b) { int64_t t = b; b = a % b; a = t; }
    return a;
}

Fraction fraction_create(int64_t numerator, int64_t denominator) {
    if (denominator == 0) {
        fprintf(stderr, "ZeroDivisionError: Fraction(%ld, 0)\n", (long)numerator);
        exit(1);
    }
    int64_t g = gcd(numerator, denominator);
    if (denominator < 0) g = -g;
    Fraction f;
    f.numerator = numerator / g;
    f.denominator = denominator / g;
    return f;
}

Fraction fraction_from_int(int64_t n) {
    Fraction f;
    f.numerator = n;
    f.denominator = 1;
    return f;
}

Fraction fraction_add(Fraction a, Fraction b) {
    return fraction_create(
        a.numerator * b.denominator + a.denominator * b.numerator,
        a.denominator * b.denominator
    );
}

Fraction fraction_sub(Fraction a, Fraction b) {
    return fraction_create(
        a.numerator * b.denominator - a.denominator * b.numerator,
        a.denominator * b.denominator
    );
}

Fraction fraction_mul(Fraction a, Fraction b) {
    return fraction_create(
        a.numerator * b.numerator,
        a.denominator * b.denominator
    );
}

Fraction fraction_div(Fraction a, Fraction b) {
    return fraction_create(
        a.numerator * b.denominator,
        a.denominator * b.numerator
    );
}

bool fraction_eq(Fraction a, Fraction b) {
    return a.numerator == b.numerator && a.denominator == b.denominator;
}

bool fraction_lt(Fraction a, Fraction b) {
    return a.numerator * b.denominator < a.denominator * b.numerator;
}

/* -- Tests -- */

int check(void) {
    /* 1. Normalization */
    Fraction f = fraction_create(8, 6);
    assert(f.numerator == 4 && f.denominator == 3);

    /* 2. Sign convention */
    f = fraction_create(10, -8);
    assert(f.numerator == -5 && f.denominator == 4);

    /* 3. Defaults */
    assert(fraction_eq(fraction_from_int(7), fraction_create(7, 1)));

    /* 4. Arithmetic */
    Fraction half = fraction_create(1, 2);
    Fraction third = fraction_create(1, 3);
    Fraction five_sixth = fraction_create(5, 6);
    assert(fraction_eq(fraction_add(half, third), five_sixth));

    Fraction two_third = fraction_create(2, 3);
    assert(fraction_eq(fraction_mul(half, two_third), third));
    assert(fraction_eq(fraction_div(half, fraction_create(3, 4)), two_third));

    Fraction quarter = fraction_create(1, 4);
    Fraction three_quarter = fraction_create(3, 4);
    assert(fraction_eq(fraction_sub(three_quarter, quarter), half));

    /* 5. Comparison */
    assert(fraction_lt(half, two_third));
    assert(!fraction_lt(half, half));
    assert(fraction_eq(half, fraction_create(2, 4)));

    return 1;
}

int main(void) {
    assert(check());
    printf("All tests passed.\n");
    return 0;
}
