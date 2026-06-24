from dataclasses import dataclass
from imgui_bundle.imgui import ImTextureRef

@dataclass
class ImageMetaData:
    shader_ref: ImTextureRef
    width: int
    height: int