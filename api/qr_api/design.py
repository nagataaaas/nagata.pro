import abc
import random
from dataclasses import dataclass
from typing import Any


class Element:
    def __init__(self):
        self.styles = {}

    @property
    @abc.abstractmethod
    def class_style(self):
        ...

    @property
    def html(self):
        return '<span style="{}{}"></span>'.format(
            self.class_style,
            ';'.join('{}: {}'.format(k, v) for k, v in self.styles.items())
        )

    @property
    @abc.abstractmethod
    def members(self) -> tuple:
        ...


class Empty(Element):
    @property
    def class_style(self):
        return 'width: 100%; height: 100%;'

    @property
    def members(self) -> tuple:
        return ()

    @property
    def html(self):
        return '<span style="{}{}" class="empty"></span>'.format(
            self.class_style,
            ';'.join('{}: {}'.format(k, v) for k, v in self.styles.items())
        )


@dataclass
class Color:
    r: int = 0
    g: int = 0
    b: int = 0
    a: int = 255

    @classmethod
    def from_hex(cls, hex_str: str) -> "Color":
        r, g, b = int(hex_str[1:3], 16), int(hex_str[3:5], 16), int(hex_str[5:7], 16)
        return cls(r, g, b)

    def to_hex(self) -> str:
        return f"#{self.r:02x}{self.g:02x}{self.b:02x}"

    def to_rgb(self) -> str:
        return f"rgb({self.r}, {self.g}, {self.b})"

    def to_rgba(self) -> str:
        return f"rgba({self.r}, {self.g}, {self.b}, {self.a / 255})"

    def to_array(self) -> list:
        return [self.r, self.g, self.b]

    @classmethod
    def random(cls) -> "Color":
        return cls(
            r=int(random.random() * 255),
            g=int(random.random() * 255),
            b=int(random.random() * 255),
        )

    @classmethod
    def random_alpha(cls) -> "Color":
        return cls(
            r=int(random.random() * 255),
            g=int(random.random() * 255),
            b=int(random.random() * 255),
            a=int(random.random() * 255),
        )

    @classmethod
    def random_alpha_range(cls, min_alpha: int, max_alpha: int) -> "Color":
        return cls(
            r=int(random.random() * 255),
            g=int(random.random() * 255),
            b=int(random.random() * 255),
            a=int(random.random() * (max_alpha - min_alpha) + min_alpha),
        )

    @property
    def members(self) -> tuple:
        return 'a', 'r', 'g', 'b'


@dataclass
class Square(Element):
    """
    A square.
    :param size: the size of the square. 100% means the square adjoin to the next one.
    :param color: the color of the square.
    :param rotate: the rotation of the square. 0 to 359.
    """
    size: int = 80
    color: Color = Color.random()
    rotate: int = 0

    def __post_init__(self):
        super().__init__()

    @property
    def class_style(self) -> str:
        return 'width: {}%; height: {}%; background-color: {}; display: inline-block; transform: rotate({}deg);'.format(
            self.size, self.size, self.color.to_rgba(), self.rotate
        )

    @property
    def members(self) -> tuple:
        return 'size', 'color', 'rotate'


@dataclass
class Circle(Square):
    """
    A circle.
    :param size: the size of the circle. 100% means the circle adjoin to the next one.
    :param color: the color of the circle.
    :param rotate: the rotation of the circle. 0 to 359.
    """

    @property
    def class_style(self) -> str:
        return 'width: {}%; height: {}%; background-color: {}; border-radius: 50%; display: inline-block;' \
               ' transform: rotate({}deg);'.format(
            self.size, self.size, self.color.to_rgba(), self.rotate
        )


@dataclass
class Ellipse(Circle):
    """
    A ellipse.
    :param size: the size of the ellipse. 100% means the ellipse adjoin to the next one.
    :param color: the color of the ellipse.
    :param radius: the radius of the ellipse.
    :param rotate: the rotation of the ellipse. 0 to 359.
    """
    radius: int = 50

    @property
    def class_style(self) -> str:
        return 'width: {}%; height: {}%; background-color: {}; border-radius: {}%; display: inline-block;' \
               ' transform: rotate({}deg);'.format(
            self.size, self.size, self.color.to_rgba(), self.radius, self.rotate
        )

    @property
    def members(self) -> tuple:
        return 'size', 'color', 'rotate', 'radius'


