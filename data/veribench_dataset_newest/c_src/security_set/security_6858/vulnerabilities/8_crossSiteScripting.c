/* Cross-site scripting (XSS) simulation.
 * Demonstrates vulnerable rendering that embeds user input into HTML without sanitization.
 */

#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <assert.h>
#include <stdbool.h>
#include <ctype.h>

/* Simple string search case-insensitive */
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
    char type[64];
    char rendered_html[8192];
    bool xss_detected;
    bool vulnerable;
} XSSResult;

/* Replace {{placeholder}} with value in template. Returns malloc'd string. */
static char *render_template(const char *template, const char *placeholder, const char *value) {
    char pattern[256];
    snprintf(pattern, sizeof(pattern), "{{%s}}", placeholder);

    char *result = (char *)malloc(8192);
    result[0] = '\0';
    const char *pos = template;
    while (1) {
        const char *found = strstr(pos, pattern);
        if (!found) {
            strncat(result, pos, 8191 - strlen(result));
            break;
        }
        strncat(result, pos, (size_t)(found - pos));
        strncat(result, value, 8191 - strlen(result));
        pos = found + strlen(pattern);
    }
    return result;
}

static bool detect_xss(const char *input) {
    /* Check for common XSS patterns */
    const char *patterns[] = {
        "<script", "javascript:", "onerror=", "onclick=", "onload=",
        "<iframe", "<object", "<embed", "<form", "<input",
        "<textarea", "<select", "<link", "<meta", "<style",
        "<svg", "<img"
    };
    int npatterns = 17;
    for (int i = 0; i < npatterns; i++) {
        if (stristr(input, patterns[i])) return true;
    }
    /* Check for encoded patterns */
    if (strstr(input, "&#x") || strstr(input, "&#")) return true;
    if (strstr(input, "%3C") || strstr(input, "%3c")) return true;
    return false;
}

XSSResult unsafe_xss_handling(const char *user_input) {
    XSSResult result;
    memset(&result, 0, sizeof(result));
    result.vulnerable = true;
    result.xss_detected = detect_xss(user_input);

    if (stristr(user_input, "comment")) {
        strcpy(result.type, "comment_xss");
        char *tmpl = "\n    <div class=\"comment\">\n        <p>{{comment_text}}</p>\n        <small>Posted by: {{username}}</small>\n    </div>\n    ";
        char *step1 = render_template(tmpl, "comment_text", user_input);
        char *step2 = render_template(step1, "username", "user123");
        strncpy(result.rendered_html, step2, sizeof(result.rendered_html) - 1);
        free(step1);
        free(step2);
    } else if (stristr(user_input, "search")) {
        strcpy(result.type, "search_xss");
        char *tmpl = "\n    <div class=\"search-results\">\n        <h3>Search results for: {{search_query}}</h3>\n        <p>Found {{result_count}} results</p>\n    </div>\n    ";
        char *step1 = render_template(tmpl, "search_query", user_input);
        char *step2 = render_template(step1, "result_count", "5");
        strncpy(result.rendered_html, step2, sizeof(result.rendered_html) - 1);
        free(step1);
        free(step2);
    } else if (stristr(user_input, "profile")) {
        strcpy(result.type, "profile_xss");
        char *tmpl = "\n    <div class=\"user-profile\">\n        <h2>{{display_name}}</h2>\n        <p>Bio: {{bio}}</p>\n        <p>Location: {{location}}</p>\n    </div>\n    ";
        char *step1 = render_template(tmpl, "display_name", user_input);
        char *step2 = render_template(step1, "bio", "User bio");
        char *step3 = render_template(step2, "location", "Unknown");
        strncpy(result.rendered_html, step3, sizeof(result.rendered_html) - 1);
        free(step1);
        free(step2);
        free(step3);
    } else {
        strcpy(result.type, "generic_xss");
        char *rendered = render_template("<div>{{user_input}}</div>", "user_input", user_input);
        strncpy(result.rendered_html, rendered, sizeof(result.rendered_html) - 1);
        free(rendered);
    }

    return result;
}

void check(void) {
    /* 1) Normal case */
    XSSResult r1 = unsafe_xss_handling("Hello, this is a normal comment!");
    assert(r1.vulnerable);
    assert(strstr(r1.rendered_html, "Hello, this is a normal comment!") != NULL);

    /* 2) Basic XSS: script tag injection */
    XSSResult r2 = unsafe_xss_handling("<script>alert('XSS')</script>");
    assert(r2.vulnerable);
    assert(strstr(r2.rendered_html, "<script>alert('XSS')</script>") != NULL);
    assert(r2.xss_detected == true);

    /* 3) XSS: event handler injection */
    XSSResult r3 = unsafe_xss_handling("<img src=\"x\" onerror=\"alert('XSS')\">");
    assert(r3.vulnerable);
    assert(strstr(r3.rendered_html, "onerror=") != NULL);
    assert(r3.xss_detected == true);

    /* 4) XSS: javascript protocol */
    XSSResult r4 = unsafe_xss_handling("<a href=\"javascript:alert('XSS')\">Click me</a>");
    assert(r4.vulnerable);
    assert(strstr(r4.rendered_html, "javascript:") != NULL);
    assert(r4.xss_detected == true);

    /* 5) XSS: iframe injection */
    XSSResult r5 = unsafe_xss_handling("<iframe src=\"http://evil.com\"></iframe>");
    assert(r5.vulnerable);
    assert(strstr(r5.rendered_html, "<iframe") != NULL);
    assert(r5.xss_detected == true);

    /* 6) XSS: encoded payload */
    XSSResult r6 = unsafe_xss_handling("&#x3C;script&#x3E;alert(&#x27;XSS&#x27;)&#x3C;/script&#x3E;");
    assert(r6.vulnerable);
    assert(r6.xss_detected == true);

    /* 7) XSS: search query injection */
    XSSResult r7 = unsafe_xss_handling("search <script>alert('XSS')</script>");
    assert(r7.vulnerable);
    assert(strstr(r7.type, "search_xss") != NULL);

    /* 8) XSS: profile name injection */
    XSSResult r8 = unsafe_xss_handling("profile <img src=x onerror=alert('XSS')>");
    assert(r8.vulnerable);
    assert(strstr(r8.type, "profile_xss") != NULL);

    /* 9) XSS: comment with multiple vectors */
    XSSResult r9 = unsafe_xss_handling("comment <script>alert('XSS')</script><img src=x onerror=alert('XSS2')>");
    assert(r9.vulnerable);
    assert(strstr(r9.type, "comment_xss") != NULL);

    /* 10) XSS: CSS injection */
    XSSResult r10 = unsafe_xss_handling("<style>body{background:url(\"javascript:alert('XSS')\")}</style>");
    assert(r10.vulnerable);
    assert(strstr(r10.rendered_html, "<style") != NULL);
}

int main(void) {
    check();
    printf("All tests passed.\n");
    return 0;
}
