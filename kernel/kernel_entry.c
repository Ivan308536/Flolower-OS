// kernel.c
//a point of entering a core

void kernel_main(void) {
    //VGA text buffer
    volatile char* vga = (volatile char*)0xB8000;

    vga[0] = 'K';
    vga[1] = 0x07; 
    while (1) {
        __asm__ __volatile__("hlt");
    }
}
