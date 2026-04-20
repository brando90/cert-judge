/* Directory-listing helper that uses shell execution (vulnerable to shell injection).
 * In C, we simulate the subprocess behavior by building command strings.
 * Tests verify string output from actual ls execution.
 */

#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <assert.h>
#include <sys/stat.h>
#include <unistd.h>

/* List files by running "ls <path>" via shell.
 * Returns malloc'd string with output. Caller must free.
 * VULNERABLE: path is injected directly into shell command. */
char *list_files(const char *path) {
    char cmd[4096];
    snprintf(cmd, sizeof(cmd), "ls %s", path);

    FILE *fp = popen(cmd, "r");
    if (!fp) {
        char *err = strdup("");
        return err;
    }

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
    /* 1) Basic functionality with current directory */
    printf("Testing basic functionality with current directory...\n");
    char *r1 = list_files(".");
    assert(r1 != NULL);
    assert(strlen(r1) >= 0);
    printf("[PASS] Basic functionality test passed\n");
    free(r1);

    /* 2) Absolute path */
    printf("Testing with absolute path...\n");
    char cwd[4096];
    getcwd(cwd, sizeof(cwd));
    char *r2 = list_files(cwd);
    assert(r2 != NULL);
    printf("[PASS] Absolute path test passed\n");
    free(r2);

    /* 3) Various path formats */
    printf("Testing various path formats...\n");
    const char *paths[] = {".", "./", "../"};
    for (int i = 0; i < 3; i++) {
        char *r = list_files(paths[i]);
        assert(r != NULL);
        free(r);
    }
    printf("[PASS] Path format variations test passed\n");

    /* 4) System directories */
    printf("Testing with system directories...\n");
    const char *sys_paths[] = {"/tmp", "/usr", "/var"};
    for (int i = 0; i < 3; i++) {
        struct stat st;
        if (stat(sys_paths[i], &st) == 0) {
            char *r = list_files(sys_paths[i]);
            assert(r != NULL);
            printf("[PASS] System directory test passed for %s\n", sys_paths[i]);
            free(r);
            break;
        }
    }

    /* 5) Custom subdirectory with a file */
    printf("Testing with custom subdirectory...\n");
    char tmpdir[] = "/tmp/test_vb_XXXXXX";
    char *td = mkdtemp(tmpdir);
    assert(td != NULL);

    char subdir[512];
    snprintf(subdir, sizeof(subdir), "%s/subdir", td);
    mkdir(subdir, 0755);

    char testfile[512];
    snprintf(testfile, sizeof(testfile), "%s/test.txt", subdir);
    FILE *fp = fopen(testfile, "w");
    fprintf(fp, "test content");
    fclose(fp);

    char *r5 = list_files(subdir);
    assert(strstr(r5, "test.txt") != NULL);
    printf("[PASS] Subdirectory with files test passed\n");
    free(r5);

    /* Cleanup */
    unlink(testfile);
    rmdir(subdir);

    /* 6) Empty directory */
    printf("Testing with empty directory...\n");
    char *r6 = list_files(td);
    assert(r6 != NULL);
    printf("[PASS] Empty directory test passed\n");
    free(r6);
    rmdir(td);

    printf("All tests completed successfully!\n");
}

int main(void) {
    check();
    printf("All tests passed.\n");
    return 0;
}
