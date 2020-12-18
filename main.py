# v1218-1724

import sys
from copy import deepcopy

DEFAULT_IMAGE_PATH = 'C:\\TEMP\\QR.bmp'
READ_BINARY = 'rb'

class QR2LINES:
    def __init__(self):
        # readed BMP file
        self.rd_file = 0

        # BMP Headers
        self.bfType = b''
        self.bfSize = b''
        self.bfReserved1 = b''
        self.bfReserved2 = b''
        self.bfOffBits = b''

        # Informations
        self.bcSize = b''
        self.bcWidth = b''
        self.bcHeight = b''
        self.bcPlanes = b''
        self.bcBitCount = b''
        self.biCompression = b''
        self.biSizeImage = b''
        self.biXPixPerMeter = b''
        self.biYPixPerMeter = b''
        self.biClrUsed = b''
        self.biCirImportant = b''

        # Image Format
        self.image_type = ''
        self.image_offset = 0
        self.image_width = 0
        self.image_height = 0
        self.image_bits = 0
        self.image_comp = 0

        # Image Array
        self.image_array = []
        self.image_start = 0

    def openImageFile(self, filepath=''):
        if filepath == '':
            filepath = DEFAULT_IMAGE_PATH

        return open(filepath, READ_BINARY)

    def closeImageFile(self):
        if self.rd_file:
            self.rd_file.close()

    def getImageHeaders(self, filepath=''):
        self.closeImageFile()
        self.rd_file = self.openImageFile(filepath)

        # BMP Headers
        self.bfType = self.rd_file.read(2)
        self.bfSize = self.rd_file.read(4)
        self.bfReserved1 = self.rd_file.read(2)
        self.bfReserved2 = self.rd_file.read(2)
        self.bfOffBits = self.rd_file.read(4)

        # Informations
        self.bcSize = self.rd_file.read(4)
        self.bcWidth = self.rd_file.read(4)
        self.bcHeight = self.rd_file.read(4)
        self.bcPlanes = self.rd_file.read(2)
        self.bcBitCount = self.rd_file.read(2)
        self.biCompression = self.rd_file.read(4)
        self.biSizeImage = self.rd_file.read(4)
        self.biXPixPerMeter = self.rd_file.read(4)
        self.biYPixPerMeter = self.rd_file.read(4)
        self.biClrUsed = self.rd_file.read(4)
        self.biCirImportant = self.rd_file.read(4)

    def getImageFormat(self):
        self.image_type = str(self.bfType.decode())
        self.image_offset = int.from_bytes(self.bfOffBits, 'little')
        self.image_width = int.from_bytes(self.bcWidth, 'little')
        self.image_height = int.from_bytes(self.bcHeight, 'little')
        self.image_bits = int.from_bytes(self.bcBitCount, 'little')
        self.image_comp = int.from_bytes(self.biCompression, 'little')

    def checkImageFormat(self):
        if self.image_type != 'BM':
            sys.exit(f'画像フォーマットが違います。BMPのみ対応: {self.image_type}')
        if self.image_bits != 1:
            sys.exit(f'ビット深度が違います。1bitのみ対応: {self.image_bits}')
        if self.image_comp != 0:
            sys.exit(f'圧縮画像は非対応です。: {self.image_comp}')

    def imageToArray(self, filepath=''):
        print(f'Image size is ({self.image_width}, {self.image_height})')
        self.image_array = [[] for i in range(self.image_height)]

        # jump to Image
        self.closeImageFile()
        self.rd_file = self.openImageFile(filepath)
        print(self.rd_file.read(self.image_offset))

        plus_one = 1 if self.image_width/8 != int(self.image_width/8) else 0
        loop_x = int(self.image_width/8) + plus_one
        plus_one = 1 if int(loop_x/4) != loop_x/4 else 0
        loop_x4 = 4*(int(loop_x/4)+plus_one) # BMP width must be x4 byte
        dummy_x = loop_x4 - loop_x

        for axis_y in range(self.image_height):
            for axis_x in range(loop_x4):
                borw = int.from_bytes(self.rd_file.read(1), 'little')

                #ここでbit単位に分解だ!!!

                self.image_array[axis_y].append(borw)
        for arr in self.image_array:
            print(arr)

    def sequenceImageToLines(self, filepath):
        self.getImageHeaders(filepath)
        self.getImageFormat()
        self.checkImageFormat()
        self.imageToArray(filepath)

def main():
    qr_cls = QR2LINES()
    qr_cls.sequenceImageToLines('C:\\TEMP\\QR.bmp')

if __name__ == '__main__':
    main()
