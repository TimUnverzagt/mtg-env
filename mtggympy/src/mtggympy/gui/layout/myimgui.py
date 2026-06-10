from collections import defaultdict

from imgui_bundle import imgui, ImVec2, ImVec4
from imgui_bundle.imgui import ImTextureRef

import mtggympy.app_config as conf
import mtggympy.gui.constants as const
from mtggympy.gameengine.cards.catalog.creatures import CreatureNames
from mtggympy.gameengine.cards.catalog.lands import LandNames
from mtggympy.gui.texture import ImageMetaData

counter = 0 # our app state
tapped_creatures: defaultdict[int, bool] = defaultdict(lambda: False)
tapped_lands: defaultdict[int, bool] = defaultdict(lambda: False)

def background(image_ref: ImTextureRef, display_size: ImVec2):
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
    
def gui(image_refs: dict[str, ImageMetaData], display_size: ImVec2):

    background(image_refs[const.BACKGROUND_IMAGE_NAME].shader_ref, display_size)

    imgui.set_next_window_pos((0, 0))
    imgui.set_next_window_size(display_size)
    root_flags = 0
    root_flags |= imgui.WindowFlags_.no_title_bar
    root_flags |= imgui.WindowFlags_.no_scrollbar
    root_flags |= imgui.WindowFlags_.no_background

    imgui.begin("root", False, root_flags)
    shared_space_avail: ImVec2 = imgui.get_content_region_avail()

    add_meta(shared_space_avail)
    imgui.same_line()
    add_players(shared_space_avail, image_refs)
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

def add_meta(parent_space_avail: ImVec2):
    meta_flags = imgui.WindowFlags_.no_scrollbar
    meta_flags |= imgui.WindowFlags_.no_background
    imgui.begin_child("Meta", ImVec2(parent_space_avail.x * 0.1, 0), True, meta_flags)
    shared_space_avail: ImVec2 = ImVec2(imgui.get_content_region_avail().x, imgui.get_content_region_avail().y-10)
    add_meta_p1(shared_space_avail)
    add_meta_game(shared_space_avail)
    add_meta_p2(shared_space_avail)
    imgui.end_child()

def add_meta_p1(parent_space_avail: ImVec2):
    meta_p1_flags = imgui.WindowFlags_.no_scrollbar
    meta_p1_flags |= imgui.WindowFlags_.no_background
    imgui.begin_child("MetaP1", ImVec2(parent_space_avail.x, parent_space_avail.y*0.4), False, meta_p1_flags)
    imgui.bullet_text("Life: 20")
    imgui.bullet_text("Library: 33")
    imgui.bullet_text("Mana_W: 0")
    imgui.bullet_text("Mana_U: 0")
    imgui.bullet_text("Mana_B: 0")
    imgui.bullet_text("Mana_R: 0")
    imgui.bullet_text("Mana_G: 0")
    imgui.end_child()

def add_meta_game(parent_space_avail: ImVec2):
    meta_game_flags = imgui.WindowFlags_.no_scrollbar
    meta_game_flags |= imgui.WindowFlags_.no_background
    imgui.begin_child("MetaGame", ImVec2(parent_space_avail.x, parent_space_avail.y*0.2), False, meta_game_flags)
    imgui.bullet_text("Current turn: 1")
    imgui.bullet_text("Active Player: 1")
    imgui.bullet_text("Current Step: MainPhase 1")
    imgui.end_child()

def add_meta_p2(parent_space_avail: ImVec2):
    meta_p2_flags = imgui.WindowFlags_.no_scrollbar
    meta_p2_flags |= imgui.WindowFlags_.no_background
    imgui.begin_child("MetaP2", ImVec2(parent_space_avail.x, parent_space_avail.y*0.4), False, meta_p2_flags)
    imgui.bullet_text("Life: 20")
    imgui.bullet_text("Library: 33")
    imgui.bullet_text("Mana_W: 0")
    imgui.bullet_text("Mana_U: 0")
    imgui.bullet_text("Mana_B: 0")
    imgui.bullet_text("Mana_R: 0")
    imgui.bullet_text("Mana_G: 0")
    imgui.end_child()


