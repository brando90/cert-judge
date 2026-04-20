/* Provides partial function application.
   Sourced from Python's standard functools library.
   NOTE: simplified from Python version -- uses a struct to store partial application state
   for a specific function signature (int64_t, int64_t, int64_t) -> int64_t. */

#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <assert.h>
#include <stdbool.h>

/* -- Implementation -- */

typedef int64_t (*Func3)(int64_t, int64_t, int64_t);

#define PARTIAL_UNSET INT64_MIN  /* sentinel for unbound argument */

typedef struct {
    Func3 func;
    int64_t arg_a;     /* first positional arg or PARTIAL_UNSET */
    int64_t arg_b;     /* second positional arg or PARTIAL_UNSET */
    int64_t arg_c;     /* keyword arg 'c' or PARTIAL_UNSET */
    bool a_set;
    bool b_set;
    bool c_set;
} Partial;

void partial_init(Partial *p, Func3 func) {
    p->func = func;
    p->arg_a = 0;
    p->arg_b = 0;
    p->arg_c = 0;
    p->a_set = false;
    p->b_set = false;
    p->c_set = false;
}

void partial_set_a(Partial *p, int64_t val) { p->arg_a = val; p->a_set = true; }
void partial_set_b(Partial *p, int64_t val) { p->arg_b = val; p->b_set = true; }
void partial_set_c(Partial *p, int64_t val) { p->arg_c = val; p->c_set = true; }

/* Call with remaining args. Unset args must be provided. */
int64_t partial_call(Partial *p, int64_t extra1, int64_t extra2, int64_t extra3,
                     bool has1, bool has2, bool has3) {
    int64_t a = p->a_set ? p->arg_a : (has1 ? extra1 : 0);
    int64_t b = p->b_set ? p->arg_b : 0;
    int64_t c = p->c_set ? p->arg_c : 0;

    /* Fill unset positional args from extras in order */
    int ext_idx = 0;
    int64_t extras[] = {extra1, extra2, extra3};
    bool has_extras[] = {has1, has2, has3};

    if (!p->a_set) {
        if (ext_idx < 3 && has_extras[ext_idx]) { a = extras[ext_idx]; ext_idx++; }
    }
    if (!p->b_set) {
        if (ext_idx < 3 && has_extras[ext_idx]) { b = extras[ext_idx]; ext_idx++; }
    }
    if (!p->c_set) {
        if (ext_idx < 3 && has_extras[ext_idx]) { c = extras[ext_idx]; ext_idx++; }
    }

    return p->func(a, b, c);
}

/* -- Tests -- */

static int64_t test_func(int64_t a, int64_t b, int64_t c) {
    return a * 100 + b * 10 + c;
}

int check(void) {
    /* p1 = partial(test_func, 1, 2) -> p1(3) = 123 */
    Partial p1;
    partial_init(&p1, test_func);
    partial_set_a(&p1, 1);
    partial_set_b(&p1, 2);
    assert(partial_call(&p1, 3, 0, 0, true, false, false) == 123);

    /* p2 = partial(test_func, b=2, c=3) -> p2(1) = 123 */
    Partial p2;
    partial_init(&p2, test_func);
    partial_set_b(&p2, 2);
    partial_set_c(&p2, 3);
    assert(partial_call(&p2, 1, 0, 0, true, false, false) == 123);

    /* p3 = partial(test_func, 1, b=2) -> p3(c=3) = 123 */
    Partial p3;
    partial_init(&p3, test_func);
    partial_set_a(&p3, 1);
    partial_set_b(&p3, 2);
    partial_set_c(&p3, 3);
    assert(partial_call(&p3, 0, 0, 0, false, false, false) == 123);

    return 1;
}

int main(void) {
    assert(check());
    printf("All tests passed.\n");
    return 0;
}
