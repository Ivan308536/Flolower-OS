#include "panic.h"
#include <stdint.h>
#include <stdbool.h>

static inline void outb_p(uint16_t port, uint8_t val) {
    asm volatile ("outb %0, %1" : : "a"(val), "Nd"(port));
}
static inline uint8_t inb_p(uint16_t port) {
    uint8_t ret;
    asm volatile ("inb %1, %0" : "=a"(ret) : "Nd"(port));
    return ret;
}
static inline void outw_p(uint16_t port, uint16_t val) {
    asm volatile ("outw %0, %1" : : "a"(val), "Nd"(port));
}

#define VGA_ADDR 0xB8000
#define VGA_W 80
#define VGA_H 25

static void panic_clear_screen() {
    volatile uint16_t* buf = (volatile uint16_t*)VGA_ADDR;
    for(int i = 0; i < VGA_W * VGA_H; i++) buf[i] = (0x4F << 8) | ' ';
}

static void panic_print_at(int x, int y, const char* str) {
    volatile uint16_t* buf = (volatile uint16_t*)VGA_ADDR;
    int idx = y * VGA_W + x;
    while(*str) {
        if(idx < VGA_W * VGA_H) buf[idx++] = (0x4F << 8) | *str++;
        else break;
    }
}

static void panic_reboot() {
    uint8_t temp;
    asm volatile ("cli");
    do { temp = inb_p(0x64); if (temp & 0x01) inb_p(0x60); } while (temp & 0x02);
    outb_p(0x64, 0xFE);
    while(1) asm volatile("hlt");
}

static void panic_shutdown() {
    outw_p(0x604, 0x2000); outw_p(0xB004, 0x2000); outw_p(0x4004, 0x3400);
    while(1) asm volatile("hlt");
}

void kernel_panic(const char* component, const char* error_msg, const char* fix_suggestion) {
    asm volatile("cli");
    panic_clear_screen();

    const char* kp[] = {
        "######  ####",
        "##  ## ##   ",
        "##  ## ##   ",
        "###### ##   ",
        "## ##  ##   ",
        "##  ##  ####"
    };

    for(int i = 0; i < 6; i++) {
        panic_print_at(4, 7 + i, kp[i]);
    }

    panic_print_at(20, 5,  "!!! KERNEL PANIC, CRITICAL SYSTEM FAILURE !!!");
    
    panic_print_at(20, 8,  "Component: "); 
    panic_print_at(32, 8,  component);
    
    panic_print_at(20, 9,  "Error:     ");     
    panic_print_at(32, 9,  error_msg);
    
    panic_print_at(20, 11, "Action:    ");   
    panic_print_at(32, 11, fix_suggestion);

    panic_print_at(20, 15, "Status: System halted to protect data.");
    
    panic_print_at(20, 19, "-> Press [ENTER] to Reboot");
    panic_print_at(20, 20, "-> Press [ESC]   to Power Off");

    while(1) {
        if (inb_p(0x64) & 1) {
            uint8_t sc = inb_p(0x60);
            if (sc == 0x1C) panic_reboot();
            if (sc == 0x01) panic_shutdown();
        }
    }
}
