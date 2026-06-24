from __future__ import annotations
from collections import defaultdict
from dataclasses import dataclass, field
from queue import Empty

from imgui_bundle import imgui, ImVec2, ImVec4
from imgui_bundle.imgui import ImTextureRef

import mtggympy.app_config as conf
from mtggympy.logging_config import UI_LOG_QUEUE
from mtggympy.logging_config import ui_log as logger

from mtggympy.helpers.pubsub import DESKTOP_INTENT_QUEUE

import mtggympy.api.gui.constants as const
from mtggympy.api.gui.texture import ImageMetaData
import mtggympy.gameengine.parsing as engine_parsing
#from mtggympy.gameengine.cards.catalog.creatures import CreatureNames
#from mtggympy.gameengine.cards.catalog.lands import LandNames
from mtggympy.gameengine.cards.catalog.lookup import FACEDOWN_CARD_NAME
from mtggympy.gameengine.state.event import ActionData, ActionIntent, PlayerEvent, event_from_step
from mtggympy.gameengine.constants import CardType, ManaColor
from mtggympy.gameengine.cards.logic.instances import CardInstance, CreatureInstance, generate_card_instance

from mtggympy.server.session.observed_state import ObservedGameState, ObservedSelfState, ObservedOpponentState
@dataclass
class UiState:
    counter = 0 # our app state
    tapped_creatures: defaultdict[int, bool] = field(default_factory=lambda: defaultdict(lambda: False))
    tapped_lands: defaultdict[int, bool] = field(default_factory=lambda: defaultdict(lambda: False))
    log_entries: list[str] = field(default_factory=lambda: [])
    current_player_event: PlayerEvent | None = field(default_factory=lambda: None)
    selected_action: ActionData | None = field(default_factory=lambda: None)
    active_action_arg: list[int] | None = field(default_factory=lambda: None)
    cached_action_args: list[list[int]] | None = field(default_factory=lambda: None)
    action_commited: bool = False
    transition_induced: bool = False #TODO: GMight be fragile to unsuccessful input transfer

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

def set_style(show_editor: bool) -> None:
    imgui.style_colors_classic()
    if(show_editor):
        imgui.show_style_editor()

def invalidate_cached_action_data(ui_state: UiState) -> None:
        logger.debug("Invalidating UI Cache")
        ui_state.selected_action = None
        ui_state.active_action_arg = []
        ui_state.cached_action_args = []
    
def gui(ui_state: UiState, game_state: ObservedGameState|None, image_refs: dict[str, ImageMetaData], display_size: ImVec2) -> None:

    add_background(image_refs[const.BACKGROUND_IMAGE_NAME].shader_ref, display_size)
    if game_state is None:
        return
    
    new_event: PlayerEvent = event_from_step(game_state.step)
    if ui_state.current_player_event is None:
        ui_state.current_player_event = new_event
    if ui_state.transition_induced:
        logger.info("Cleaning ui_state due to event transition")
        invalidate_cached_action_data(ui_state)
        ui_state.current_player_event = new_event
        ui_state.action_commited = False
        ui_state.transition_induced = False
        logger.debug("Action blocked: {}".format(ui_state.action_commited))
    

    imgui.set_next_window_pos((0, 0))
    imgui.set_next_window_size(display_size)
    root_flags = 0
    root_flags |= imgui.WindowFlags_.no_title_bar
    root_flags |= imgui.WindowFlags_.no_scrollbar
    root_flags |= imgui.WindowFlags_.no_background
    root_flags |= imgui.WindowFlags_.no_resize

    imgui.begin("root", False, root_flags)
    shared_space_avail: ImVec2 = imgui.get_content_region_avail()

    add_meta(ui_state, game_state, shared_space_avail)
    imgui.same_line()
    add_players(ui_state, game_state, shared_space_avail, image_refs)
    imgui.same_line()
    add_interface(ui_state, game_state,shared_space_avail)
    set_style(show_editor=False)
    imgui.end()

def add_wrapping_text(text_space_avail: ImVec2, text: str) -> None: 
        imgui.push_text_wrap_pos(imgui.get_cursor_pos()[0] + text_space_avail.x)
        imgui.text(text)
        imgui.pop_text_wrap_pos()

