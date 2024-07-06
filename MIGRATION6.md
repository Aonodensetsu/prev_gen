# Migration guide from prior versions to 6.x+

## General
- Camel case switched to snake case

## Color
The major changes in this version stem from a backend change for color support.  
This allows much flexibility, at the cost of dropping backwards compatibility.

Clarifications:
- mode -> model
- lch -> oklch
- rgb -> srgb
- dict() -> to_dict()
- to_dict now returns a dict instead of a list, it contains only non-default values

Changes:
- alpha is now a separate attribute, clamped between 0. and 1.
- name, desc_left, desc_right cannot be None anymore, use empty strings
- denormalized support dropped
- however, colors can be created with any Sequence, including numpy arrays
- "original" attribute marks the first used model, it has no conversion error
- despite sRGB being the default model, the *always* available format is RGB due to less conversion error
- anything can be checked for equality with a Color, it will return true if it matches the color's sRGB
- color equality checks have a tolerance of 1%
- *color model* attributes are automatically lowercased

---

Since backwards compatibility was dropped, further renaming occurred for clarification. 

## Table
Renamed to `Palette`

## Preview
Renamed to `Previewer`

## PreviewSVG
Replaced by `Previewer(output='svg')`

## Reverse
Renamed to `Reverser`

## ReverseSVG
Combined into `Reverser` based on parameter type or file extension

## TOML, PYTHON, JSON, YAML
Combined into `Config(output='<file ext>')`, default yml.  
- `tomlkit` instead of `toml` used for parsing TOML, this allows the use of inline dicts.

## Settings
The bar and text functions are no longer user-editable.

## LazyloadError
Removed, this was a subclass of AttributeError, and is simply replaced by an AttributeError.

## Literals
Removed, still supported via the upstream library as simply a string

## Additions
- Better type hints for literals (config & image formats and supported colors models)

