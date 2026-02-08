#include "device.h"

static inline void outb(unsigned short port, unsigned char val) {
    __asm__ volatile ("outb %0, %1" : : "a"(val), "Nd"(port));
}

void device_init() {
    outb(0x43, 0x36);
    outb(0x40, 0);
    outb(0x40, 0);
}
