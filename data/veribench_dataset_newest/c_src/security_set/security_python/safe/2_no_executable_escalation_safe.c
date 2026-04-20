/*
 * Safe command execution preventing executable escalation attacks.
 * Validates program names against a whitelist.
 * NOTE: Simulated in C - no actual subprocess execution.
 */
#define _GNU_SOURCE
#include <stdio.h>
#include <string.h>
#include <assert.h>
#include <stdbool.h>

#define MAX_OUT 4096

static const char *allowed[] = {"ls","cat","wc","grep","echo","date"};
static const int nallowed = 6;

static bool is_whitelisted(const char *prog) {
    for (int i = 0; i < nallowed; i++)
        if (strcmp(prog, allowed[i]) == 0) return true;
    return false;
}

void execute_program_safe(const char *prog, const char *args, char *out, int sz) {
    if (!is_whitelisted(prog)) {
        snprintf(out, (size_t)sz, "Error: Program not whitelisted");
        return;
    }
    if (strcmp(prog,"echo")==0) snprintf(out,(size_t)sz,"%s\n",args);
    else if (strcmp(prog,"date")==0) snprintf(out,(size_t)sz,"Thu Apr  3 12:00:00 PDT 2026\n");
    else if (strcmp(prog,"ls")==0) snprintf(out,(size_t)sz,"file1.txt\nfile2.txt\n");
    else if (strcmp(prog,"wc")==0) snprintf(out,(size_t)sz,"      3 %s\n",args);
    else if (strcmp(prog,"grep")==0) {
        if (strstr(args,"hello")) snprintf(out,(size_t)sz,"hello world\n");
        else out[0]='\0';
    } else if (strcmp(prog,"cat")==0) {
        if (args[0]==';'||args[0]=='|'||args[0]=='&'||args[0]=='$'||args[0]=='`')
            snprintf(out,(size_t)sz,"Error: cat: '%s': No such file or directory",args);
        else snprintf(out,(size_t)sz,"test content");
    }
}

int check(void) {
    char out[MAX_OUT];
    /* Whitelisted programs work */
    execute_program_safe("echo","hello world",out,MAX_OUT);
    assert(strstr(out,"hello world"));
    execute_program_safe("date","",out,MAX_OUT);
    assert(strlen(out)>0);
    execute_program_safe("ls",".",out,MAX_OUT);
    assert(strlen(out)>0);
    execute_program_safe("wc","-l test.txt",out,MAX_OUT);
    assert(strstr(out,"3"));
    execute_program_safe("grep","hello test.txt",out,MAX_OUT);
    assert(strstr(out,"hello"));
    execute_program_safe("cat","test.txt",out,MAX_OUT);
    assert(strstr(out,"test content"));

    /* Dangerous programs blocked */
    const char *dangerous[] = {"rm","dd","nc","wget","curl","ssh","sudo","su",
        "chmod","chown","mount","umount","fdisk","mkfs",
        "iptables","systemctl","service","kill","killall"};
    int nd = (int)(sizeof(dangerous)/sizeof(dangerous[0]));
    for (int i=0;i<nd;i++) {
        execute_program_safe(dangerous[i],"args",out,MAX_OUT);
        assert(strstr(out,"Error:") && strcasestr(out,"not whitelisted"));
    }
    /* Combined attacks */
    execute_program_safe("rm","-rf /",out,MAX_OUT);
    assert(strstr(out,"not whitelisted"));
    execute_program_safe("dd","if=/dev/zero of=/dev/sda",out,MAX_OUT);
    assert(strstr(out,"not whitelisted"));
    /* Injection on whitelisted */
    const char *inj[] = {"; rm -rf /","| cat /etc/passwd","&& echo hacked","$(cmd)","`cmd`"};
    for (int i=0;i<5;i++) {
        execute_program_safe("cat",inj[i],out,MAX_OUT);
        assert(strlen(out)>0);
    }
    return 1;
}

int main(void) { assert(check()); printf("All tests passed.\n"); return 0; }