def add_card(ui_state: UiState, image_refs: dict[str, ImageMetaData], card:CardInstance, position: int, tapped:bool) -> bool:
    imgui.set_next_item_allow_overlap()
    uv0: ImVec2 = ImVec2(0.0, 0.0)
    uv1: ImVec2 = ImVec2(1.0, 1.0)
    bg_col: ImVec4 = ImVec4(0.0, 0.0, 0.0, 1.0)
    tint_col: ImVec4 = ImVec4(1.0, 1.0, 1.0, 1.0); 
    if(isinstance(card, CreatureInstance) and card.summoning_sick):
        tint_col: ImVec4 = ImVec4(0.8, 0.75, 0.75, 0.75); 
    if(isinstance(card, CreatureInstance) and card.attacking):
        tint_col: ImVec4 = ImVec4(0.8, 0.3, 0.3, 1.0); 
    imgui.push_style_var(imgui.StyleVar_.frame_padding, ImVec2(0, 0))
    imgui.push_id(position)
    tapping_offset: int = int(conf.CARD_HEIGHT * (1 - conf.CARD_WH_RATIO) + 1)
    if(tapped):
        imgui.set_cursor_pos_y(imgui.get_cursor_pos_y() + tapping_offset)
        image_meta: ImageMetaData = image_refs[card.card_name + const.TAPPED_MODIFIER]
        button_size: ImVec2 = ImVec2(conf.CARD_HEIGHT, int(conf.CARD_HEIGHT * conf.CARD_WH_RATIO))
    else:
        image_meta: ImageMetaData = image_refs[card.card_name]
        button_size: ImVec2 = ImVec2(int(conf.CARD_HEIGHT * conf.CARD_WH_RATIO), conf.CARD_HEIGHT)

    clicked: bool = False
    if imgui.image_button("Box", image_meta.shader_ref, button_size, uv0, uv1, bg_col, tint_col):
        clicked = True
    imgui.pop_id()
    imgui.pop_style_var()
    return clicked

def add_meta(ui_state: UiState, game_state: ObservedGameState, parent_space_avail: ImVec2):
    meta_flags = imgui.WindowFlags_.no_scrollbar
    meta_flags |= imgui.WindowFlags_.no_background
    imgui.begin_child("Meta", ImVec2(parent_space_avail.x * 0.1, 0), True, meta_flags)
    shared_space_avail: ImVec2 = ImVec2(imgui.get_content_region_avail().x, imgui.get_content_region_avail().y-10)
    add_meta_player(ui_state, game_state.opponent_states[0], shared_space_avail, 2)
    add_meta_game(ui_state, game_state, shared_space_avail)
    add_meta_player(ui_state, game_state.self_state, shared_space_avail, 1)
    imgui.end_child()

def add_meta_player(ui_state: UiState, player_state: ObservedSelfState | ObservedOpponentState, parent_space_avail: ImVec2, position: int):
    meta_p1_flags = imgui.WindowFlags_.no_scrollbar
    meta_p1_flags |= imgui.WindowFlags_.no_background
    imgui.begin_child("MetaP"+str(position), ImVec2(parent_space_avail.x, parent_space_avail.y*0.4), False, meta_p1_flags)
    imgui.bullet_text("Life: {}".format(player_state.current_life))
    imgui.bullet_text("Library: {}".format(player_state.cards_in_library))
    imgui.bullet_text("Mana_W: {}".format(player_state.floating_mana[ManaColor.WHITE]))
    imgui.bullet_text("Mana_U: {}".format(player_state.floating_mana[ManaColor.BLUE]))
    imgui.bullet_text("Mana_B: {}".format(player_state.floating_mana[ManaColor.BLACK]))
    imgui.bullet_text("Mana_R: {}".format(player_state.floating_mana[ManaColor.RED]))
    imgui.bullet_text("Mana_G: {}".format(player_state.floating_mana[ManaColor.GREEN]))
    imgui.bullet_text("Mana_C: {}".format(player_state.floating_mana[ManaColor.COLORLESS]))
    imgui.end_child()

