import base64
import math
from dataclasses import field
from io import BytesIO
from typing import List

import jinja2
import qrcode
from PIL import Image
from html2image import Html2Image

from .connection import *
from .design import *
import os
from uuid import uuid4

hti = Html2Image(custom_flags=['--no-sandbox', '--disable-setuid-sandbox', '--disable-gpu', '--no-sandbox',
                               '--disable-dev-shm-usage'])

current_dir = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(current_dir, 'templates', 'qr.html'), 'r') as f:
    template = jinja2.Template(f.read())


def random_image_name() -> str:
    return '{}.png'.format(uuid4())


def str_to_qr(string: str, version=6, mask_pattern=2, error_correction=qrcode.constants.ERROR_CORRECT_H) -> Image:
    qr = qrcode.QRCode(version=version, box_size=1, border=0, error_correction=error_correction,
                       mask_pattern=mask_pattern)
    qr.add_data(string)
    qr.make(fit=True)
    return qr.get_matrix()


def set_marker(matrix: List[List[Element]], marker: Marker) -> None:
    marker_size = None
    max_ind = len(matrix)
    for i, item in enumerate(matrix[0]):
        if isinstance(item, Empty):
            marker_size = i
            break
    if marker_size is None:
        return
    for offset_x, offset_y in [(max_ind - marker_size, 0), (0, max_ind - marker_size), (0, 0)]:
        for i in range(marker_size):
            for j in range(marker_size):
                matrix[offset_y + i].pop(offset_x)
    marker.width = marker_size
    matrix[0].insert(0, marker)
    matrix[0].append(marker)
    matrix[max_ind - marker_size].insert(0, marker)


def set_connection(matrix: List[List[Element]], connection: Connection):
    if isinstance(connection, Horizontal):
        for i, line in enumerate(matrix):
            connected = False
            for j, item in enumerate(line):
                if isinstance(item, Empty):
                    connected = False
                elif isinstance(item, Element):
                    if connected:
                        before = matrix[i][j - 1]
                        item.styles['border-bottom-left-radius'] = 0
                        item.styles['border-top-left-radius'] = 0
                        item.styles['width'] = '100%'
                        item.styles['height'] = f'{connection.height}%'
                        before.styles['border-bottom-right-radius'] = 0
                        before.styles['border-top-right-radius'] = 0
                        before.styles['width'] = '100%'
                        before.styles['height'] = f'{connection.height}%'

                    connected = True

    elif isinstance(connection, Vertical):
        for i, _ in enumerate(matrix):
            connected = False
            for j, _ in enumerate(matrix[i]):
                item = matrix[j][i]
                if isinstance(item, Empty):
                    connected = False
                elif isinstance(item, Element):
                    if connected:
                        before = matrix[j - 1][i]
                        item.styles['border-top-left-radius'] = 0
                        item.styles['border-top-right-radius'] = 0
                        item.styles['height'] = '100%'
                        item.styles['width'] = f'{connection.width}%'
                        before.styles['border-bottom-left-radius'] = 0
                        before.styles['border-bottom-right-radius'] = 0
                        before.styles['height'] = '100%'
                        before.styles['width'] = f'{connection.width}%'

                    connected = True

    elif isinstance(connection, All):
        set_connection(matrix, Horizontal(100))
        set_connection(matrix, Vertical(100))


@dataclass
class QRImage:
    image: str = ''

    type: str or None = None
    masked: bool = False

    style_: dict = field(default_factory=dict)

    def set_image(self, image: Image):
        buffer = BytesIO()
        image.save(buffer, format='PNG')
        self.image = f"data:image/png;base64,{base64.b64encode(buffer.getvalue()).decode('utf-8')}"
        self.type = 'image'

    def set_css(self, css: str):
        self.image = css
        self.type = 'css'

    def set_style(self, style: str, value: str):
        self.style_[style] = value

    @property
    def style(self):
        return ';'.join([f'{k}: {v}' for k, v in self.style_.items()])


@dataclass
class ImageInfo:
    height: float
    width: float
    padding: int
    background: QRImage = QRImage()
    center_image: QRImage = QRImage()


