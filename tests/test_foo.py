from texture_atlas import (
    atlas_region_to_rect,
    build_sprite_dict,
    parse_name_from_filepath,
)


def test_parse_name_from_filepath():
    filepath = "raw_assets/balloon1.png"
    name = parse_name_from_filepath(filepath)
    assert name == "balloon1"


def test_atlas_region_to_rect():
    region = {
        "filepath": "raw_assets/balloon1.png",
        "x": 1,
        "y": 1,
        "width": 204,
        "height": 256,
    }
    rect = atlas_region_to_rect(region)
    assert rect.left == region["x"]
    assert rect.top == region["y"]
    assert rect.right == region["x"] + region["width"]
    assert rect.bottom == region["y"] + region["height"]


def test_build_sprite_dict_zero():
    assert build_sprite_dict([]) == {}


def test_build_sprite_dict_no_sprites():
    assert build_sprite_dict(["noggen_fogger"]) == {}


def test_build_sprite_dict_one_sprite():
    assert build_sprite_dict(["noggen-01", "noggen-02"]) == {
        "noggen": ["noggen-01", "noggen-02"]
    }


def test_build_sprite_dict_one_sprite_wrong_order():
    assert build_sprite_dict(["noggen-02", "noggen-01"]) == {
        "noggen": ["noggen-01", "noggen-02"]
    }


def test_build_sprite_dict_multi_sprite():
    assert build_sprite_dict(["noggen-02", "flarf-01"]) == {
        "noggen": ["noggen-02"],
        "flarf": ["flarf-01"],
    }
