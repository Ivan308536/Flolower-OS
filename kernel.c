#include <stdint.h>

#define MULTIBOOT_HEADER_MAGIC 0x1BADB002
#define MULTIBOOT_HEADER_FLAGS 0x00000003
#define CHECKSUM -(MULTIBOOT_HEADER_MAGIC + MULTIBOOT_HEADER_FLAGS)

__attribute__((section(".multiboot")))
const uint32_t multiboot_header[] = {
    MULTIBOOT_HEADER_MAGIC,
    MULTIBOOT_HEADER_FLAGS,
    CHECKSUM
};

struct ExecHeader {
    uint32_t magic;
    uint32_t entry_point;
    uint32_t code_size;
    uint32_t data_size;
    uint32_t stack_size;
};

#define EXEC_MAGIC 0xDEADBEEF
#define EXEC_MEMORY_BASE 0x100000
#define USER_STACK_BASE  0x800000

extern "C" {
    typedef void (*constructor_func)();
    extern constructor_func __init_array_start[];
    extern constructor_func __init_array_end[];
}

// VGA
volatile uint16_t* video_memory = (volatile uint16_t*)0xB8000;
const int VGA_WIDTH = 80;
const int VGA_HEIGHT = 25;
int cursor_x = 0;
int cursor_y = 0;

// VGA Fun
void clear_screen() {
    for (int y = 0; y < VGA_HEIGHT; y++) {
        for (int x = 0; x < VGA_WIDTH; x++) {
            video_memory[y * VGA_WIDTH + x] = 0x0F00 | ' ';
        }
    }
    cursor_x = cursor_y = 0;
}

void print_char(char c, uint8_t color = 0x0F) {
    if (c == '\n') {
        cursor_x = 0;
        cursor_y++;
    } else {
        video_memory[cursor_y * VGA_WIDTH + cursor_x] = (color << 8) | c;
        cursor_x++;
    }
    
    if (cursor_x >= VGA_WIDTH) {
        cursor_x = 0;
        cursor_y++;
    }
    if (cursor_y >= VGA_HEIGHT) {
        cursor_y = VGA_HEIGHT - 1;
        for (int y = 0; y < VGA_HEIGHT - 1; y++) {
            for (int x = 0; x < VGA_WIDTH; x++) {
                video_memory[y * VGA_WIDTH + x] = video_memory[(y + 1) * VGA_WIDTH + x];
            }
        }
        for (int x = 0; x < VGA_WIDTH; x++) {
            video_memory[(VGA_HEIGHT - 1) * VGA_WIDTH + x] = 0x0F00 | ' ';
        }
    }
}

void print_string(const char* str, uint8_t color = 0x0F) {
    while (*str) print_char(*str++, color);
}

void print_hex(uint32_t n, uint8_t color = 0x0F) {
    char buf[9];
    const char* hex = "0123456789ABCDEF";
    for (int i = 7; i >= 0; i--) {
        buf[i] = hex[n & 0xF];
        n >>= 4;
    }
    buf[8] = 0;
    print_string("0x", color);
    print_string(buf, color);
}

// FS

struct File {
    const char* name;
    const uint8_t* data;
    uint32_t size;
    bool is_executable;
};

const uint8_t test_exe_data[] = {
    0xEF, 0xBE, 0xAD, 0xDE,
    0x00, 0x00, 0x20, 0x00,
    0x30, 0x00, 0x00, 0x00,
    0x00, 0x00, 0x00, 0x00,
    0x00, 0x10, 0x00, 0x00,
    
    0x60,
    0xB8, 0x48, 0x65, 0x6C, 0x6C, 0x6F, // mov eax, 'Hello'
    0xBB, 0x00, 0x80, 0x0B, 0x00,       // mov ebx, 0xB8000
    0x89, 0x03,                         // mov [ebx], eax
    0x61,                               // popa
    0xC3                                // ret
};

class VirtualFileSystem {
private:
    File files[16];
    int file_count;

public:
    VirtualFileSystem() : file_count(0) {
        add_file("/system/", nullptr, 0, false);
        add_file("/temp/", nullptr, 0, false);
        add_file("/system/core.py", core_py_data, sizeof(core_py_data), false);
        add_file("/system/kernel.py", kernel_py_data, sizeof(kernel_py_data), false);
        add_file("/system/boot.asm", boot_asm_data, sizeof(boot_asm_data), false);
        add_file("/README.md", readme_data, sizeof(readme_data), false);
        add_file("/test.exe", test_exe_data, sizeof(test_exe_data), true);
    }

    void add_file(const char* name, const uint8_t* data, uint32_t size, bool executable) {
        if (file_count < 16) {
            files[file_count].name = name;
            files[file_count].data = data;
            files[file_count].size = size;
            files[file_count].is_executable = executable;
            file_count++;
        }
    }

    File* find_file(const char* filename) {
        for (int i = 0; i < file_count; i++) {
            const char* fname = files[i].name;
            const char* search = filename;
            
            while (*fname && *search && *fname == *search) {
                fname++;
                search++;
            }
            
            if (*fname == 0 && *search == 0) {
                return &files[i];
            }
        }
        return nullptr;
    }

    bool file_exists(const char* filename) {
        return find_file(filename) != nullptr;
    }

