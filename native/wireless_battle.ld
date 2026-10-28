/* Standalone ARM9 test image. This address is only used by the CPU harness;
 * it is not a reserved or approved location in either retail game's RAM. */
ENTRY(xwb_init)
SECTIONS {
    . = 0x02040000;
    .text : { *(.text*) }
    .rodata : { *(.rodata*) }
    .data : { *(.data*) }
    .bss : { *(.bss*) *(COMMON) }
}
