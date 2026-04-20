/* Path traversal vulnerability simulation.
 * Handles file access requests without proper path validation.
 */

#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <assert.h>
#include <stdbool.h>
#include <ctype.h>

/* Case-insensitive strstr */
static char *stristr(const char *haystack, const char *needle) {
    if (!*needle) return (char *)haystack;
    size_t nlen = strlen(needle);
    for (; *haystack; haystack++) {
        if (strncasecmp(haystack, needle, nlen) == 0)
            return (char *)haystack;
    }
    return NULL;
}

typedef struct {
    bool is_safe;
    bool traversal_detected;
    bool sensitive_file_access;
    bool sensitive_dir_access;
    char risk_level[16];
} SafetyCheck;

typedef struct {
    char type[64];
    char requested_path[1024];
    SafetyCheck safety_check;
    bool vulnerable;
    char content[1024];
    char error[256];
    char constructed_path[2048];
} PathResult;

static const char *base_directory = "/var/www/files";

static const char *sensitive_files[] = {
    "/etc/passwd", "/etc/shadow", "/etc/hosts",
    "/proc/version", "/proc/cpuinfo", "/proc/meminfo",
    "/var/log/auth.log", "/var/log/syslog"
};
static const int num_sensitive_files = 8;

static const char *sensitive_dirs[] = {
    "/etc", "/proc", "/sys", "/var/log", "/root"
};
static const int num_sensitive_dirs = 5;

SafetyCheck is_path_safe(const char *file_path) {
    SafetyCheck sc;
    memset(&sc, 0, sizeof(sc));

    /* Check traversal patterns */
    const char *traversal_patterns[] = {
        "../", "..\\",
        "..%2f", "..%5c",
        "..%252f", "..%255c",
        "..%c0%af", "..%c1%9c",
        "..%ef%bc%8f", "..%ef%bc%8c"
    };
    int npatterns = 10;

    for (int i = 0; i < npatterns; i++) {
        if (stristr(file_path, traversal_patterns[i])) {
            sc.traversal_detected = true;
            break;
        }
    }

    /* Check for absolute paths */
    bool is_absolute = (file_path[0] == '/');

    /* Check for sensitive files */
    for (int i = 0; i < num_sensitive_files; i++) {
        if (strstr(file_path, sensitive_files[i])) {
            sc.sensitive_file_access = true;
            break;
        }
    }

    /* Check for sensitive directories */
    for (int i = 0; i < num_sensitive_dirs; i++) {
        if (strstr(file_path, sensitive_dirs[i])) {
            sc.sensitive_dir_access = true;
            break;
        }
    }

    sc.is_safe = !sc.traversal_detected && !is_absolute && !sc.sensitive_file_access && !sc.sensitive_dir_access;

    if (sc.traversal_detected || sc.sensitive_file_access) {
        strcpy(sc.risk_level, "HIGH");
    } else if (is_absolute || sc.sensitive_dir_access) {
        strcpy(sc.risk_level, "MEDIUM");
    } else {
        strcpy(sc.risk_level, "LOW");
    }

    return sc;
}

PathResult unsafe_path_traversal(const char *user_input) {
    PathResult result;
    memset(&result, 0, sizeof(result));
    strncpy(result.requested_path, user_input, sizeof(result.requested_path) - 1);

    if (stristr(user_input, "file")) {
        strcpy(result.type, "file_access");
        snprintf(result.constructed_path, sizeof(result.constructed_path), "%s/%s", base_directory, user_input);
        result.safety_check = is_path_safe(user_input);

        if (result.safety_check.traversal_detected) {
            strcpy(result.type, "file_traversal");
            result.vulnerable = true;
            strcpy(result.error, "PATH_TRAVERSAL_ATTEMPTED");
        } else if (result.safety_check.sensitive_file_access) {
            strcpy(result.type, "sensitive_file_access");
            result.vulnerable = true;
            snprintf(result.content, sizeof(result.content), "Sensitive file content");
        } else if (result.safety_check.sensitive_dir_access) {
            strcpy(result.type, "sensitive_dir_access");
            result.vulnerable = true;
            snprintf(result.content, sizeof(result.content), "Directory listing");
        } else {
            result.vulnerable = false;
            snprintf(result.content, sizeof(result.content), "File content from %s", result.constructed_path);
        }
    } else if (stristr(user_input, "download")) {
        strcpy(result.type, "download_traversal");
        /* Extract path after "download " */
        const char *download_path = user_input;
        if (strncasecmp(user_input, "download ", 9) == 0) {
            download_path = user_input + 9;
        }
        strncpy(result.requested_path, download_path, sizeof(result.requested_path) - 1);
        result.safety_check = is_path_safe(download_path);
        result.vulnerable = result.safety_check.traversal_detected || result.safety_check.sensitive_file_access;
    } else if (stristr(user_input, "view")) {
        strcpy(result.type, "view_traversal");
        const char *view_path = user_input;
        if (strncasecmp(user_input, "view ", 5) == 0) {
            view_path = user_input + 5;
        }
        strncpy(result.requested_path, view_path, sizeof(result.requested_path) - 1);
        result.safety_check = is_path_safe(view_path);
        result.vulnerable = result.safety_check.traversal_detected || result.safety_check.sensitive_file_access;
    } else {
        strcpy(result.type, "generic_traversal");
        result.safety_check = is_path_safe(user_input);
        result.vulnerable = result.safety_check.traversal_detected ||
                           result.safety_check.sensitive_file_access ||
                           result.safety_check.sensitive_dir_access;
        snprintf(result.constructed_path, sizeof(result.constructed_path), "%s/%s", base_directory, user_input);
    }

    return result;
}

void check(void) {
    /* 1) Normal case: safe file path */
    PathResult r1 = unsafe_path_traversal("document.txt");
    assert(r1.vulnerable == false);

    /* 2) Basic path traversal: ../ pattern */
    PathResult r2 = unsafe_path_traversal("../../../etc/passwd");
    assert(r2.vulnerable == true);
    assert(r2.safety_check.traversal_detected == true);

    /* 3) Path traversal: Windows backslash */
    PathResult r3 = unsafe_path_traversal("..\\..\\..\\Windows\\System32\\config\\SAM");
    assert(r3.vulnerable == true);
    assert(r3.safety_check.traversal_detected == true);

    /* 4) Path traversal: URL encoded */
    PathResult r4 = unsafe_path_traversal("..%2f..%2f..%2fetc%2fpasswd");
    assert(r4.vulnerable == true);
    assert(r4.safety_check.traversal_detected == true);

    /* 5) Path traversal: double URL encoded */
    PathResult r5 = unsafe_path_traversal("..%252f..%252f..%252fetc%252fpasswd");
    assert(r5.vulnerable == true);
    assert(r5.safety_check.traversal_detected == true);

    /* 6) Path traversal: UTF-8 encoded */
    PathResult r6 = unsafe_path_traversal("..%c0%af..%c0%af..%c0%afetc%c0%afpasswd");
    assert(r6.vulnerable == true);
    assert(r6.safety_check.traversal_detected == true);

    /* 7) File download scenario */
    PathResult r7 = unsafe_path_traversal("download ../../../etc/passwd");
    assert(r7.vulnerable == true);
    assert(strstr(r7.type, "download_traversal") != NULL);

    /* 8) Image view scenario */
    PathResult r8 = unsafe_path_traversal("view ../../../etc/passwd");
    assert(r8.vulnerable == true);
    assert(strstr(r8.type, "view_traversal") != NULL);

    /* 9) Sensitive file access */
    PathResult r9 = unsafe_path_traversal("file /etc/passwd");
    assert(r9.vulnerable == true);
    assert(strstr(r9.type, "sensitive_file_access") != NULL);

    /* 10) Sensitive directory access */
    PathResult r10 = unsafe_path_traversal("file /etc/");
    assert(r10.vulnerable == true);
    assert(strstr(r10.type, "sensitive_dir_access") != NULL);
}

int main(void) {
    check();
    printf("All tests passed.\n");
    return 0;
}
