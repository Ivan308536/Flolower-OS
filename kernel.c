#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

enum vga_color {
    VGA_COLOR_BLACK = 0,
    VGA_COLOR_BLUE = 1,
    VGA_COLOR_GREEN = 2,
    VGA_COLOR_CYAN = 3,
    VGA_COLOR_RED = 4,
    VGA_COLOR_MAGENTA = 5,
    VGA_COLOR_BROWN = 6,
    VGA_COLOR_LIGHT_GREY = 7,
    VGA_COLOR_DARK_GREY = 8,
    VGA_COLOR_LIGHT_BLUE = 9,
    VGA_COLOR_LIGHT_GREEN = 10,
    VGA_COLOR_LIGHT_CYAN = 11,
    VGA_COLOR_LIGHT_RED = 12,
    VGA_COLOR_LIGHT_MAGENTA = 13,
    VGA_COLOR_LIGHT_BROWN = 14,
    VGA_COLOR_WHITE = 15,
};

static const size_t VGA_WIDTH = 80;
static const size_t VGA_HEIGHT = 25;
uint16_t* terminal_buffer = (uint16_t*) 0xB8000;
size_t terminal_row = 0;
size_t terminal_column = 0;
uint8_t terminal_color;

#define HISTORY_SIZE 16
#define CMD_MAX_LEN 256

char command_history[HISTORY_SIZE][CMD_MAX_LEN];
int history_count = 0;
int history_index = -1;

typedef struct {
    char signature[8];
    uint8_t checksum;
    char oem_id[6];
    uint8_t revision;
    uint32_t rsdt_address;
} __attribute__((packed)) RSDP;

typedef struct {
    char signature[4];
    uint32_t length;
    uint8_t revision;
    uint8_t checksum;
    char oem_id[6];
    char oem_table_id[8];
    uint32_t oem_revision;
    uint32_t creator_id;
    uint32_t creator_revision;
} __attribute__((packed)) ACPISDTHeader;

typedef struct {
    ACPISDTHeader header;
    uint32_t entry[];
} __attribute__((packed)) RSDT;

typedef struct {
    ACPISDTHeader header;
    uint32_t firmware_ctrl;
    uint32_t dsdt;
    uint8_t reserved;
    uint8_t preferred_pm_profile;
    uint16_t sci_interrupt;
    uint32_t smi_command_port;
    uint8_t acpi_enable;
    uint8_t acpi_disable;
    uint8_t s4bios_req;
    uint8_t pstate_control;
    uint32_t pm1a_event_block;
    uint32_t pm1b_event_block;
    uint32_t pm1a_control_block;
    uint32_t pm1b_control_block;
    uint32_t pm2_control_block;
    uint32_t pm_timer_block;
    uint32_t gpe0_block;
    uint32_t gpe1_block;
    uint8_t pm1_event_length;
    uint8_t pm1_control_length;
    uint8_t pm2_control_length;
    uint8_t pm_timer_length;
    uint8_t gpe0_length;
    uint8_t gpe1_length;
    uint8_t gpe1_base;
    uint8_t cstate_control;
    uint16_t worst_c2_latency;
    uint16_t worst_c3_latency;
    uint16_t flush_size;
    uint16_t flush_stride;
    uint8_t duty_offset;
    uint8_t duty_width;
    uint8_t day_alarm;
    uint8_t month_alarm;
    uint8_t century;
    uint16_t boot_arch_flags;
    uint8_t reserved2;
    uint32_t flags;
} __attribute__((packed)) FADT;

static inline uint8_t vga_entry_color(enum vga_color fg, enum vga_color bg) {
    return fg | bg << 4;
}

static inline uint16_t vga_entry(unsigned char uc, uint8_t color) {
    return (uint16_t) uc | (uint16_t) color << 8;
}

static inline void outb(uint16_t port, uint8_t val) {
    asm volatile ("outb %0, %1" : : "a"(val), "Nd"(port));
}

static inline uint8_t inb(uint16_t port) {
    uint8_t ret;
    asm volatile ("inb %1, %0" : "=a"(ret) : "Nd"(port));
    return ret;
}

static inline void outw(uint16_t port, uint16_t val) {
    asm volatile ("outw %0, %1" : : "a"(val), "Nd"(port));
}

static inline uint16_t inw(uint16_t port) {
    uint16_t ret;
    asm volatile ("inw %1, %0" : "=a"(ret) : "Nd"(port));
    return ret;
}

static inline void outl(uint16_t port, uint32_t val) {
    asm volatile ("outl %0, %1" : : "a"(val), "Nd"(port));
}

