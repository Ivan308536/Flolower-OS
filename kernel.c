#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>
#include "ata.h"
#include "panic.h"

size_t strlen(const char* str);
void strcpy(char* dest, const char* src);
void terminal_write(const char* data);
void save_history_to_disk();
void load_history_from_disk();
void memset(void* dest, int val, size_t len);

#define COLOR_BLACK   0x000000
#define COLOR_WHITE   0xFFFFFF
#define COLOR_GREEN   0x00FF00
#define COLOR_RED     0xFF0000
#define COLOR_BLUE    0x0000FF
#define COLOR_GRAY    0x808080
#define HISTORY_START_SECTOR 1000
#define MAX_SEARCH_LIMIT 1000
#define SECTOR_SIZE 512
#define HISTORY_MAGIC 0xDEADBEEF

typedef struct {
    uint32_t magic;
    uint32_t cmd_len;
    char command[504];
} __attribute__((packed)) HistorySector;

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

void update_cursor(int x, int y) {
    uint16_t pos = y * VGA_WIDTH + x;
    outb(0x3D4, 0x0F);
    outb(0x3D5, (uint8_t) (pos & 0xFF));
    outb(0x3D4, 0x0E);
    outb(0x3D5, (uint8_t) ((pos >> 8) & 0xFF));
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

void terminal_putchar(char c) {
    if (c == '\n') {
        terminal_column = 0;
        if (++terminal_row == VGA_HEIGHT) {
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
    } else if (c == '\b') {
        if (terminal_column > 0) {
            terminal_column--;
            terminal_putentryat(' ', terminal_color, terminal_column, terminal_row);
        }
    } else {
        terminal_putentryat(c, terminal_color, terminal_column, terminal_row);
        if (++terminal_column == VGA_WIDTH) {
            terminal_column = 0;
            if (++terminal_row == VGA_HEIGHT) {
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
        }
    }
    update_cursor(terminal_column, terminal_row);
}

void terminal_write(const char* data) {
    for (size_t i = 0; i < strlen(data); i++)
        terminal_putchar(data[i]);
}

bool is_sector_empty(uint8_t* buffer) {
    for (int i = 0; i < SECTOR_SIZE; i++) {
        if (buffer[i] != 0) {
            return false;
        }
    }
    return true;
}

uint32_t find_free_history_sector() {
    uint8_t buffer[SECTOR_SIZE];
    for (uint32_t i = 0; i < MAX_SEARCH_LIMIT; i++) {
        uint32_t current_lba = HISTORY_START_SECTOR + i;
        if (!ata_read_sector(current_lba, buffer)) {
            terminal_write("Disk Read Error!\n");
            return 0;
        }
        HistorySector* sector = (HistorySector*)buffer;
        if (sector->magic == HISTORY_MAGIC) {
            continue;
        }
        if (is_sector_empty(buffer)) {
            return current_lba;
        }
    }
    terminal_write("Disk Full! No free history slots.\n");
    return 0;
}

void delay(uint32_t ms) {
    for(volatile uint32_t i = 0; i < ms * 100000; i++);
}

bool check_cpu() {
    uint32_t eax, edx;
    asm volatile ("cpuid" : "=a"(eax) : "a"(0x80000000) : "ebx", "ecx");
    if (eax < 0x80000001) return false;

    asm volatile ("cpuid" : "=d"(edx) : "a"(0x80000001) : "ebx", "ecx");
    return (edx & (1 << 29)) != 0; 
}

bool check_ata() {
    if (!ata_identify()) return false;
    
    uint8_t buffer[512];
    if (!ata_read_sector(0, buffer)) return false;
    
    for(int i = 0; i < 512; i++) {
        if (buffer[i] != 0) return true;
    }
    return true; 
}

bool check_vga() {
    volatile uint16_t* test_ptr = (volatile uint16_t*)0xB8000;
    uint16_t backup = *test_ptr;
    
    *test_ptr = 0x55AA;
    if (*test_ptr != 0x55AA) return false;
    
    *test_ptr = backup;
    return true;
}

void bootscreen_animate_check(int y, const char* component, bool status, const char* error_msg, const char* fix) {
    const char* frames[] = {" ---  ", " #--  ", " -#-  ", " --#  "};
    uint8_t color_white = vga_entry_color(VGA_COLOR_WHITE, VGA_COLOR_BLACK);
    uint8_t color_green = vga_entry_color(VGA_COLOR_GREEN, VGA_COLOR_BLACK);
    uint8_t color_red = vga_entry_color(VGA_COLOR_RED, VGA_COLOR_BLACK);
    
    int total_width = 30; 
    int start_x = (VGA_WIDTH - total_width) / 2;

    for(int frame = 0; frame < 4; frame++) {
        char buffer[64];
        memset(buffer, ' ', 64);
        
        for(int i = 0; component[i]; i++) buffer[i] = component[i];
        
        buffer[18] = '[';
        for(int i = 0; frames[frame][i]; i++) buffer[19+i] = frames[frame][i];
        buffer[25] = ']';
        buffer[26] = '\0';
        
        for(int i = 0; i < (int)strlen(buffer); i++) {
            terminal_putentryat(buffer[i], color_white, start_x + i, y);
        }
        delay(150);
    }
    
    for(int i = 0; component[i]; i++) terminal_putentryat(component[i], color_white, start_x + i, y);
    
    if(status) {
        const char* ok_msg = "[  OK  ]";
        for(int i = 0; ok_msg[i]; i++) terminal_putentryat(ok_msg[i], color_green, start_x + 18 + i, y);
    } else {
        const char* fail_msg = "[ FAIL ]";
        for(int i = 0; fail_msg[i]; i++) terminal_putentryat(fail_msg[i], color_red, start_x + 18 + i, y);
        delay(500);
        
        kernel_panic(component, error_msg, fix);
    }
}

void show_boot_sequence() {
    terminal_color = vga_entry_color(VGA_COLOR_WHITE, VGA_COLOR_BLACK);
    terminal_clear();

    const char* flolower_art[] = {
        " _____ _   ___  _      _____ _       _____ ____ ",
        "|  ___| |  / _ \\| |    /  _  | |     /  _  |  _ \\",
        "| |_  | |  | | | | |    | | | | |     | | | | |_) |",
        "|  _| | |  | | | | |    | | | | |     | | | |  _ < ",
        "| |   | |__| |_| | |___ | |_| | |___ | |_| | | \\ \\",
        "|_|   |_____\\___/|_____| \\___/|_____| \\___/|_|  \\_\\"
    };

    int art_y = 3;
    int art_x = (VGA_WIDTH - 52) / 2;
    for (int i = 0; i < 6; i++) {
        for (int j = 0; flolower_art[i][j]; j++) {
            terminal_putentryat(flolower_art[i][j], vga_entry_color(VGA_COLOR_LIGHT_CYAN, VGA_COLOR_BLACK), art_x + j, art_y + i);
        }
        delay(50); 
    }

    int center_y = 12;
    
    bool cpu_ok = check_cpu();
    bootscreen_animate_check(center_y, "CPUID", cpu_ok, 
        "Processor does not support x86_64 or long mode", 
        "Upgrade your processor to a newer x86-x64 (long mode)");
    delay(200);

    bool vga_ok = check_vga();
    bootscreen_animate_check(center_y + 1, "VGA Buffer", vga_ok, 
        "Cannot write to video memory at 0xB8000", 
        "Ensure VGA device is initialized in BIOS/UEFI");
    delay(200);

    bool ata_ok = check_ata();
    bootscreen_animate_check(center_y + 2, "ATA Primary", ata_ok, 
        "No IDE drive found or controller not responding", 
        "Check your disk to see if it is full or if there are any problems with it.");
    delay(200);

    extern uint64_t stack_top;
    bool mem_ok = (&stack_top != NULL);
    bootscreen_animate_check(center_y + 3, "Memory Stack", mem_ok, 
        "Kernel stack pointer is invalid (NULL)", 
        "Verify bootloader memory map and b.s alignment");

    delay(500);
    const char* success_msg = "Starting fos.bin...";
    delay(2000);
    int s_x = (VGA_WIDTH - strlen(success_msg)) / 2;
    for(int i=0; i<(int)strlen(success_msg); i++) 
        terminal_putentryat(success_msg[i], vga_entry_color(VGA_COLOR_GREEN, VGA_COLOR_BLACK), s_x + i, center_y + 6);
    
    delay(1500);
    terminal_clear();
}

void memset(void* dest, int val, size_t len) {
    unsigned char* ptr = dest;
    while(len-- > 0)
        *ptr++ = val;
}

#define HISTORY_SIZE 256
#define CMD_MAX_LEN 256

char command_history[HISTORY_SIZE][CMD_MAX_LEN];
int history_count = 0;
int history_index = -1;
char current_input_backup[CMD_MAX_LEN];
bool navigating_history = false;

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

int memcmp(const void* s1, const void* s2, size_t n) {
    const unsigned char *p1 = s1, *p2 = s2;
    while(n--) {
        if (*p1 != *p2) return *p1 - *p2;
        p1++; p2++;
    }
    return 0;
}

RSDP* find_rsdp() {
    uintptr_t ebda = (uintptr_t)(*(volatile uint16_t*)0x40E) << 4;
    for (uintptr_t addr = ebda; addr < ebda + 1024; addr += 16) {
        if (memcmp((void*)addr, "RSD PTR ", 8) == 0) return (RSDP*)addr;
    }
    for (uintptr_t addr = 0xE0000; addr < 0x100000; addr += 16) {
        if (*(uint64_t*)addr == 0x2052545020445352ULL) return (RSDP*)addr;
    }
    return NULL;
}

FADT* find_fadt(RSDT* rsdt) {
    int entries = (rsdt->header.length - sizeof(ACPISDTHeader)) / 4;
    for (int i = 0; i < entries; i++) {
        ACPISDTHeader* header = (ACPISDTHeader*)(uintptr_t)rsdt->entry[i];
        if (header->signature[0] == 'F' && header->signature[1] == 'A' && 
            header->signature[2] == 'C' && header->signature[3] == 'P') return (FADT*)header;
    }
    return NULL;
}

void acpi_shutdown() {
    terminal_write("Initializing ACPI shutdown...\n");
    RSDP* rsdp = find_rsdp();
    if (rsdp) {
        RSDT* rsdt = (RSDT*)(uintptr_t)rsdp->rsdt_address;
        FADT* fadt = find_fadt(rsdt);
        if (fadt) {
            outw(fadt->pm1a_control_block, (5 << 10) | (1 << 13));
            if (fadt->pm1b_control_block) outw(fadt->pm1b_control_block, (5 << 10) | (1 << 13));
        }
    }
    outw(0x604, 0x2000); outw(0xB004, 0x2000); outw(0x4004, 0x3400);
    while(1) asm volatile ("hlt");
}

void reboot(void) {
    terminal_write("Rebooting...\n");
    asm volatile ("cli");
    uint8_t temp;
    do { temp = inb(0x64); if (temp & 0x01) inb(0x60); } while (temp & 0x02);
    outb(0x64, 0xFE);
    outb(0x92, inb(0x92) | 1);
    while(1) asm volatile ("hlt");
}

char input_buffer[256];
int input_index = 0;

void save_command_to_disk(const char* cmd) {
    uint32_t free_lba = find_free_history_sector();
    if (free_lba == 0) return;
    HistorySector sector;
    memset(&sector, 0, sizeof(HistorySector));
    sector.magic = HISTORY_MAGIC;
    sector.cmd_len = strlen(cmd);
    strcpy(sector.command, cmd);
    ata_write_sector(free_lba, (uint8_t*)&sector);
}

void load_history_from_disk() {
    uint8_t buffer[SECTOR_SIZE];
    history_count = 0;
    for (uint32_t i = 0; i < MAX_SEARCH_LIMIT; i++) {
        uint32_t current_lba = HISTORY_START_SECTOR + i;
        if (!ata_read_sector(current_lba, buffer)) break;
        HistorySector* sector = (HistorySector*)buffer;
        if (sector->magic == HISTORY_MAGIC && history_count < HISTORY_SIZE) {
            strcpy(command_history[history_count++], sector->command);
        }
    }
    history_index = history_count;
}

void add_to_history(const char* cmd) {
    if (strlen(cmd) == 0) return;
    if (history_count < HISTORY_SIZE) {
        strcpy(command_history[history_count++], cmd);
    } else {
        for (int i = 0; i < HISTORY_SIZE - 1; i++) strcpy(command_history[i], command_history[i + 1]);
        strcpy(command_history[HISTORY_SIZE - 1], cmd);
    }
    history_index = history_count;
    save_command_to_disk(cmd);
}

void load_from_history(int direction) {
    if (history_count == 0) return;
    if (!navigating_history) {
        input_buffer[input_index] = '\0';
        strcpy(current_input_backup, input_buffer);
        history_index = history_count;
        navigating_history = true;
    }
    history_index += direction;
    if (history_index < 0 || history_index >= history_count) {
        history_index = (history_index < 0) ? -1 : history_count;
        navigating_history = false;
        while (input_index > 0) { input_index--; terminal_putchar('\b'); }
        strcpy(input_buffer, current_input_backup);
        input_index = strlen(input_buffer);
        terminal_write(input_buffer);
        return;
    }
    while (input_index > 0) { input_index--; terminal_putchar('\b'); }
    strcpy(input_buffer, command_history[history_index]);
    input_index = strlen(input_buffer);
    terminal_write(input_buffer);
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
        terminal_write("  off      - Shutdown system\n");
//      terminal_write("  panic    - Trigger kernel panic\n\n");
    } else if (strcmp(input_buffer, "clear") == 0) {
        terminal_clear();
    } else if (strcmp(input_buffer, "info") == 0) {
        terminal_write("Flolower-OS v1.0 x86-64\n");
        terminal_write("Architecture: x86-64 (64-bit)\n");
        terminal_write("Features: ACPI, ATA disk-based history, kernel panic\n\n");
    } else if (strcmp(input_buffer, "reboot") == 0) {
        reboot();
    } else if (strcmp(input_buffer, "off") == 0) {
        acpi_shutdown();
//  } else if (strcmp(input_buffer, "panic") == 0) {
//      kernel_panic("User", "Manual panic triggered via command", "Restart the system");
    } else {
        terminal_write("Unknown command: ");
        terminal_write(input_buffer);
        terminal_write("\nType 'help' for available commands.\n\n");
    }
    input_index = 0;
}

void kernel_main(void) {
    show_boot_sequence();
    terminal_color = vga_entry_color(VGA_COLOR_WHITE, VGA_COLOR_BLACK);
    enable_cursor(13, 15);
    terminal_clear();
    if(ata_identify()) load_history_from_disk();
    terminal_write("=== Flolower OS v1.0 ===\n");
    terminal_write("Type 'help' for commands\n\n");
    terminal_write("Flolower> ");
    uint8_t last_scancode = 0;
    while(1) {
        if (inb(0x64) & 1) {
            uint8_t scancode = inb(0x60);
            if (scancode != last_scancode) {
                if (scancode == 0x48) load_from_history(-1);
                else if (scancode == 0x50) load_from_history(1);
                else if (!(scancode & 0x80)) {
                    navigating_history = false;
                    char c = scancode_to_ascii(scancode);
                    if (c == '\n') { execute_command(); terminal_write("Flolower> "); }
                    else if (c == '\b') { if (input_index > 0) { input_index--; terminal_putchar('\b'); } }
                    else if (c > 0 && input_index < 255) { input_buffer[input_index++] = c; terminal_putchar(c); }
                }
                last_scancode = scancode;
            }
        }
    }
}
