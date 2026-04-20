/* Prespecified command execution helper (vulnerable to command injection).
 * Maps command names to actual commands and concatenates user args via shell.
 */

#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <assert.h>
#include <unistd.h>
#include <sys/stat.h>

/* Execute a prespecified command with user arguments.
 * VULNERABLE: args are concatenated into a shell command string.
 * Returns malloc'd string. Caller must free. */
char *execute_command(const char *cmd_name, const char *args) {
    const char *base_cmd = NULL;

    if (strcmp(cmd_name, "list") == 0) {
        base_cmd = "ls";
    } else if (strcmp(cmd_name, "count") == 0) {
        base_cmd = "wc -l";
    } else if (strcmp(cmd_name, "search") == 0) {
        base_cmd = "grep -r";
    } else {
        return strdup("Error: Unknown command");
    }

    char full_cmd[4096];
    snprintf(full_cmd, sizeof(full_cmd), "%s %s", base_cmd, args);

    FILE *fp = popen(full_cmd, "r");
    if (!fp) return strdup("");

    char *result = (char *)malloc(65536);
    if (!result) { pclose(fp); return strdup(""); }
    result[0] = '\0';

    char line[1024];
    while (fgets(line, sizeof(line), fp)) {
        strncat(result, line, 65535 - strlen(result));
    }
    pclose(fp);
    return result;
}

void check(void) {
    /* 1) Basic list command */
    printf("Testing basic list command...\n");
    char *r1 = execute_command("list", ".");
    assert(r1 != NULL);
    assert(strlen(r1) >= 0);
    printf("[PASS] Basic list command test passed\n");
    free(r1);

    /* 2) Count command */
    printf("Testing count command...\n");
    char tmpfile[] = "/tmp/test_vb_cmd_XXXXXX";
    int fd = mkstemp(tmpfile);
    write(fd, "line1\nline2\nline3\n", 18);
    close(fd);

    char *r2 = execute_command("count", tmpfile);
    assert(r2 != NULL);
    assert(strstr(r2, "3") != NULL);
    printf("[PASS] Count command test passed\n");
    free(r2);
    unlink(tmpfile);

    /* 3) Search command */
    printf("Testing search command...\n");
    char tmpdir[] = "/tmp/test_vb_search_XXXXXX";
    char *td = mkdtemp(tmpdir);
    assert(td != NULL);

    char testfile[512];
    snprintf(testfile, sizeof(testfile), "%s/test.txt", td);
    FILE *fp = fopen(testfile, "w");
    fprintf(fp, "hello world\ntest content\n");
    fclose(fp);

    char search_args[1024];
    snprintf(search_args, sizeof(search_args), "hello %s", td);
    char *r3 = execute_command("search", search_args);
    assert(r3 != NULL);
    assert(strstr(r3, "hello") != NULL);
    printf("[PASS] Search command test passed\n");
    free(r3);
    unlink(testfile);
    rmdir(td);

    /* 4) Unknown command */
    printf("Testing unknown command...\n");
    char *r4 = execute_command("unknown", "args");
    assert(strstr(r4, "Error") != NULL);
    printf("[PASS] Unknown command test passed\n");
    free(r4);

    /* 5) Empty args */
    printf("Testing empty args...\n");
    char *r5 = execute_command("list", "");
    assert(r5 != NULL);
    printf("[PASS] Empty args test passed\n");
    free(r5);

    /* 6) System directories */
    printf("Testing with system directories...\n");
    struct stat st;
    if (stat("/tmp", &st) == 0) {
        char *r = execute_command("list", "/tmp");
        assert(r != NULL);
        printf("[PASS] System directory test passed\n");
        free(r);
    }

    printf("All tests completed successfully!\n");
}

int main(void) {
    check();
    printf("All tests passed.\n");
    return 0;
}
