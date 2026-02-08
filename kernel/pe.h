#ifndef PE_H
#define PE_H

#include <stdint.h>

typedef struct {
    uint32_t entry_point;
    uint32_t image_base;
    uint32_t code_base;
} PEInfo;

int pe_load(uint8_t* exe, uint32_t size, PEInfo* info);

#endif
