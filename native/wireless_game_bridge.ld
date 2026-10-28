/* The build reserves the complete image in the main arena before loading it.
 * This address follows the original wireless overlay's code and BSS. */
ENTRY(xwb_overlay_boot)
SECTIONS {
    . = 0x022234A0;
    .text : { *(.text*) }
    .rodata : { *(.rodata*) }
    .data : { *(.data*) }
    .bss (NOLOAD) : { *(.bss*) *(COMMON) }
}
