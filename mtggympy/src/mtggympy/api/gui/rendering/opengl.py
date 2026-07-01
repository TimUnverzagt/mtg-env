import threading

import pygame
import time
from pygame import Surface
from threading import Thread, Condition
from imgui_bundle import imgui, ImVec2
from imgui_bundle.imgui import IO
from imgui_bundle.python_backends import pygame_backend
import OpenGL.GL as gl

import os
from collections import defaultdict

from pygame.time import Clock

import mtggympy.config.app_config as conf
from mtggympy.gameengine.constants import GameStep
import mtggympy.api.gui.layout.myimgui as layout
import mtggympy.api.gui.constants as const
from mtggympy.api.gui.texture import ImageMetaData
from mtggympy.gameengine.state.core import GameState, PlayerState
from mtggympy.gameengine.cards.catalog.creatures import CreatureNames
from mtggympy.gameengine.cards.catalog.lands import LandNames
from mtggympy.gameengine.cards.catalog.info import CreatureInfo, LandInfo
import mtggympy.gameengine.cards.catalog.lookup as lookup
from mtggympy.gameengine.cards.instances.factory import generate_card_instance
from mtggympy.server.session.obfuscation import observe_game_state
from mtggympy.server.session.observed_state import ObservedGameState
    
def load_image(path_from_asset_dir: str) -> Surface:
    filepath: str = os.path.join(conf.ASSET_DIR, path_from_asset_dir)
    return pygame.image.load(filepath)

def load_card_image(card_name:str) -> Surface:
    return load_image(os.path.join("cards", card_name + ".png"))

class GlRenderer():

    def __init__(self) -> None:
        self.ui_thread = Thread(target=self.run_renderer, daemon=True)
        self.ui_thread.start()
        self.obs_condition = Condition()
        self.screen: Surface
        self.clock: Clock
        self.impl: pygame_backend.PygameRenderer
        self.running: bool
        self.io: IO
        self.observations: ObservedGameState | None = None
        
    def _init_from_thread(self) -> None:
        pygame.init()
        imgui.create_context()

        self.screen = pygame.display.set_mode((conf.UI_STARTING_WIDTH, conf.UI_STARTING_HEIGHT), pygame.DOUBLEBUF | pygame.OPENGL | pygame.RESIZABLE)
        self.clock = pygame.time.Clock()
        self.impl = pygame_backend.PygameRenderer()
        self.running = True
        self.io = imgui.get_io()
        self.io.display_size = ImVec2(self.screen.get_size()[0], self.screen.get_size()[1])


        self.image_assets: dict[str, ImageMetaData] = {}
        background: Surface = load_image(const.BACKGROUND_IMAGE_NAME)
        self.image_assets[const.BACKGROUND_IMAGE_NAME] = self.add_texture_to_gl(background)
        cardback: Surface = load_card_image(lookup.FACEDOWN_CARD_NAME)
        self.image_assets[lookup.FACEDOWN_CARD_NAME] = self.add_texture_to_gl(cardback)

        for name, info in lookup.FULL_CATALOG.items():
            card_surface:Surface = load_card_image(name)
            self.image_assets[name] = self.add_texture_to_gl(card_surface)
            if isinstance(info, CreatureInfo) or isinstance(info, LandInfo):
                self.image_assets[name + const.TAPPED_MODIFIER] = self.add_texture_to_gl(pygame.transform.rotate(card_surface, 270.0))

    def _del_from_thread(self):
        pygame.quit()


    def add_texture_to_gl(self, surface: pygame.Surface) -> ImageMetaData:
        surface = surface.convert_alpha()

        width, height = surface.get_size()
        pixel_data = pygame.image.tostring(surface, "RGBA", False)

        tex_id = gl.glGenTextures(1) # type: ignore
        gl.glBindTexture(gl.GL_TEXTURE_2D, tex_id) # type: ignore

        gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MIN_FILTER, gl.GL_LINEAR) # type: ignore
        gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MAG_FILTER, gl.GL_LINEAR) # type: ignore

        gl.glTexImage2D(
            gl.GL_TEXTURE_2D, # type: ignore
            0,
            gl.GL_RGBA, # type: ignore
            width,
            height,
            0,
            gl.GL_RGBA, # type: ignore
            gl.GL_UNSIGNED_BYTE, # type: ignore
            pixel_data
        )
        tex_id = int(tex_id)# type:ignore
        return ImageMetaData(imgui.ImTextureRef(tex_id), surface.get_width(), surface.get_height())

    def run_renderer(self):
        self._init_from_thread()
        ui_state: layout.UiState = layout.UiState()
        while self.running:

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                self.impl.process_event(event) # type: ignore
            self.impl.process_inputs()

            # Flush old frame
            imgui.new_frame()
            gl.glClearColor(0, 0, 0, 1) # type: ignore
            gl.glClear(gl.GL_COLOR_BUFFER_BIT) # type: ignore

            # Layout UI 
            with self.obs_condition:
                layout.gui(ui_state, self.observations, self.image_assets, self.io.display_size)

            # Render new frame
            imgui.render()
            self.impl.render(imgui.get_draw_data())
            pygame.display.flip()
            self.clock.tick(60)

        self._del_from_thread()


