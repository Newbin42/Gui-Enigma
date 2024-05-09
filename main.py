from __future__ import annotations
from types import NoneType
import pygame
import asyncio

import EnigmaLib, GuiMixins
from Button import Button
from Keyboard import Key, createKeyBoard, createKeyBoard_Rects

ASSETS: str = "./Assets/"
KEYS: list[list[str]] = [
            ["q", "w", "e", "r", "t", "z", "u", "i", "o"],
            ["a", "s", "d", "f", "g", "h", "j", "k"],
            ["p", "y", "x", "c", "v", "b", "n", "m", "l"],
        ]
MACHINE_BACKGROUND: pygame.Color = pygame.Color(164, 122, 24, 255)
DARKER_MACHINE_BACKGROUND: pygame.Color = pygame.Color(140, 77, 8, 255)
BLACK: pygame.Color = pygame.Color(0, 0, 0, 255)

ROTOR_WIRINGS = [
    "maoujfgqxcibetplskvywhdznr",
    "ianwupxcotghbvfjdlrzseymkq",
    "vqeftnswkbacjrpudiozhylgmx",
    "kbxaozniflysewdgmvqpcjthur",
    "kydhmevpwxrolcanugfqiztjsb",
    "ntczskoablhqpwmdugfrxyevij",
]

MIRROR = EnigmaLib.Mirror({
    'o': 'm', 'a': 'y', 'x': 'n',
    's': 'b', 'g': 'i', 'f': 'q',
    'h': 'p', 'k': 'z', 'w': 'j',
    'u': 't', 'e': 'l', 'c': 'r',
    'v': 'd', 'd': 'v', 'r': 'c',
    'l': 'e', 't': 'u', 'j': 'w',
    'z': 'k', 'p': 'h', 'q': 'f',
    'i': 'g', 'b': 's', 'n': 'x',
    'y': 'a', 'm': 'o'
    }, False
)

class Plug(GuiMixins.Surface):
    @staticmethod
    def from_key(key: Key, parent: pygame.Surface) -> Plug:
        return Plug(key.strKey, key.rect, parent)

    def __init__(self, char: str, rect: pygame.Rect, parent: pygame.Surface = None) -> None:
        GuiMixins.Surface.__init__(self, rect, parent)

        self.sprite = pygame.transform.scale(pygame.image.load(f'{ASSETS}Plugboard Barrel.png'), pygame.Vector2(self.rect.width, self.rect.height) * 0.8)

        top = (self.get_height() - self.sprite.get_height()) // 2
        left = (self.get_width() - self.sprite.get_width()) // 2

        self.blit(self.sprite, (left, top))

        self.connection: Plug = None
        self.char = char

    def flush(self):
        super().flush()

        top = (self.get_height() - self.sprite.get_height()) // 2
        left = (self.get_width() - self.sprite.get_width()) // 2
        self.blit(self.sprite, (left, top))

    def link(self, other: Plug) -> None:
        if (self.connection == None):
            self.connection = other
            other.connection = self
            return
        
        other.connection = None
        self.connection = None

    def unlink(self) -> None:
        self.connection.connection = None
        self.connection = None

    def hovered_over(self, mousePos: pygame.Vector2) -> bool:
        mousePos -= self.get_pos()
        return self.rect.collidepoint(mousePos)

    def draw_pair(self, where: pygame.Surface = None) -> None:
        if (self.connection != None):
            pygame.draw.line(self if where == None else where,
                             pygame.Color(255, 255, 255, 255),
                             self.get_center(), self.connection.get_center(), 2)
    
    def __eq__(self, other: Plug) -> bool:
        return type(other) != NoneType and hash(self) == hash(other)
    
    def __ne__(self, other: Plug) -> bool:
        return type(other) == NoneType or hash(self) != hash(other)

