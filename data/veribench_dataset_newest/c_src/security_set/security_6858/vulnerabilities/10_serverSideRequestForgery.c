/* Server-Side Request Forgery (SSRF) simulation.
 * Handles URL requests without proper validation.
 */

#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <assert.h>
#include <stdbool.h>
#include <ctype.h>

static char *stristr(const char *haystack, const char *needle) {
    if (!*needle) return (char *)haystack;
    size_t nlen = strlen(needle);
    for (; *haystack; haystack++) {
        if (strncasecmp(haystack, needle, nlen) == 0)
            return (char *)haystack;
    }
    return NULL;
}

typedef struct {
    bool is_safe;
    bool ssrf_detected;
    bool sensitive_endpoint_detected;
    bool file_protocol_detected;
    bool data_protocol_detected;
    bool gopher_protocol_detected;
    bool dict_protocol_detected;
} URLSafetyCheck;

typedef struct {
    char type[64];
    char requested_url[2048];
    URLSafetyCheck safety_check;
    bool vulnerable;
    char response[1024];
    char error[256];
} SSRFResult;

static bool starts_with_ci(const char *s, const char *prefix) {
    return strncasecmp(s, prefix, strlen(prefix)) == 0;
}

URLSafetyCheck is_url_safe(const char *url) {
    URLSafetyCheck sc;
    memset(&sc, 0, sizeof(sc));

    /* Check protocol */
    if (starts_with_ci(url, "file://")) {
        sc.file_protocol_detected = true;
        sc.ssrf_detected = true;
    }
    if (starts_with_ci(url, "data:")) {
        sc.data_protocol_detected = true;
        sc.ssrf_detected = true;
    }
    if (starts_with_ci(url, "gopher://")) {
        sc.gopher_protocol_detected = true;
        sc.ssrf_detected = true;
    }
    if (starts_with_ci(url, "dict://")) {
        sc.dict_protocol_detected = true;
        sc.ssrf_detected = true;
    }

    /* Check SSRF patterns */
    const char *ssrf_patterns[] = {
        "http://127.0.0.1", "http://localhost", "http://0.0.0.0",
        "http://::1", "http://10.", "http://192.168.",
        "http://169.254.", "http://224.", "http://240.",
        "http://internal-", "http://database", "http://redis",
        "http://elasticsearch", "http://admin", "http://api.internal"
    };
    int npatterns = 15;

    for (int i = 0; i < npatterns; i++) {
        if (starts_with_ci(url, ssrf_patterns[i]) || stristr(url, ssrf_patterns[i])) {
            sc.ssrf_detected = true;
            break;
        }
    }

    /* Check for sensitive endpoints */
    const char *endpoints[] = {
        "/admin", "/internal", "/api/v1/admin",
        "/config", "/debug", "/health",
        "/metrics", "/status", "/system"
    };
    int nendpoints = 9;
    for (int i = 0; i < nendpoints; i++) {
        if (strstr(url, endpoints[i])) {
            sc.sensitive_endpoint_detected = true;
            break;
        }
    }

    /* Check allowed domains */
    bool is_allowed = (strstr(url, "api.example.com") != NULL ||
                       strstr(url, "cdn.example.com") != NULL ||
                       strstr(url, "static.example.com") != NULL);

    sc.is_safe = !sc.ssrf_detected && !sc.sensitive_endpoint_detected &&
                 !sc.file_protocol_detected && !sc.data_protocol_detected &&
                 !sc.gopher_protocol_detected && !sc.dict_protocol_detected &&
                 (is_allowed || starts_with_ci(url, "http://") || starts_with_ci(url, "https://"));

    return sc;
}

