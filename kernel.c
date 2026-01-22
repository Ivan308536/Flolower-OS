#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

static const size_t VGA_WIDTH = 80;
static const size_t VGA_HEIGHT = 25;
uint16_t* terminal_buffer = (uint16_t*) 0xB8000;
size_t terminal_row = 0;
size_t terminal_column = 0;
uint8_t terminal_color = 0x02;

static inline uint8_t vga_entry_color(enum vga_color fg, enum vga_color bg) {
	return fg | bg << 4;
}

static inline uint16_t vga_entry(unsigned char uc, uint8_t color) {
	return (uint16_t) uc | (uint16_t) color << 8;
}

size_t strlen(const char* str) {
	size_t len = 0;
	while (str[len]) len++;
	return len;
}

void terminal_putentryat(char c, uint8_t color, size_t x, size_t y) {
	const size_t index = y * VGA_WIDTH + x;
	terminal_buffer[index] = vga_entry(c, color);
}

void terminal_scroll() {
    for (size_t y = 0; y < VGA_HEIGHT - 1; y++) {
        for (size_t x = 0; x < VGA_WIDTH; x++) {
            terminal_buffer[y * VGA_WIDTH + x] = terminal_buffer[(y + 1) * VGA_WIDTH + x];
        }
    }
    for (size_t x = 0; x < VGA_WIDTH; x++) {
        terminal_putentryat(' ', terminal_color, x, VGA_HEIGHT - 1);
    }
    terminal_row = VGA_HEIGHT - 1;
}

void terminal_putchar(char c) {
	if (c == '\n') {
		terminal_column = 0;
		if (++terminal_row == VGA_HEIGHT) terminal_scroll();
	} else if (c == '\b') {
        if (terminal_column > 0) {
            terminal_column--;
            terminal_putentryat(' ', terminal_color, terminal_column, terminal_row);
        }
    } else {
		terminal_putentryat(c, terminal_color, terminal_column, terminal_row);
		if (++terminal_column == VGA_WIDTH) {
			terminal_column = 0;
			if (++terminal_row == VGA_HEIGHT) terminal_scroll();
		}
	}
}

void terminal_write(const char* data) {
	size_t datalen = strlen(data);
	for (size_t i = 0; i < datalen; i++)
		terminal_putchar(data[i]);
}

void terminal_clear() {
    for (size_t y = 0; y < VGA_HEIGHT; y++) {
        for (size_t x = 0; x < VGA_WIDTH; x++) {
            terminal_putentryat(' ', terminal_color, x, y);
        }
    }
    terminal_row = 0;
    terminal_column = 0;
}

static inline uint8_t inb(uint16_t port) {
    uint8_t ret;
    asm volatile ( "inb %1, %0" : "=a"(ret) : "Nd"(port) );
    return ret;
}

int strcmp(const char* s1, const char* s2) {
    while(*s1 && (*s1 == *s2)) {
        s1++; s2++;
    }
    return *(const unsigned char*)s1 - *(const unsigned char*)s2;
}

char input_buffer[256];
int input_index = 0;

char scancode_to_ascii(uint8_t scancode) {
    const char sc_ascii[] = {
        0, 0, '1', '2', '3', '4', '5', '6', '7', '8', '9', '0', '-', '=', '\b',
        '\t', 'q', 'w', 'e', 'r', 't', 'y', 'u', 'i', 'o', 'p', '[', ']', '\n',
        0, 'a', 's', 'd', 'f', 'g', 'h', 'j', 'k', 'l', ';', '\'', '`', 0, '\\',
        'z', 'x', 'c', 'v', 'b', 'n', 'm', ',', '.', '/', 0, '*', 0, ' '
    };
    if (scancode < sizeof(sc_ascii)) return sc_ascii[scancode];
    return 0;
}

void execute_command() {
    terminal_write("\n");
    if (input_index == 0) return;

    if (strcmp(input_buffer, "help") == 0) {
        terminal_write("Available commands Follower OS:\n");
        terminal_write("  help    - Commands menu\n");
        terminal_write("  clear   - Clear shell\n");
        terminal_write("  info    - About Flolower OS\n");
    } 
    else if (strcmp(input_buffer, "clear") == 0) {
        terminal_clear();
        terminal_write("Flolower-OS Terminal v1.0\n");
    }
    else if (strcmp(input_buffer, "info") == 0) {
        terminal_write("Flolower-OS: Terminal v1.0\n");
    }
    else {
        terminal_write("Error: Unknown Command: ");
        terminal_write(input_buffer);
        terminal_write("\n");
    }

    for(int i=0; i<256; i++) input_buffer[i] = 0;
    input_index = 0;
}

void kernel_main(void) {
	terminal_clear();
    terminal_write("=========================================\n");
	terminal_write("         Welcome to Flolower-OS          \n");
    terminal_write("=========================================\n");
    terminal_write("Type 'help' for menu commands.\n\n");