class Plugboard(GuiMixins.Surface):
    def __init__(self, rect: pygame.Rect, parent: pygame.Surface = None) -> None:
        GuiMixins.Surface.__init__(self, rect, parent)

        self.keys: list[pygame.Rect] = createKeyBoard_Rects(self, KEYS)
        self.plugs: list[Plug] = [Plug(key[1], key[0], self) for key in self.keys]

        width = self.plugs[0].rect.right
        for plug in self.plugs:
            if plug.rect.right > width: width = plug.rect.right
        
        pos = self.plugs[0].rect.topleft

        width = width - pos[0]
        height = self.plugs[-1].rect.bottom

        self.smallerSurface: GuiMixins.Surface = GuiMixins.Surface(pygame.Rect(pos[0], pos[1], width, height), self)
        self.smallerSurface.fill(DARKER_MACHINE_BACKGROUND)

        self.blit(self.smallerSurface, self.smallerSurface.rect.topleft)
        self.fill(DARKER_MACHINE_BACKGROUND)

        self.pair_: list[int] = []
        self.active_a = None
        self.active_b = None

    def passthrough(self, char: str) -> str:
        for plug in self.plugs:
            if (chr(plug.char) == char and plug.connection != None):
                return chr(plug.connection.char)
        
        return char

    def flush(self):
        super().flush()
        width = self.plugs[0].rect.right
        for plug in self.plugs:
            if plug.rect.right > width: width = plug.rect.right
        
        pos = self.plugs[0].rect.topleft

        width = width - pos[0]
        height = self.plugs[-1].rect.bottom

        self.smallerSurface: GuiMixins.Surface = GuiMixins.Surface(pygame.Rect(pos[0], pos[1], width, height), self)
        self.smallerSurface.fill(DARKER_MACHINE_BACKGROUND)

        self.blit(self.smallerSurface, self.smallerSurface.rect.topleft)
        self.fill(DARKER_MACHINE_BACKGROUND)

    def pair(self, index: int) -> bool:
        output: bool = False
        if (self.active_a == None):
            self.active_a = index
            output = True
        else:
            self.active_b = index

        if (self.active_b != None):
            if (self.plugs[self.active_b].connection == None):
                self.plugs[self.active_a].link(self.plugs[self.active_b])

            self.active_a = None
            self.active_b = None

        elif (self.plugs[self.active_a].connection != None):
            self.unpair(index)
            self.active_a = None
            output = False
        
        return output
    
    def unpair(self, index: int) -> None:
        if (self.plugs[index].connection == None): return
        
        self.plugs[index].unlink()
        self.flush()

    def hovered_over(self, mousePos: pygame.Vector2) -> bool:
        return self.rect.collidepoint(mousePos - self.get_pos())

    def is_clicked(self, mousePos: pygame.Vector2) -> bool:
        clicked = False

        for i in range(len(self.plugs)):
            if (not self.plugs[i].hovered_over(mousePos - self.get_pos())):
                continue
            
            self.pair_.append(i)
            clicked = True

        if (len(self.pair_) != 2): return clicked

        if (self.plugs[self.pair_[0]].connection == None):
            self.plugs[self.pair_[0]].link(self.plugs[self.pair_[0]])
        
        self.pair_ = []
        return clicked
    
    def draw_pairs(self, where: pygame.Surface = None) -> None:
        for plug in self.plugs:
            plug.draw_pair(self if where == None else where)
        
    def draw(self, where: pygame.Surface = None) -> None:
        super().draw(where)

        for plug in self.plugs:
            plug.draw(where)
        
        self.draw_pairs(where)

class GuiButton(GuiMixins.Surface):
    def __init__(self, rect: pygame.Rect, parent: pygame.Surface = None) -> None:
        GuiMixins.Surface.__init__(self, rect, parent)

        self.sheet = pygame.transform.scale(pygame.image.load(f'{ASSETS}Rotor Buttons_Min.png'), (self.rect.width, self.rect.height))

        self.button_forward = pygame.Surface([self.rect.width, int(self.rect.height * 0.3125)], flags = pygame.SRCALPHA)
        self.button_forward.blit(self.sheet, (0, 0))
        self.button_forward: Button = Button(self.button_forward, pygame.Vector2(0, 0), self)
        self.button_forward.draw()

        self.button_reset = pygame.Surface([self.rect.width, int(self.rect.height * 0.375)], flags = pygame.SRCALPHA)
        self.button_reset.blit(self.sheet, (0, -int(self.rect.height * 0.3125)))
        self.button_reset: Button = Button(self.button_reset, pygame.Vector2(0, int(self.rect.height * 0.3125)), self)
        self.button_reset.draw()

        self.button_backward = pygame.Surface([self.rect.width, int(self.rect.height * 0.3125)], flags = pygame.SRCALPHA)
        self.button_backward.blit(self.sheet, (0, -int(self.rect.height * 0.6875)))
        self.button_backward: Button = Button(self.button_backward, pygame.Vector2(0, int(self.rect.height * 0.6875)), self)
        self.button_backward.draw()
    
    def clicked_forward(self, mousePos: pygame.Vector2) -> bool:
        return self.button_forward.clicked_on(mousePos)
    
    def clicked_reset(self, mousePos: pygame.Vector2) -> bool:
        return self.button_reset.clicked_on(mousePos)
    
    def clicked_backward(self, mousePos: pygame.Vector2) -> bool:
        return self.button_backward.clicked_on(mousePos)

