from pygame import Surface
from pygame.font import Font
from pygame import Vector2 as Vector

import rendering.bounding_box as BoxFunctions
import rendering.surface as SurfaceFuntions
import rendering.frames.padding as Padding
from gameengine.state import GameState
from gameengine.player import PlayerInfo
from gameengine.gameobjects import CardInstance
from rendering.bounding_box import BoundingBox
from rendering.frame_tree import FrameTree, build_frame_tree_from_ratios
import rendering.constants as const


def render_text(text: str) -> Surface:
    font: Font = Font(None, 30)
    return font.render(text, True, const.WHITE, const.BLACK)

def compose_surfaces_into_bounding_frame(name: str, surfaces: list[Surface], target_box: BoundingBox, parent:FrameTree) -> FrameTree:
    total_height: int = sum(map(SurfaceFuntions.get_height, surfaces))
    max_width: int = max(map(SurfaceFuntions.get_width, surfaces))
    containing_frame: FrameTree = FrameTree(name, Vector(max_width, total_height), target_box.offsets)
    relative_y_offset: int = 0
    for idx, surface in enumerate(surfaces):
        sub_frame_dimensions: Vector = Vector(surface.get_width(), surface.get_height())
        sub_frame_offsets: Vector = Vector(target_box.offsets[0], target_box.offsets[1] + relative_y_offset)
        sub_frame: FrameTree = FrameTree(name + "-child-" + str(idx), sub_frame_dimensions, sub_frame_offsets)
        sub_frame.set_content(surface)
        relative_y_offset += surface.get_height()
        containing_frame.add_child(sub_frame)

    frame_scaling: float = BoxFunctions.get_scaling_to_fit_first_box_to_second(containing_frame.global_bounding_box, target_box)
    containing_frame.scale_by(frame_scaling, target_box, parent)
    return containing_frame


def build_player_ui_frame(parent: FrameTree, player_number:int, game_state: GameState) -> FrameTree:
    parent_box: BoundingBox = parent.global_bounding_box
    info: PlayerInfo = game_state.player_infos[player_number - 1]
    ui_target_box:BoundingBox = BoundingBox(
        Vector(parent_box.dimensions[0] * 0.2, parent_box.dimensions[1]), 
        parent_box.offsets)

    ui_texts: list[Surface] = []
    ui_texts.append(render_text("{}: {} hp".format(info.name, info.current_life)))
    ui_texts.append(render_text("Cards in Hand: {} ".format(len(info.cards_in_hand))))
    ui_texts.append(render_text("Cards in Library: {} ".format(len(info.cards_in_library))))
    ui_frame: FrameTree = compose_surfaces_into_bounding_frame("PlayerUI"+str(player_number),ui_texts, ui_target_box, parent)
    return ui_frame

def render_card(card: CardInstance) -> Surface:
    return SurfaceFuntions.load_image(card.card_name, "png", ["assets", "cards"])

def build_player_hand_frame(parent: FrameTree, player_number:int, game_state: GameState, render_topside: bool):
    parent_box: BoundingBox = parent.global_bounding_box
    info: PlayerInfo = game_state.player_infos[player_number-1]
    y_offset_ratio:float = 0 if render_topside else 0.5
    hand_target_box: BoundingBox = BoundingBox(
        Vector(parent_box.dimensions[0]*0.8, parent_box.dimensions[1]*0.5), 
        Vector(parent_box.offsets[0] + parent_box.dimensions[0]* (0.2), 
               parent_box.offsets[1] + parent_box.dimensions[1]*(y_offset_ratio))
    )

    card_surfaces: list[Surface] = []
    for card in info.cards_in_hand:
        card_surfaces.append(render_card(card))
    hand_frame: FrameTree = compose_surfaces_into_bounding_frame("PlayerHand" + str(player_number), card_surfaces, hand_target_box, parent)
    padding_backgroud: Surface = SurfaceFuntions.load_image("padding-border", "png", ["assets"])
    padded_hand_frame: FrameTree = Padding.build_padded_frame_in_place(hand_frame, parent, padding_backgroud, 20, 20, 20, 20)
    return padded_hand_frame

def build_player_frame(background_box: BoundingBox, player_number: int, game_state: GameState, number_of_players: int=2) -> FrameTree:
    y_ratio: float = 1 / number_of_players
    y_offset_ratio: float =  (number_of_players - player_number) / number_of_players
    render_hand_topside: bool = (player_number == 2)
    player_frame: FrameTree = build_frame_tree_from_ratios("PlayerFrame" + str(player_number),
                                                             background_box, Vector(1.0, y_ratio), 
                                                             Vector(0, y_offset_ratio))
    player_frame.add_child(build_player_ui_frame(player_frame, player_number, game_state))
    player_frame.add_child(build_player_hand_frame(player_frame, player_number, game_state, render_hand_topside))
    return player_frame

def build_full_frame(game_state: GameState, width: int, height: int) -> FrameTree:
    background_frame: FrameTree = FrameTree("BaseFrame", Vector(width, height))
    background_frame.set_content(SurfaceFuntions.load_image("battle-background", "png", ["assets"]))
    background_frame.add_child(build_player_frame(background_frame.global_bounding_box, player_number=1, game_state=game_state, number_of_players=2))
    background_frame.add_child(build_player_frame(background_frame.global_bounding_box, player_number=2, game_state=game_state, number_of_players=2))
    return background_frame