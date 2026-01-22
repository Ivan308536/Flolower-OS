.section .multiboot
.align 8
multiboot_header_start:
    .long 0xe85250d6
    .long 0
    .long multiboot_header_end - multiboot_header_start
    .long 0x100000000 - (0xe85250d6 + 0 + (multiboot_header_end - multiboot_header_start))

    .short 0
    .short 0
    .long 8
multiboot_header_end:

.section .bss
.align 16
stack_bottom:
    .skip 32768
stack_top:

.align 4096
boot_pml4:
    .skip 4096
boot_pdpt:
    .skip 4096
boot_pd:
    .skip 4096

.section .data
.align 8
gdt64:
    .quad 0x0000000000000000
    .quad 0x00AF9A000000FFFF
    .quad 0x00AF92000000FFFF
gdt64_ptr:
    .word gdt64_ptr - gdt64 - 1
    .quad gdt64

.section .text
.code32
.global _start
.type _start, @function

_start:
    mov $stack_top, %esp
    
    pushfl
    pop %eax
    mov %eax, %ecx
    xor $(1 << 21), %eax
    push %eax
    popfl
    pushfl
    pop %eax
    push %ecx
    popfl
    xor %ecx, %eax
    jz no_long_mode
    
    mov $0x80000000, %eax
    cpuid
    cmp $0x80000001, %eax
    jb no_long_mode
    
    mov $0x80000001, %eax
    cpuid
    test $(1 << 29), %edx
    jz no_long_mode
    
    mov $boot_pdpt, %eax
    or $0x3, %eax  # Present + Writable
    mov %eax, boot_pml4
    
    mov $boot_pd, %eax
    or $0x3, %eax
    mov %eax, boot_pdpt

    mov $0x83, %eax
    mov %eax, boot_pd
    
    mov $boot_pml4, %eax
    mov %eax, %cr3
    
    mov %cr4, %eax
    or $0x20, %eax
    mov %eax, %cr4

    mov $0xC0000080, %ecx
    rdmsr
    or $0x100, %eax
    wrmsr
    
    mov %cr0, %eax
    or $0x80000000, %eax
    mov %eax, %cr0
    
    lgdt gdt64_ptr
    
    ljmp $0x08, $long_mode_start

no_long_mode:
    mov $0xB8000, %edi
    movl $0x4F524F45, (%edi)
    movl $0x4F524F52, 4(%edi)
    hlt

.code64
long_mode_start:
    xor %ax, %ax
    mov %ax, %ds
    mov %ax, %es
    mov %ax, %fs
    mov %ax, %gs
    mov %ax, %ss
    
    mov $stack_top, %rsp
    
    call kernel_main
    
    cli
1:
    hlt
    jmp 1b

.size _start, . - _start
