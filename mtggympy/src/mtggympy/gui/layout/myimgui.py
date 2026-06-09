from collections import defaultdict

from imgui_bundle import imgui, ImVec2

import mtggympy.app_config as conf

counter = 0 # our app state
tapped_cards: defaultdict[int, bool] = defaultdict(lambda: False)

def background(image_ref: int, display_size: ImVec2):
    imgui.set_next_window_pos((0, 0))
    imgui.set_next_window_size(display_size)
    imgui.begin("bg", False,
        imgui.WindowFlags_.no_title_bar |
        imgui.WindowFlags_.no_move |
        imgui.WindowFlags_.no_inputs |
        imgui.WindowFlags_.no_scrollbar |
        imgui.WindowFlags_.no_bring_to_front_on_focus
    )

    imgui.image(imgui.ImTextureRef(image_ref), display_size)
    imgui.end()
    
def gui(image_refs: dict[str, int], display_size: ImVec2):

    background(image_refs["background"], display_size)

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
    add_players(shared_space_avail)
    imgui.same_line()
    add_interface(shared_space_avail)
    imgui.end()

def add_meta(parent_space_avail: ImVec2):
    meta_flags = imgui.WindowFlags_.no_scrollbar
    meta_flags |= imgui.WindowFlags_.no_background
    imgui.begin_child("Meta", ImVec2(parent_space_avail.x * 0.2, 0), True, meta_flags)
    shared_space_avail: ImVec2 = ImVec2(imgui.get_content_region_avail().x, imgui.get_content_region_avail().y-10)
    add_meta_p1(shared_space_avail)
    add_meta_game(shared_space_avail)
    add_meta_p2(shared_space_avail)
    imgui.end_child()

def add_meta_p1(parent_space_avail: ImVec2):
    meta_p1_flags = imgui.WindowFlags_.no_scrollbar
    meta_p1_flags |= imgui.WindowFlags_.no_background
    imgui.begin_child("MetaP1", ImVec2(parent_space_avail.x, parent_space_avail.y*0.4), False, meta_p1_flags)
    for i in range(100):
        imgui.text("%04d: scrollable region" % i)
    imgui.end_child()

def add_meta_game(parent_space_avail: ImVec2):
    meta_game_flags = imgui.WindowFlags_.no_scrollbar
    meta_game_flags |= imgui.WindowFlags_.no_background
    imgui.begin_child("MetaGame", ImVec2(parent_space_avail.x, parent_space_avail.y*0.2), False, meta_game_flags)
    for i in range(100):
        imgui.text("%04d: scrollable region" % i)
    imgui.end_child()

def add_meta_p2(parent_space_avail: ImVec2):
    meta_p2_flags = imgui.WindowFlags_.no_scrollbar
    meta_p2_flags |= imgui.WindowFlags_.no_background
    imgui.begin_child("MetaP2", ImVec2(parent_space_avail.x, parent_space_avail.y*0.4), False, meta_p2_flags)
    for i in range(100):
        imgui.text("%04d: scrollable region" % i)
    imgui.end_child()


def add_players(parent_space_avail: ImVec2):
    players_flags = imgui.WindowFlags_.no_scrollbar
    players_flags |= imgui.WindowFlags_.no_background
    imgui.begin_child("Players", ImVec2(parent_space_avail.x * 0.6, 0), False, players_flags)
    shared_space_avail: ImVec2 = ImVec2(imgui.get_content_region_avail().x, imgui.get_content_region_avail().y-25)
    add_player(shared_space_avail, hand_on_bottom=False, player_id="2")
    add_player(shared_space_avail, hand_on_bottom=True, player_id="1")
    imgui.end_child()

def add_player(parent_space_avail: ImVec2, hand_on_bottom: bool, player_id: str):
    player_flags = imgui.WindowFlags_.no_scrollbar
    player_flags |= imgui.WindowFlags_.no_background
    imgui.begin_child("Player-{}".format(player_id), ImVec2(0, parent_space_avail.y * 0.5), True, player_flags)
    shared_space_avail: ImVec2 = ImVec2(imgui.get_content_region_avail().x, imgui.get_content_region_avail().y)
    imgui.begin_child("Player-{}".format(player_id), ImVec2(shared_space_avail.x*0.8, 0), 
                      False,
                      imgui.WindowFlags_.no_scrollbar)
    shared_child_space_avail: ImVec2 = ImVec2(imgui.get_content_region_avail().x, imgui.get_content_region_avail().y-10)
    if hand_on_bottom:
        add_battlefield(shared_child_space_avail, player_id)
        add_hand(shared_child_space_avail, player_id)
    else:
        add_hand(shared_child_space_avail, player_id)
        add_battlefield(shared_child_space_avail, player_id)
    imgui.end_child()
    imgui.same_line()
    add_lands(shared_space_avail, player_id)
    imgui.end_child()

def add_hand(parent_space_avail: ImVec2, player_id: str):
    hand_flags = imgui.WindowFlags_.horizontal_scrollbar
    hand_flags |= imgui.WindowFlags_.no_background
    imgui.begin_child("Hand-{}".format(player_id), ImVec2(0, parent_space_avail.y * 0.5), False, hand_flags)
    button_size=ImVec2(int(conf.CARD_HEIGHT * conf.CARD_WH_RATIO), conf.CARD_HEIGHT)
    for n in range(100):
        imgui.push_id(n)
        imgui.button("Box", button_size)
        imgui.same_line()
        imgui.pop_id()
    imgui.end_child()

def add_battlefield(parent_space_avail: ImVec2, player_id: str):
    battlefield_flags = imgui.WindowFlags_.horizontal_scrollbar
    battlefield_flags |= imgui.WindowFlags_.no_background
    imgui.begin_child("Battlefield-{}".format(player_id), ImVec2(0, parent_space_avail.y * 0.5), False, battlefield_flags)
    button_size=ImVec2(int(conf.CARD_HEIGHT * conf.CARD_WH_RATIO), conf.CARD_HEIGHT)
    for n in range(100):
        imgui.push_id(n)
        if(tapped_cards[n]):
            varied_size = ImVec2(button_size.y, button_size.x)
        else:
            varied_size = button_size
        if imgui.button("Box", varied_size):
            tapped_cards[n] = not tapped_cards[n]
        imgui.same_line()
        imgui.pop_id()
    imgui.end_child()

def add_lands(parent_space_avail: ImVec2, player_id: str):
    lands_flags = imgui.WindowFlags_.no_background
    imgui.begin_child("Lands-{}".format(player_id), ImVec2(parent_space_avail.x*0.2, 0), False, lands_flags)
    button_size=ImVec2(int(conf.CARD_HEIGHT * conf.CARD_WH_RATIO), conf.CARD_HEIGHT)
    for n in range(100):
        imgui.push_id(n)
        imgui.button("Box", button_size)
        imgui.pop_id()
    imgui.end_child()

def add_interface(parent_space_avail: ImVec2):
    interface_flags = imgui.WindowFlags_.no_scrollbar
    interface_flags |= imgui.WindowFlags_.no_background
    imgui.begin_child("Interface", ImVec2(parent_space_avail.x * 0.2, 0), True, interface_flags)
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