static inline uint32_t inl(uint16_t port) {
    uint32_t ret;
    asm volatile ("inl %1, %0" : "=a"(ret) : "Nd"(port));
    return ret;
}

void update_cursor(int x, int y) {
    uint16_t pos = y * VGA_WIDTH + x;
    outb(0x3D4, 0x0F);
    outb(0x3D5, (uint8_t) (pos & 0xFF));
    outb(0x3D4, 0x0E);
    outb(0x3D5, (uint8_t) ((pos >> 8) & 0xFF));
}

void enable_cursor(uint8_t cursor_start, uint8_t cursor_end) {
    outb(0x3D4, 0x0A);
    outb(0x3D5, (inb(0x3D5) & 0xC0) | cursor_start);
    outb(0x3D4, 0x0B);
    outb(0x3D5, (inb(0x3D5) & 0xE0) | cursor_end);
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

void terminal_clear() {
    for (size_t y = 0; y < VGA_HEIGHT; y++) {
        for (size_t x = 0; x < VGA_WIDTH; x++) {
            terminal_putentryat(' ', terminal_color, x, y);
        }
    }
    terminal_row = 0;
    terminal_column = 0;
    update_cursor(terminal_column, terminal_row);
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
    update_cursor(terminal_column, terminal_row);
}

void terminal_write(const char* data) {
    for (size_t i = 0; i < strlen(data); i++)
        terminal_putchar(data[i]);
}

int strcmp(const char* s1, const char* s2) {
    while(*s1 && (*s1 == *s2)) {
        s1++; s2++;
    }
    return *(const unsigned char*)s1 - *(const unsigned char*)s2;
}

void strcpy(char* dest, const char* src) {
    while (*src) {
        *dest++ = *src++;
    }
    *dest = '\0';
}

void itoa(int num, char* str, int base) {
    int i = 0;
    bool isNegative = false;
    
    if (num == 0) {
        str[i++] = '0';
        str[i] = '\0';
        return;
    }
    
    if (num < 0 && base == 10) {
        isNegative = true;
        num = -num;
    }
    
    while (num != 0) {
        int rem = num % base;
        str[i++] = (rem > 9) ? (rem - 10) + 'A' : rem + '0';
        num = num / base;
    }
    
    if (isNegative)
        str[i++] = '-';
    
    str[i] = '\0';
    
    int start = 0;
    int end = i - 1;
    while (start < end) {
        char temp = str[start];
        str[start] = str[end];
        str[end] = temp;
        start++;
        end--;
    }
}

RSDP* find_rsdp() {
    volatile uint16_t* ptr = (volatile uint16_t*)0x40E;
    uintptr_t ebda = (uintptr_t)(*ptr) << 4;
    
    for (uintptr_t addr = ebda; addr < ebda + 1024; addr += 16) {
        if (*(uint64_t*)addr == 0x2052545020445352ULL) {
            return (RSDP*)addr;
        }
    }
    
    for (uintptr_t addr = 0xE0000; addr < 0x100000; addr += 16) {
        if (*(uint64_t*)addr == 0x2052545020445352ULL) {
            return (RSDP*)addr;
        }
    }
    
    return NULL;
}

FADT* find_fadt(RSDT* rsdt) {
    int entries = (rsdt->header.length - sizeof(ACPISDTHeader)) / 4;
    
    for (int i = 0; i < entries; i++) {
        ACPISDTHeader* header = (ACPISDTHeader*)(uintptr_t)rsdt->entry[i];
        if (header->signature[0] == 'F' && 
            header->signature[1] == 'A' && 
            header->signature[2] == 'C' && 
            header->signature[3] == 'P') {
            return (FADT*)header;
        }
    }
    
    return NULL;
}

void acpi_shutdown() {
    terminal_write("Initializing ACPI shutdown...\n");
    
    RSDP* rsdp = find_rsdp();
    if (!rsdp) {
        terminal_write("ACPI not supported - trying legacy methods...\n");
        goto legacy_shutdown;
    }
    
    RSDT* rsdt = (RSDT*)(uintptr_t)rsdp->rsdt_address;
    FADT* fadt = find_fadt(rsdt);
    
    if (!fadt) {
        terminal_write("FADT not found - trying legacy methods...\n");
        goto legacy_shutdown;
    }
    
    uint32_t pm1a_ctrl = fadt->pm1a_control_block;
    uint32_t pm1b_ctrl = fadt->pm1b_control_block;
    
    terminal_write("Sending ACPI shutdown signal...\n");
    
    uint16_t slp_typa = 5 << 10;
    uint16_t slp_en = 1 << 13;
    
    if (pm1a_ctrl) {
        outw(pm1a_ctrl, slp_typa | slp_en);
    }
    if (pm1b_ctrl) {
        outw(pm1b_ctrl, slp_typa | slp_en);
    }
    
    for (volatile int i = 0; i < 10000000; i++);
    
legacy_shutdown:
    outw(0x604, 0x2000);  // QEMU
    outw(0xB004, 0x2000); // Bochs
    outw(0x4004, 0x3400); // VirtualBox
    
    uint8_t temp;
    do {
        temp = inb(0x64);
        if (temp & 0x01) inb(0x60);
    } while (temp & 0x02);
    outb(0x64, 0xFE);
    
    terminal_write("Shutdown failed. Please power off manually.\n");
    while(1) {
        asm volatile ("hlt");
    }
}

void reboot(void) {
    terminal_write("Rebooting...\n");
    
    uint8_t temp;
    asm volatile ("cli");
    
    do {
        temp = inb(0x64);
        if (temp & 0x01) inb(0x60);
    } while (temp & 0x02);
    
    outb(0x64, 0xFE);
    
    outb(0x92, inb(0x92) | 1);
    
    while(1) {
        asm volatile ("hlt");
    }
}

char input_buffer[256];
int input_index = 0;

void add_to_history(const char* cmd) {
    if (strlen(cmd) == 0) return;
    
    if (history_count < HISTORY_SIZE) {
        strcpy(command_history[history_count], cmd);
        history_count++;
    } else {
        for (int i = 0; i < HISTORY_SIZE - 1; i++) {
            strcpy(command_history[i], command_history[i + 1]);
        }
        strcpy(command_history[HISTORY_SIZE - 1], cmd);
    }
    
    history_index = history_count;
}

void load_from_history(int direction) {
    if (history_count == 0) return;
    
    history_index += direction;
    if (history_index < 0) history_index = 0;
    if (history_index >= history_count) history_index = history_count - 1;
    
    while (input_index > 0) {
        input_index--;
        terminal_putchar('\b');
    }

    strcpy(input_buffer, command_history[history_index]);
    input_index = strlen(input_buffer);
    terminal_write(input_buffer);
    update_cursor(terminal_column, terminal_row);
}

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

    input_buffer[input_index] = '\0';
    add_to_history(input_buffer);

    if (strcmp(input_buffer, "help") == 0) {
        terminal_write("Available commands:\n");
        terminal_write("  help     - Show this menu\n");
        terminal_write("  clear    - Clear terminal\n");
        terminal_write("  info     - System information\n");
        terminal_write("  reboot   - Reboot system\n");
        terminal_write("  off      - Shutdown system\n\n");
    } 
    else if (strcmp(input_buffer, "clear") == 0) {
        terminal_clear();
    }
    else if (strcmp(input_buffer, "info") == 0) {
        terminal_write("Flolower-OS v1.0 x86-64\n");
        terminal_write("Architecture: x86-64 (64-bit)\n");
        terminal_write("Features: ACPI, RAM-based history\n\n");
    }
    else if (strcmp(input_buffer, "reboot") == 0) {
        reboot();
    }
    else if (strcmp(input_buffer, "off") == 0) {
        acpi_shutdown();
    }
    else {
        terminal_write("Unknown command: ");
        terminal_write(input_buffer);
        terminal_write("\nType 'help' for available commands.\n\n");
    }

    input_index = 0;
}

