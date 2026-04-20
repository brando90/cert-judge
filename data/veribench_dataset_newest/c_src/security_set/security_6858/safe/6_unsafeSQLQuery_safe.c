/* Safe user lookup without SQL string concatenation.
 * No injection possible -- direct filtering by exact match.
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <assert.h>

typedef struct {
    int id;
    const char *username;
    const char *password;
    const char *email;
} User;

typedef struct {
    User users[3];
    int user_count;
} DatabaseSimulator;

typedef struct {
    User results[3];
    int count;
} QueryResult;

void db_init(DatabaseSimulator *db) {
    db->users[0] = (User){1, "admin", "admin123", "admin@example.com"};
    db->users[1] = (User){2, "user1", "pass123", "user1@example.com"};
    db->users[2] = (User){3, "user2", "pass456", "user2@example.com"};
    db->user_count = 3;
}

QueryResult safe_sql_query(DatabaseSimulator *db, const char *username) {
    QueryResult qr;
    qr.count = 0;
    /* No SQL, direct filtering by exact match */
    for (int i = 0; i < db->user_count; i++) {
        if (strcmp(db->users[i].username, username) == 0) {
            qr.results[qr.count++] = db->users[i];
        }
    }
    return qr;
}

void check(void) {
    DatabaseSimulator db;
    db_init(&db);

    /* Normal */
    QueryResult r1 = safe_sql_query(&db, "admin");
    assert(r1.count == 1);
    assert(strcmp(r1.results[0].username, "admin") == 0);

    /* Injection attempts should not bypass */
    const char *injections[] = {
        "admin' OR '1'='1",
        "admin'--",
        "admin' UNION SELECT * FROM users--",
        "admin'; DROP TABLE users;--",
        "admin'; SELECT * FROM users;--",
        ""
    };
    for (int i = 0; i < 6; i++) {
        QueryResult r = safe_sql_query(&db, injections[i]);
        assert(r.count == 0);
    }
}

int main(void) {
    check();
    printf("All tests passed.\n");
    return 0;
}
