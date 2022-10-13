import unswizzle
import helpers
import sys
import struct

bytesPerTile = {
    0x63: 16
}

# i'm lazy, temporary solution
# MipLookup_Square = [0x85C, 0x86C, 0x89C, 0x105C, 0x205C, 0x405C, 0x805C, 0x1005C, 0x2005C, 0x4005C, 0x8005C, 0x10005C, 0x20005C, 0x40005C, 0x80005C, 0x100005C]

if len(sys.argv) < 2:
    print("USAGE: tex_file.texture <outfile.dds>")
    
if len(sys.argv) == 2:
    ofile = "outfile.dds"
    
else:
    ofile = sys.argv[2]

with open(sys.argv[1], "rb") as texture:
    with open(ofile, "wb") as out:
        magic = texture.read(4)
        if magic != b"1TAD":
            print("Not a 1TAD file!")
            exit()
        AssetType = struct.unpack("<I", texture.read(4))[0]
        if AssetType != 0x8F53A199:
            print("Not a Texture File!")
            exit()
        HeaderSize = struct.unpack("<I", texture.read(4))[0]  # really the 1TAD size
        SectionCount = struct.unpack("<H", texture.read(2))[0]
        ZeroUnlessShader = struct.unpack("<H", texture.read(2))[0]
        # textures only have 1 section
        TextureBuiltSectionHash = struct.unpack("<I", texture.read(4))[0]
        TextureBuiltSectionOffset = struct.unpack("<I", texture.read(4))[0]
        TextureBuiltSectionSize = struct.unpack("<I", texture.read(4))[0]
        texture.seek(TextureBuiltSectionOffset)
        ImageBuiltSize = struct.unpack("<I", texture.read(4))[0]
        ImageStreamSize = struct.unpack("<I", texture.read(4))[0]
        ImageStreamDimensions = struct.unpack("<HH", texture.read(4))
        ImageBuiltDimensions = struct.unpack("<HH", texture.read(4))
        ImageUnk01 = struct.unpack("<H", texture.read(2))[0]
        ImageUnk02 = struct.unpack("<H", texture.read(2))[0]
        ImageFormat = struct.unpack("<H", texture.read(2))[0]
        ImageMipCount = struct.unpack("<H", texture.read(2))[0]
        ImageUnk03 = struct.unpack("<H", texture.read(2))[0]
        ImageUnk04 = struct.unpack("<H", texture.read(2))[0]
        ImageUnk05 = struct.unpack("<H", texture.read(2))[0]
        ImageUnk06 = struct.unpack("<H", texture.read(2))[0]
        ImageUnksRest = texture.read(12)
        # begin the DDS
        out.write(b"DDS\x20")
        out.write(b"\x7C\x00\x00\x00")
        out.write(b"\x07\x10\x0A\x00")
        out.write(struct.pack("<II", *ImageBuiltDimensions))
        out.write(struct.pack("<I", (ImageBuiltDimensions[0]*ImageBuiltDimensions[1]) * bytesPerTile[ImageFormat]))
        # others when i find them and confirm they work
        out.write(b"\x00\x00\x00\x00")  # depth, unknown if cubemaps exist
        out.write(struct.pack("<I", 1))  # 1 because idc about mipmaps anymore
        out.write(b"\x00" * 44)
        out.write(b"\x20\x00\x00\x00\x04\x00\x00\x00DX10\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x10\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00")
        out.write(struct.pack("<I", ImageFormat))
        out.write(b"\x03\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00")
        # start of image data is 0x85C, 0x800 align plus 0x5C 1TAD
        texture.seek(0x85C)
        
        
        # now we can write image data
        #mips = []
        #curMip = 0
        #for i in range(ImageMipCount-1, -1, -1):
        #    
        #    print(hex(texture.tell())
        #    curMip += 1
        #    mipWidth = ImageBuiltDimensions[0] // (2 ** i)
        #    mipHeight = ImageBuiltDimensions[1] // (2 ** i)
        #    
        #    tileWidth = mipWidth // 4
        #    tileHeight = mipWidth // 4
        #    
        #    if tileWidth < 4: tileWidth = 4
        #    if tileHeight < 4: tileHeight = 4
        #    
        #    if tileWidth > 4 or tileHeight > 4:
        #        swizzled = texture.read((tileWidth * tileHeight) * bytesPerTile[ImageFormat])
        #        repaired = helpers.ReorderCorners(bytes(helpers.RepairColumns(bytes(unswizzle.UnswizzleTexture(swizzled, tileWidth, tileHeight, bytesPerTile[ImageFormat])), tileWidth, tileHeight, bytesPerTile[ImageFormat])), tileWidth, tileHeight, bytesPerTile[ImageFormat])
        #
        #        mips.append(bytes(repaired))
        #    else:
        #        mips.append(texture.read((tileWidth * tileHeight) * bytesPerTile[ImageFormat]))
        
        #for i in range(ImageMipCount-1, -1, -1):
        #    print(i)
        #    out.write(mips[i])
        
        # i don't care about the mipmaps anymore
        texture.seek(-(ImageBuiltDimensions[0]*ImageBuiltDimensions[1]), 2)
        swizzled = texture.read(ImageBuiltDimensions[0]*ImageBuiltDimensions[1])
        unswizzled = unswizzle.UnswizzleTexture(swizzled, ImageBuiltDimensions[0] // 4, ImageBuiltDimensions[1] // 4, bytesPerTile[ImageFormat])
        repaired = helpers.RepairColumns(bytes(unswizzled), ImageBuiltDimensions[0] // 4, ImageBuiltDimensions[1] // 4, bytesPerTile[ImageFormat])
        reordered = helpers.ReorderCorners(bytes(repaired), ImageBuiltDimensions[0] // 4, ImageBuiltDimensions[1] // 4, bytesPerTile[ImageFormat])
        out.write(bytes(reordered))