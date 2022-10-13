# unswizzle logic by https://github.com/FireyFly, implemented in C# by https://github.com/xdanieldzd, ported to python by https://github.com/thtrandomlurker

# for anything where you see val % 0x100000000 it's a simple use of modulo to ensure values overflow as expected
import math

def Compact1By1(x):
    x = (x & 0x55555555) % 0x100000000
    x = ((x ^ (x >> 1)) & 0x33333333) % 0x100000000
    x = ((x ^ (x >> 2)) & 0x0f0f0f0f) % 0x100000000
    x = ((x ^ (x >> 4)) & 0x00ff00ff) % 0x100000000
    x = ((x ^ (x >> 8)) & 0x0000ffff) % 0x100000000
    return x
    
def DecodeMorton2X(code):
    return Compact1By1(code >> 0)
    
def DecodeMorton2Y(code):
    return Compact1By1(code >> 1)

def UnswizzleTexture(pixelData, width, height, bytesPerTile):
    print(width, height)
    print(len(pixelData))
    # allocate the unswizzled list
    unswizzled = [0] * len(pixelData)
    
    # loop through the pixels
    for i in range(width * height):
        
        # find the smallest dimension
        dMin = width if width < height else height  # love ternary expressions in python
        k = int(math.log(dMin, 2))
        
        x, y = 0, 0  # might be redundant, but that's to worry about later
        if height < width:
            # XXXyxyxyx -> XXXxxxyyy
            j = (i >> (2 * k) << (2 * k) | (DecodeMorton2Y(i) & (dMin - 1)) << k | (DecodeMorton2X(i) & (dMin - 1)) << 0) % 0x100000000
            x = j // height
            y = j % height
        else:
            # YYYyxyxyx -> YYYyyyxxx
            j = (i >> (2 * k) << (2 * k) | (DecodeMorton2X(i) & (dMin - 1)) << k | (DecodeMorton2Y(i) & (dMin - 1)) << 0) % 0x100000000
            x = j % width
            y = j // width
            
        if y >= height or x >= width: continue
        
        # in-place replacement for BlockCopy
        for b in range(bytesPerTile):
            #print((((y * width) + x) * bytesPerTile) + b)
            unswizzled[(((y * width) + x) * bytesPerTile) + b] = pixelData[(i * bytesPerTile) + b]

    return unswizzled