class Window(GuiMixins.Surface):
    def __init__(self, rect: pygame.Rect, parent: pygame.Surface = None, label: str = "Label") -> None:
        GuiMixins.Surface.__init__(self, rect, parent)

        self.window: pygame.Surface = pygame.transform.scale(pygame.image.load(f'{ASSETS}Rotor Window_Min.png'), (self.rect.width, self.rect.height)).convert_alpha()
        self.localWindowPosition = pygame.Vector2(0, 0)

        self.text: str = " "
        self.textColor: pygame.Color = pygame.Color(0, 0, 0, 255)
        self.fsize: int = 12
        self.fontcode = "default"
        self.font: pygame.font.Font = pygame.font.SysFont(self.fontcode, size = self.fsize)
        self.rendered: pygame.Surface = self.__render_text__()
        self.rendRect: pygame.Rect = self.rendered.get_rect()
        self.rendRect.center = (int(self.get_width() / 2), int(self.get_height() / 2)  * 1.25)

        self.labelText: str = label
        self.labelfsize: int = 12
        self.labelFont: pygame.font.Font = pygame.font.SysFont(self.fontcode, size = self.labelfsize)
        self.renderedLabel: pygame.Surface = self.__render_label__()
        self.rendLabelRect: pygame.Rect = self.rendered.get_rect()
        self.rendLabelRect.topleft = (0, 0)

        self.fill(pygame.Color(150, 150, 150, 255))
        self.blit(self.rendered, self.rendRect.topleft)
        self.blit(self.window, self.localWindowPosition)

        self.blit(self.renderedLabel, self.rendLabelRect.topleft)

    def set_text(self, text: str, reset_size = False) -> None:
        self.text = text

        self.__rerender_text__(reset_size)

    def __render_label__(self):
        #Larger font width
        while (self.labelFont.size(self.labelText)[0] < self.get_width()):
            self.labelfsize += 4
            self.labelFont = pygame.font.SysFont(self.fontcode, self.labelfsize)
        
        while (self.labelFont.size(self.labelText)[0] >= self.get_width()):
            self.labelfsize -= 4
            self.labelFont = pygame.font.SysFont(self.fontcode, self.labelfsize)

        while (self.labelFont.size(self.labelText)[0] >= self.get_width()):
            self.labelfsize -= 1
            self.labelFont = pygame.font.SysFont(self.fontcode, self.labelfsize)

        return self.labelFont.render(self.labelText, True, self.textColor)
    
    def __render_text__(self, reset_size = False) -> pygame.Surface:
        if (reset_size):
            #Larger font width
            #if (self.font.size(EnigmaLib.NUM_REF[self.text])[0] > self.font.size(EnigmaLib.NUM_REF[self.text])[1]):
            while (self.font.size(EnigmaLib.REF[self.text])[0] < self.get_width()):
                self.fsize += 4
                self.font = pygame.font.SysFont(self.fontcode, self.fsize)
            
            while (self.font.size(EnigmaLib.REF[self.text])[0] >= self.get_width()):
                self.fsize -= 4
                self.font = pygame.font.SysFont(self.fontcode, self.fsize)
            #else:
            while (self.font.size(EnigmaLib.REF[self.text])[1] < self.get_width()):
                self.fsize += 4
                self.font = pygame.font.SysFont(self.fontcode, self.fsize)
            
            while (self.font.size(EnigmaLib.REF[self.text])[1] >= self.get_width()):
                self.fsize -= 4
                self.font = pygame.font.SysFont(self.fontcode, self.fsize)

            while (self.font.size(EnigmaLib.REF[self.text])[0] >= self.get_width()):
                self.fsize -= 1
                self.font = pygame.font.SysFont(self.fontcode, self.fsize)
            
            while (self.font.size(EnigmaLib.REF[self.text])[1] >= self.get_width()):
                self.fsize -= 1
                self.font = pygame.font.SysFont(self.fontcode, self.fsize)

        return self.font.render(self.text, True, self.textColor)
    
    def __rerender_text__(self, reset_size = False) -> None:
        self.rendered = self.__render_text__(reset_size)
        self.rendRect = self.rendered.get_rect()
        self.rendRect.center = (int(self.get_width() / 2) * 0.975, int(self.get_height() / 2)  * 1.075)

        self.fill(pygame.Color(150, 150, 150, 255))
        self.blit(self.rendered, self.rendRect.topleft)
        self.blit(self.window, pygame.Vector2(0, 0))
        self.blit(self.renderedLabel, self.rendLabelRect.topleft)

class Rotor(GuiMixins.Surface):
    rid: int = 0
    @staticmethod
    def gui_to_machine(rotor: Rotor) -> EnigmaLib.Rotor:
        return rotor.rotor
    
    def machine_to_gui(rect: pygame.Rect, rotor: EnigmaLib.Rotor, parent: pygame.Surface = None) -> Rotor:
        output = Rotor(rect, str(rotor.get_pid()), list(rotor.ratchet.dict), parent)
        output.rotor = rotor
        return output 

    def __init__(self, rect: pygame.Rect, id: str = "I", ratchetKeys = "AEIOUY", parent: pygame.Surface = None) -> None:
        GuiMixins.Surface.__init__(self, rect, parent)

        self.rotor: EnigmaLib.Rotor = EnigmaLib.Rotor(EnigmaLib.ALPHABET, ROTOR_WIRINGS[self.rid], hash(id), ratchetKeys)
        Rotor.rid += 1

        self.texture: pygame.Surface = pygame.transform.scale(pygame.image.load(f'{ASSETS}Rotor Icon.png'), (self.rect.width, self.rect.height)).convert_alpha()

        self.text: str = id
        self.textColor: pygame.Color = pygame.Color(255, 255, 255, 255)
        self.fsize: int = 12
        self.fontcode = "default"
        self.font: pygame.font.Font = pygame.font.SysFont(self.fontcode, size = self.fsize)
        self.rendered: pygame.Surface = self.__render_text__(True)
        self.rendRect: pygame.Rect = self.rendered.get_rect()
        self.rendRect.center = (int(self.get_width() / 2), int(self.get_height() / 2))

        self.blit(self.texture, (0, 0))
        self.blit(self.rendered, self.rendRect.topleft)

        self.dragging = False
    
    def update(self, mousePos: pygame.Vector2) -> None:
        if (self.rect.collidepoint(mousePos) and self.dragging): self.set_center(mousePos)

    def set_text(self, text: str, reset_size = False) -> None:
        self.text = text
        self.__rerender_text__(reset_size)

    def toggle_drag(self, mousePos: pygame.Vector2) -> None:
        if (self.rect.collidepoint(mousePos)): self.dragging = True
        else: self.dragging = False

    def __render_text__(self, reset_size = False) -> pygame.Surface:
        if (reset_size):
            #Larger font width
            if (self.font.size(self.text)[0] > self.font.size(self.text)[1]):
                while (self.font.size(self.text)[0] < 0.3125 * self.get_width() / 2):
                    self.fsize += 4
                    self.font = pygame.font.SysFont(self.fontcode, self.fsize)
                
                while (self.font.size(self.text)[0] >= 0.3125 * self.get_width() / 2):
                    self.fsize -= 4
                    self.font = pygame.font.SysFont(self.fontcode, self.fsize)
            else:
                while (self.font.size(self.text)[1] < 0.3125 * self.get_height()):
                    self.fsize += 4
                    self.font = pygame.font.SysFont(self.fontcode, self.fsize)
                
                while (self.font.size(self.text)[1] >= 0.3125 * self.get_height()):
                    self.fsize -= 4
                    self.font = pygame.font.SysFont(self.fontcode, self.fsize)

            while (self.font.size(self.text)[0] >= 0.3125 * self.get_width()):
                self.fsize -= 1
                self.font = pygame.font.SysFont(self.fontcode, self.fsize)
            
            while (self.font.size(self.text)[1] >= 0.3125 * self.get_height()):
                self.fsize -= 1
                self.font = pygame.font.SysFont(self.fontcode, self.fsize)

        return self.font.render(self.text, True, self.textColor)

    def __rerender_text__(self, reset_size = False) -> None:
        self.rendered = self.__render_text__(reset_size)
        self.rendRect = self.rendered.get_rect()
        self.rendRect.center = (int(self.get_width() / 2), int(self.get_height() / 2))

        self.blit(self.texture, (0, 0))
        self.blit(self.rendered, self.rendRect.topleft)

class RotorSlot(GuiMixins.Surface):
    def __init__(self, rect: pygame.Rect, parent: pygame.Surface = None) -> None:
        GuiMixins.Surface.__init__(self, rect, parent)

        self.rotorButtons = GuiButton(pygame.Rect(0, 0, self.rect.width * 0.25, self.rect.height), self)
        self.rotorButtons.draw()

        self.rotor_window: Window = Window(pygame.Rect(int(self.rect.width * 0.25), 0, int(self.rect.width * 0.25), self.rect.height), self, "Rotor")
        self.rotor_window.draw()

        self.ratchet_window: Window = Window(pygame.Rect(int(self.rect.width * 0.5), 0, int(self.rect.width * 0.25), self.rect.height), self, "Ratch")
        self.ratchet_window.draw()

        self.ratchetButtons = GuiButton(pygame.Rect(int(self.rect.width * 0.75), 0, self.rect.width * 0.25, self.rect.height), self)
        self.ratchetButtons.draw()

        self.rotor: EnigmaLib.Rotor = None

    def rerender(self) -> None:
        self.rotorButtons.draw()
        self.rotor_window.draw()
        self.ratchet_window.draw()
        self.ratchetButtons.draw()

    def rotor_settings(self, keysIn: str | bool, keysOut: str, rotorID: int, ratchets: str | dict = "AEIOUY") -> None:
        self.rotor = EnigmaLib.Rotor(keysIn, keysOut, rotorID, ratchets)
        self.rotor_window.set_text(EnigmaLib.REF[self.rotor.window()], True)
        self.ratchet_window.set_text(self.rotor.ratchet.str_window(), True)
        self.rerender()

    def insert_rotor(self, rotor: Rotor) -> None:
        if (type(self.rotor) != None):
            raise ValueError("Please remove the current rotor.")
        
        self.rotor = Rotor.gui_to_machine(rotor)
        self.rotor_window.set_text(EnigmaLib.REF[self.rotor.window()], True)
        self.ratchet_window.set_text(self.rotor.ratchet.str_window(), True)
        self.rerender()
    
    def swap_rotor(self, rotor: Rotor) -> EnigmaLib.Rotor:
        temp = self.rotor
        self.rotor = Rotor.gui_to_machine(rotor)

        self.rotor_window.set_text(EnigmaLib.REF[self.rotor.window()], True)
        self.ratchet_window.set_text(self.rotor.ratchet.str_window(), True)
        self.rerender()
        return temp
    
    def uninstall_rotor(self) -> EnigmaLib.Rotor:
        temp = self.rotor
        self.rotor = None

        self.rotor_window.set_text(" ")
        self.ratchet_window.set_text(" ")
        self.rerender()

        return temp
    
    def udpate_spinners(self, mousePos: pygame.Vector2) -> None:
        if (type(self.rotor) == NoneType): return

        mousePos -= self.get_pos()
        if (self.rotorButtons.rect.collidepoint(mousePos)):
            mousePos -= self.rotorButtons.get_pos()
            if (self.rotorButtons.button_forward.clicked_on(mousePos)): #Forward
                self.rotor.rotate_forward()
            elif (self.rotorButtons.button_reset.clicked_on(mousePos)): #Reset
                self.rotor.reset_orientation()
            elif (self.rotorButtons.button_backward.clicked_on(mousePos)): #Backward
                self.rotor.rotate_backward()
            
            self.rotor_window.set_text(EnigmaLib.REF[self.rotor.window()])

        elif (self.ratchetButtons.rect.collidepoint(mousePos)):
            mousePos -= self.ratchetButtons.get_pos()
            if (self.ratchetButtons.button_forward.clicked_on(mousePos)): #Forward
                self.rotor.ratchet.rotate_1(1)
            elif (self.ratchetButtons.button_reset.clicked_on(mousePos)): #Reset
                self.rotor.ratchet.reset()
            elif (self.ratchetButtons.button_backward.clicked_on(mousePos)): #Backward
                self.rotor.ratchet.rotate_1(-1)

        self.ratchet_window.set_text(self.rotor.ratchet.str_window())
        self.rerender()

    def hovered_over(self, mousePos: pygame.Vector2) -> None:
        mousePos -= self.get_pos()
        return self.rect.collidepoint(mousePos)
    
    def hovered_over_window(self, mousePos: pygame.Vector2) -> None:
        return self.rotor_window.rect.collidepoint(mousePos) or self.ratchet_window.rect.collidepoint(mousePos)

    def clicked_forward(self, mousePos: pygame.Vector2) -> bool:
        if (self.rotorButtons.clicked_forward(mousePos - self.get_pos())):
            return True
            
        offsetPos = mousePos - pygame.Vector2(*self.rotor_window.rect.topright)
        offsetPos -= pygame.Vector2(*self.rotorButtons.rect.topright)
        if (self.ratchetButtons.clicked_forward(offsetPos - self.get_pos())):
            return True
        
        return False
    
    def clicked_reset(self, mousePos: pygame.Vector2) -> bool:
        if (self.rotorButtons.clicked_reset(mousePos - self.get_pos())):
            return True
            
        offsetPos = mousePos - pygame.Vector2(*self.rotor_window.rect.topright)
        offsetPos -= pygame.Vector2(*self.rotorButtons.rect.topright)
        if (self.ratchetButtons.clicked_reset(offsetPos - self.get_pos())):
            return True
        
        return False
    
    def clicked_backward(self, mousePos: pygame.Vector2) -> bool:
        if (self.rotorButtons.clicked_backward(mousePos - self.get_pos())):
            return True
            
        offsetPos = mousePos - pygame.Vector2(*self.rotor_window.rect.topright)
        offsetPos -= pygame.Vector2(*self.rotorButtons.rect.topright)
        if (self.ratchetButtons.clicked_backward(offsetPos - self.get_pos())):
            return True
        
        return False

