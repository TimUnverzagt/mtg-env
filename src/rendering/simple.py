import pygame
from pygame import Surface
from pygame import Rect
from pygame.font import Font
import keyboard
from typing import Callable

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
        self.seperator_thickness: int = 10
        self._draw_background()
        pygame.display.flip()

    def step(self, env: MtgEnv) -> None:
        self.render_environment(env)
        keyboard.wait('enter')

    def render_environment(self, env: MtgEnv) -> None:
        self._draw_background()
        
        # Render player screens
        self.screen.blit(self.render_player_screen(env.players[0]), (0,0))
        player2_origin: tuple[int, int] = (0, self.height//2 + self.seperator_thickness//2 )
        self.screen.blit(self.render_player_screen(env.players[1]), player2_origin)

        # Render misc ui
        ui: Surface = self.render_ui(env)
        ui_padding_top: int = 15
        ui_padding_right: int = 15
        ui_origin: tuple[int, int] = (
            self.width - (ui.get_size()[0] + ui_padding_right),
            ui_padding_top)
        self.screen.blit(ui, ui_origin)

        # Update whole image
        pygame.display.flip()
        return
    
    def render_ui(self, env: MtgEnv) -> Surface:
        ui_elements: list[Surface] = []
        ui_elements.append(self._render_text("Turn: {}".format(env.player_turns_completed//len(env.players) + 1)))
        ui_elements.append(self._render_text("Active Player: {}".format(env.players[env.active_player_index].name)))
        current_env_step: str  = MtgEnv.action_event_catalog[env.steps_in_turn_completed].name
        ui_elements.append(self._render_text("Current Step: {}".format(current_env_step)))
                
        get_surface_width: Callable[[Surface], int] = lambda surf: surf.get_width()
        get_surface_height: Callable[[Surface], int] = lambda surf: surf.get_height()
        ui_width: int = max(map(get_surface_width, ui_elements))
        ui_height: int = sum(map(get_surface_height, ui_elements))
        ui_size: tuple[int, int] = (ui_width, ui_height)
        ui_screen: Surface = Surface(ui_size)
        height_offset: int = 0
        for surface in ui_elements:
            ui_screen.blit(surface, (0, height_offset))
            height_offset += surface.get_height()
        return ui_screen
    
    def _render_text(self, text: str) -> Surface:
        font: Font = Font (None, 30)
        return font.render(
            text,
            True,
            const.WHITE,
            const.BLACK)

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