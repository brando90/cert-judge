/*
 * Return the sample covariance of two inputs.
 * Positive covariance = variables move together. Negative = inverse.
 */
#include <stdio.h>
#include <stdlib.h>
#include <assert.h>
#include <math.h>

int pre_covariance(const double *x, int nx, const double *y, int ny) {
    return x != NULL && y != NULL && nx == ny && nx >= 2;
}

double covariance(const double *x, const double *y, int n, int *ok) {
    if (n < 2) { *ok = 0; return 0.0; }
    *ok = 1;
    double xbar = 0, ybar = 0;
    for (int i = 0; i < n; i++) { xbar += x[i]; ybar += y[i]; }
    xbar /= n; ybar /= n;
    double sxy = 0;
    for (int i = 0; i < n; i++) sxy += (x[i]-xbar)*(y[i]-ybar);
    return sxy / (n-1);
}

double benchmark_covariance(const double *x, int nx, const double *y, int ny, int *ok) {
    if (!pre_covariance(x, nx, y, ny)) { *ok = 0; return 0.0; }
    return covariance(x, y, nx, ok);
}

int check(void) {
    int ok;
    /* Basic */
    { double x[]={1,2,3,4,5,6,7,8,9}, y[]={1,2,3,1,2,3,1,2,3};
      double r = benchmark_covariance(x,9,y,9,&ok);
      assert(ok && fabs(r-0.75)<1e-9); }
    /* Negative */
    { double x[]={1,2,3,4,5,6,7,8,9}, z[]={9,8,7,6,5,4,3,2,1};
      assert(fabs(benchmark_covariance(x,9,z,9,&ok)-(-7.5))<1e-9 && ok); }
    /* Positive correlation */
    { double a[]={1,2,3,4,5}, b[]={2,4,6,8,10};
      assert(benchmark_covariance(a,5,b,5,&ok) > 0 && ok); }
    /* Negative correlation */
    { double a[]={1,2,3,4,5}, c[]={5,4,3,2,1};
      assert(benchmark_covariance(a,5,c,5,&ok) < 0 && ok); }
    /* Zero (constant y) */
    { double d[]={1,2,3,4,5}, e[]={3,3,3,3,3};
      assert(fabs(benchmark_covariance(d,5,e,5,&ok))<1e-9 && ok); }
    /* Two values */
    { double x[]={1,2}, y[]={3,4};
      assert(fabs(benchmark_covariance(x,2,y,2,&ok)-0.5)<1e-9 && ok); }
    /* Float */
    { double x[]={1.5,2.5,3.5}, y[]={2.0,3.0,4.0};
      assert(fabs(benchmark_covariance(x,3,y,3,&ok)-1.0)<1e-9 && ok); }
    /* cov(x,x) = var(x) */
    { double d[]={1,2,3,4,5};
      double cv = benchmark_covariance(d,5,d,5,&ok);
      double mean=3.0, var=0;
      for(int i=0;i<5;i++) var+=(d[i]-mean)*(d[i]-mean);
      var/=4; assert(fabs(cv-var)<1e-9 && ok); }
    /* Errors */
    { double x[]={1}, y[]={2}; benchmark_covariance(x,1,y,1,&ok); assert(!ok); }
    { double x[]={1,2,3}, y[]={4,5}; benchmark_covariance(x,3,y,2,&ok); assert(!ok); }
    return 1;
}

int main(void) { assert(check()); printf("All tests passed.\n"); return 0; }