class Lightboard(GuiMixins.Surface):
    def __init__(self, rect: pygame.Rect, parent: pygame.Surface = None):
        """width = max(map(lambda x : x.rect.right, self.lightboard))
        height = self.lightboard[-1].rect.bottom

        self.rows = height // self.lightboard[0].get_height()"""

        GuiMixins.Surface.__init__(self, rect, parent)

        self.lightboard: list[Key] = createKeyBoard(self, KEYS, pygame.Vector2(0, 0))
        self.prevLit: Key = None

        width = self.lightboard[0].rect.right
        for plug in self.lightboard:
            if plug.rect.right > width: width = plug.rect.right
        
        pos = self.lightboard[0].rect.topleft

        width = width - pos[0]
        height = self.lightboard[-1].rect.bottom

        smallerSurface: GuiMixins.Surface = GuiMixins.Surface(pygame.Rect(pos[0], pos[1], width, height), self)
        smallerSurface.fill(DARKER_MACHINE_BACKGROUND)
        self.fill(DARKER_MACHINE_BACKGROUND)

        self.blit(smallerSurface, smallerSurface.rect.topleft)
    
    def toggle_key_by_str(self, char: str) -> None:
        char = char.upper()
        if (type(self.prevLit) != NoneType):
            for key in self.lightboard:
                if (key.strKey == self.prevLit.strKey):
                    key.toggle_press()
                    break

        for key in self.lightboard:
            if (key.strKey == char):
                self.prevLit = key
                key.toggle_press()
                return

    def draw(self, where: pygame.Surface = None) -> None:
        super().draw(where)
        for key in self.lightboard:
            key.draw(where)

