; boot.asm - MBR bootloader with FAT12 filesystem support
[org 0x7c00]
[bits 16]

%define KERNEL_LOAD_SEGMENT  0x1000
%define KERNEL_LOAD_OFFSET   0x0000
%define KERNEL_FILENAME      "KERNEL  BIN"
%define EXE_SIGNATURE        0x5A4D

start:
    cli
    xor ax, ax
    mov ds, ax
    mov es, ax
    mov ss, ax
    mov sp, 0x7c00
    sti

    mov [boot_drive], dl

    mov si, msg_boot
    call print_string

    call load_root_directory

    mov si, kernel_filename
    call find_file
    jc kernel_not_found

    mov ax, KERNEL_LOAD_SEGMENT
    mov es, ax
    mov bx, KERNEL_LOAD_OFFSET
    call load_file
    jc kernel_load_error

    mov si, msg_kernel_loaded
    call print_string
    jmp KERNEL_LOAD_SEGMENT:KERNEL_LOAD_OFFSET

kernel_not_found:
    mov si, msg_kernel_not_found
    call print_string
    jmp hang

kernel_load_error:
    mov si, msg_kernel_error
    call print_string
    jmp hang

load_root_directory:
    mov ax, 19
    mov cx, 14
    mov bx, buffer
    call read_sectors
    ret

find_file:
    pusha
    mov di, buffer
    
.search_loop:
    cmp byte [di], 0
    je .not_found
    
    mov cx, 11
    push si
    push di
    repe cmpsb
    pop di
    pop si
    je .found
    
    add di, 32
    jmp .search_loop

.found:
    mov ax, [di + 26]
    popa
    clc
    ret

.not_found:
    popa
    stc
    ret

load_file:
    pusha
    mov [current_cluster], ax

.load_cluster:
    ; Convert cluster to LBA
    mov ax, [current_cluster]
    sub ax, 2
    mov cx, 1
    mul cx
    add ax, 33
    
    mov cx, 1
    call read_sectors
    
    mov ax, [current_cluster]
    mov cx, ax
    mov dx, ax
    shr dx, 1
    add cx, dx
    
    mov si, buffer
    add si, cx
    mov ax, [si]
    
    test word [current_cluster], 1
    jnz .odd_cluster
    
.even_cluster:
    and ax, 0x0FFF
    jmp .check_end
    
.odd_cluster:
    shr ax, 4

.check_end:
    cmp ax, 0x0FF8
    jae .done
    
    mov [current_cluster], ax
    add bx, 512
    jmp .load_cluster

.done:
    popa
    clc
    ret

read_sectors:
    pusha
    
    mov [lba_sector], ax
    mov [sector_count], cx
    
    mov ax, [lba_sector]
    mov cx, 18
    xor dx, dx
    div cx
    
    mov ch, al
    mov cl, dl
    inc cl
    
    mov ax, [lba_sector]
    mov bl, 36
    div bl
    
    mov dh, ah
    mov dl, [boot_drive]
    
    mov ax, [sector_count]
    
.read:
    mov ah, 0x02
    mov al, 1
    int 0x13
    jc .error
    
    add bx, 512
    inc word [lba_sector]
    dec word [sector_count]
    jnz .read
    
    popa
    clc
    ret

.error:
    popa
    stc
    ret

print_string:
    pusha
.print_char:
    lodsb
    cmp al, 0
    je .done
    mov ah, 0x0E
    mov bh, 0
    mov bl, 7
    int 0x10
    jmp .print_char
.done:
    popa
    ret

hang:
    cli
    hlt
    jmp hang

msg_boot                db "Boot -> Loading kernel...", 13, 10, 0
msg_kernel_loaded       db "Kernel loaded successfully!", 13, 10, 0
msg_kernel_not_found    db "Error: Kernel not found!", 13, 10, 0
msg_kernel_error        db "Error: Kernel load failed!", 13, 10, 0
kernel_filename         db "KERNEL  BIN"

boot_drive              db 0
current_cluster         dw 0
lba_sector              dw 0
sector_count            dw 0

; 510 bytes
times 510-($-$$) db 0
dw 0xAA55

; Buffer for filesystem operations
buffer:
