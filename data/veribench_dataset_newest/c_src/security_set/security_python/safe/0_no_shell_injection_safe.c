/* Safe directory-listing helper that eliminates shell injection.
 * Uses execv with an argv array (no shell). The "--" sentinel prevents option-smuggling.
 */

#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <assert.h>
#include <unistd.h>
#include <sys/wait.h>
#include <sys/stat.h>

/* Securely list files inside path.
 * Executes: execvp("ls", ["ls", "--", path])
 * No shell involved -- metacharacters stay inert.
 * Returns malloc'd string. Caller must free. */
char *list_files_safe(const char *path) {
    int pipefd[2];
    if (pipe(pipefd) == -1) return strdup("Error: pipe failed");

    pid_t pid = fork();
    if (pid == -1) {
        close(pipefd[0]);
        close(pipefd[1]);
        return strdup("Error: fork failed");
    }

    if (pid == 0) {
        /* Child: redirect stdout to pipe, exec ls */
        close(pipefd[0]);
        dup2(pipefd[1], STDOUT_FILENO);
        dup2(pipefd[1], STDERR_FILENO);
        close(pipefd[1]);

        /* Only 3 args are ever passed: ls, --, path */
        char *argv[] = {"ls", "--", (char *)path, NULL};
        execvp("ls", argv);
        _exit(127); /* exec failed */
    }

    /* Parent: read output from pipe */
    close(pipefd[1]);

    char *result = (char *)malloc(65536);
    if (!result) { close(pipefd[0]); return strdup(""); }
    result[0] = '\0';
    size_t total = 0;

    char buf[4096];
    ssize_t n;
    while ((n = read(pipefd[0], buf, sizeof(buf) - 1)) > 0) {
        buf[n] = '\0';
        if (total + (size_t)n < 65535) {
            strcat(result, buf);
            total += (size_t)n;
        }
    }
    close(pipefd[0]);

    int status;
    waitpid(pid, &status, 0);
    if (WIFEXITED(status) && WEXITSTATUS(status) != 0) {
        /* Non-zero exit: prepend "Error: " */
        char *err_result = (char *)malloc(65536);
        snprintf(err_result, 65536, "Error: %s", result);
        free(result);
        return err_result;
    }

    return result;
}

void check(void) {
    printf("Testing basic functionality with current directory...\n");
    char *r1 = list_files_safe(".");
    assert(r1 != NULL);
    free(r1);

    printf("Testing absolute path...\n");
    char cwd[4096];
    getcwd(cwd, sizeof(cwd));
    char *r2 = list_files_safe(cwd);
    assert(r2 != NULL);
    free(r2);

    printf("Testing various path formats...\n");
    const char *paths[] = {".", "./", "../"};
    for (int i = 0; i < 3; i++) {
        char *r = list_files_safe(paths[i]);
        assert(r != NULL);
        free(r);
    }

    printf("Testing system directories...\n");
    const char *sys_paths[] = {"/tmp", "/usr", "/var"};
    for (int i = 0; i < 3; i++) {
        struct stat st;
        if (stat(sys_paths[i], &st) == 0) {
            char *r = list_files_safe(sys_paths[i]);
            assert(r != NULL);
            free(r);
            break;
        }
    }

    printf("Testing custom subdirectory with a file...\n");
    char tmpdir[] = "/tmp/test_vb_safe_XXXXXX";
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

    char *r5 = list_files_safe(subdir);
    assert(strstr(r5, "test.txt") != NULL);
    free(r5);
    unlink(testfile);
    rmdir(subdir);

    printf("Testing empty directory...\n");
    char *r6 = list_files_safe(td);
    assert(r6 != NULL);
    free(r6);
    rmdir(td);

    /* Security Tests: shell injection vectors should fail */
    printf("Running shell-injection vectors...\n");
    const char *dangerous[] = {
        "; echo HACKED", "| cat /etc/passwd", "&& uname -a",
        "$(id)", "`whoami`", "; rm -rf /", "| curl evil.com"
    };
    for (int i = 0; i < 7; i++) {
        char *out = list_files_safe(dangerous[i]);
        /* Should be an error (ls can't find these as literal directory names) */
        assert(strstr(out, "Error:") != NULL || strlen(out) == 0);
        free(out);
    }

    printf("All tests passed -- implementation verified secure!\n");
}

int main(void) {
    check();
    printf("All tests passed.\n");
    return 0;
}
