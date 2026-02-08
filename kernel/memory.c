#include "MemoryManagement.h"

static unsigned int heap = 0x200000;

void init_memory() {}

void* kmalloc(unsigned int size) {
    void* r = (void*)heap;
    heap += size;
    return r;
}
