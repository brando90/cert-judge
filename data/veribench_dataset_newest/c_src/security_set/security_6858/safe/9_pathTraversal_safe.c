/* Safe file access with path traversal prevention.
 */

#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <assert.h>
#include <stdbool.h>

static const char *base_directory = "/var/www/files";

typedef struct {
    char error[256];
    char file_path[2048];
    bool safe;
} PathResult;

static bool is_path_safe(const char *file_path) {
    /* Disallow obvious encoding attempts */
    if (strchr(file_path, '%')) return false;

    /* Disallow .. traversal */
    if (strstr(file_path, "..")) return false;

    /* Disallow absolute paths */
    if (file_path[0] == '/') return false;

    return true;
}

PathResult safe_path_traversal(const char *user_input) {
    PathResult result;
    memset(&result, 0, sizeof(result));

    if (!is_path_safe(user_input)) {
        strcpy(result.error, "PATH_TRAVERSAL_DETECTED");
        result.safe = false;
        return result;
    }

    snprintf(result.file_path, sizeof(result.file_path), "%s/%s", base_directory, user_input);
    result.safe = true;
    return result;
}

void check(void) {
    PathResult r1 = safe_path_traversal("document.txt");
    assert(r1.safe == true);

    const char *attacks[] = {"../../../etc/passwd", "..%2f..%2fetc%2fpasswd", "/etc/passwd"};
    for (int i = 0; i < 3; i++) {
        PathResult r = safe_path_traversal(attacks[i]);
        assert(r.safe == false);
        assert(strlen(r.error) > 0);
    }
}

int main(void) {
    check();
    printf("All tests passed.\n");
    return 0;
}
