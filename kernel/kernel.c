#include "commands.h"
#include "screen.h"
#include "keyboard.h"
#include "memory.h"
#include "process.h"

static void halt() {
    while (1) {
        __asm__ volatile ("hlt");
    }
}

void kernel_main() {
    memory_init();
    screen_init();
    keyboard_init();
    process_init();
    commands_init();

    print_string("Welcome to Flolower-OS!\n");

    char input_buffer[256];

    while (1) {
        for (int i = 0; i < 256; i++)
            input_buffer[i] = 0;

        keyboard_read_line(input_buffer, 256);
        commands_execute(input_buffer);
        schedule();
    }

    halt();
}
