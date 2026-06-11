from collections import defaultdict

from imgui_bundle import imgui, ImVec2, ImVec4
from imgui_bundle.imgui import ImTextureRef

import mtggympy.app_config as conf
import mtggympy.gui.constants as const
#from mtggympy.gameengine.cards.catalog.creatures import CreatureNames
#from mtggympy.gameengine.cards.catalog.lands import LandNames
from mtggympy.gameengine.state import GameState, PlayerState
from mtggympy.gameengine.constants import CardType, ManaColor
from mtggympy.gameengine.gameobjects import CardInstance
from mtggympy.gui.texture import ImageMetaData

counter = 0 # our app state
tapped_creatures: defaultdict[int, bool] = defaultdict(lambda: False)
tapped_lands: defaultdict[int, bool] = defaultdict(lambda: False)

def add_background(image_ref: ImTextureRef, display_size: ImVec2):
    imgui.set_next_window_pos((0, 0))
    imgui.set_next_window_size(display_size)
    imgui.begin("bg", False,
        imgui.WindowFlags_.no_title_bar |
        imgui.WindowFlags_.no_move |
        imgui.WindowFlags_.no_inputs |
        imgui.WindowFlags_.no_scrollbar |
        imgui.WindowFlags_.no_bring_to_front_on_focus
    )

    imgui.image(image_ref, display_size)
    imgui.end()
    
def gui(game_state: GameState|None, image_refs: dict[str, ImageMetaData], display_size: ImVec2):

    add_background(image_refs[const.BACKGROUND_IMAGE_NAME].shader_ref, display_size)
    if game_state is None:
        return

    imgui.set_next_window_pos((0, 0))
    imgui.set_next_window_size(display_size)
    root_flags = 0
    root_flags |= imgui.WindowFlags_.no_title_bar
    root_flags |= imgui.WindowFlags_.no_scrollbar
    root_flags |= imgui.WindowFlags_.no_background
    root_flags |= imgui.WindowFlags_.no_resize

    imgui.begin("root", False, root_flags)
    shared_space_avail: ImVec2 = imgui.get_content_region_avail()

    add_meta(game_state, shared_space_avail)
    imgui.same_line()
    add_players(game_state, shared_space_avail, image_refs)
    imgui.same_line()
    add_interface(shared_space_avail)
    imgui.end()



def add_card(image_refs: dict[str, ImageMetaData], card_name:str, position: int, tapped:bool) -> bool:
    imgui.set_next_item_allow_overlap()
    uv0: ImVec2 = ImVec2(0.0, 0.0)
    uv1: ImVec2 = ImVec2(1.0, 1.0)
    bg_col: ImVec4 = ImVec4(0.0, 0.0, 0.0, 1.0)
    tint_col: ImVec4 = ImVec4(1.0, 1.0, 1.0, 1.0); 
    imgui.push_style_var(imgui.StyleVar_.frame_padding, ImVec2(0, 0))
    imgui.push_id(position)
    tapping_offset: int = int(conf.CARD_HEIGHT * (1 - conf.CARD_WH_RATIO) + 1)
    if(tapped):
        imgui.set_cursor_pos_y(imgui.get_cursor_pos_y() + tapping_offset)
        image_meta: ImageMetaData = image_refs[card_name + const.TAPPED_MODIFIER]
        button_size: ImVec2 = ImVec2(conf.CARD_HEIGHT, int(conf.CARD_HEIGHT * conf.CARD_WH_RATIO))
    else:
        image_meta: ImageMetaData = image_refs[card_name]
        button_size: ImVec2 = ImVec2(int(conf.CARD_HEIGHT * conf.CARD_WH_RATIO), conf.CARD_HEIGHT)

    clicked: bool = False
    if imgui.image_button("Box", image_meta.shader_ref, button_size, uv0, uv1, bg_col, tint_col):
        clicked = True
    imgui.pop_id()
    imgui.pop_style_var()
    return clicked

