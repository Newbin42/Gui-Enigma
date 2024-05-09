import pygame
import Keyboard

class Surface(pygame.Surface):
    def __init__(self, rect: pygame.Rect, parent: pygame.Surface = None) -> None:
        pygame.Surface.__init__(self, [rect.width, rect.height], flags = pygame.SRCALPHA)

        self.rect: pygame.Rect = rect
        self.parent: pygame.Surface = parent if (parent) else pygame.Surface([rect.width, rect.height])

    def flush(self):
        self.fill(pygame.Color(0, 0, 0, 255))

    def set_pos(self, pos: list[float, float]) -> None:
        self.rect.topleft = pos
    
    def set_center(self, pos: list[float, float]) -> None:
        self.rect.center = pos
    
    def get_pos(self) -> pygame.Vector2:
        return pygame.Vector2(self.rect.topleft)
    
    def get_center(self) -> pygame.Vector2:
        return pygame.Vector2(self.rect.center)

    def draw(self, where: pygame.Surface = None) -> None:
        "Will draw on an empty defaut parent if no surface or parent is provided."
        if (where != None): where.blit(self, self.get_pos())
        else: self.parent.blit(self, self.get_pos())

class KeyboardSurface(Surface):
    def __init__(self, rect: pygame.Rect, parent: pygame.Surface = None) -> None:
        super().__init__(rect, parent)

        self.keyboard = Keyboard.createKeyBoard(self)
        