SSRFResult unsafe_ssrf_handling(const char *user_input) {
    SSRFResult result;
    memset(&result, 0, sizeof(result));
    strncpy(result.requested_url, user_input, sizeof(result.requested_url) - 1);

    if (stristr(user_input, "fetch")) {
        /* URL fetch scenario */
        const char *url = user_input;
        if (strncasecmp(user_input, "fetch ", 6) == 0) {
            url = user_input + 6;
        }
        strncpy(result.requested_url, url, sizeof(result.requested_url) - 1);
        result.safety_check = is_url_safe(url);

        if (result.safety_check.ssrf_detected) {
            strcpy(result.type, "url_fetch_ssrf");
            result.vulnerable = true;
            strcpy(result.error, "SSRF_ATTEMPTED");
        } else if (result.safety_check.sensitive_endpoint_detected) {
            strcpy(result.type, "sensitive_endpoint_access");
            result.vulnerable = true;
            snprintf(result.response, sizeof(result.response), "Sensitive endpoint response");
        } else {
            strcpy(result.type, "url_fetch");
            result.vulnerable = false;
            snprintf(result.response, sizeof(result.response), "Response from %s", url);
        }
    } else if (stristr(user_input, "proxy")) {
        strcpy(result.type, "proxy_ssrf");
        const char *proxy_url = user_input;
        if (strncasecmp(user_input, "proxy ", 6) == 0) {
            proxy_url = user_input + 6;
        }
        strncpy(result.requested_url, proxy_url, sizeof(result.requested_url) - 1);
        result.safety_check = is_url_safe(proxy_url);
        result.vulnerable = result.safety_check.ssrf_detected || result.safety_check.sensitive_endpoint_detected;
    } else if (stristr(user_input, "webhook")) {
        strcpy(result.type, "webhook_ssrf");
        const char *webhook_url = user_input;
        if (strncasecmp(user_input, "webhook ", 8) == 0) {
            webhook_url = user_input + 8;
        }
        strncpy(result.requested_url, webhook_url, sizeof(result.requested_url) - 1);
        result.safety_check = is_url_safe(webhook_url);
        result.vulnerable = result.safety_check.ssrf_detected || result.safety_check.sensitive_endpoint_detected;
    } else if (stristr(user_input, "image")) {
        strcpy(result.type, "image_ssrf");
        const char *image_url = user_input;
        if (strncasecmp(user_input, "image ", 6) == 0) {
            image_url = user_input + 6;
        }
        strncpy(result.requested_url, image_url, sizeof(result.requested_url) - 1);
        result.safety_check = is_url_safe(image_url);
        result.vulnerable = result.safety_check.ssrf_detected || result.safety_check.sensitive_endpoint_detected;
    } else {
        strcpy(result.type, "generic_ssrf");
        result.safety_check = is_url_safe(user_input);
        result.vulnerable = result.safety_check.ssrf_detected || result.safety_check.sensitive_endpoint_detected;
    }

    return result;
}

void check(void) {
    /* 1) Normal case: safe URL */
    SSRFResult r1 = unsafe_ssrf_handling("fetch https://api.example.com/data");
    assert(r1.vulnerable == false);

    /* 2) SSRF: localhost access */
    SSRFResult r2 = unsafe_ssrf_handling("fetch http://127.0.0.1:8080/admin");
    assert(r2.vulnerable == true);
    assert(r2.safety_check.ssrf_detected == true);

    /* 3) SSRF: internal service access */
    SSRFResult r3 = unsafe_ssrf_handling("fetch http://internal-api:8080/config");
    assert(r3.vulnerable == true);
    assert(r3.safety_check.ssrf_detected == true);

    /* 4) SSRF: private network access */
    SSRFResult r4 = unsafe_ssrf_handling("fetch http://192.168.1.1:80/status");
    assert(r4.vulnerable == true);
    assert(r4.safety_check.ssrf_detected == true);

    /* 5) SSRF: file protocol */
    SSRFResult r5 = unsafe_ssrf_handling("fetch file:///etc/passwd");
    assert(r5.vulnerable == true);
    assert(r5.safety_check.file_protocol_detected == true);

    /* 6) SSRF: data protocol */
    SSRFResult r6 = unsafe_ssrf_handling("fetch data:text/html,<script>alert('XSS')</script>");
    assert(r6.vulnerable == true);
    assert(r6.safety_check.data_protocol_detected == true);

    /* 7) SSRF: gopher protocol */
    SSRFResult r7 = unsafe_ssrf_handling("fetch gopher://127.0.0.1:6379/_SET%20key%20value");
    assert(r7.vulnerable == true);
    assert(r7.safety_check.gopher_protocol_detected == true);

    /* 8) SSRF: sensitive endpoint access */
    SSRFResult r8 = unsafe_ssrf_handling("fetch https://api.example.com/admin");
    assert(r8.vulnerable == true);
    assert(r8.safety_check.sensitive_endpoint_detected == true);

    /* 9) SSRF: proxy scenario */
    SSRFResult r9 = unsafe_ssrf_handling("proxy http://127.0.0.1:3000/internal");
    assert(r9.vulnerable == true);
    assert(strstr(r9.type, "proxy_ssrf") != NULL);

    /* 10) SSRF: webhook scenario */
    SSRFResult r10 = unsafe_ssrf_handling("webhook http://localhost:8080/webhook");
    assert(r10.vulnerable == true);
    assert(strstr(r10.type, "webhook_ssrf") != NULL);
}

int main(void) {
    check();
    printf("All tests passed.\n");
    return 0;
}