def add_meta_game(ui_state: UiState, game_state: ObservedGameState, parent_space_avail: ImVec2):
    meta_game_flags = imgui.WindowFlags_.no_scrollbar
    meta_game_flags |= imgui.WindowFlags_.no_background
    child_space: ImVec2 = ImVec2(parent_space_avail.x, parent_space_avail.y*0.2)
    imgui.begin_child("MetaGame", child_space, False, meta_game_flags)
    add_wrapping_text(child_space, "Current turn: {}".format(int(game_state.halfturns_completed/2) + 1))
    active_player_name: str = game_state.name_of_active_player
    add_wrapping_text(child_space, "Active Player: {}".format(active_player_name))
    add_wrapping_text(child_space, "Current Step: {}".format(game_state.step.name))
    add_wrapping_text(child_space, "Lands played: {}".format(game_state.lands_played_this_turn))
    imgui.end_child()


def add_players(ui_state: UiState, game_state: ObservedGameState, parent_space_avail: ImVec2, image_refs: dict[str, ImageMetaData]):
    players_flags = imgui.WindowFlags_.no_scrollbar
    players_flags |= imgui.WindowFlags_.no_background
    imgui.begin_child("Players", ImVec2(parent_space_avail.x * 0.75, 0), False, players_flags)
    shared_space_avail: ImVec2 = ImVec2(imgui.get_content_region_avail().x, imgui.get_content_region_avail().y-25)
    add_player(ui_state, game_state.opponent_states[0], shared_space_avail, image_refs, position=2)
    add_player(ui_state, game_state.self_state, shared_space_avail, image_refs, position=1)
    imgui.end_child()

def add_player(ui_state: UiState, state: ObservedSelfState | ObservedOpponentState, parent_space_avail: ImVec2, image_refs: dict[str, ImageMetaData], position: int):
    player_flags = imgui.WindowFlags_.no_scrollbar
    player_flags |= imgui.WindowFlags_.no_background
    imgui.begin_child("Player-{}".format(position), ImVec2(0, parent_space_avail.y * 0.5), True, player_flags)
    shared_space_avail: ImVec2 = ImVec2(imgui.get_content_region_avail().x, imgui.get_content_region_avail().y)
    imgui.begin_child("Player-{}".format(position), ImVec2(shared_space_avail.x*0.85, 0), 
                      False,
                      imgui.WindowFlags_.no_scrollbar)
    shared_child_space_avail: ImVec2 = ImVec2(imgui.get_content_region_avail().x, imgui.get_content_region_avail().y-10)
    if isinstance(state, ObservedSelfState):
        add_battlefield(ui_state, state, shared_child_space_avail, image_refs, position)
        add_hand_self(ui_state, state, shared_child_space_avail, image_refs, position)
    else:
        add_hand_opponent(ui_state, state, shared_child_space_avail, image_refs, position)
        add_battlefield(ui_state, state,shared_child_space_avail, image_refs, position)
    imgui.end_child()
    imgui.same_line()
    add_lands(ui_state, state, shared_space_avail, image_refs, position)
    imgui.end_child()

def add_hand_self(ui_state: UiState, state: ObservedSelfState, parent_space_avail: ImVec2, image_refs: dict[str, ImageMetaData], position: int):
    hand_flags = imgui.WindowFlags_.horizontal_scrollbar
    hand_flags |= imgui.WindowFlags_.no_background
    imgui.begin_child("Hand-{}".format(position), ImVec2(0, parent_space_avail.y * 0.5), False, hand_flags)
    for n in range(len(state.cards_in_hand)):
        add_card(ui_state, image_refs, state.cards_in_hand[n], n, False)
        imgui.same_line()
    imgui.end_child()

def add_hand_opponent(ui_state: UiState, state: ObservedOpponentState, parent_space_avail: ImVec2, image_refs: dict[str, ImageMetaData], position: int):
    hand_flags = imgui.WindowFlags_.horizontal_scrollbar
    hand_flags |= imgui.WindowFlags_.no_background
    imgui.begin_child("Hand-{}".format(position), ImVec2(0, parent_space_avail.y * 0.5), False, hand_flags)
    for n in range(state.cards_in_hand):
        add_card(ui_state, image_refs, generate_card_instance(FACEDOWN_CARD_NAME), n, False)
        imgui.same_line()
    imgui.end_child()

