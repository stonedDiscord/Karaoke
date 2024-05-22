char magic[9] @ 0x00; // OSM_FONT2
u16 glyphcount @ 0x18;

struct glyph {
u8 width;
u8 height;
u8 idk;
u8 value;
u8 mmm;
u8 imgdata[width*height/2];
};

u32 pointerArray[glyphs] @ 0x28;

glyph i @ pointerArray[55];
