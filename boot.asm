; boot.asm - MBR bootloader with FAT12 filesystem support
[org 0x7c00]
[bits 16]

%define KERNEL_LOAD_SEGMENT  0x1000
%define KERNEL_LOAD_OFFSET   0x0000
%define KERNEL_FILENAME      "KERNEL  BIN"
%define EXE_SIGNATURE        0x5A4D  ; "MZ" signature

start:
    cli
    xor ax, ax
    mov ds, ax
    mov es, ax
    mov ss, ax
    mov sp, 0x7c00
    sti

    mov [boot_drive], dl    ; Save boot drive

    ; Print boot message
    mov si, msg_boot
    call print_string

    ; Load FAT12 root directory
    call load_root_directory

    ; Find and load kernel
    mov si, kernel_filename
    call find_file
    jc kernel_not_found

    ; Load kernel to 0x1000:0x0000
    mov ax, KERNEL_LOAD_SEGMENT
    mov es, ax
    mov bx, KERNEL_LOAD_OFFSET
    call load_file
    jc kernel_load_error

    ; Jump to kernel
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

; === FAT12 Filesystem Functions ===

load_root_directory:
    ; Calculate root directory size and location
    mov ax, 19          ; Root directory starts at sector 19
    mov cx, 14          ; 14 sectors for root directory
    mov bx, buffer      ; Load to buffer
    call read_sectors
    ret

find_file:
    ; Search for filename in root directory
    ; Input: SI = filename (11 chars)
    ; Output: CF=0 if found, AX=cluster
    pusha
    mov di, buffer      ; Root directory buffer
    
.search_loop:
    cmp byte [di], 0    ; End of directory?
    je .not_found
    
    mov cx, 11          ; Compare 11 chars
    push si
    push di
    repe cmpsb
    pop di
    pop si
    je .found
    
    add di, 32          ; Next directory entry
    jmp .search_loop

.found:
    mov ax, [di + 26]   ; Get first cluster
    popa
    clc
    ret

.not_found:
    popa
    stc
    ret

load_file:
    ; Load file to ES:BX
    ; Input: AX = first cluster
    pusha
    mov [current_cluster], ax

.load_cluster:
    ; Convert cluster to LBA
    mov ax, [current_cluster]
    sub ax, 2
    mov cx, 1           ; Sectors per cluster
    mul cx
    add ax, 33          ; First data sector
    
    ; Read cluster
    mov cx, 1
    call read_sectors
    
    ; Calculate next cluster
    mov ax, [current_cluster]
    mov cx, ax
    mov dx, ax
    shr dx, 1           ; Divide by 2
    add cx, dx          ; 1.5 * cluster
    
    mov si, buffer
    add si, cx
    mov ax, [si]        ; Read FAT entry
    
    test word [current_cluster], 1
    jnz .odd_cluster
    
.even_cluster:
    and ax, 0x0FFF      ; Even cluster
    jmp .check_end
    
.odd_cluster:
    shr ax, 4           ; Odd cluster

.check_end:
    cmp ax, 0x0FF8      ; End of chain?
    jae .done
    
    mov [current_cluster], ax
    add bx, 512         ; Next memory location
    jmp .load_cluster

.done:
    popa
    clc
    ret

; === Disk I/O Functions ===

read_sectors:
    ; Read sectors from disk
    ; Input: AX = LBA, CX = count, ES:BX = buffer
    pusha
    
    mov [lba_sector], ax
    mov [sector_count], cx
    
    ; Convert LBA to CHS
    mov ax, [lba_sector]
    mov cx, 18          ; Sectors per track
    xor dx, dx
    div cx              ; AX = track, DX = sector (0-based)
    
    mov ch, al          ; Cylinder
    mov cl, dl          ; Sector (0-based)
    inc cl              ; Sectors are 1-based in INT 13h
    
    mov ax, [lba_sector]
    mov bl, 36          ; Heads per cylinder
    div bl              ; AL = cylinder, AH = head
    
    mov dh, ah          ; Head
    mov dl, [boot_drive] ; Drive
    
    mov ax, [sector_count]
    
.read:
    mov ah, 0x02        ; Read sectors
    mov al, 1           ; Read one sector at a time
    int 0x13
    jc .error
    
    add bx, 512         ; Next buffer
    inc word [lba_sector] ; Next sector
    dec word [sector_count]
    jnz .read
    
    popa
    clc
    ret

.error:
    popa
    stc
    ret

; === Utility Functions ===

print_string:
    ; Print null-terminated string
    ; Input: SI = string
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

; === Data Section ===
msg_boot                db "PyBoot -> Loading kernel...", 13, 10, 0
msg_kernel_loaded       db "Kernel loaded successfully!", 13, 10, 0
msg_kernel_not_found    db "Error: Kernel not found!", 13, 10, 0
msg_kernel_error        db "Error: Kernel load failed!", 13, 10, 0
kernel_filename         db "KERNEL  BIN"

boot_drive              db 0
current_cluster         dw 0
lba_sector              dw 0
sector_count            dw 0

; Fill to 510 bytes
times 510-($-$$) db 0
dw 0xAA55

; Buffer for filesystem operations
buffer:
