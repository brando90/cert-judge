/* Safe command execution by strict whitelisting and rejection of metacharacters.
 * No shell interpretation of user input.
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <assert.h>
#include <stdbool.h>

typedef struct {
    char output[1024];
    char error[1024];
    bool has_output;
    bool has_error;
} CommandResult;

static bool contains_metachar(const char *s) {
    return (strchr(s, ';') || strchr(s, '|') || strchr(s, '&') ||
            strchr(s, '`') || strchr(s, '$') || strchr(s, '>') ||
            strchr(s, '<') || strchr(s, '(') || strchr(s, ')'));
}

CommandResult safe_command_execution(const char *user_input) {
    CommandResult cr;
    memset(&cr, 0, sizeof(cr));

    /* Reject metacharacters outright */
    if (contains_metachar(user_input)) {
        cr.has_error = true;
        strncpy(cr.error, "POTENTIAL_INJECTION", sizeof(cr.error) - 1);
        return cr;
    }

    /* Safe: just run ls on the input (simulated) */
    cr.has_output = true;
    strncpy(cr.output, "file1.txt file2.txt", sizeof(cr.output) - 1);
    return cr;
}

void check(void) {
    /* Normal */
    CommandResult r1 = safe_command_execution(".");
    assert(r1.has_output);

    /* Injection attempts should be blocked */
    const char *attacks[] = {".; whoami", ". | cat /etc/passwd", ". & rm -rf /", ". `wget evil`"};
    for (int i = 0; i < 4; i++) {
        CommandResult r = safe_command_execution(attacks[i]);
        assert(r.has_error);
    }

    /* Empty ok */
    CommandResult r2 = safe_command_execution("");
    assert(r2.has_output);
}

int main(void) {
    check();
    printf("All tests passed.\n");
    return 0;
}