def clip_center(matrix: List[List[Element]], ratio: int, image_padding=10) -> ImageInfo:
    if ratio < 0:
        raise ValueError('ratio must be positive')
    size = math.floor(len(matrix) * math.sqrt(ratio / 100))
    if size % 2 != len(matrix) % 2:
        size += 1
    offset = (len(matrix) - size) // 2
    for i in range(size):
        for j in range(size):
            matrix[offset + i][offset + j] = Empty()
    return ImageInfo(size, size, image_padding)


def clip_center_with_image(matrix: List[List[Element]], ratio: int, image: Image, image_padding=10,
                           as_mask=False) -> ImageInfo:
    if ratio < 0:
        raise ValueError('ratio must be positive')
    # replace certain ratio of the matrix with empty elements
    matrix_area = len(matrix) ** 2
    image_area = image.height * image.width

    n = math.sqrt(matrix_area / image_area * ratio / 100)
    height, width = math.ceil(image.height * n), math.ceil(image.width * n)
    if height % 2 != len(matrix) % 2:
        height += 1
    if width % 2 != len(matrix[0]) % 2:
        width += 1
    top = math.floor((len(matrix) - height) / 2)
    left = math.floor((len(matrix[0]) - width) / 2)
    for i in range(height):
        for j in range(width):
            matrix[top + i][left + j] = Empty()
    if width / image.width > height / image.height:
        width = image.width * height / image.height
    else:
        height = image.height * width / image.width
    image_info = ImageInfo(height, width, image_padding)
    image_info.center_image.set_image(image)
    image_info.center_image.as_mask = as_mask
    return image_info


def round_empty(matrix: List[List[Element]], radius: int, color: Color):
    max_ind = len(matrix)
    for i, line in enumerate(matrix):
        for j, item in enumerate(line):
            if not isinstance(item, Empty):
                continue
            for offset_x, offset_y in [(-1, -1), (-1, 1), (1, -1), (1, 1)]:
                for k in range(3):
                    i_ = i + offset_y * (k != 2)
                    j_ = j + offset_x * (k != 1)
                    if i_ < 0 or i_ >= max_ind or j_ < 0 or j_ >= max_ind or isinstance(matrix[i_][j_], Empty):
                        break
                else:
                    right_left = ['left', 'right'][offset_x != -1]
                    top_bottom = ['top', 'bottom'][offset_y != -1]
                    matrix[i][j].styles[f'border-{top_bottom}-{right_left}-radius'] = f'{radius}%'
                    matrix[i][j].styles['box-shadow'] = f'0 0 0 0.5em {color.to_rgba()};'


# def str_to_html(string: str, dot_size=20, margin=10, dot: Union[Ellipse, Circle, Square, Range] = None,
#                 marker: Marker = None, connection: Connection = None, connection_size: int = 80,
#                 round_surrounded: bool = False, round_surrounded_size: int = 0,
#                 round_surrounded_color: Color = Color(0, 0, 0, 0)) -> [str, int]:
#     if dot is None:
#         dot = Circle(size=20, color=Color.from_hex('#000000'))
#     if not isinstance(dot, Range):
#         dot = Range(dot, dot)
#     if marker is None:
#         marker = Marker(20, color=Color.from_hex('#000000'))
#     matrix = str_to_qr(string)
#     with open('templates/qr.html', 'r') as f:
#         template = jinja2.Template(f.read())
#     qrcode = [[dot.generate() if i else Empty() for i in line] for line in
#               matrix]
#     image_info = clip_center_with_image(qrcode, 8,
#                                         Image.open('../dino.png'),
#                                         image_padding=0, as_mask=True)
#     image_info.center_image.set_style('image-rendering', 'pixelated')
#     # image_info = clip_center(qrcode, 20, image_padding=5)
#     if image_info is None:
#         raise Exception('Too small')
#     # image_info.center_image.set_image(Image.open(r'C:\Users\nagata\Desktop\program\qrcode-design\insta.png'))
#     # image_info.center_image.as_mask = True
#     # image_info.background.set_image(Image.open(r'C:\Users\nagata\Desktop\program\qrcode-design\32694778.jfif'))
#     # image_info.background.set_css('linear-gradient(40deg, #E4546C, #CC2E92, #AF13AE, #8134af);')
#     # image_info.background.set_css('linear-gradient(60deg, #c5087c, #b80895, #aa07ac);')
#     image_info.background.set_css('black;')
#     if connection:
#         set_connection(qrcode, Horizontal(connection_size))
#     if round_surrounded:
#         if connection is not All:
#             warnings.warn('round_surrounded may be weird when connection is not All')
#         round_empty(qrcode, round_surrounded_size, round_surrounded_color)
#     set_marker(qrcode, marker)
#
#     vars = {'isinstance': isinstance, 'Marker': Marker, 'image_info': image_info, 'dot_size': dot_size,
#             'margin': margin, 'background_color': 'white'}
#     qr, size = template.render(qrcode=qrcode, **vars), dot_size * len(matrix) + margin * 2
#     with open('qr.html', 'w') as f:
#         f.write(qr)
#     print('start initializing')
#     hti = Html2Image(size=(size, size))
#     hti.screenshot(html_str=qr, save_as='qr.png')


