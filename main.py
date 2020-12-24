# v1225-0816

import sys
import threading
import modules
from copy import deepcopy

DEFAULT_IMAGE_PATH = 'C:\\TEMP\\BAR.bmp'
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

        # Drawing Points
        self.start_point_x = 0
        self.end_point_x = 0
        self.start_point_y = 0
        self.end_point_y = 0
        self.min_offset_x = 0
        self.min_offset_y = 0

        # Circle Drawing
        self.circle_points = []

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
                borw = 255 - int.from_bytes(self.rd_file.read(1), 'little')
                #ここでbit単位に分解だ!!!
                borw_binlist = reversed(modules.num2binList(borw, 8))
                borw_binlist = borw_binlist
                self.image_array[axis_y].extend(borw_binlist)
            self.image_array[axis_y] = self.image_array[axis_y][: self.image_width]
        print(f'Length of self.image_array = {len(self.image_array)}')
        # debug print
        for arr in self.image_array:
            #print(arr)
            pass

    def searchDrawPoint(self, axis_x, axis_y, xory, start_or_end):
        temp_x = axis_x
        draw_x = axis_x
        temp_y = axis_y
        draw_y = axis_y
        ending = 0

        if xory == 'x':
            if start_or_end == 'start':
                # search true start_point_x
                while not ending:
                    temp_x = draw_x - 1
                    temp_x = 0 if temp_x < 0 else temp_x
                    if self.image_array[axis_y][temp_x]:
                        draw_x = temp_x
                        if draw_x == 0:
                            ending = 1
                    else:
                        ending = 1
                self.start_point_x = draw_x

            elif start_or_end == 'end':
                # search true end_point_x
                while not ending:
                    temp_x = draw_x + 1
                    temp_x = self.image_width-1 if temp_x > self.image_width-1 else temp_x
                    if self.image_array[axis_y][temp_x]:
                        draw_x = temp_x
                        if draw_x == self.image_width-1:
                            ending = 1
                    else:
                        ending = 1
                self.end_point_x = draw_x
        elif xory == 'y':
            if start_or_end == 'start':
                # search true start_point_y
                while not ending:
                    temp_y = draw_y - 1
                    temp_y = 0 if temp_y < 0 else temp_y
                    if self.image_array[temp_y][axis_x]:
                        draw_y = temp_y
                        if draw_y == 0:
                            ending = 1
                    else:
                        ending = 1
                self.start_point_y = draw_y
            elif start_or_end == 'end':
                # search true end_point_y
                while not ending:
                    temp_y = draw_y + 1
                    temp_y = self.image_height-1 if temp_y > self.image_height-1 else temp_y
                    if self.image_array[temp_y][axis_x]:
                        draw_y = temp_y
                        if draw_y == self.image_height:
                            ending = 1
                    else:
                        ending = 1
                self.end_point_y = draw_y

    def arrayToBarDrawing(self):
        offset_x = 0
        offset_y = 0
        scaling = 1
        argv = sys.argv
        print(argv)
        if len(argv) == 2:
            offset_x = float(argv[1][: argv[1].find(' ')])
            offset_y = float(argv[1][argv[1].find(' ')+1: ])
        elif len(argv) >= 3:
            offset_x = float(argv[1])
            offset_y = float(argv[2])
            scaling = float(argv[3])

        scaled_line_list = []
        trimmed_line_set = set()

        self.min_offset_x = self.image_width
        self.min_offset_y = self.image_height
        for axis_y in range(self.image_height):
            for axis_x in range(self.image_width):
                if self.image_array[axis_y][axis_x]:
                    # search drawinf points
                    args3 = (axis_x, axis_y, 'y', 'start')
                    args4 = (axis_x, axis_y, 'y', 'end')
                    args_set = [args3, args4]
                    th_list = []
                    # never use multiprocessing!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
                    for args_exe in args_set:
                        th = threading.Thread(target=self.searchDrawPoint, args=args_exe)
                        th.start()
                        th_list.append(th)
                    # wait for threads finish
                    for thz in th_list:
                        thz.join()
                    # make vertical drawing
                    if self.start_point_y - self.end_point_y:
                        scaled_line_list.append([offset_x+axis_x*scaling, offset_y+self.start_point_y*scaling, offset_x+axis_x*scaling, offset_y+self.end_point_y*scaling])
        print(f'Length of scaled_line_list = {len(scaled_line_list)}')
        self.min_offset_x = min(scaled_line_list, key=lambda x: x[0])[0]-offset_x
        self.min_offset_y = min(scaled_line_list, key=lambda x: x[1])[1]-offset_y
        # trimming white zone
        for elem in scaled_line_list:
            trimmed_line_set.add(str(f'{round(elem[0]-self.min_offset_x, 3)} {round(elem[1]-self.min_offset_y, 3)}_{round(elem[2]-self.min_offset_x, 3)} {round(elem[3]-self.min_offset_x, 3)}'))
        print(f'Length of trimmed_line_set = {len(trimmed_line_set)*2}')

        # debug print
        #print(trimmed_line_set)

        return trimmed_line_set

    def searchCircleDrawPoint(self, axis_x_start, axis_y_start, axis_x_end, axis_y_end):
        # search true start_point_x
        for temp_y in range(int(axis_y_end - axis_y_start)):
            for temp_x in range(int(axis_x_end - axis_x_start)):
                if self.image_array[temp_y][temp_x]:
                    self.circle_points.append([temp_x, temp_y])

    def writeOutTextFile(self, filename='', all_text='', line_or_circle=''):
        with open(filename, mode='w', encoding='Shift-JIS') as op_file:
            for lines in all_text:
                if line_or_circle == 'circle':
                    op_file.write(lines+'\n')
                elif line_or_circle == 'line':
                    op_file.write(lines[: lines.find('_')]+'\n')
                    op_file.write(lines[lines.find('_')+1: ]+'\n')
                else:
                    op_file.write(lines[: lines.find('_')]+'\n')
                    op_file.write(lines[lines.find('_')+1: ]+'\n')


    def sequenceImageToLines(self, filepath):
        self.getImageHeaders(filepath)
        self.getImageFormat()
        self.checkImageFormat()
        self.imageToArray(filepath)
        result = self.arrayToBarDrawing()
        self.writeOutTextFile('C:\\TEMP\\BAR.txt', result, 'line')

def main():
    qr_cls = QR2LINES()
    qr_cls.sequenceImageToLines('C:\\TEMP\\BAR.bmp')

if __name__ == '__main__':
    main()
