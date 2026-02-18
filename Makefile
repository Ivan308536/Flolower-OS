CC = gcc
AS = as
LD = ld

CFLAGS = -m64 -c -std=gnu99 -ffreestanding -O2 -Wall -Wextra \
         -mcmodel=large -mno-red-zone -mno-mmx -mno-sse -mno-sse2

LDFLAGS = -n -T linker.ld --no-warn-rwx-segments

BIN = fos.bin
ISO = flolower-os.iso
OBJS = b.o kernel.o ata.o panic.o

.PHONY: all clean

all: $(ISO)

$(ISO): $(BIN)
	mkdir -p isodir/boot/grub
	cp $(BIN) isodir/boot/$(BIN)
	cp info.txt isodir/boot/grub/info.txt
	cp grub.cfg isodir/boot/grub/grub.cfg
	grub-mkrescue -o $(ISO) isodir

$(BIN): $(OBJS)
	$(LD) $(LDFLAGS) -o $@ $(OBJS)

b.o: b.s
	$(AS) $< -o $@

kernel.o: kernel.c ata.h panic.h
	$(CC) $(CFLAGS) $< -o $@

panic.o: panic.c panic.h
	$(CC) $(CFLAGS) $< -o $@

ata.o: ata.c ata.h
	$(CC) $(CFLAGS) $< -o $@

clean:
	rm -rf *.o $(BIN) $(ISO) isodir