def instagram_style_qrcode(string: str):
    dot = Range(Circle(size=60, color=Color(0, 0, 0)),
                Circle(size=90, color=Color(0, 0, 0)))
    marker = Marker(20, Color(0, 0, 0), 20, 20, 50, is_super_ellipse=True)

    matrix = str_to_qr(string)
    dot_size = 20
    margin = 100

    qr = [[dot.generate() if i else Empty() for i in line] for line in matrix]
    image_info = clip_center(qr, 10, image_padding=5)
    image_info.center_image.set_image(Image.open(os.path.join(current_dir, 'image', 'insta.png')))
    image_info.center_image.as_mask = True
    # image_info.background.set_css('linear-gradient(40deg, #E4546C, #CC2E92, #AF13AE, #8134af);')
    image_info.background.set_css('linear-gradient(60deg, #c5087c, #b80895, #aa07ac);')
    set_marker(qr, marker)

    vars = {'isinstance': isinstance, 'Marker': Marker, 'image_info': image_info, 'dot_size': dot_size,
            'margin': margin, 'background_color': 'white'}
    qr, size = template.render(qrcode=qr, **vars), dot_size * len(matrix) + margin * 2

    image_name = random_image_name()
    hti.screenshot(html_str=qr, save_as=image_name, size=(size, size))
    image = Image.open(image_name).copy()
    os.remove(image_name)
    return image


def chrome_style_qrcode(string: str) -> Image:
    dot = Circle(size=80, color=Color(0, 0, 0))
    marker = Marker(20, Color(0, 0, 0), 15, 20, 33, is_super_ellipse=False)

    dot_size = 20
    margin = 100

    if dot is None:
        dot = Circle(size=20, color=Color.from_hex('#000000'))
    if not isinstance(dot, Range):
        dot = Range(dot, dot)
    if marker is None:
        marker = Marker(20, color=Color.from_hex('#000000'))
    matrix = str_to_qr(string, version=6, mask_pattern=7, error_correction=qrcode.constants.ERROR_CORRECT_M)

    qr = [[dot.generate() if i else Empty() for i in line] for line in matrix]
    image_info = clip_center_with_image(qr, 4,
                                        Image.open(os.path.join(current_dir, 'image', 'dino.png')),
                                        image_padding=0, as_mask=False)
    image_info.center_image.set_style('image-rendering', 'pixelated')
    set_marker(qr, marker)

    vars = {'isinstance': isinstance, 'Marker': Marker, 'image_info': image_info, 'dot_size': dot_size,
            'margin': margin, 'background_color': 'white'}
    qr, size = template.render(qrcode=qr, **vars), dot_size * len(matrix) + margin * 2
    image_name = random_image_name()
    hti.screenshot(html_str=qr, save_as=image_name, size=(size, size))

    image = Image.open(image_name)
    image = resize_image(image, (size / 2, size / 2), True)
    # print(size)
    image = image.convert('L').point(lambda x: 0 if x < 128 else 255)
    # image = image.convert('1')
    # image = resize_image(image, (size, size), False)
    os.remove(image_name)
    return image


def resize_image(image: Image, size: (int, int), anti_aliasing: bool = True):
    image = image.resize(map(int, size), Image.ANTIALIAS if anti_aliasing else Image.NEAREST)
    return image