def add_battlefield(ui_state: UiState, state: ObservedSelfState | ObservedOpponentState, parent_space_avail: ImVec2, image_refs: dict[str, ImageMetaData], position: int):
    battlefield_flags = imgui.WindowFlags_.horizontal_scrollbar
    battlefield_flags |= imgui.WindowFlags_.no_background
    nonlands: list[CardInstance] = []
    for card in state.cards_in_play:
        if card.type is not CardType.LAND:
            nonlands.append(card)
    imgui.begin_child("Battlefield-{}".format(position), ImVec2(0, parent_space_avail.y * 0.5), False, battlefield_flags)
    for n, card in enumerate(nonlands):
        #clicked: bool = add_card(image_refs, card.card_name, n , card.tapped)
        #if clicked:
        add_card(ui_state, image_refs, card, n , card.tapped)
        imgui.same_line()
    imgui.end_child()

def add_lands(ui_state: UiState, state: ObservedSelfState | ObservedOpponentState, parent_space_avail: ImVec2, image_refs: dict[str, ImageMetaData], position: int):
    lands_flags = imgui.WindowFlags_.no_background
    lands: list[CardInstance] = []
    for card in state.cards_in_play:
        if card.type is CardType.LAND:
            lands.append(card)
    imgui.begin_child("Lands-{}".format(position), ImVec2(parent_space_avail.x*0.15, 0), False, lands_flags)
    for n, card in enumerate(lands):
        clicked: bool = add_card(ui_state, image_refs, card , n , card.tapped)
        if clicked:
            card.tapped = not card.tapped
        imgui.set_cursor_pos_y(imgui.get_cursor_pos_y() - conf.CARD_HEIGHT * 0.9)
    imgui.end_child()

def add_interface(ui_state: UiState, game_state: ObservedGameState, parent_space_avail: ImVec2):
    interface_flags = imgui.WindowFlags_.no_background
    interface_flags |= imgui.WindowFlags_.no_scroll_with_mouse
    interface_flags |= imgui.WindowFlags_.no_scrollbar
    imgui.begin_child("Interface", ImVec2(parent_space_avail.x * 0.15, 0), True, interface_flags)
    shared_space_avail: ImVec2 = imgui.get_content_region_avail()
    add_log(ui_state, shared_space_avail)
    add_actions(ui_state, game_state, shared_space_avail)
    imgui.end_child()

def add_log(ui_state: UiState, parent_space_avail: ImVec2): 
    try:
        new_record = UI_LOG_QUEUE.get_nowait()
        ui_state.log_entries.append(new_record.getMessage())
    except Empty:
        pass
    #log_flags = imgui.WindowFlags_.no_scrollbar
    log_flags = imgui.WindowFlags_.no_background
    imgui.begin_child("Log", ImVec2(0, parent_space_avail.y*0.5), True, log_flags)
    for entry in ui_state.log_entries:
        add_wrapping_text(parent_space_avail, entry)
    imgui.end_child()

def add_actions(ui_state: UiState, game_state: ObservedGameState, parent_space_avail: ImVec2): 
    event: PlayerEvent = event_from_step(game_state.step)
    actions_flags = imgui.WindowFlags_.no_scrollbar
    actions_flags |= imgui.WindowFlags_.no_background
    child_space_avail: ImVec2 = ImVec2(parent_space_avail.x, parent_space_avail.y*0.5)
    imgui.begin_child("Actions", child_space_avail, False, actions_flags)
    imgui.text("Action Menu")
    item_height: float = imgui.get_text_line_height_with_spacing() + 1
    if imgui.begin_list_box("##Action", ImVec2(child_space_avail.x, item_height*len(event.value.possible_actions))):
        for action in event.value.possible_actions:
            imgui.push_id(action.name)
            is_previously_selected: bool = (ui_state.selected_action is not None) and (action == ui_state.selected_action)
            clicked, _ = imgui.selectable(action.name, is_previously_selected)
            if clicked and ui_state.selected_action != action:
                invalidate_cached_action_data(ui_state)
                ui_state.selected_action = action
            imgui.pop_id()
        imgui.end_list_box()
    if ui_state.selected_action is None:
        imgui.text("None")
    else:
        imgui.text(ui_state.selected_action.name)
    # Argument Input UI
    if ui_state.selected_action:
        if ui_state.selected_action.value.dimensionality <= 0:
            add_commit_button(ui_state)
        else: 
            if ui_state.selected_action.value.expects_collection:
                add_collection_input_ui(ui_state)
            else:
                add_simple_input_ui(ui_state)
    imgui.end_child()