def add_players(parent_space_avail: ImVec2, image_refs: dict[str, ImageMetaData]):
    players_flags = imgui.WindowFlags_.no_scrollbar
    players_flags |= imgui.WindowFlags_.no_background
    imgui.begin_child("Players", ImVec2(parent_space_avail.x * 0.75, 0), False, players_flags)
    shared_space_avail: ImVec2 = ImVec2(imgui.get_content_region_avail().x, imgui.get_content_region_avail().y-25)
    add_player(shared_space_avail,image_refs, hand_on_bottom=False, player_id="2")
    add_player(shared_space_avail,image_refs, hand_on_bottom=True, player_id="1")
    imgui.end_child()

def add_player(parent_space_avail: ImVec2, image_refs: dict[str, ImageMetaData], hand_on_bottom: bool, player_id: str):
    player_flags = imgui.WindowFlags_.no_scrollbar
    player_flags |= imgui.WindowFlags_.no_background
    imgui.begin_child("Player-{}".format(player_id), ImVec2(0, parent_space_avail.y * 0.5), True, player_flags)
    shared_space_avail: ImVec2 = ImVec2(imgui.get_content_region_avail().x, imgui.get_content_region_avail().y)
    imgui.begin_child("Player-{}".format(player_id), ImVec2(shared_space_avail.x*0.85, 0), 
                      False,
                      imgui.WindowFlags_.no_scrollbar)
    shared_child_space_avail: ImVec2 = ImVec2(imgui.get_content_region_avail().x, imgui.get_content_region_avail().y-10)
    if hand_on_bottom:
        add_battlefield(shared_child_space_avail, image_refs, player_id)
        add_hand(shared_child_space_avail, image_refs, player_id)
    else:
        add_hand(shared_child_space_avail, image_refs, player_id)
        add_battlefield(shared_child_space_avail, image_refs, player_id)
    imgui.end_child()
    imgui.same_line()
    add_lands(shared_space_avail, image_refs, player_id)
    imgui.end_child()

def add_hand(parent_space_avail: ImVec2, image_refs: dict[str, ImageMetaData], player_id: str):
    hand_flags = imgui.WindowFlags_.horizontal_scrollbar
    hand_flags |= imgui.WindowFlags_.no_background
    imgui.begin_child("Hand-{}".format(player_id), ImVec2(0, parent_space_avail.y * 0.5), False, hand_flags)
    for n in range(7):
        if(player_id == "1"):
            add_card(image_refs, CreatureNames.METALLIC_SLIVER.value, n, False)
        else:
            add_card(image_refs, const.CARDBACK_IMAGE_NAME, n, False)
        imgui.same_line()
    imgui.end_child()

def add_battlefield(parent_space_avail: ImVec2, image_refs: dict[str, ImageMetaData], player_id: str):
    battlefield_flags = imgui.WindowFlags_.horizontal_scrollbar
    battlefield_flags |= imgui.WindowFlags_.no_background
    imgui.begin_child("Battlefield-{}".format(player_id), ImVec2(0, parent_space_avail.y * 0.5), False, battlefield_flags)
    for n in range(3):
        clicked: bool = add_card(image_refs, CreatureNames.ALPHA_MYR.value ,n, tapped_creatures[n])
        if clicked:
            tapped_creatures[n] = not tapped_creatures[n]
        imgui.same_line()
    imgui.end_child()

def add_lands(parent_space_avail: ImVec2, image_refs: dict[str, ImageMetaData], player_id: str):
    lands_flags = imgui.WindowFlags_.no_background
    imgui.begin_child("Lands-{}".format(player_id), ImVec2(parent_space_avail.x*0.15, 0), False, lands_flags)
    for n in range(5):
        clicked: bool = add_card(image_refs, LandNames.WASTES.value ,n, tapped_lands[n])
        if clicked:
            tapped_lands[n] = not tapped_lands[n]
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



