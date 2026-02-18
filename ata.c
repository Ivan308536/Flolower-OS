#include "ata.h"

static inline void outb(uint16_t port, uint8_t val) {
    asm volatile ("outb %0, %1" : : "a"(val), "Nd"(port));
}

static inline uint8_t inb(uint16_t port) {
    uint8_t ret;
    asm volatile ("inb %1, %0" : "=a"(ret) : "Nd"(port));
    return ret;
}

static inline uint16_t inw(uint16_t port) {
    uint16_t ret;
    asm volatile ("inw %1, %0" : "=a"(ret) : "Nd"(port));
    return ret;
}

static inline void outw(uint16_t port, uint16_t val) {
    asm volatile ("outw %0, %1" : : "a"(val), "Nd"(port));
}

static void ata_400ns_delay() {
    for(int i = 0; i < 4; i++)
        inb(ATA_PRIMARY_IO + ATA_REG_STATUS);
}

void ata_wait_bsy() {
    while(inb(ATA_PRIMARY_IO + ATA_REG_STATUS) & ATA_SR_BSY);
}

void ata_wait_drq() {
    while(!(inb(ATA_PRIMARY_IO + ATA_REG_STATUS) & ATA_SR_DRQ));
}

bool ata_identify() {
    outb(ATA_PRIMARY_IO + ATA_REG_DRIVE, 0xA0);
    ata_400ns_delay();
    
    outb(ATA_PRIMARY_IO + ATA_REG_COMMAND, ATA_CMD_IDENTIFY);
    ata_400ns_delay();
    
    if(inb(ATA_PRIMARY_IO + ATA_REG_STATUS) == 0) return false;
    
    ata_wait_bsy();
    
    uint8_t status = inb(ATA_PRIMARY_IO + ATA_REG_STATUS);
    if(status & ATA_SR_ERR) return false;
    
    ata_wait_drq();
    
    uint16_t buffer[256];
    for(int i = 0; i < 256; i++)
        buffer[i] = inw(ATA_PRIMARY_IO + ATA_REG_DATA);
    
    (void)buffer;
    return true;
}

bool ata_read_sector(uint32_t lba, uint8_t* buffer) {
    ata_wait_bsy();
    
    outb(ATA_PRIMARY_IO + ATA_REG_DRIVE, 0xE0 | ((lba >> 24) & 0x0F));
    outb(ATA_PRIMARY_IO + ATA_REG_SECCOUNT, 1);
    outb(ATA_PRIMARY_IO + ATA_REG_LBA_LO, (uint8_t)lba);
    outb(ATA_PRIMARY_IO + ATA_REG_LBA_MID, (uint8_t)(lba >> 8));
    outb(ATA_PRIMARY_IO + ATA_REG_LBA_HI, (uint8_t)(lba >> 16));
    outb(ATA_PRIMARY_IO + ATA_REG_COMMAND, ATA_CMD_READ_PIO);
    
    ata_wait_bsy();
    ata_wait_drq();
    
    uint16_t* buf16 = (uint16_t*)buffer;
    for(int i = 0; i < 256; i++)
        buf16[i] = inw(ATA_PRIMARY_IO + ATA_REG_DATA);
    
    ata_400ns_delay();
    return true;
}

bool ata_write_sector(uint32_t lba, uint8_t* buffer) {
    ata_wait_bsy();
    
    outb(ATA_PRIMARY_IO + ATA_REG_DRIVE, 0xE0 | ((lba >> 24) & 0x0F));
    outb(ATA_PRIMARY_IO + ATA_REG_SECCOUNT, 1);
    outb(ATA_PRIMARY_IO + ATA_REG_LBA_LO, (uint8_t)lba);
    outb(ATA_PRIMARY_IO + ATA_REG_LBA_MID, (uint8_t)(lba >> 8));
    outb(ATA_PRIMARY_IO + ATA_REG_LBA_HI, (uint8_t)(lba >> 16));
    outb(ATA_PRIMARY_IO + ATA_REG_COMMAND, ATA_CMD_WRITE_PIO);
    
    ata_wait_bsy();
    ata_wait_drq();
    
    uint16_t* buf16 = (uint16_t*)buffer;
    for(int i = 0; i < 256; i++)
        outw(ATA_PRIMARY_IO + ATA_REG_DATA, buf16[i]);
    
    ata_400ns_delay();
    ata_wait_bsy();
    
    outb(ATA_PRIMARY_IO + ATA_REG_COMMAND, 0xE7);
    ata_wait_bsy();
    
    return true;
}
