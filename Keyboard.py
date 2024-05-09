from __future__ import annotations
import pygame

KEYS: dict[int | str, str | int] = {
    pygame.K_0: "0",
    pygame.K_1: "1",
    pygame.K_2: "2",
    pygame.K_3: "3",
    pygame.K_4: "4",
    pygame.K_5: "5",
    pygame.K_6: "6",
    pygame.K_7: "7",
    pygame.K_8: "8",
    pygame.K_9: "9",

    pygame.K_a: "a",
    pygame.K_b: "b",
    pygame.K_c: "c",
    pygame.K_d: "d",
    pygame.K_e: "e",
    pygame.K_f: "f",
    pygame.K_g: "g",
    pygame.K_h: "h",
    pygame.K_i: "i",
    pygame.K_j: "j",
    pygame.K_k: "k",
    pygame.K_l: "l",
    pygame.K_m: "m",
    pygame.K_n: "n",
    pygame.K_o: "o",
    pygame.K_p: "p",
    pygame.K_q: "q",
    pygame.K_r: "r",
    pygame.K_s: "s",
    pygame.K_t: "t",
    pygame.K_u: "u",
    pygame.K_v: "v",
    pygame.K_w: "w",
    pygame.K_x: "x",
    pygame.K_y: "y",
    pygame.K_z: "z",

    pygame.K_BACKSPACE: "Back",
    pygame.K_TAB: "Tab",
    pygame.K_SPACE: "Space",
    pygame.K_RETURN: "Enter",
    pygame.K_LSHIFT: "LShift",
    pygame.K_RSHIFT: "RShift",
    pygame.K_LALT: "LAlt",
    pygame.K_RALT: "RAlt",
    pygame.K_LCTRL: "LCtrl",
    pygame.K_RCTRL: "RCtrl",

    "0": pygame.K_0,
    "1": pygame.K_1,
    "2": pygame.K_2,
    "3": pygame.K_3,
    "4": pygame.K_4,
    "5": pygame.K_5,
    "6": pygame.K_6,
    "7": pygame.K_7,
    "8": pygame.K_8,
    "9": pygame.K_9,

    "a": pygame.K_a,
    "b": pygame.K_b,
    "c": pygame.K_c,
    "d": pygame.K_d,
    "e": pygame.K_e,
    "f": pygame.K_f,
    "g": pygame.K_g,
    "h": pygame.K_h,
    "i": pygame.K_i,
    "j": pygame.K_j,
    "k": pygame.K_k,
    "l": pygame.K_l,
    "m": pygame.K_m,
    "n": pygame.K_n,
    "o": pygame.K_o,
    "p": pygame.K_p,
    "q": pygame.K_q,
    "r": pygame.K_r,
    "s": pygame.K_s,
    "t": pygame.K_t,
    "u": pygame.K_u,
    "v": pygame.K_v,
    "w": pygame.K_w,
    "x": pygame.K_x,
    "y": pygame.K_y,
    "z": pygame.K_z,

    "`": pygame.K_BACKQUOTE,
    "-": pygame.K_MINUS,
    "=": pygame.K_EQUALS,
    "[": pygame.K_LEFTBRACKET,
    "]": pygame.K_RIGHTBRACKET,
    ";": pygame.K_SEMICOLON,
    "'": pygame.K_QUOTE,
    ",": pygame.K_COMMA,
    ".": pygame.K_PERIOD,
    "/": pygame.K_SLASH,
    "\\": pygame.K_BACKSLASH,

    "Back": pygame.K_BACKSPACE,
    "Tab": pygame.K_TAB,
    "Space": pygame.K_SPACE,
    "Enter": pygame.K_RETURN,
    "Return": pygame.K_RETURN,
    "LShift": pygame.K_LSHIFT,
    "RShift": pygame.K_RSHIFT,
    "LAlt": pygame.K_LALT,
    "RAlt": pygame.K_RALT,
    "LCtrl": pygame.K_LCTRL,
    "RCtrl": pygame.K_RCTRL,
    "CLock": pygame.K_CAPSLOCK,
}