def add_meta(game_state: GameState, parent_space_avail: ImVec2):
    meta_flags = imgui.WindowFlags_.no_scrollbar
    meta_flags |= imgui.WindowFlags_.no_background
    imgui.begin_child("Meta", ImVec2(parent_space_avail.x * 0.1, 0), True, meta_flags)
    shared_space_avail: ImVec2 = ImVec2(imgui.get_content_region_avail().x, imgui.get_content_region_avail().y-10)
    add_meta_player(game_state.player_states[1], shared_space_avail, 2)
    add_meta_game(game_state, shared_space_avail)
    add_meta_player(game_state.player_states[0], shared_space_avail, 1)
    imgui.end_child()

def add_meta_player(player_state: PlayerState, parent_space_avail: ImVec2, position: int):
    meta_p1_flags = imgui.WindowFlags_.no_scrollbar
    meta_p1_flags |= imgui.WindowFlags_.no_background
    imgui.begin_child("MetaP"+str(position), ImVec2(parent_space_avail.x, parent_space_avail.y*0.4), False, meta_p1_flags)
    imgui.bullet_text("Life: {}".format(player_state.current_life))
    imgui.bullet_text("Library: {}".format(len(player_state.cards_in_library)))
    imgui.bullet_text("Mana_W: {}".format(player_state.floating_mana[ManaColor.WHITE]))
    imgui.bullet_text("Mana_U: {}".format(player_state.floating_mana[ManaColor.BLUE]))
    imgui.bullet_text("Mana_B: {}".format(player_state.floating_mana[ManaColor.BLACK]))
    imgui.bullet_text("Mana_R: {}".format(player_state.floating_mana[ManaColor.RED]))
    imgui.bullet_text("Mana_G: {}".format(player_state.floating_mana[ManaColor.GREEN]))
    imgui.bullet_text("Mana_C: {}".format(player_state.floating_mana[ManaColor.COLORLESS]))
    imgui.end_child()

def add_meta_game(game_state: GameState, parent_space_avail: ImVec2):
    meta_game_flags = imgui.WindowFlags_.no_scrollbar
    meta_game_flags |= imgui.WindowFlags_.no_background
    imgui.begin_child("MetaGame", ImVec2(parent_space_avail.x, parent_space_avail.y*0.2), False, meta_game_flags)
    imgui.bullet_text("Current turn: {}".format(int(game_state.halfturns_completed/2) + 1))
    active_player_name: str = game_state.player_states[game_state.active_player_index].name
    imgui.bullet_text("Active Player: {}".format(active_player_name))
    imgui.bullet_text("Current Step: {}".format(game_state.upcoming_event.name))
    imgui.end_child()


def add_players(game_state: GameState, parent_space_avail: ImVec2, image_refs: dict[str, ImageMetaData]):
    players_flags = imgui.WindowFlags_.no_scrollbar
    players_flags |= imgui.WindowFlags_.no_background
    imgui.begin_child("Players", ImVec2(parent_space_avail.x * 0.75, 0), False, players_flags)
    shared_space_avail: ImVec2 = ImVec2(imgui.get_content_region_avail().x, imgui.get_content_region_avail().y-25)
    add_player(game_state.player_states[1], shared_space_avail, image_refs, hand_on_bottom=False, position=2)
    add_player(game_state.player_states[0], shared_space_avail, image_refs, hand_on_bottom=True, position=1)
    imgui.end_child()

def add_player(player_state: PlayerState, parent_space_avail: ImVec2, image_refs: dict[str, ImageMetaData], hand_on_bottom: bool, position: int):
    player_flags = imgui.WindowFlags_.no_scrollbar
    player_flags |= imgui.WindowFlags_.no_background
    imgui.begin_child("Player-{}".format(position), ImVec2(0, parent_space_avail.y * 0.5), True, player_flags)
    shared_space_avail: ImVec2 = ImVec2(imgui.get_content_region_avail().x, imgui.get_content_region_avail().y)
    imgui.begin_child("Player-{}".format(position), ImVec2(shared_space_avail.x*0.85, 0), 
                      False,
                      imgui.WindowFlags_.no_scrollbar)
    shared_child_space_avail: ImVec2 = ImVec2(imgui.get_content_region_avail().x, imgui.get_content_region_avail().y-10)
    if hand_on_bottom:
        add_battlefield(player_state, shared_child_space_avail, image_refs, position)
        add_hand(player_state, shared_child_space_avail, image_refs, position)
    else:
        add_hand(player_state, shared_child_space_avail, image_refs, position)
        add_battlefield(player_state,shared_child_space_avail, image_refs, position)
    imgui.end_child()
    imgui.same_line()
    add_lands(player_state, shared_space_avail, image_refs, position)
    imgui.end_child()