@dataclass(frozen=True)
class Range:
    from_element: Any
    to_element: Any

    def __post_init__(self):
        if self.from_element.__class__ != self.to_element.__class__:
            raise ValueError("min_element and max_element must be of the same type")
        if isinstance(self.from_element, Element) and self.from_element.members != self.to_element.members:
            raise ValueError("min_element and max_element must have the same members")

    def generate(self):
        if isinstance(self.from_element, int):
            return random.randint(self.from_element, self.to_element)
        if isinstance(self.from_element, float):
            return random.uniform(self.from_element, self.to_element)
        if isinstance(self.from_element, (Element, Color)):
            new_element = self.from_element.__class__()
            if isinstance(self.from_element, Element):
                new_element.styles = {**new_element.styles, **self.from_element.styles, **self.to_element.styles}
            for member in self.from_element.members:
                vmin, vmax = getattr(self.from_element, member), getattr(self.to_element, member)
                try:
                    vmin, vmax = min(vmin, vmax), max(vmin, vmax)
                except TypeError:
                    pass
                if vmin.__class__ != vmax.__class__:
                    raise ValueError(f"{member} must be of the same type")
                if vmax == vmin:
                    new_element.__setattr__(member, vmin)
                if isinstance(vmin, int):
                    new_element.__setattr__(member, random.randint(vmin, vmax))
                elif isinstance(vmin, float):
                    new_element.__setattr__(member, random.uniform(vmin, vmax))
                elif isinstance(vmin, (Element, Color)):
                    new_element.__setattr__(member, Range(vmin, vmax).generate())
                else:
                    raise ValueError(f"{member} must be of the same type")
            return new_element


@dataclass
class Marker(Element):
    dot_size: int
    color: Color = Color.from_hex('#000000')
    outline_outside_radius: int = 0
    outline_inside_radius: int = 0

    inside_radius: int = 0

    width: int = 0

    is_super_ellipse: bool = False

    def __post_init__(self):
        super().__init__()
        self.styles['width'] = '100%'
        self.styles['height'] = '100%'

    @property
    def class_style(self) -> str:
        raise NotImplementedError

    @property
    def html(self):
        if self.is_super_ellipse:
            return '''
            <div class="center" style="{}">
            <div style="{div_style}{}" class="super-ellipse">
                <span style="{}{span_style}"></span>
                <span class="se1" style="{se_color}"></span>
                <span class="se2" style="{se_color}"></span>
            </div>
            <div style="{div_style}{}" class="super-ellipse">
                <span style="{}{span_style}"></span>
                <span class="se1"></span>
                <span class="se2"></span>
            </div>
            <div style="{div_style}{}"><span style="{}{span_style}"></span></div>
            </div>'''.format(
                f"""
                opacity: {self.color.a / 255};
                """,
                'background-color: white;',
                f"""
                border-radius: {self.outline_outside_radius}%;
                background-color: {self.color.to_rgb()};
                """,
                f"""
                width: calc(100% - {self.dot_size * 2}px);  
                height: calc(100% - {self.dot_size * 2}px);
                """,
                f"""
                background-color: white;
                border-radius: {self.outline_inside_radius}%;
                """,
                f"""
                width: calc(100% - {self.dot_size * 4}px); 
                height: calc(100% - {self.dot_size * 4}px);
                """,
                f"""
                background-color: {self.color.to_rgb()};
                border-radius: {self.inside_radius}%;
                """,
                se_color=f"background-color: {self.color.to_rgb()};",
                div_style="""
                width: 100%; 
                height: 100%; 
                display: flex; 
                align-items: center;
                justify-content: center;
                position: absolute;
                """,
                span_style=';'.join('{}: {}'.format(k, v) for k, v in self.styles.items())
            )
        return '''
        <div class="center" style="{}">
        <div style="{div_style}{}"><span style="{}{span_style}"></span></div>
        <div style="{div_style}{}"><span style="{}{span_style}"></span></div>
        <div style="{div_style}{}"><span style="{}{span_style}"></span></div>
        </div>'''.format(
            f"""
            opacity: {self.color.a / 255};
            """,
            'background-color: white;',
            f"""
            border-radius: {self.outline_outside_radius}%;
            background-color: {self.color.to_rgb()};
            """,
            f"""
            width: calc(100% - {self.dot_size * 2}px);  
            height: calc(100% - {self.dot_size * 2}px);
            """,
            f"""
            background-color: white;
            border-radius: {self.outline_inside_radius}%;
            """,
            f"""
            width: calc(100% - {self.dot_size * 4}px); 
            height: calc(100% - {self.dot_size * 4}px);
            """,
            f"""
            background-color: {self.color.to_rgb()};
            border-radius: {self.inside_radius}%;
            """,
            div_style="""
            width: 100%; 
            height: 100%; 
            display: flex; 
            align-items: center;
            justify-content: center;
            position: absolute;
            """,
            span_style=';'.join('{}: {}'.format(k, v) for k, v in self.styles.items())
        )

    @property
    def members(self) -> tuple:
        return 'size', 'color'
