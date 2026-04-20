/* Check if given string is a palindrome. */
#include <stdio.h>
#include <string.h>
#include <assert.h>
#include <stdbool.h>

bool is_palindrome(const char *text) {
    int len = strlen(text);
    for (int i = 0; i < len; i++) {
        if (text[i] != text[len - 1 - i]) return false;
    }
    return true;
}

void check(void) {
    assert(is_palindrome("") == true);
    assert(is_palindrome("aba") == true);
    assert(is_palindrome("aaaaa") == true);
    assert(is_palindrome("zbcd") == false);
    assert(is_palindrome("xywyx") == true);
    assert(is_palindrome("xywyz") == false);
    assert(is_palindrome("xywzx") == false);
}

int main(void) {
    check();
    printf("All tests passed.\n");
    return 0;
}