if __name__ == "__main__":
    p1_info: PlayerState = PlayerState("Alice",
                                     current_life=20,
                                     cards_in_hand=[generate_card_instance(CreatureNames.ALPHA_MYR.value),
                                                    generate_card_instance(LandNames.WASTES.value),
                                                    generate_card_instance(CreatureNames.SLIVER_CONSTRUCT.value),
                                                    generate_card_instance(CreatureNames.OMEGA_MYR.value),
                                                    generate_card_instance(LandNames.WASTES.value),
                                                    generate_card_instance(LandNames.WASTES.value)],
                                     cards_in_play=[generate_card_instance(LandNames.WASTES.value),
                                                    generate_card_instance(LandNames.WASTES.value),
                                                    generate_card_instance(CreatureNames.OMEGA_MYR.value)],
                                     cards_in_library=[generate_card_instance(CreatureNames.SLIVER_CONSTRUCT.value),
                                                       generate_card_instance(CreatureNames.SLIVER_CONSTRUCT.value),
                                                       generate_card_instance(CreatureNames.SLIVER_CONSTRUCT.value)],
                                     death_description=None,
                                     floating_mana=defaultdict(lambda: 0),
                                     additional_land_drops=0)
    p2_info: PlayerState = PlayerState("Bob",
                                     current_life=20,
                                     cards_in_hand=[generate_card_instance(CreatureNames.ALPHA_MYR.value),
                                                    generate_card_instance(LandNames.WASTES.value),
                                                    generate_card_instance(CreatureNames.SLIVER_CONSTRUCT.value),
                                                    generate_card_instance(CreatureNames.OMEGA_MYR.value),
                                                    generate_card_instance(LandNames.WASTES.value),
                                                    generate_card_instance(LandNames.WASTES.value)],
                                     cards_in_play=[generate_card_instance(LandNames.WASTES.value),
                                                    generate_card_instance(LandNames.WASTES.value),
                                                    generate_card_instance(CreatureNames.OMEGA_MYR.value),
                                                    generate_card_instance(CreatureNames.METALLIC_SLIVER.value)],
                                     cards_in_library=[generate_card_instance(CreatureNames.METALLIC_SLIVER.value),
                                                       generate_card_instance(CreatureNames.METALLIC_SLIVER.value),
                                                       generate_card_instance(CreatureNames.METALLIC_SLIVER.value),
                                                       generate_card_instance(CreatureNames.METALLIC_SLIVER.value)],
                                     death_description=None,
                                     floating_mana=defaultdict(lambda: 0),
                                     additional_land_drops= 0)
    current_state: GameState = GameState(halfturns_completed=2, 
              active_player_index=0, 
              game_over=False,
              step=GameStep.MAIN_1,
              player_states=[p1_info, p2_info],
              winner_positions=[],
              lands_played_this_turn=1)
    
    renderer: GlRenderer = GlRenderer()
    time.sleep(1)
    renderer.observations = observe_game_state(current_state, 0)
    forever = threading.Event()
    forever.wait()