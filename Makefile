CC = gcc
AS = as
LD = ld

CFLAGS = -m64 -c -std=gnu99 -ffreestanding -O2 -Wall -Wextra \
         -mcmodel=large -mno-red-zone -mno-mmx -mno-sse -mno-sse2

ASFLAGS = --64
LDFLAGS = -n -T linker.ld --no-warn-rwx-segments

BIN = fos.bin
ISO = flolower-os.iso
OBJS = b.o kernel.o

.PHONY: all clean

all: $(ISO)

$(ISO): $(BIN)
	mkdir -p isodir/boot/grub
	cp $(BIN) isodir/boot/$(BIN)
	@echo 'set timeout=10' > isodir/boot/grub/grub.cfg
	@echo 'set default=0' >> isodir/boot/grub/grub.cfg
	@echo '' >> isodir/boot/grub/grub.cfg
	@echo 'menuentry "Flolower OS (RAM)" {' >> isodir/boot/grub/grub.cfg
	@echo '  multiboot2 /boot/$(BIN)' >> isodir/boot/grub/grub.cfg
	@echo '  boot' >> isodir/boot/grub/grub.cfg
	@echo '}' >> isodir/boot/grub/grub.cfg
	@echo '' >> isodir/boot/grub/grub.cfg
	@echo 'menuentry "Reboot System" {' >> isodir/boot/grub/grub.cfg
	@echo '  reboot' >> isodir/boot/grub/grub.cfg
	@echo '}' >> isodir/boot/grub/grub.cfg
	grub-mkrescue -o $(ISO) isodir
	@echo "make> Build complete!"
	@echo "ISO created: $(ISO)"

$(BIN): $(OBJS)
	$(LD) $(LDFLAGS) -o $@ $(OBJS)

b.o: b.s
	$(AS) $(ASFLAGS) $< -o $@

kernel.o: kernel.c
	$(CC) $(CFLAGS) $< -o $@

clean:
	rm -rf *.o $(BIN) $(ISO) isodir
	@echo "Cleaned all build files"
