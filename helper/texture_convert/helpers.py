def RepairColumns(pixelData, width, height, bytesPerTile):
    repaired = [0] * len(pixelData)
    # repaired offset formula (((y * width) + x) * bytesPerTile)
    for y in range(height):
        for x in range(width):
            if x % 2 == 1:  # is even
                if y % 4 < 2:  # is within the even row data
                    # this is where we shift the data down and left
                    # in-place replacement for BlockCopy
                    for b in range(bytesPerTile):
                        repaired[((((y + 2) * width) + (x - 1)) * bytesPerTile) + b] = pixelData[(((y * width) + x) * bytesPerTile) + b]
                else:
                    # in-place replacement for BlockCopy
                    for b in range(bytesPerTile):
                        repaired[(((y * width) + x) * bytesPerTile) + b] = pixelData[(((y * width) + x) * bytesPerTile) + b]
            else:
                if y % 4 > 1:
                    # in-place replacement for BlockCopy
                    for b in range(bytesPerTile):
                        repaired[((((y - 2) * width) + (x + 1)) * bytesPerTile) + b] = pixelData[(((y * width) + x) * bytesPerTile) + b]
                else:
                    # in-place replacement for BlockCopy
                    for b in range(bytesPerTile):
                        repaired[(((y * width) + x) * bytesPerTile) + b] = pixelData[(((y * width) + x) * bytesPerTile) + b]
    
    return repaired
    
def ReorderCorners(pixelData, width, height, bytesPerTile):
    reordered = [0] * len(pixelData)
    
    if height >= width:
        for y in range(height):
            for x in range(width):
                if x < width // 2:
                    if y < height // 2:
                        # top left, this is correct
                        # in-place replacement for BlockCopy
                        for b in range(bytesPerTile):
                            reordered[(((y * width) + x) * bytesPerTile) + b] = pixelData[(((y * width) + x) * bytesPerTile) + b]
                    else:
                        # bottom left, this is wrong
                        # in-place replacement for BlockCopy
                        for b in range(bytesPerTile):
                            reordered[((((y % (height // 2)) * width) + (x + (width // 2))) * bytesPerTile) + b] = pixelData[(((y * width) + x) * bytesPerTile) + b]
                else:
                    if y < height // 2:
                        # top right, this is wrong
                        # in-place replacement for BlockCopy
                        for b in range(bytesPerTile):
                            reordered[((((y + (height // 2)) * width) + (x - (width // 2))) * bytesPerTile) + b] = pixelData[(((y * width) + x) * bytesPerTile) + b]
                    else:
                        # bottom right, this is right
                        # in-place replacement for BlockCopy
                        for b in range(bytesPerTile):
                            reordered[(((y * width) + x) * bytesPerTile) + b] = pixelData[(((y * width) + x) * bytesPerTile) + b]
        return reordered
    else:
        return pixelData
    
    