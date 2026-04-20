/*
 * Return the low median of numeric data.
 * When odd count, middle value. When even, smaller of two middle values.
 */
#include <stdio.h>
#include <stdlib.h>
#include <assert.h>

int pre_median_low(const double *data, int n) { return data != NULL && n > 0; }

static int cmp_double(const void *a, const void *b) {
    double da = *(const double *)a, db = *(const double *)b;
    return (da > db) - (da < db);
}

/* Returns low median. Sets *ok=0 on error. */
double median_low(const double *data, int n, int *ok) {
    if (n == 0) { *ok = 0; return 0.0; }
    *ok = 1;
    double *s = (double *)malloc((size_t)n * sizeof(double));
    for (int i = 0; i < n; i++) s[i] = data[i];
    qsort(s, (size_t)n, sizeof(double), cmp_double);
    double r = (n % 2 == 1) ? s[n/2] : s[n/2 - 1];
    free(s);
    return r;
}

double benchmark_median_low(const double *data, int n, int *ok) {
    if (!pre_median_low(data, n)) { *ok = 0; return 0.0; }
    return median_low(data, n, ok);
}

int check(void) {
    int ok;
    { double d[] = {1,3,5}; assert(benchmark_median_low(d,3,&ok)==3 && ok); }
    { double d[] = {1,2,3,4,5,6,9}; assert(benchmark_median_low(d,7,&ok)==4 && ok); }
    { double d[] = {1,3,5,7}; assert(benchmark_median_low(d,4,&ok)==3 && ok); }
    { double d[] = {1,2,3,4,5,6}; assert(benchmark_median_low(d,6,&ok)==3 && ok); }
    { double d[] = {42}; assert(benchmark_median_low(d,1,&ok)==42 && ok); }
    { double d[] = {10,20}; assert(benchmark_median_low(d,2,&ok)==10 && ok); }
    { double d[] = {9,1,6,2,5,4,3}; assert(benchmark_median_low(d,7,&ok)==4 && ok); }
    { double d[] = {-5,-1,0,3,7}; assert(benchmark_median_low(d,5,&ok)==0 && ok); }
    { double d[] = {-10,-5,5,10}; assert(benchmark_median_low(d,4,&ok)==-5 && ok); }
    benchmark_median_low(NULL, 0, &ok); assert(ok == 0);
    return 1;
}

int main(void) { assert(check()); printf("All tests passed.\n"); return 0; }
