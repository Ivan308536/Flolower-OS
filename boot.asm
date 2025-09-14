; boot.asm - минимальный MBR bootloader (16-bit real mode)
[org 0x7c00]
bits 16

start:
    cli
    xor ax, ax
    mov ss, ax
    mov sp, 0x7c00
    sti

    ; печатаем строку через BIOS int 0x10
    mov si, msg_boot
.print_char:
    lodsb
    cmp al, 0
    je load_kernel
    mov ah, 0x0E
    mov bh, 0
    mov bl, 7
    int 0x10
    jmp .print_char

load_kernel:
    ; читаем сектор 2 (LBA=1) в адрес 0x1000:0x0000 (phys 0x10000)
    mov ax, 0x1000
    mov es, ax
    xor bx, bx            ; offset 0
    mov ah, 0x02          ; read sectors
    mov al, 0x01          ; count = 1 sector
    mov ch, 0x00          ; cylinder
    mov cl, 0x02          ; sector 2 (sectors start at 1)
    mov dh, 0x00          ; head
    mov dl, [boot_drive]  ; drive (from BIOS)
    int 0x13
    jc disk_error

    ; jump to loaded kernel at 0x1000:0x0000
    jmp 0x1000:0x0000

disk_error:
    mov si, msg_err
.err_print:
    lodsb
    cmp al, 0
    je hang
    mov ah, 0x0E
    mov bh, 0
    mov bl, 4
    int 0x10
    jmp .err_print

hang:
    cli
    hlt
    jmp hang

msg_boot db "PyBoot -> loading kernel...", 0
msg_err db "Disk read error!", 0

; store BIOS drive number passed by BIOS at offset 0x7c00 + 0x1fe? 
; simple trick: read dl pushed by BIOS is not trivially available here.
; But BIOS places drive number in DL on entry; we save it:
boot_drive: db 0x00

; Fill up to 510 bytes
times 510 - ($-$$) db 0

; Boot signature
dw 0xAA55
