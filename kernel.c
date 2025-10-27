#include <stdint.h>

// Multiboot заголовок
#define MULTIBOOT_HEADER_MAGIC 0x1BADB002
#define MULTIBOOT_HEADER_FLAGS 0x00000003
#define CHECKSUM -(MULTIBOOT_HEADER_MAGIC + MULTIBOOT_HEADER_FLAGS)

__attribute__((section(".multiboot")))
const uint32_t multiboot_header[] = {
    MULTIBOOT_HEADER_MAGIC,
    MULTIBOOT_HEADER_FLAGS,
    CHECKSUM
};

// Структура исполняемого файла
struct ExecHeader {
    uint32_t magic;          // 0xDEADBEEF
    uint32_t entry_point;    // Точка входа
    uint32_t code_size;      // Размер кода
    uint32_t data_size;      // Размер данных
    uint32_t stack_size;     // Размер стека
};

// Константы
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

// Функции VGA
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
        // Простой скролл
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

// === ВАША ФАЙЛОВАЯ СИСТЕМА ===

struct File {
    const char* name;
    const uint8_t* data;
    uint32_t size;
    bool is_executable;
};

// Пример исполняемого файла (простая программа)
const uint8_t test_exe_data[] = {
    // Заголовок ExecHeader
    0xEF, 0xBE, 0xAD, 0xDE, // magic = 0xDEADBEEF
    0x00, 0x00, 0x20, 0x00, // entry_point = 0x200000
    0x30, 0x00, 0x00, 0x00, // code_size = 48 bytes
    0x00, 0x00, 0x00, 0x00, // data_size = 0
    0x00, 0x10, 0x00, 0x00, // stack_size = 4096
    
    // Код программы (просто возвращает управление)
    0x60,                   // pusha
    0xB8, 0x48, 0x65, 0x6C, 0x6C, 0x6F, // mov eax, 'Hello'
    0xBB, 0x00, 0x80, 0x0B, 0x00,       // mov ebx, 0xB8000
    0x89, 0x03,                         // mov [ebx], eax
    0x61,                               // popa
    0xC3                                // ret
};

// Данные для системных файлов (заглушки)
const uint8_t core_py_data[] = { 
    '#', ' ', 'C', 'o', 'r', 'e', ' ', 'P', 'y', 't', 'h', 'o', 'n', ' ', 's', 'y', 's', 't', 'e', 'm', '\n' 
};

const uint8_t kernel_py_data[] = { 
    '#', ' ', 'K', 'e', 'r', 'n', 'e', 'l', ' ', 'i', 'n', ' ', 'P', 'y', 't', 'h', 'o', 'n', '\n' 
};

const uint8_t boot_asm_data[] = { 
    ';', ' ', 'B', 'o', 'o', 't', 'l', 'o', 'a', 'd', 'e', 'r', ' ', 'c', 'o', 'd', 'e', '\n' 
};

const uint8_t readme_data[] = { 
    'P', 'y', 'O', 'S', ' ', '-', ' ', 'S', 'i', 'm', 'p', 'l', 'e', ' ', 'O', 'S', ' ', 'w', 'i', 't', 'h', ' ', 'P', 'y', 't', 'h', 'o', 'n', '\n' 
};

class VirtualFileSystem {
private:
    File files[16];
    int file_count;

public:
    VirtualFileSystem() : file_count(0) {
        // Инициализируем файловую систему
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
            // Простое сравнение строк (в реальной ОС нужно полное сравнение путей)
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
                // Простой вывод размера
                char size_buf[16];
                const char* digits = "0123456789";
                uint32_t size = files[i].size;
                int pos = 0;
                
                do {
                    size_buf[pos++] = digits[size % 10];
                    size /= 10;
                } while (size > 0 && pos < 15);
                
                // Реверсируем строку
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

// === ЗАГРУЗЧИК EXE ФАЙЛОВ ===

class ExecutableLoader {
private:
    VirtualFileSystem& fs;

    bool validate_header(const ExecHeader* header) {
        if (header->magic != EXEC_MAGIC) {
            print_string("Error: Invalid EXE magic\n", 0x04);
            return false;
        }
        if (header->code_size > 1024 * 1024) { // 1MB max
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
        
        // Читаем заголовок
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
        
        // Загружаем код в память
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
        
        // Получаем точку входа
        ExecHeader header;
        fs.read_file(filename, &header, sizeof(header));
        
        print_string("  Jumping to: ", 0x0E);
        print_hex(header.entry_point, 0x0E);
        print_string("\n", 0x0E);
        
        uint32_t user_stack = USER_STACK_BASE;
        
        // Переход в пользовательский код
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
        
        // В реальной ОС нужно сканировать файловую систему
        // Здесь просто проверяем известные EXE файлы
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

// Глобальные объекты
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
    
    print_string("=== PyOS Kernel ===\n\n", 0x0F);
    
    print_string("Virtual File System Ready!\n\n", 0x0E);
    
    // Показываем содержимое файловой системы
    vfs.list_files();
    
    print_string("\n", 0x0F);
    
    // Демонстрируем работу с EXE файлами
    exec_loader.list_executables();
    
    print_string("\n", 0x0F);
    
    // Запускаем тестовую программу
    if (vfs.file_exists("/test.exe")) {
        print_string("Running test program:\n", 0x0E);
        exec_loader.execute("/test.exe");
    }
    
    print_string("\nKernel execution complete\n", 0x0F);
    print_string("Type 'exec_loader.execute(\"/test.exe\")' to run again\n", 0x08);
    
    while (1) asm volatile("hlt");
}
