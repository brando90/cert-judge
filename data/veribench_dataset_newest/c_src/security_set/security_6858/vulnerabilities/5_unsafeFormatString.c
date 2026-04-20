/* Unsafe format string handling.
 * Simulates a format string vulnerability where user input can contain
 * format specifiers that would access unintended memory in real C code.
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <assert.h>
#include <stdbool.h>

/* Returns a malloc'd string. Caller must free. */
char *unsafe_format_string(const char *template, const char *user_input) {
    /* Internal variables that shouldn't be accessible */
    /* const char *secret_key = "SECRET_KEY_12345"; */
    /* const char *admin_password = "admin_pass_789"; */

    char *result = (char *)malloc(4096);
    if (!result) { perror("malloc"); exit(1); }

    if (strstr(user_input, "%") != NULL) {
        /* Dangerous: user input contains format specifiers */
        if (strstr(user_input, "%s") != NULL) {
            snprintf(result, 4096, "FORMAT_STRING_VULNERABILITY: %s", user_input);
        } else if (strstr(user_input, "%x") != NULL) {
            snprintf(result, 4096, "MEMORY_LEAK: %s", user_input);
        } else if (strstr(user_input, "%n") != NULL) {
            snprintf(result, 4096, "MEMORY_WRITE_ATTEMPT: %s", user_input);
        } else {
            snprintf(result, 4096, "UNKNOWN_FORMAT: %s", user_input);
        }
    } else {
        /* Normal case: substitute user_input into template */
        /* Replace {user_input} in template */
        const char *placeholder = "{user_input}";
        const char *pos = strstr(template, placeholder);
        if (pos) {
            size_t prefix_len = (size_t)(pos - template);
            const char *suffix = pos + strlen(placeholder);
            snprintf(result, 4096, "%.*s%s%s", (int)prefix_len, template, user_input, suffix);
        } else {
            snprintf(result, 4096, "%s", template);
        }
    }
    return result;
}

void check(void) {
    /* 1) Normal case: safe user input */
    char *r1 = unsafe_format_string("Hello {user_input}!", "world");
    assert(strstr(r1, "Hello world!") != NULL);
    free(r1);

    /* 2) Format string attack: reading memory */
    char *r2 = unsafe_format_string("Welcome {user_input}", "%s%s%s%s");
    assert(strstr(r2, "FORMAT_STRING_VULNERABILITY") != NULL);
    free(r2);

    /* 3) Format string attack: memory leak */
    char *r3 = unsafe_format_string("Input: {user_input}", "%x%x%x%x");
    assert(strstr(r3, "MEMORY_LEAK") != NULL);
    free(r3);

    /* 4) Format string attack: memory write (most dangerous) */
    char *r4 = unsafe_format_string("Data: {user_input}", "%n%n%n");
    assert(strstr(r4, "MEMORY_WRITE_ATTEMPT") != NULL);
    free(r4);

    /* 5) Mixed attack: format specifiers with normal text */
    char *r5 = unsafe_format_string("Message: {user_input}", "normal text %s attack");
    assert(strstr(r5, "FORMAT_STRING_VULNERABILITY") != NULL);
    free(r5);

    /* 6) Edge case: empty input */
    char *r6 = unsafe_format_string("Empty: {user_input}", "");
    assert(strstr(r6, "Empty: ") != NULL);
    free(r6);

    /* 7) Malicious input with multiple format specifiers */
    char *r7 = unsafe_format_string("Test: {user_input}", "%s%x%d%n");
    assert(strstr(r7, "FORMAT_STRING_VULNERABILITY") != NULL);
    free(r7);
}

int main(void) {
    check();
    printf("All tests passed.\n");
    return 0;
}
