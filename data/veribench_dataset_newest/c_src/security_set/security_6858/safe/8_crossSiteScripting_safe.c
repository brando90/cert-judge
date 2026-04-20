/* Safe rendering that escapes user input to prevent XSS.
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <assert.h>
#include <stdbool.h>

/* HTML-escape a string. Returns malloc'd string. Caller must free. */
static char *html_escape(const char *input) {
    /* Worst case: every char becomes 6 chars (&quot;) */
    size_t len = strlen(input);
    char *result = (char *)malloc(len * 6 + 1);
    if (!result) { perror("malloc"); exit(1); }
    char *p = result;
    for (size_t i = 0; i < len; i++) {
        switch (input[i]) {
            case '<':  memcpy(p, "&lt;", 4);   p += 4; break;
            case '>':  memcpy(p, "&gt;", 4);   p += 4; break;
            case '&':  memcpy(p, "&amp;", 5);  p += 5; break;
            case '"':  memcpy(p, "&quot;", 6); p += 6; break;
            case '\'': memcpy(p, "&#x27;", 6); p += 6; break;
            default:   *p++ = input[i]; break;
        }
    }
    *p = '\0';
    return result;
}

/* Replace {{placeholder}} with value in template. Returns malloc'd string. */
static char *render_template(const char *tmpl, const char *placeholder, const char *value) {
    char pattern[256];
    snprintf(pattern, sizeof(pattern), "{{%s}}", placeholder);

    char *result = (char *)malloc(8192);
    if (!result) { perror("malloc"); exit(1); }
    result[0] = '\0';
    const char *pos = tmpl;
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

typedef struct {
    char rendered_html[8192];
    bool vulnerable;
} XSSResult;

XSSResult safe_xss_handling(const char *user_input) {
    XSSResult result;
    memset(&result, 0, sizeof(result));
    result.vulnerable = false;

    /* Escape user input */
    char *escaped = html_escape(user_input);

    const char *tmpl = "\n    <div class=\"comment\">\n        <p>{{comment_text}}</p>\n        <small>Posted by: {{username}}</small>\n    </div>\n    ";
    char *step1 = render_template(tmpl, "comment_text", escaped);
    char *step2 = render_template(step1, "username", "user123");
    strncpy(result.rendered_html, step2, sizeof(result.rendered_html) - 1);
    free(escaped);
    free(step1);
    free(step2);

    return result;
}

void check(void) {
    XSSResult r = safe_xss_handling("<script>alert('XSS')</script>");
    assert(r.vulnerable == false);
    /* Should not contain raw <script */
    assert(strstr(r.rendered_html, "<script") == NULL);
    /* Should contain escaped version */
    assert(strstr(r.rendered_html, "&lt;script") != NULL);
}

int main(void) {
    check();
    printf("All tests passed.\n");
    return 0;
}
