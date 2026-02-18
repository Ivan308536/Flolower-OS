#ifndef PANIC_H
#define PANIC_H

void kernel_panic(const char* component, const char* reason, const char* suggestion);

#endif