def add_simple_input_ui(ui_state: UiState) -> None:
    if ui_state.selected_action is None:
        return
    if not ui_state.active_action_arg:
        ui_state.active_action_arg = []
    prior_arg: list[int]
    if len(ui_state.active_action_arg) == ui_state.selected_action.value.dimensionality:
        prior_arg = ui_state.active_action_arg
    else:
        prior_arg = [0]*ui_state.selected_action.value.dimensionality
    new_arg: list[int] = []
    for n in range(0, ui_state.selected_action.value.dimensionality):
        imgui.push_id(str(ui_state.selected_action.name) + "Arg" + str(n))
        # changed, content
        _, new_input = imgui.input_int("Position", prior_arg[n])
        new_arg.append(new_input)
        imgui.pop_id()
    ui_state.active_action_arg = new_arg
    add_commit_button(ui_state)
    pass

def add_collection_input_ui(ui_state: UiState) -> None:    
    if ui_state.selected_action is None:
        return
    if not ui_state.cached_action_args:
        ui_state.cached_action_args = []
    if not ui_state.active_action_arg:
        ui_state.active_action_arg = []
    add_commit_button(ui_state)
        
    if imgui.begin_table("args_table", 1):
        imgui.table_setup_column("Cached Arguments")
        imgui.table_headers_row()
        for n, arg in enumerate(ui_state.cached_action_args):
            imgui.table_next_row()
            imgui.table_set_column_index(0)
            imgui.text_unformatted(",".join(map(str, arg)))
    imgui.end_table()
    prior_arg: list[int]
    if len(ui_state.active_action_arg) == ui_state.selected_action.value.dimensionality:
        prior_arg = ui_state.active_action_arg
    else:
        prior_arg = [0]*ui_state.selected_action.value.dimensionality
    new_arg: list[int] = []
    for n in range(0, ui_state.selected_action.value.dimensionality):
        imgui.push_id(str(ui_state.selected_action.name) + "Arg" + str(n))
        # changed, content
        _, new_input = imgui.input_int("Position", prior_arg[n])
        new_arg.append(new_input)
        imgui.pop_id()
    ui_state.active_action_arg = new_arg
    if imgui.button("Cache Action Argument"):
        logger.debug("Caching argument {}".format(ui_state.active_action_arg))
        ui_state.cached_action_args.append(new_arg)
        ui_state.active_action_arg = None

def add_commit_button(ui_state: UiState) -> None:
    assert ui_state.selected_action
    if not ui_state.action_commited:
        if ui_state.cached_action_args and len(ui_state.cached_action_args) > 0 :
            if imgui.button("Commit Action"):
                commit_action(ui_state, ui_state.selected_action, ui_state.cached_action_args)
        elif ui_state.active_action_arg and len(ui_state.active_action_arg) > 0 :
            if imgui.button("Commit Action"):
                commit_action(ui_state, ui_state.selected_action, [ui_state.active_action_arg])
        else:
            if imgui.button("Commit Action"):
                commit_action(ui_state, ui_state.selected_action, None)

def commit_action(ui_state: UiState, action: ActionData, params: list[list[int]] | None) -> None:    
    if params:
        logger.debug("Deciding on {} with argument {}".format(action.name, params))
        DESKTOP_INTENT_QUEUE.put(ActionIntent(action, engine_parsing.collection_to_numpy(params)), block=False)
    else:
        logger.debug("Deciding on {} without arguments".format(ui_state.selected_action))
        DESKTOP_INTENT_QUEUE.put(ActionIntent(action, None), block=False)
    ui_state.action_commited = True
    ui_state.transition_induced = True
    logger.debug("Ui Intent Queue length: {}".format(DESKTOP_INTENT_QUEUE.qsize()))



