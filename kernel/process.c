#include "process.h"

#define MAX_PROCESSES 8

typedef struct {
    void (*entry)();
    int active;
} process_t;

static process_t processes[MAX_PROCESSES];
static int current = 0;

void process_init() {
    for (int i = 0; i < MAX_PROCESSES; i++)
        processes[i].active = 0;
}

void process_create(void (*entry)()) {
    for (int i = 0; i < MAX_PROCESSES; i++) {
        if (!processes[i].active) {
            processes[i].entry = entry;
            processes[i].active = 1;
            break;
        }
    }
}

void schedule() {
    current = (current + 1) % MAX_PROCESSES;
    if (processes[current].active)
        processes[current].entry();
}

void task_a() {
    volatile char* v = (char*)0xB8000;
    v[0] = 'A';
    v[1] = 0x0F;
}

void task_b() {
    volatile char* v = (char*)0xB8000;
    v[2] = 'B';
    v[3] = 0x0F;
}
