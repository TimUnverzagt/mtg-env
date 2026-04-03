import pygame
from pygame import Surface
from pygame import Rect
from pygame.font import Font
from typing import Callable
from logging_config import main_log

import rendering.constants as const
from gameengine.player import PlayerInfo
from gameengine.state import GameState
                
get_surface_width: Callable[[Surface], int] = lambda surf: surf.get_width()
get_surface_height: Callable[[Surface], int] = lambda surf: surf.get_height()

class SimpleVisualization:

    def __init__(self) -> None:
        pygame.init()
        self.width: int = 1280
        self.height: int = 960
        self.size: tuple[int, int] = self.width, self.height
        self.screen: Surface = pygame.display.set_mode(self.size)
        self.seperator_thickness: int = 10
        self._draw_background()
        pygame.display.flip()
        main_log.debug("Vizualisation is ready.")

    def step(self, game_state: GameState) -> None:
        self.render_environment(game_state)                

    def render_environment(self, game_state: GameState) -> None:
        self._draw_background()
        
        # Render player screens
        self.screen.blit(self.render_player_screen(game_state.player_infos[0]), (15,15))
        player2_origin: tuple[int, int] = (0 + 15, self.height//2 + self.seperator_thickness//2 + 15)
        self.screen.blit(self.render_player_screen(game_state.player_infos[1]), player2_origin)

        # Render misc ui
        ui: Surface = self.render_ui(game_state)
        ui_padding_top: int = 15
        ui_padding_right: int = 15
        ui_origin: tuple[int, int] = (
            self.width - (ui.get_size()[0] + ui_padding_right),
            ui_padding_top)
        self.screen.blit(ui, ui_origin)

        # Update whole image
        pygame.display.flip()
        return
    
    def render_ui(self, game_state: GameState) -> Surface:
        ui_elements: list[Surface] = []
        ui_elements.append(self._render_text("Turn: {}".format(game_state.player_turns_completed//len(game_state.player_infos) + 1)))
        ui_elements.append(self._render_text("Active Player: {}".format(game_state.player_infos[game_state.active_player_index].name)))
        current_env_step: str  = game_state.upcoming_event.name
        ui_elements.append(self._render_text("Current Step: {}".format(current_env_step)))

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

    def render_player_screen(self, info: PlayerInfo) -> Surface:
        player_screen_size: tuple[int, int] = (self.width, self.height//2 - self.seperator_thickness//2)
        player_screen: Surface = Surface(player_screen_size)

        player_screen_elements: list[Surface] = []
        player_screen_elements.append (self._render_text("{}: {} hp".format(info.name, info.current_life)))
        player_screen_elements.append (self._render_text("Cards in Hand: {} ".format(len(info.cards_in_hand))))
        player_screen_elements.append (self._render_text("Cards in Library: {} ".format(info.cards_in_library)))

        player_screen_width: int = max(map(get_surface_width, player_screen_elements))
        player_screen_height: int = sum(map(get_surface_height, player_screen_elements))
        player_screen_size: tuple[int, int] = (player_screen_width, player_screen_height)
        player_screen: Surface = Surface(player_screen_size)
        height_offset: int = 0
        for surface in player_screen_elements:
            player_screen.blit(surface, (0, height_offset))
            height_offset += surface.get_height()
        return player_screen
    
    def _draw_background(self) -> None:
        self.screen.fill(const.BLACK)
        
        #draw player seperator
        seperator_origin: tuple[int, int] = (0, self.height//2 - self.seperator_thickness//2) 
        seperator_size: tuple[int, int] = (self.width, self.seperator_thickness)
        seperator: Rect = Rect(seperator_origin, seperator_size)
        pygame.draw.rect(self.screen, const.WHITE, seperator)