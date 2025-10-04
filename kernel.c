extern "C" void kmain() {
    // VGA текстовый режим: 0xB8000, 80x25, 2 байта на символ (ASCII + цвет)
    volatile char* video = (volatile char*)0xB8000;
    const char* msg = "Hello from C++ kernel!";
    for(int i = 0; msg[i] != '\0'; i++) {
        video[i*2] = msg[i];      // символ
        video[i*2 + 1] = 0x0F;    // цвет (белый на черном)
    }
    while(1) {
        asm volatile("hlt");      // бесконечный цикл
    }
}
