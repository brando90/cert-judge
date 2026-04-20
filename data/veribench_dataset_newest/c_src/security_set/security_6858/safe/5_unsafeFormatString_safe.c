/* Safe string formatting: never treat user input as a format string.
 * We only substitute a known placeholder literally.
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <assert.h>

/* Replace {user_input} placeholder in template with user_input.
 * Returns malloc'd string. Caller must free. */
char *safe_format_string(const char *template, const char *user_input) {
    const char *placeholder = "{user_input}";
    char *result = (char *)malloc(4096);
    if (!result) { perror("malloc"); exit(1); }
    result[0] = '\0';

    const char *pos = template;
    while (1) {
        const char *found = strstr(pos, placeholder);
        if (!found) {
            strncat(result, pos, 4095 - strlen(result));
            break;
        }
        strncat(result, pos, (size_t)(found - pos));
        strncat(result, user_input, 4095 - strlen(result));
        pos = found + strlen(placeholder);
    }
    return result;
}

void check(void) {
    /* Normal */
    char *r1 = safe_format_string("Hello {user_input}!", "world");
    assert(strcmp(r1, "Hello world!") == 0);
    free(r1);

    /* Format string attacks become plain text, no special behavior */
    const char *attacks[] = {"%s%s%s", "%x%x", "%n", "normal text %s attack"};
    for (int i = 0; i < 4; i++) {
        char expected[256];
        snprintf(expected, sizeof(expected), "Input: %s", attacks[i]);
        char *r = safe_format_string("Input: {user_input}", attacks[i]);
        assert(strcmp(r, expected) == 0);
        free(r);
    }

    /* Empty */
    char *r2 = safe_format_string("Empty: {user_input}", "");
    assert(strcmp(r2, "Empty: ") == 0);
    free(r2);
}

int main(void) {
    check();
    printf("All tests passed.\n");
    return 0;
}