class GuiEnigmaLib(GuiMixins.Surface):
    def __init__(self, rect: pygame.Rect, parent: pygame.Surface = None):
        GuiMixins.Surface.__init__(self, rect, parent)

        self.slots: list[RotorSlot] = [
            RotorSlot(pygame.Rect(0, 0, int(self.rect.width * 1/3), int(self.rect.width / 3 * 2/3)), self),
            RotorSlot(pygame.Rect((int(self.rect.width * 1/3) - 1), 0, int(self.rect.width * 1/3), int(self.rect.width / 3 * 2/3)), self),
            RotorSlot(pygame.Rect((int(self.rect.width * 1/3) - 1)*2, 0, int(self.rect.width * 1/3), int(self.rect.width / 3 * 2/3)), self),
        ]

        self.machine = EnigmaLib.EnigmaEnigmaLib(len(self.slots))

        #Remove existing plugboard for external one
        self.machine.remove_plugboard()
        self.machine.swap_mirror_plate(MIRROR)

        rheight = self.get_height() - self.slots[0].get_height()
        self.lightboard: Lightboard = Lightboard(pygame.Rect(0, self.slots[0].get_height(), self.get_width(), rheight // 2), self)
        self.plugboard: Plugboard = Plugboard(pygame.Rect(0, self.lightboard.rect.bottom, self.get_width(), rheight // 2), self)

        self.fill(DARKER_MACHINE_BACKGROUND)

    def full(self) -> bool:
        for slot in self.slots:
            if (type(slot.rotor) == NoneType): return False
        
        return True

    def encrypt(self, key) -> None:
        char: str = self.plugboard.passthrough(key)
        char = self.machine.encode_char(char)
        char = self.plugboard.passthrough(char)
        
        self.lightboard.toggle_key_by_str(char)

        for slot in range(len(self.slots)):
            self.slots[slot].rotor_window.set_text(EnigmaLib.REF[self.slots[slot].rotor.window()])
            self.slots[slot].ratchet_window.set_text(self.slots[slot].rotor.ratchet.str_window())
            self.slots[slot].rerender()

    def insert_rotor(self, rotor: Rotor, slot: int) -> None:
        self.machine.remove_from_slot(slot)
        self.machine.insert(Rotor.gui_to_machine(rotor), slot, "A")
        self.slots[slot - 1].swap_rotor(rotor)

    def hovered_over(self, mousePos: pygame.Vector2) -> int:
        p = mousePos - self.get_pos()
        for slot in range(len(self.slots)):
            if (self.slots[slot].hovered_over(p)): return slot + 1
        
        return 0
    
    def hovered_over_window(self, mousePos: pygame.Vector2) -> int:
        p = mousePos - self.get_pos()
        for slot in range(len(self.slots)):
            if (self.slots[slot].hovered_over_window(p - self.slots[slot].get_pos())): return slot + 1
        
        return 0
    
    def hovered_over_plugboard(self, mousePos: pygame.Vector2) -> int:
        testPos = mousePos - self.get_pos()
        if (not self.plugboard.rect.collidepoint(testPos)): return -1
        for i in range(len(self.plugboard.plugs)):
            if (self.plugboard.plugs[i].rect.collidepoint(testPos - self.plugboard.get_pos())):
                return i
        
        return -1
    
    def uninstall_rotor(self, rotor: int) -> EnigmaLib.Rotor:
        self.slots[rotor - 1].uninstall_rotor()
        return self.machine.remove_from_slot(rotor)
    
    def update_spinners(self, mousePos: pygame.Vector2) -> None:
        for slot in self.slots:
            slot.udpate_spinners(mousePos - self.get_pos())

    def draw(self, where: pygame.Surface = None) -> None:
        super().draw(where)
        for slot in self.slots:
            slot.draw(where)
        
        self.lightboard.draw(where)
        self.plugboard.draw(where)
        
class GroupedRotors(list):
    def __init__(self, parent: pygame.Surface = None) -> None:
        list.__init__(self, [None for _ in range(6)])

        self.parent = parent if (type(parent) != None) else pygame.Surface([0, 0])
        self.prevPos: list[pygame.Vector2] = [None for _ in range(6)]

    def insert(self, *rotors: Rotor, slot: int = None) -> None:
        if (slot == None):
            if (len(rotors) == 1):
                for i in range(len(self)):
                    if (self[i] == None):
                        if (self.prevPos[i] != None): rotors[0].set_pos(self.prevPos[i])
                        self[i] = rotors[0]
                        break
            else:
                for rotor in rotors:
                    for i in range(len(self)):
                        if (self[i] == None):
                            if (self.prevPos[i] != None): rotor.set_pos(self.prevPos[i])
                            self[i] = rotor
                            break
        
        else:
            if (self.prevPos[slot] != None):
                rotors[0].set_pos(self.prevPos[slot])

            self[slot] = rotors[0]
        
    def pop(self, index: int | pygame.Vector2 = None) -> Rotor:
        if (index == None): index = 0
        
        if (type(index) != pygame.Vector2):
            super().insert(index, None)
            output: Rotor = super().pop(index + 1)

            if (type(output) != NoneType):
                self.prevPos[index] = output.get_pos()

            return output

        for r in range(len(self)):
            if (self[r] != None and self[r].rect.collidepoint(index)):
                return self.pop(r)

    def draw(self, where: pygame.Surface = None):
        for rotor in self:
            if (rotor == None): continue

            if (where != None): where.blit(rotor, rotor.get_pos())
            else: self.parent.blit(rotor, rotor.get_pos())

async def main():
    pygame.init()
    #monitor_resolution = pygame.Vector2(exts.getResolution())
    display = pygame.display.set_mode([720, 405], pygame.RESIZABLE)
    freeRotors: GroupedRotors = GroupedRotors(display)
    unfreeRotors: GroupedRotors = GroupedRotors(display)

    rotor_sqr = int(display.get_height() / len(freeRotors))

    freeRotor_1 = Rotor(pygame.Rect(0, rotor_sqr * 0, rotor_sqr, rotor_sqr), "I", "A", display)
    freeRotor_2 = Rotor(pygame.Rect(0, rotor_sqr * 1, rotor_sqr, rotor_sqr), "II", "D", display)
    freeRotor_3 = Rotor(pygame.Rect(0, rotor_sqr * 2, rotor_sqr, rotor_sqr), "III", "I", display)
    freeRotor_4 = Rotor(pygame.Rect(0, rotor_sqr * 3, rotor_sqr, rotor_sqr), "IV", "M", display)
    freeRotor_5 = Rotor(pygame.Rect(0, rotor_sqr * 4, rotor_sqr, rotor_sqr), "V", "Q", display)
    freeRotor_6 = Rotor(pygame.Rect(0, rotor_sqr * 5, rotor_sqr, rotor_sqr), "VI", "U", display)

    machine = GuiEnigmaLib(pygame.Rect(rotor_sqr, 0, display.get_width() - rotor_sqr, display.get_height()), display)

    freeRotor: Rotor = None
    freeRotors.insert(freeRotor_1, freeRotor_2, freeRotor_3, freeRotor_4, freeRotor_5, freeRotor_6)

    plug = -1
    running: bool = True
    while running:
        await asyncio.sleep(0)
        display.fill(pygame.Color(0, 0, 0, 255))
        mousePos = pygame.Vector2(pygame.mouse.get_pos())

        for event in pygame.event.get():
            if (event.type == pygame.QUIT):
                running = False
                pygame.quit()
            
            elif (event.type == pygame.MOUSEBUTTONDOWN):
                plug = machine.hovered_over_plugboard(mousePos)
                if (plug != -1): machine.plugboard.pair(plug)
                else:
                    freeRotor = freeRotors.pop(mousePos)
                    if (freeRotor != None): freeRotor.toggle_drag(mousePos)

                    hslot = machine.hovered_over_window(mousePos)
                    if (hslot != 0):
                        machine.uninstall_rotor(hslot)
                        freeRotor = unfreeRotors.pop(hslot)

                        if (freeRotor != None): freeRotor.toggle_drag(mousePos)

                machine.update_spinners(mousePos)
            
            elif (event.type == pygame.MOUSEBUTTONUP):
                if (freeRotor != None):
                    hslot = machine.hovered_over_window(mousePos)
                    if (hslot != 0 and freeRotor.dragging):
                        machine.insert_rotor(freeRotor, hslot)
                        unfreeRotors.insert(freeRotor, slot = hslot)
                    else:
                        freeRotor.dragging = False
                        freeRotors.insert(freeRotor)
                    
                    freeRotor = None
            
            elif (event.type == pygame.KEYDOWN):
                if (machine.full()):
                    for key in machine.lightboard.lightboard:
                        if (pygame.key.get_pressed()[key.key]):
                            machine.encrypt(key.strKey.lower())
            
        if (running):
            if (freeRotor != None and freeRotor.dragging): 
                freeRotor.update(mousePos)

            machine.draw()
            freeRotors.draw()
            if (freeRotor != None):
                freeRotor.draw(display)

            pygame.display.update()

if __name__ == "__main__":
    asyncio.run(main())