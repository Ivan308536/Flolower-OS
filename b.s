.section .multiboot, "a"
.align 8
multiboot_header_start:
    .long 0xe85250d6
    .long 0
    .long multiboot_header_end - multiboot_header_start
    .long 0x100000000 - (0xe85250d6 + 0 + (multiboot_header_end - multiboot_header_start))

    .align 8
    .short 0
    .short 0
    .long 8
multiboot_header_end:

.section .bss
.align 4096
boot_pml4:
    .skip 4096
boot_pdpt:
    .skip 4096
boot_pd0:
    .skip 4096

.align 16
stack_bottom:
    .skip 32768
stack_top:

.section .data
.align 8
gdt64:
    .quad 0x0000000000000000
    .quad 0x00AF9A000000FFFF
    .quad 0x00CF92000000FFFF
gdt64_ptr:
    .short . - gdt64 - 1
    .quad gdt64

.section .text
.code32
.global _start
_start:
    mov $stack_top, %esp

    mov $boot_pdpt, %eax
    or $0x3, %eax
    mov %eax, (boot_pml4)

    mov $boot_pd0, %eax
    or $0x3, %eax
    mov %eax, (boot_pdpt)

    mov $0x83, %eax
    mov %eax, (boot_pd0)

    mov %cr4, %eax
    or $0x20, %eax
    mov %eax, %cr4

    mov $boot_pml4, %eax
    mov %eax, %cr3

    mov $0xC0000080, %ecx
    rdmsr
    or $0x100, %eax
    wrmsr

    mov %cr0, %eax
    or $0x80000001, %eax
    mov %eax, %cr0

    lgdt gdt64_ptr
    ljmp $0x08, $start64

.code64
start64:
    mov $0x10, %ax
    mov %ax, %ds
    mov %ax, %es
    mov %ax, %fs
    mov %ax, %gs
    mov %ax, %ss

    .extern kernel_main
    call kernel_main

hang:
    hlt
    jmp hang