def add_hand(player_state: PlayerState, parent_space_avail: ImVec2, image_refs: dict[str, ImageMetaData], position: int):
    hand_flags = imgui.WindowFlags_.horizontal_scrollbar
    hand_flags |= imgui.WindowFlags_.no_background
    imgui.begin_child("Hand-{}".format(position), ImVec2(0, parent_space_avail.y * 0.5), False, hand_flags)
    for n in range(len(player_state.cards_in_hand)):
        if(position == 1):
            add_card(image_refs, player_state.cards_in_hand[n].card_name, n, False)
        else:
            add_card(image_refs, const.CARDBACK_IMAGE_NAME, n, False)
        imgui.same_line()
    imgui.end_child()

def add_battlefield(player_state: PlayerState, parent_space_avail: ImVec2, image_refs: dict[str, ImageMetaData], position: int):
    battlefield_flags = imgui.WindowFlags_.horizontal_scrollbar
    battlefield_flags |= imgui.WindowFlags_.no_background
    nonlands: list[CardInstance] = []
    for card in player_state.cards_in_play:
        if card.type is not CardType.LAND:
            nonlands.append(card)
    imgui.begin_child("Battlefield-{}".format(position), ImVec2(0, parent_space_avail.y * 0.5), False, battlefield_flags)
    for n, card in enumerate(nonlands):
        clicked: bool = add_card(image_refs, card.card_name, n , card.tapped)
        if clicked:
            card.tapped = not card.tapped
        imgui.same_line()
    imgui.end_child()

def add_lands(player_state: PlayerState, parent_space_avail: ImVec2, image_refs: dict[str, ImageMetaData], position: int):
    lands_flags = imgui.WindowFlags_.no_background
    lands: list[CardInstance] = []
    for card in player_state.cards_in_play:
        if card.type is CardType.LAND:
            lands.append(card)
    imgui.begin_child("Lands-{}".format(position), ImVec2(parent_space_avail.x*0.15, 0), False, lands_flags)
    for n, card in enumerate(lands):
        clicked: bool = add_card(image_refs, card.card_name , n , card.tapped)
        if clicked:
            card.tapped = not card.tapped
        imgui.set_cursor_pos_y(imgui.get_cursor_pos_y() - conf.CARD_HEIGHT * 0.9)
    imgui.end_child()

def add_interface(parent_space_avail: ImVec2):
    interface_flags = imgui.WindowFlags_.no_scrollbar
    interface_flags |= imgui.WindowFlags_.no_background
    imgui.begin_child("Interface", ImVec2(parent_space_avail.x * 0.15, 0), True, interface_flags)
    shared_space_avail: ImVec2 = imgui.get_content_region_avail()
    add_log(shared_space_avail)
    add_actions(shared_space_avail)
    imgui.end_child()

def add_log(parent_space_avail: ImVec2): 
    log_flags = imgui.WindowFlags_.no_scrollbar
    log_flags |= imgui.WindowFlags_.no_background
    imgui.begin_child("Log", ImVec2(0, parent_space_avail.y*0.5), False, log_flags)
    for i in range(100):
        imgui.text("%04d: scrollable region" % i)
    imgui.end_child()

def add_actions(parent_space_avail: ImVec2): 
    actions_flags = imgui.WindowFlags_.no_scrollbar
    actions_flags |= imgui.WindowFlags_.no_background
    imgui.begin_child("Actions", ImVec2(0, parent_space_avail.y*0.5), False, actions_flags)
    for i in range(100):
        imgui.text("%04d: scrollable region" % i)
    imgui.end_child()



