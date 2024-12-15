# CLI Tool
This library installs the prev_gen command-line tool to expose commonly used functions in a simpler format.  
It can be used for previews and conversions between all supported formats, run it with no arguments for more details.

# Classes
Each entry below is a class you can import from this library  
(except the palette, that entry is needed to explain the usage modes)

## Color:
### An object that represents a single color  
<details><summary>Available parameters</summary>

```python
color: Color | str | Sequence[float] | NDArray
# The color value to assign, you need to include this value
# Or a hex string
#   '#00f8'     - blue with half opacity
#   '#FFF'      - white, letters can be capital too
#   '00fa00'    - off-green with full opacity
#   '0000'      - black with full transparency, equivalent to no color at all
#                 well, any fully transparent color works the same
#                 this is the way to leave a field empty in 3.0
# Or a css literal
name: str | None = None
# The name to display, hex if empty
desc_left: str | None = None
# Left corner description
desc_right: str | None = None
# Right corner description
model = 'srgb'
```
Full list of models on [github](https://github.com/colour-science/colour?tab=readme-ov-file#31automatic-colour-conversion-graph---colourgraph).
</details>
<details><summary>You can change the mode by specifying the type of color you want</summary>

```python
Color((0.4, 0.2, 0.7))                # sRGB is the default
Color((0.4, 0.2, 0.7), model='oklch') # oklch is the suggested mode due to being based on human perception
Color((0.4, 0.2, 0.7), alpha=.5)      # all work with transparency
```
</details>
<details><summary>you can also specify a name for a color or not</summary>

```python
Color((200, 100, 235), 'purple')     # denormalized RGB with name
Color((0.2, 0.4, 0.7), model='hsv')  # normalized HSV without name
```
</details>
<details><summary>HEX and CSS works regardless of mode specified</summary>
    
```python
Color('#52C7A7', 'mint', model='hsv') # HEX with name (mode ignored)
Color('darkred', model='hsv')         # CSS with no name (mode ignored)
# for css, name not added by default to allow for palettes without any names
```
</details>

## Palette:
### The colors you want to convert to an image

- the user writes Preview(palette) instead of Preview(Palette(palette))

<details><summary>Usage 1 - "It just works"</summary>

(1d list) place colors in the order you want them to appear in the generated image  
the program will figure out a rectangle big enough to fit them all  
</details>
<details><summary>Usage 2 - "Do what I say"</summary>

(2d list) each inner list will be treated as a single row of colors, left-to-right  
use this for full control over the placement of colors in the final image  
- you can leave entire rows transparent if you pass an empty list  
</details>

Check the [example](example.py) for a more direct explanation, it uses mode two.  
Use `Color('0000')` to leave a spot empty - it's simply a fully transparent color

#### Not really meant for direct usage
But not stopping you  
This class actually converts the palette into a standard representation and generates meta information  
This is also an iterator of the colors so you might find some use there  
I don't expect this to actually be useful to anyone, but you can check the code out if you want

<details><summary>Available parameters</summary>

```python
colors: list[Settings | Color] | list[Settings | list[Color]]
# The color palette used
# The long type hint is because of the two Usage modes
```
</details>

<details><summary>Iterator usage</summary>

```python
palette = ...
p = Palette(palette)
p.settings  # Settings
for i in p:
    i.pos  # top-left (x, y) 
    i.size  # (x, y)
    i.col  # Color
```
</details>

## Settings:
### An object that controls the behavior of the program  
- if you don't want to overwrite any settings just omit it  

<details><summary>Available parameters</summary>

```python
fileName: str = 'result'
# File name to save into (no extension, png)
fontName: str = 'Nunito'
# for png = local file name (no extension, true type)
# for svg = Google Font name
# the default is packaged with the module, no need to have installed
fontOpts: dict | None = None
# Google Fonts API options (for svg)
gridHeight: int = 168
# Height of each individual color tile
gridWidth: int = 224
# Width of each individual color tile
barHeight: int = 10
# Height of the darkened bar at the bottom of each tile
nameOffset: int = -10
# Vertical offset of the color name printed within the tile
hexOffset: int = 35
# Vertical offset of the hex value printed below color name
hexOffsetNameless: int = 0
# Vertical offset of the hex value printed if no name given
descOffsetX: int = 15
# Horizontal offset of the corner descriptions
descOffsetY: int = 20
# Vertical offset of the corner descriptions
nameSize: int = 40
# Text size of the color name
hexSize: int = 26
# Text size of the hex value printed under the color name
hexSizeNameless: int = 34
# Text size of the hex value printed if no name given
descSize: int = 26
# Text size of the corner descriptions
showHash: bool = False
# Display the hash symbol before hex colors
```
</details>

## Previewer:
### The entrypoint that generates the image
It always returns the generated image, either as PIL.Image (png) or XML.etree.ElementTree (svg)
  
<details><summary>Available parameters</summary>

```python
palette: list[Settings | Color] | list[Settings | list[Color]]
# The palette of colors to generate an image for
# The long type hint is because of the two Usage modes
show: bool = True
# Whether to display the generated image to the user
save: bool = False
# Whether to save the image to disk
output: Literal['png', 'svg'] = 'png'
# Output file type
```
</details>

## Reverser:
### Regenerate the code
Take an image and get back the code used to generate it

<details><summary>Available parameters</summary>

```python
image: Image | ElementTree | str
save: Literal['py', 'yml', 'json', 'toml'] | None = None
# If set, will save the file to reverse.<ext>
```
</details>

## Config:
### Configuration file readers
The internal configuration is a Python dictionary, but it can be saved in any of these formats with the use of the corresponding class

<details><summary>Available parameters</summary>

```python
palette: list[Settings | list[Color]]
# the Usage 2 representation of the palette
output: Literal['py', 'yml', 'toml', 'json'] = 'yml'
# File 
```
</details>

<details><summary>Available attributes</summary>

`palette` -> internal usage2 representation  
`data` -> formatted string
</details>

<details><summary>Available methods</summary>

`.read(file)` -> read a file into the internal representation  
`.write(filename)` -> save to a formatted file
</details>

## Filters:
### Mangle your images (artfully)

<details><summary>Available parameters</summary>

```python
image: str | PIL.Image
# the filename to open or PIL.Image to use
```
</details>

<details><summary>Available methods</summary>

```python
iterate() -> Iterable[tuple[int, int]]
# iterate through (x, y) pixel coordinates with a progress bar
monochrome(chroma: float = 0., hue: float = 0., fileName: str | None = None) -> PIL.Image
# make a picture perceptually monochroma, with optional chroma and hue
# impossible colors get clipped to sRGB
```
</details>

## GUI:
### An interactive editor
If you change the example, it will be saved to gui.py.  
It also returns the image, just in case you wanted it.  
I don't expect people to use it, but if you only have a notepad - this at least has syntax highlighting.
