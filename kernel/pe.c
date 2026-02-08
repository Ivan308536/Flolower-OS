#include "pe.h"
#include "memory.h"

typedef unsigned short u16;
typedef unsigned int u32;

typedef struct {
    u16 e_magic;
    u16 e_cblp;
    u16 e_cp;
    u16 e_crlc;
    u16 e_cparhdr;
    u16 e_minalloc;
    u16 e_maxalloc;
    u16 e_ss;
    u16 e_sp;
    u16 e_csum;
    u16 e_ip;
    u16 e_cs;
    u16 e_lfarlc;
    u16 e_ovno;
    u16 e_res[4];
    u16 e_oemid;
    u16 e_oeminfo;
    u16 e_res2[10];
    u32 e_lfanew;
} dos_header_t;

typedef struct {
    u32 Signature;
} nt_header_t;

typedef struct {
    u16 Machine;
    u16 NumberOfSections;
    u32 TimeDateStamp;
    u32 PointerToSymbolTable;
    u32 NumberOfSymbols;
    u16 SizeOfOptionalHeader;
    u16 Characteristics;
} file_header_t;

typedef struct {
    u16 Magic;
    u8  MajorLinkerVersion;
    u8  MinorLinkerVersion;
    u32 SizeOfCode;
    u32 SizeOfInitializedData;
    u32 SizeOfUninitializedData;
    u32 AddressOfEntryPoint;
    u32 BaseOfCode;
    u32 BaseOfData;
    u32 ImageBase;
} optional_header_t;

int pe_load_and_exec(void* image) {
    dos_header_t* dos = (dos_header_t*)image;
    if (dos->e_magic != 0x5A4D)
        return -1;

    nt_header_t* nt = (nt_header_t*)((u32)image + dos->e_lfanew);
    if (nt->Signature != 0x00004550)
        return -1;

    file_header_t* file = (file_header_t*)((u32)nt + 4);
    optional_header_t* opt = (optional_header_t*)((u32)file + sizeof(file_header_t));

    void (*entry)() = (void (*)())(opt->ImageBase + opt->AddressOfEntryPoint);
    entry();
    return 0;
}