    void list_files() {
        print_string("File System Contents:\n", 0x0E);
        print_string("=====================\n", 0x0E);
        
        for (int i = 0; i < file_count; i++) {
            print_string("  ", 0x0F);
            print_string(files[i].name, 0x0F);
            
            if (files[i].is_executable) {
                print_string(" [EXE]", 0x0A);
            } else if (files[i].data == nullptr) {
                print_string(" [DIR]", 0x09);
            } else {
                print_string(" [FILE]", 0x0B);
            }
            
            if (files[i].data != nullptr) {
                print_string(" (", 0x08);
                char size_buf[16];
                const char* digits = "0123456789";
                uint32_t size = files[i].size;
                int pos = 0;
                
                do {
                    size_buf[pos++] = digits[size % 10];
                    size /= 10;
                } while (size > 0 && pos < 15);
                
                for (int j = 0; j < pos / 2; j++) {
                    char temp = size_buf[j];
                    size_buf[j] = size_buf[pos - 1 - j];
                    size_buf[pos - 1 - j] = temp;
                }
                
                size_buf[pos] = 'B';
                size_buf[pos + 1] = ')';
                size_buf[pos + 2] = 0;
                print_string(size_buf, 0x08);
            }
            
            print_string("\n", 0x0F);
        }
    }

    int read_file(const char* filename, void* buffer, uint32_t max_size) {
        File* file = find_file(filename);
        if (!file || !file->data) {
            return -1;
        }
        
        uint32_t bytes_to_copy = file->size;
        if (bytes_to_copy > max_size) {
            bytes_to_copy = max_size;
        }
        
        const uint8_t* src = file->data;
        uint8_t* dest = (uint8_t*)buffer;
        
        for (uint32_t i = 0; i < bytes_to_copy; i++) {
            dest[i] = src[i];
        }
        
        return bytes_to_copy;
    }
};

class ExecutableLoader {
private:
    VirtualFileSystem& fs;

    bool validate_header(const ExecHeader* header) {
        if (header->magic != EXEC_MAGIC) {
            print_string("Error: Invalid EXE magic\n", 0x04);
            return false;
        }
        if (header->code_size > 1024 * 1024) { // 1 MB
            print_string("Error: Code too large\n", 0x04);
            return false;
        }
        return true;
    }

public:
    ExecutableLoader(VirtualFileSystem& filesystem) : fs(filesystem) {}

    int load_executable(const char* filename) {
        print_string("Loading EXE: ", 0x0E);
        print_string(filename, 0x0E);
        print_string("\n", 0x0E);
        
        File* file = fs.find_file(filename);
        if (!file) {
            print_string("Error: File not found\n", 0x04);
            return -1;
        }
        
        if (!file->is_executable) {
            print_string("Error: Not an executable file\n", 0x04);
            return -1;
        }
        
        ExecHeader header;
        if (fs.read_file(filename, &header, sizeof(header)) != sizeof(header)) {
            print_string("Error: Cannot read EXE header\n", 0x04);
            return -1;
        }
        
        if (!validate_header(&header)) {
            return -1;
        }
        
        print_string("  Entry point: ", 0x0F);
        print_hex(header.entry_point, 0x0A);
        print_string("\n  Code size: ", 0x0F);
        print_hex(header.code_size, 0x0A);
        print_string(" bytes\n", 0x0F);
        
        uint8_t* code_dest = (uint8_t*)header.entry_point;
        int bytes_read = fs.read_file(filename, code_dest, header.code_size);
        
        if (bytes_read != (int)header.code_size) {
            print_string("Error: Failed to load code\n", 0x04);
            return -1;
        }
        
        print_string("  Code loaded at: ", 0x0F);
        print_hex((uint32_t)code_dest, 0x0A);
        print_string("\n", 0x0F);
        
        return 0;
    }
    
    void execute(const char* filename) {
        print_string("Executing: ", 0x0A);
        print_string(filename, 0x0A);
        print_string("\n", 0x0A);
        
        if (load_executable(filename) != 0) {
            print_string("Execution failed\n", 0x04);
            return;
        }
        
        ExecHeader header;
        fs.read_file(filename, &header, sizeof(header));
        
        print_string("  Jumping to: ", 0x0E);
        print_hex(header.entry_point, 0x0E);
        print_string("\n", 0x0E);
        
        uint32_t user_stack = USER_STACK_BASE;
        
        asm volatile(
            "mov %0, %%esp\n\t"
            "mov %0, %%ebp\n\t"
            "call *%1\n\t"
            :
            : "r"(user_stack), "r"(header.entry_point)
            : "memory"
        );
        
        print_string("Program returned successfully\n", 0x0A);
    }
    
    void list_executables() {
        print_string("Executable files:\n", 0x0E);
        bool found = false;
        
        const char* exe_files[] = {"/test.exe", nullptr};
        
        for (int i = 0; exe_files[i] != nullptr; i++) {
            if (fs.file_exists(exe_files[i])) {
                print_string("  ", 0x0F);
                print_string(exe_files[i], 0x0F);
                print_string("\n", 0x0F);
                found = true;
            }
        }
        
        if (!found) {
            print_string("  No executable files found\n", 0x08);
        }
    }
};

VirtualFileSystem vfs;
ExecutableLoader exec_loader(vfs);

static void call_constructors() {
    for (auto constructor = __init_array_start; constructor < __init_array_end; constructor++) {
        (*constructor)();
    }
}

extern "C" void _start() {
    asm volatile("mov $0x90000, %esp");
    asm volatile("mov $0x90000, %ebp");
    
    call_constructors();
    kmain();
    
    while (1) asm volatile("hlt");
}

extern "C" void kmain() {
    clear_screen();
    
    print_string("=== Kernel ===\n\n", 0x0F);
    
    print_string("Virtual File System Ready!\n\n", 0x0E);
    
    vfs.list_files();
    
    print_string("\n", 0x0F);
    
    exec_loader.list_executables();
    
    print_string("\n", 0x0F);
    
    print_string("\nKernel execution complete\n", 0x0F);
    
    while (1) asm volatile("hlt");
}
