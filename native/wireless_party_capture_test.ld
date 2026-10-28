/* ARM946-only test image, outside the RAM ranges used by the party fixtures. */
ENTRY(xwb_capture_formation_party)
SECTIONS {
    . = 0x02040000;
    .text : { *(.text*) }
    .rodata : { *(.rodata*) }
    .data : { *(.data*) }
    .bss : { *(.bss*) *(COMMON) }
}
