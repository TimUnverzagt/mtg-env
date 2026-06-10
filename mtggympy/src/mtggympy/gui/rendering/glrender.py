import pygame
from pygame import Surface
from imgui_bundle import imgui, ImVec2
from imgui_bundle.python_backends import pygame_backend
import OpenGL.GL as gl

import os

import mtggympy.app_config as conf
import mtggympy.gui.layout.myimgui as layout
import mtggympy.gui.constants as const
from mtggympy.gui.texture import ImageMetaData
from mtggympy.gameengine.cards.catalog.creatures import CreatureNames
from mtggympy.gameengine.cards.catalog.lands import LandNames

def load_image(path_from_asset_dir: str) -> Surface:
    filepath: str = os.path.join(conf.ASSET_DIR, path_from_asset_dir)
    return pygame.image.load(filepath)

def load_card_image(card_name:str) -> Surface:
    return load_image(os.path.join("cards", card_name + ".png"))

def add_texture_to_gl(surface: pygame.Surface) -> ImageMetaData:
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


def main():
    pygame.init()
    screen = pygame.display.set_mode((conf.UI_STARTING_WIDTH, conf.UI_STARTING_HEIGHT), pygame.DOUBLEBUF | pygame.OPENGL | pygame.RESIZABLE)
    clock = pygame.time.Clock()

    imgui.create_context()
    impl = pygame_backend.PygameRenderer()
    running = True

    image_assets: dict[str, ImageMetaData] = {}
    background: Surface = load_image(const.BACKGROUND_IMAGE_NAME)
    image_assets[const.BACKGROUND_IMAGE_NAME] = add_texture_to_gl(background)
    cardback: Surface = load_image(const.CARDBACK_IMAGE_NAME)
    image_assets[const.CARDBACK_IMAGE_NAME] = add_texture_to_gl(cardback)

    for name in CreatureNames:
        card_surface:Surface = load_card_image(name.value)
        image_assets[name.value] = add_texture_to_gl(card_surface)
        image_assets[name.value + const.TAPPED_MODIFIER] = add_texture_to_gl(pygame.transform.rotate(card_surface, 270.0))

    for name in LandNames:
        card_surface:Surface = load_card_image(name.value)
        image_assets[name.value] = add_texture_to_gl(card_surface)
        image_assets[name.value + const.TAPPED_MODIFIER] = add_texture_to_gl(pygame.transform.rotate(card_surface, 270.0))
    
    io = imgui.get_io()
    io.display_size = ImVec2(screen.get_size()[0], screen.get_size()[1])

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            impl.process_event(event) # type: ignore
        impl.process_inputs()

        imgui.new_frame()

        # Flush old frame
        gl.glClearColor(0, 0, 0, 1) # type: ignore
        gl.glClear(gl.GL_COLOR_BUFFER_BIT) # type: ignore

        # --- UI ---
        layout.gui(image_assets, io.display_size)

        imgui.render()
        impl.render(imgui.get_draw_data())
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()


if __name__ == "__main__":
    main()