#include <assert.h>
#include <stdlib.h>
#include <string.h>
#include <stdio.h>

// This is best in a project central header file
#define OK 0
#define ERR_MEM -1  // Memory error
#define ERR_EXAMPLE -2  // An example error
// End header file


#define BUFFLENGTH 100

int bar(int a)
{
    int ret = OK;
    if (a < 0)
    {   // Always add parantheses, google "goto fail"
        // https://nakedsecurity.sophos.com/2014/02/24/anatomy-of-a-goto-fail-apples-ssl-bug-explained-plus-an-unofficial-patch/
        ret = ERR_EXAMPLE;
    }

    return ret;
}

int foo(int a)
{
    void * buff = NULL;
    int ret = OK;

    assert(a > -10);
    assert(a < 100);

    buff = malloc(BUFFLENGTH);
    if (buff == NULL)
    {
        ret = ERR_MEM;
        goto cleanupthemess;
    }

    ret = bar(a);
    if (ret != OK)
    {
        printf("error now\n");
        goto cleanupthemess;
    }

    printf("Never reached\n");

cleanupthemess:

    if (buff)
    {
        memset(buff, 0, BUFFLENGTH); // For sensitive content like passwords
        free(buff);
        buff = NULL;  // Prevents double frees
    }
    return ret;

}


int main()
{
    exit(foo(-1));  // 0 indicates ok, everything else is an error
}
