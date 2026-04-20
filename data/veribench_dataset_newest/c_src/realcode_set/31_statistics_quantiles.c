/*
 * Divide data into n continuous intervals with equal probability.
 * Returns (n-1) cut points. n=4 for quartiles, 10 for deciles, 100 for percentiles.
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <assert.h>
#include <math.h>

int pre_quantiles(const double *data, int len, int n, int method) {
    return data != NULL && len >= 2 && n >= 1 && (method == 0 || method == 1);
}

static int cmp_d(const void *a, const void *b) {
    double da = *(const double *)a, db = *(const double *)b;
    return (da > db) - (da < db);
}

/* method: 0=exclusive, 1=inclusive. Returns count of cut points written to out. */
int quantiles(const double *data, int ld, int n, int method, double *out) {
    if (n < 1 || ld < 2) return 0;
    double *s = (double *)malloc((size_t)ld * sizeof(double));
    memcpy(s, data, (size_t)ld * sizeof(double));
    qsort(s, (size_t)ld, sizeof(double), cmp_d);
    int cnt = 0;
    if (method == 1) { /* inclusive */
        int m = ld - 1;
        for (int i = 1; i < n; i++) {
            int j = (i*m)/n, delta = (i*m)%n;
            out[cnt++] = (s[j]*(n-delta) + s[j+1]*delta) / (double)n;
        }
    } else { /* exclusive */
        int m = ld + 1;
        for (int i = 1; i < n; i++) {
            int j = (i*m)/n;
            if (j < 1) j = 1; if (j > ld-1) j = ld-1;
            int delta = i*m - j*n;
            out[cnt++] = (s[j-1]*(n-delta) + s[j]*delta) / (double)n;
        }
    }
    free(s);
    return cnt;
}

int benchmark_quantiles(const double *data, int len, int n, int method, double *out) {
    if (!pre_quantiles(data, len, n, method)) return 0;
    return quantiles(data, len, n, method, out);
}

int check(void) {
    double out[100]; int c;
    /* Quartiles exclusive */
    { double d[]={1,2,3,4}; c=benchmark_quantiles(d,4,4,0,out);
      assert(c==3 && fabs(out[0]-1.25)<1e-9 && fabs(out[1]-2.5)<1e-9 && fabs(out[2]-3.75)<1e-9); }
    /* Deciles */
    { double d[]={0,1,2,3,4,5,6,7,8,9,10}; c=benchmark_quantiles(d,11,10,0,out); assert(c==9); }
    /* Median n=2 */
    { double d[]={1,2,3,4,5}; c=benchmark_quantiles(d,5,2,0,out); assert(c==1 && fabs(out[0]-3.0)<1e-9); }
    /* Inclusive */
    { double d[]={1,2,3,4}; c=benchmark_quantiles(d,4,4,1,out);
      assert(c==3 && fabs(out[0]-1.75)<1e-9 && fabs(out[1]-2.5)<1e-9 && fabs(out[2]-3.25)<1e-9); }
    /* Unsorted */
    { double d[]={4,1,3,2}; c=benchmark_quantiles(d,4,4,0,out); assert(c==3); }
    /* Float */
    { double d[]={1.5,2.5,3.5,4.5}; c=benchmark_quantiles(d,4,2,0,out); assert(c==1 && fabs(out[0]-3.0)<1e-9); }
    /* Errors */
    { double d[]={1}; assert(benchmark_quantiles(d,1,4,0,out)==0); }
    { double d[]={1,2}; assert(benchmark_quantiles(d,2,0,0,out)==0); }
    { double d[]={1,2,3}; assert(benchmark_quantiles(d,3,4,2,out)==0); }
    return 1;
}

int main(void) { assert(check()); printf("All tests passed.\n"); return 0; }
