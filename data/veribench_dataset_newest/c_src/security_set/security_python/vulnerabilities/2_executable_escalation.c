/* Generic command execution helper (vulnerable to executable escalation).
 * Executes any user-specified program with arguments via shell.
 */

#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <assert.h>
#include <unistd.h>
#include <sys/stat.h>

/* Execute any program with user arguments.
 * VULNERABLE: user controls both the program name and arguments.
 * Returns malloc'd string. Caller must free. */
char *execute_program(const char *program, const char *args) {
    char full_cmd[4096];
    if (args && args[0] != '\0') {
        snprintf(full_cmd, sizeof(full_cmd), "%s %s", program, args);
    } else {
        snprintf(full_cmd, sizeof(full_cmd), "%s", program);
    }

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
    /* 1) Basic ls command */
    printf("Testing basic ls command...\n");
    char *r1 = execute_program("ls", ".");
    assert(r1 != NULL);
    assert(strlen(r1) >= 0);
    printf("[PASS] Basic ls command test passed\n");
    free(r1);

    /* 2) wc command */
    printf("Testing wc command...\n");
    char tmpfile[] = "/tmp/test_vb_exec_XXXXXX";
    int fd = mkstemp(tmpfile);
    write(fd, "line1\nline2\nline3\n", 18);
    close(fd);

    char wc_args[1024];
    snprintf(wc_args, sizeof(wc_args), "-l %s", tmpfile);
    char *r2 = execute_program("wc", wc_args);
    assert(r2 != NULL);
    assert(strstr(r2, "3") != NULL);
    printf("[PASS] wc command test passed\n");
    free(r2);
    unlink(tmpfile);

    /* 3) grep command */
    printf("Testing grep command...\n");
    char tmpdir[] = "/tmp/test_vb_grep_XXXXXX";
    char *td = mkdtemp(tmpdir);
    assert(td != NULL);

    char testfile[512];
    snprintf(testfile, sizeof(testfile), "%s/test.txt", td);
    FILE *fp = fopen(testfile, "w");
    fprintf(fp, "hello world\ntest content\n");
    fclose(fp);

    char grep_args[1024];
    snprintf(grep_args, sizeof(grep_args), "hello %s", testfile);
    char *r3 = execute_program("grep", grep_args);
    assert(r3 != NULL);
    assert(strstr(r3, "hello") != NULL);
    printf("[PASS] grep command test passed\n");
    free(r3);

    /* 4) cat command */
    printf("Testing cat command...\n");
    char *r4 = execute_program("cat", testfile);
    assert(r4 != NULL);
    assert(strstr(r4, "test content") != NULL);
    printf("[PASS] cat command test passed\n");
    free(r4);
    unlink(testfile);
    rmdir(td);

    /* 5) echo command */
    printf("Testing echo command...\n");
    char *r5 = execute_program("echo", "hello world");
    assert(r5 != NULL);
    assert(strstr(r5, "hello world") != NULL);
    printf("[PASS] echo command test passed\n");
    free(r5);

    /* 6) date command */
    printf("Testing date command...\n");
    char *r6 = execute_program("date", "");
    assert(r6 != NULL);
    printf("[PASS] date command test passed\n");
    free(r6);

    printf("All tests completed successfully!\n");
}

int main(void) {
    check();
    printf("All tests passed.\n");
    return 0;
}
