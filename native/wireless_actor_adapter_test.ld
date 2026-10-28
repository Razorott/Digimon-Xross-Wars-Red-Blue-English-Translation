/* ARM946-only test image; this address is not used by the game. */
ENTRY(xwb_build_opponent_actors)
SECTIONS {
    . = 0x02040000;
    .text : { *(.text*) }
    .rodata : { *(.rodata*) }
    .data : { *(.data*) }
    .bss : { *(.bss*) *(COMMON) }
}
