CC = gcc
AS = as
LD = ld

CFLAGS = -m32 -c -std=gnu99 -ffreestanding -O2 -Wall -Wextra
ASFLAGS = --32
LDFLAGS = -m elf_i386 -T linker.ld

BIN = fos.bin
ISO = flolower-os.iso
OBJS = b.o kernel.o

.PHONY: all clean

all: $(ISO)

$(ISO): $(BIN)
	mkdir -p isodir/boot/grub
	cp $(BIN) isodir/boot/$(BIN)
	@echo 'menuentry "Flolower-OS" {' > isodir/boot/grub/grub.cfg
	@echo '  multiboot /boot/$(BIN)' >> isodir/boot/grub/grub.cfg
	@echo '}' >> isodir/boot/grub/grub.cfg
	grub-mkrescue -o $(ISO) isodir

$(BIN): $(OBJS)
	$(LD) $(LDFLAGS) -o $@ $(OBJS)

b.o: b.s
	$(AS) $(ASFLAGS) $< -o $@

kernel.o: kernel.c
	$(CC) $(CFLAGS) $< -o $@

clean:
	rm -rf *.o $(BIN) $(ISO) isodir
