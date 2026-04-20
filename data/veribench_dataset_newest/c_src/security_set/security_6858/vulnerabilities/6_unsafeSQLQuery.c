/* Unsafe SQL query with user input concatenated without sanitization.
 * Simulates SQL injection vulnerability using string operations.
 */

#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <assert.h>
#include <stdbool.h>
#include <ctype.h>

/* Simulated user record */
typedef struct {
    int id;
    const char *username;
    const char *password;
    const char *email;
} User;

/* Simulated database */
typedef struct {
    User users[3];
    int user_count;
} DatabaseSimulator;

/* Result from a query */
typedef struct {
    User *results;      /* array of User (shallow copies) */
    int count;
    char *error;        /* NULL if no error */
} QueryResult;

void db_init(DatabaseSimulator *db) {
    db->users[0] = (User){1, "admin", "admin123", "admin@example.com"};
    db->users[1] = (User){2, "user1", "pass123", "user1@example.com"};
    db->users[2] = (User){3, "user2", "pass456", "user2@example.com"};
    db->user_count = 3;
}

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

QueryResult db_execute_query(DatabaseSimulator *db, const char *query) {
    QueryResult qr;
    qr.results = NULL;
    qr.count = 0;
    qr.error = NULL;

    char *query_upper = strdup(query);
    for (char *p = query_upper; *p; p++) *p = toupper((unsigned char)*p);

    /* Check for destructive operations */
    if (strstr(query_upper, "DROP") || strstr(query_upper, "DELETE")) {
        qr.error = strdup("DESTRUCTIVE_OPERATION_ATTEMPTED");
        free(query_upper);
        return qr;
    }

    /* Check for data modification */
    if (strstr(query_upper, "INSERT") || strstr(query_upper, "UPDATE")) {
        qr.error = strdup("DATA_MODIFICATION_ATTEMPTED");
        free(query_upper);
        return qr;
    }

    if (strstr(query_upper, "SELECT")) {
        /* UNION attack */
        if (strstr(query_upper, "UNION")) {
            qr.results = (User *)malloc(db->user_count * sizeof(User));
            memcpy(qr.results, db->users, db->user_count * sizeof(User));
            qr.count = db->user_count;
            free(query_upper);
            return qr;
        }

        /* OR bypass */
        if (strstr(query_upper, "OR")) {
            const char *or_patterns[] = {"'1'='1", "1=1"};
            for (int i = 0; i < 2; i++) {
                if (stristr(query, or_patterns[i])) {
                    qr.results = (User *)malloc(db->user_count * sizeof(User));
                    memcpy(qr.results, db->users, db->user_count * sizeof(User));
                    qr.count = db->user_count;
                    free(query_upper);
                    return qr;
                }
            }
        }

        /* Multiple statements (before comment detection) */
        if (strchr(query, ';')) {
            /* Check if any part has SELECT FROM */
            char *copy = strdup(query);
            char *tok = strtok(copy, ";");
            while (tok) {
                char *tok_upper = strdup(tok);
                for (char *p = tok_upper; *p; p++) *p = toupper((unsigned char)*p);
                if (strstr(tok_upper, "SELECT") && strstr(tok_upper, "FROM")) {
                    free(tok_upper);
                    free(copy);
                    qr.results = (User *)malloc(db->user_count * sizeof(User));
                    memcpy(qr.results, db->users, db->user_count * sizeof(User));
                    qr.count = db->user_count;
                    free(query_upper);
                    return qr;
                }
                free(tok_upper);
                tok = strtok(NULL, ";");
            }
            free(copy);
        }

        /* Comment attack */
        if (strstr(query, "--")) {
            char *before_comment = strdup(query);
            char *dash = strstr(before_comment, "--");
            if (dash) *dash = '\0';
            /* Extract username */
            char *uname_eq = strstr(before_comment, "username");
            if (uname_eq) {
                char *quote1 = strchr(uname_eq, '\'');
                if (quote1) {
                    quote1++;
                    char *quote2 = strchr(quote1, '\'');
                    if (quote2) {
                        size_t len = (size_t)(quote2 - quote1);
                        char *uname = (char *)malloc(len + 1);
                        strncpy(uname, quote1, len);
                        uname[len] = '\0';
                        for (int i = 0; i < db->user_count; i++) {
                            if (strcmp(db->users[i].username, uname) == 0) {
                                qr.results = (User *)malloc(sizeof(User));
                                qr.results[0] = db->users[i];
                                qr.count = 1;
                                break;
                            }
                        }
                        free(uname);
                    }
                }
            }
            free(before_comment);
            free(query_upper);
            return qr;
        }

        /* Normal WHERE clause processing */
        char *where_pos = strstr(query_upper, "WHERE");
        if (where_pos) {
            size_t offset = (size_t)(where_pos - query_upper);
            const char *where_clause = query + offset + 5; /* skip "WHERE" */
            if (strstr(where_clause, "username") || stristr(where_clause, "username")) {
                /* Extract username from WHERE clause */
                const char *orig_where = query + offset + 5;
                char *quote1 = strchr((char *)orig_where, '\'');
                if (quote1) {
                    quote1++;
                    char *quote2 = strchr(quote1, '\'');
                    if (quote2) {
                        size_t len = (size_t)(quote2 - quote1);
                        char *uname = (char *)malloc(len + 1);
                        strncpy(uname, quote1, len);
                        uname[len] = '\0';
                        for (int i = 0; i < db->user_count; i++) {
                            if (strcmp(db->users[i].username, uname) == 0) {
                                qr.results = (User *)malloc(sizeof(User));
                                qr.results[0] = db->users[i];
                                qr.count = 1;
                                break;
                            }
                        }
                        free(uname);
                    }
                }
            }
        } else {
            /* SELECT without WHERE - return all */
            qr.results = (User *)malloc(db->user_count * sizeof(User));
            memcpy(qr.results, db->users, db->user_count * sizeof(User));
            qr.count = db->user_count;
        }
    }

    free(query_upper);
    return qr;
}

