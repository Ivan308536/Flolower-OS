all: kernel.iso

kernel.bin:
	nasm -f elf32 boot.asm -o boot.o
	i686-elf-gcc -ffreestanding -m32 -c kernel.c process.c memory.c device.c
	i686-elf-gcc -T linker.ld -ffreestanding -m32 -nostdlib *.o -o kernel.bin

kernel.iso: kernel.bin
	mkdir -p iso/boot/grub
	cp kernel.bin iso/boot/kernel.bin
	echo 'set timeout=0' > iso/boot/grub/grub.cfg
	echo 'menuentry "My OS" { multiboot2 /boot/kernel.bin }' >> iso/boot/grub/grub.cfg
	grub-mkrescue -o kernel.iso iso

run:
	qemu-system-i386 -cdrom kernel.iso
