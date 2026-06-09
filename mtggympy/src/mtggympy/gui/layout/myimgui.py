from imgui_bundle import imgui, ImVec2

counter = 0 # our app state

def background(image_ref: int, display_size: ImVec2):
    imgui.set_next_window_pos((0, 0))
    imgui.set_next_window_size(display_size)
    imgui.begin("bg", False,
        imgui.WindowFlags_.no_title_bar |
        imgui.WindowFlags_.no_resize |
        imgui.WindowFlags_.no_move |
        imgui.WindowFlags_.no_inputs |
        imgui.WindowFlags_.no_bring_to_front_on_focus
    )

    imgui.image(imgui.ImTextureRef(image_ref), display_size)
    imgui.end()
    
    
def gui(image_refs: dict[str, int], display_size: ImVec2):
    background(image_refs["background"], display_size)
    global counter

    # The state of the UI is always in sync with the app state,
    # via standard variables: debugging UI becomes trivial!
    imgui.text(f"Counter ={counter}")

    # We can display a button, and handle its action in one line:
    if imgui.button("increment counter"):
        counter += 1
    # Below, we can also set the counter value via a slider between 0 and 100
    value_changed, counter = imgui.slider_int("Set counter", counter, 0, 100)

    imgui.begin_group()
    #am: Texture = image_refs["alpha-myr"]
    #imgui.image(imgui.ImTextureRef(am.id), imgui.ImVec2(am.width, am.height))
    imgui.end_group()