ASSETS = "./Assets/"

class Key(pygame.Surface):
    def __init__(self, rect: pygame.Rect, key: int, parent: pygame.Surface = None) -> None:
        pygame.Surface.__init__(self, [rect.width, rect.height], flags = pygame.SRCALPHA)
        self.rect: pygame.Rect = rect
        self.pos: list[int] = self.rect.topleft

        self.key: Key = key
        self.strKey: str = KEYS[self.key].upper()
        self.pressed: bool = False

        self.parent: pygame.Surface = parent if (parent) else pygame.Surface()
        self.texture_1: pygame.Surface = pygame.transform.scale(pygame.image.load(f'{ASSETS}Key_Background_Unlit.png'), (self.rect.width, self.rect.height))
        self.texture_2: pygame.Surface = pygame.transform.scale(pygame.image.load(f'{ASSETS}Key_Background_Lit.png'), (self.rect.width, self.rect.height))

        self.textColor: pygame.Color = pygame.Color(0, 0, 0, 255)

        self.fsize: int = 12
        self.font: pygame.font.Font = pygame.font.SysFont("default", size = self.fsize)
        self.rendered: pygame.Surface = self.__render_text__()
        self.rendRect: pygame.Rect = self.rendered.get_rect()
        self.rendRect.center = (int(self.get_width() / 2), int(self.get_height() / 2))

        self.blit(self.texture_1, pygame.Vector2(0, 0))
        self.blit(self.rendered, self.rendRect.topleft)

    def toggle_press(self):
        self.pressed = not self.pressed
        self.swap_texture()

    def swap_texture(self) -> None:
        temp: pygame.Surface = self.texture_1
        self.texture_1 = self.texture_2
        self.texture_2 = temp

        #self.fill(self.color)
        self.blit(self.texture_1, pygame.Vector2(0, 0))
        self.blit(self.rendered, self.rendRect.topleft)

    def set_pos(self, pos: list[float]) -> None:
        self.rect.topleft = pos
        self.pos = pos

    def update_base_texture(self, texture: pygame.Surface) -> None:
        self.texture_1 = texture
    
    def update_secondary_texture(self, texture: pygame.Surface) -> None:
        self.texture_2 = texture

    def update_text_color(self, color: pygame.Color) -> None:
        self.textColor = color

    def draw(self, where: pygame.Surface = None) -> None:
        "Will draw on an empty defaut parent if no surface or parent is provided."
        if (self.__has_been_shrunk__()): self.rendered = self.__rerender_text__()

        if (where != None): where.blit(self, self.pos)
        else: self.parent.blit(self, self.pos)
    
    def __has_been_shrunk__(self) -> bool:
        #Test width
        if (self.font.size(self.strKey)[0] >= self.get_width()):
            return True
        
        #Test height
        if (self.font.size(self.strKey)[1] >= self.get_height()):
            return True

        return False

    def __render_text__(self) -> pygame.Surface:
        #Larger font width
        if (self.font.size(self.strKey)[0] > self.font.size(self.strKey)[1]):
            while (self.font.size(self.strKey)[0] < self.get_width()):
                self.fsize += 1
                self.font = pygame.font.SysFont("default", self.fsize)
            
            while (self.font.size(self.strKey)[0] >= self.get_width()):
                self.fsize -= 1
                self.font = pygame.font.SysFont("default", self.fsize)
        
        #Larger font height
        else:
            while (self.font.size(self.strKey)[1] < self.get_height()):
                self.fsize += 1
                self.font = pygame.font.SysFont("default", self.fsize)
            
            while (self.font.size(self.strKey)[1] >= self.get_height()):
                self.fsize -= 1
                self.font = pygame.font.SysFont("default", self.fsize)

        return self.font.render(self.strKey, True, self.textColor)
    
    def __rerender_text__(self) -> None:
        self.rendered = self.__render_text__()
        self.rendRect = self.rendered.get_rect()
        self.rendRect.center = (int(self.get_width() / 2), int(self.get_height() / 2))

        #self.fill(self.color)
        self.blit(self.texture_1, pygame.Vector2(0, 0))
        self.blit(self.rendered, self.rendRect.topleft)
    
    def __str__(self) -> str:
        return f'{self.pos}, {self.strKey}'