void kernel_main(void) {
    terminal_color = vga_entry_color(VGA_COLOR_WHITE, VGA_COLOR_BLACK);
    
    enable_cursor(13, 15);
    update_cursor(terminal_column, terminal_row);
    terminal_clear();
    
    terminal_write("=== Flolower OS v1.0 ===\n");
    terminal_write("Type 'help' for commands\n\n");
    terminal_write("Flolower> ");

    uint8_t last_scancode = 0;

    while(1) {
        if (inb(0x64) & 1) {
            uint8_t scancode = inb(0x60);
            if (scancode != last_scancode) {
                if (scancode == 0x48) {
                    load_from_history(-1);
                }
                else if (scancode == 0x50) {
                    load_from_history(1);
                }
                else if (!(scancode & 0x80)) {
                    char c = scancode_to_ascii(scancode);
                    if (c == '\n') {
                        execute_command();
                        terminal_write("Flolower> ");
                    } else if (c == '\b') {
                        if (input_index > 0) {
                            input_index--;
                            terminal_putchar('\b');
                        }
                    } else if (c > 0) {
                        if (input_index < 255) {
                            input_buffer[input_index++] = c;
                            terminal_putchar(c);
                        }
                    }
                }
                last_scancode = scancode;
            }
        }
    }
}
