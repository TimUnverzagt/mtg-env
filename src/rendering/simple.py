import pygame
from pygame import Surface
from pygame import Rect
from pygame.font import Font
import rendering.constants as const
from environment.base import BaseEnvironment as MtgEnv
from environment.player import Player

class SimpleVisualization:

    def __init__(self) -> None:
        pygame.init()
        self.width: int = 640
        self.height: int = 480
        self.size: tuple[int, int] = self.width, self.height
        self.screen: Surface = pygame.display.set_mode(self.size)
        self.seperator_thickness: int = 10;
        self._draw_background()
        pygame.display.flip()

    def render_environment(self, env: MtgEnv) -> None:
        self._draw_background()
        self.screen.blit(self.render_player_screen(env.players[0]), (0,0))
        player2_origin: tuple[int, int] = (0, self.height//2 + self.seperator_thickness//2 )
        self.screen.blit(self.render_player_screen(env.players[1]), player2_origin)
        pygame.display.flip()
        return
    
    def render_player_screen(self, player: Player) -> Surface:
        player_screen_size: tuple[int, int] = (self.width, self.height//2 - self.seperator_thickness//2)
        player_screen: Surface = Surface(player_screen_size)

        life_text: Font = Font(None, 30)
        life_display: Surface = life_text.render(
            "Player1: {} hp".format(player.current_life),
            True,
            const.WHITE,
            const.BLACK)
        player_screen.blit(life_display, (15,15))
        return player_screen
    
    def _draw_background(self) -> None:
        self.screen.fill(const.BLACK)
        
        #draw player seperator
        seperator_origin: tuple[int, int] = (0, self.height//2 - self.seperator_thickness//2) 
        seperator_size: tuple[int, int] = (self.width, self.seperator_thickness)
        seperator: Rect = Rect(seperator_origin, seperator_size)
        pygame.draw.rect(self.screen, const.WHITE, seperator)