def createKeyBoard_Rects(parent: pygame.Surface, keys: list[list[str]] = None, offset: pygame.Vector2 = None) -> list[pygame.Rect]:
    if (offset == None): offset = pygame.Vector2(0, 0)

    if (keys == None): #Default
        keys: list[list[str]] = [
            ["`", "1", "2", "3", "4", "5", "6", "7", "8", "9", "0", "-", "="],
            ["Tab", "q", "w", "e", "r", "t", "y", "u", "i", "o", "p", "[", "]", "\\"] ,
            ["CLock", "a", "s", "d", "f", "g", "h", "j", "k", "l", "Return"],
            ["LShift", "z", "x", "c", "v", "b", "n", "m", ",", ".", "/", "RShift"],
            ["LCtrl", "LAlt", "Space", "RAlt", "RCtrl"]
        ]

    #GetMaxLength
    length = len(keys[0])
    for row in keys:
        if (len(row) > length):
            length = len(row)

    rows = len(keys)
    sqrSize = min(int(parent.get_width() / length), int(parent.get_height() / len(keys)))
    
    output: list[pygame.Rect] = []
    for y in range(rows):
        xoffset = (parent.get_width() - (sqrSize * len(keys[y]))) / 2
        for x in range(len(keys[y])):
            k: pygame.Rect = pygame.Rect(x * sqrSize + xoffset + offset.x, y * sqrSize + offset.y, sqrSize, sqrSize), KEYS[keys[y][x]]
            output.append(k)
    
    return output

def createKeyBoard(parent: pygame.Surface, keys: list[list[str]] = None, offset: pygame.Vector2 = None) -> list[Key]:
    return [Key(rect[0], rect[1], parent) for rect in createKeyBoard_Rects(parent, keys, offset)]
    
def createKeys(parent: pygame.Surface) -> list[Key]:
    keyboardRows = 3
    sqrSize = int(display.get_width() / (len(KEYS) / keyboardRows))
    keysPerRow = int(display.get_width() / sqrSize)
    keysPerRow = keysPerRow + int((len(KEYS) - (keysPerRow*keyboardRows)) / keyboardRows + 0.5)
    k = 0
    lkeys = [key for key, _ in KEYS.items()]

    keys: list[list[Key]] = []

    for y in range(keyboardRows):
        if (k >= len(KEYS)): break
        row = []
        for x in range(keysPerRow):
            if (k >= len(KEYS)): break
            row.append(Key(pygame.Rect(x * sqrSize, y * sqrSize, sqrSize, sqrSize), lkeys[k], parent))
            k += 1

        keys.append(row)

    if (len(keys[-1]) < keysPerRow):
        offset = (display.get_width() - (sqrSize * len(keys[-1]))) / 2

        for x in range(len(keys[-1])):
            keys[-1][x].set_pos([keys[-1][x].pos[0] + offset, keys[-1][x].pos[1]])

    return keys

if __name__ == "__main__":
    pygame.init()
    #monitor_resolution = pygame.Vector2(exts.getResolution())
    display = pygame.display.set_mode([480, 270], pygame.RESIZABLE)
    keys = createKeyBoard(display)

    keydown = False
    running = True
    while (running):
        keys_ = pygame.key.get_pressed()
        for event in pygame.event.get():
            if (event.type == pygame.QUIT):
                running = False
                pygame.quit()
            
            elif (event.type == pygame.KEYDOWN):
                keydown = True

            elif (event.type == pygame.KEYUP):
                keydown = False
        
        if(keydown):
            #print(key)
            for key in keys:
                if (not key.pressed and keys_[key.key]):
                    key.toggle_press()
        else:
            for key in keys:
                if (key.pressed):
                    key.toggle_press()
        
        if (running):
            for key in keys:
                key.draw()

            pygame.display.update()