QueryResult unsafe_sql_query(DatabaseSimulator *db, const char *username) {
    /* Dangerous: directly concatenate user input into SQL query */
    char query[2048];
    snprintf(query, sizeof(query), "SELECT * FROM users WHERE username = '%s'", username);
    return db_execute_query(db, query);
}

void free_result(QueryResult *qr) {
    free(qr->results);
    free(qr->error);
    qr->results = NULL;
    qr->error = NULL;
}

void check(void) {
    DatabaseSimulator db;
    db_init(&db);

    /* 1) Normal case */
    QueryResult r1 = unsafe_sql_query(&db, "admin");
    assert(r1.count == 1);
    assert(strcmp(r1.results[0].username, "admin") == 0);
    free_result(&r1);

    /* 2) SQL injection: bypass authentication */
    QueryResult r2 = unsafe_sql_query(&db, "admin' OR '1'='1");
    printf("Test 2 - Input: admin' OR '1'='1, Result length: %d\n", r2.count);
    assert(r2.count == 3);
    free_result(&r2);

    /* 3) SQL injection: comment out rest of query */
    QueryResult r3 = unsafe_sql_query(&db, "admin'--");
    assert(r3.count == 1);
    free_result(&r3);

    /* 4) SQL injection: UNION attack */
    QueryResult r4 = unsafe_sql_query(&db, "admin' UNION SELECT * FROM users--");
    assert(r4.count == 3);
    free_result(&r4);

    /* 5) SQL injection: drop table attempt */
    QueryResult r5 = unsafe_sql_query(&db, "admin'; DROP TABLE users;--");
    assert(r5.error != NULL);
    assert(strstr(r5.error, "DESTRUCTIVE_OPERATION_ATTEMPTED") != NULL);
    free_result(&r5);

    /* 6) SQL injection: insert malicious data */
    QueryResult r6 = unsafe_sql_query(&db, "admin'; INSERT INTO users VALUES (999, 'hacker', 'pass', 'hack@evil.com');--");
    assert(r6.error != NULL);
    assert(strstr(r6.error, "DATA_MODIFICATION_ATTEMPTED") != NULL);
    free_result(&r6);

    /* 7) SQL injection: multiple statements */
    QueryResult r7 = unsafe_sql_query(&db, "admin'; SELECT * FROM users;--");
    printf("Test 7 - Input: admin'; SELECT * FROM users;--, Result length: %d\n", r7.count);
    assert(r7.count == 3);
    free_result(&r7);

    /* 8) Edge case: empty username */
    QueryResult r8 = unsafe_sql_query(&db, "");
    assert(r8.count == 0);
    free_result(&r8);
}

int main(void) {
    check();
    printf("All tests passed.\n");
    return 0;
}
