/* Safe SSRF handling with URL validation.
 */

#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <assert.h>
#include <stdbool.h>

typedef struct {
    char error[256];
    char url[2048];
    bool safe;
} SSRFResult;

static bool starts_with_ci(const char *s, const char *prefix) {
    return strncasecmp(s, prefix, strlen(prefix)) == 0;
}

static bool is_url_safe(const char *url) {
    /* Only allow http/https */
    if (!starts_with_ci(url, "http://") && !starts_with_ci(url, "https://")) {
        return false;
    }

    /* Block localhost/private ranges */
    const char *blocked[] = {
        "http://127.", "http://localhost", "http://0.0.0.0",
        "http://10.", "http://192.168.", "http://169.254.",
        "https://127.", "https://localhost", "https://0.0.0.0",
        "https://10.", "https://192.168.", "https://169.254."
    };
    for (int i = 0; i < 12; i++) {
        if (starts_with_ci(url, blocked[i])) return false;
    }

    /* Allow only whitelisted domains */
    const char *allowed[] = {"api.example.com", "cdn.example.com", "static.example.com"};
    for (int i = 0; i < 3; i++) {
        if (strstr(url, allowed[i])) return true;
    }
    return false;
}

SSRFResult safe_ssrf_handling(const char *user_input) {
    SSRFResult result;
    memset(&result, 0, sizeof(result));

    if (!is_url_safe(user_input)) {
        strcpy(result.error, "SSRF_DETECTED");
        result.safe = false;
        return result;
    }

    strncpy(result.url, user_input, sizeof(result.url) - 1);
    result.safe = true;
    return result;
}

void check(void) {
    SSRFResult r1 = safe_ssrf_handling("https://api.example.com/data");
    assert(r1.safe == true);

    const char *bad_urls[] = {
        "http://127.0.0.1:8080/admin",
        "http://localhost:8080/internal",
        "file:///etc/passwd",
        "gopher://127.0.0.1/",
        "http://192.168.1.1/status"
    };
    for (int i = 0; i < 5; i++) {
        SSRFResult r = safe_ssrf_handling(bad_urls[i]);
        assert(r.safe == false);
        assert(strlen(r.error) > 0);
    }
}

int main(void) {
    check();
    printf("All tests passed.\n");
    return 0;
}
