# CLI Tool
This library installs the prev_gen command-line tool to expose commonly used functions in a simpler format.  
It can be used for previews and conversions between all supported formats, run it with no arguments for more details.

# Classes
Each entry below is a class you can import from this library  
(except the palette, that entry is needed to explain the usage modes)

## Palette:
### The colors you want to convert to an image

The class that corresponds to this is Table, however it is used internally for brevity
- the user writes Preview(palette) instead of Preview(Table(palette))

<details><summary>Usage 1 - "It just works"</summary>

(1d list) place colors in the order you want them to appear in the generated image  
the program will make a rectangle big enough to fit them all  
</details>
<details><summary>Usage 2 - "Do what I say"</summary>

(2d list) each inner list will be treated as a single row of colors, left-to-right  
use this for full control over the placement of colors in the final image  
- you can leave entire rows transparent if you pass an empty list  
</details>

Check the [example](example.py) for a more direct explanation, it uses mode two.  
Use `Color('0000')` to leave a spot empty - it's simply a fully transparent color

## Color:
### An object that represents a single color  
<details><summary>Available parameters</summary>

```python
color: Color | Literals | str | tuple[float, float, float] | tuple[float, float, float, float] | tuple[int, int, int] | tuple[int, int, int, int]
# The color value to assign, you need to include this value
# Four values if using transparency, three otherwise (modes below)
# Or a hex string
#   '#fb0000fe' - off-red with almost full opacity
#   '#00f8'     - blue with half opacity
#   '#FFF'      - white, letters can be capital too
#   '00fa00'    - off-green with full opacity
#   '0000'      - black with full transparency, equivalent to no color at all
#                 well, any fully transparent color works the same
#                 this is the way to leave a field empty in 3.0
# Or a css literal
# A full list of which is available in the Literals class
#   'aliceblue' = Literals.aliceblue = '#f0f8ff'
name: str | None = None
# The name to display, hex if empty
descLeft: str | None = None
# Left corner description
descRight: str | None = None
# Right corner description
mode: Literal['rgb', 'hsv', 'hls', 'yiq', 'lch'] = 'rgb'
# Specifies type of color to convert from
```
</details>
<details><summary>You can change the mode by specifying the type of color you want</summary>

```python
Color((0.4, 0.2, 0.7))             # RGB is the default
Color((0.4, 0.2, 0.7), mode='lch') # OKLCH is the suggested mode due to being based on human perception
Color((0.4, 0.2, 0.7), mode='hsv') # other supported modes are HSV, HLS and YIQ
Color((0.4, 0.2, 0.7, 0.5))        # all work with transparency
```
</details>
<details><summary>All the modes support normalized and denormalized values</summary>

but make sure to look at the ranges of values if you want to use denormalized ones  
```python
(R: 0-255,  G: 0-255,  B: 0-255)
(H: 0-179,  S: 0-255,  V: 0-255)
(H: 0-360,  L: 0-100,  S: 0-100)
(Y: 0-255,  I: 0-255,  Q: 0-255)
(L: 0-100,  C: 0-100,  H: 0-360)
* alpha has a range of 0-255
```
</details>
<details><summary>you can also specify a name for a color or not</summary>

```python
Color((200, 100, 235), 'purple')    # denormalized RGB with name
Color((0.2, 0.4, 0.7), mode='hsv')  # normalized HSV without name
```
</details>
<details><summary>HEX and CSS works regardless of mode specified</summary>
    
```python
Color('#52C7A7', 'mint', mode='hls') # HEX with name (mode ignored)
Color('darkred', mode='hls')         # CSS with no name (mode ignored)
# for css, name not added by default to allow for palettes without any names
```
</details>

## Literals:
### Just CSS Literals
That's it, this is an enum of CSS colors, import and use in Color by name  
Or simply write the name as a string

```python
Literals.aliceblue is 'aliceblue' is 'F0F8FF'  
# The class (enum) is just here for convenience if you don't remember them and your editor has hints
```

## Table:
### Not really meant for usage
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
t = Table(palette)
t.settings  # Settings()
for i in t:
    i.pos  # top-left (x, y) 
    i.size  # (x, y)
    i.col  # Color()
    if i.col.alpha == 0: ...
        # will never be the case, invisible colors are filtered
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
barFn: Callable[[Color], Color] = (L * 0.9, C, H)
# Function to determine bar color from background color
# You probably shouldn't touch this
textFn: Callable[[Color], Color] = (dark ? L * 0.9 + 0.3 : L * 0.75 - 0.15, C, H)
# Function to determine text color from background color
# You probably shouldn't touch this
```
</details>

## Preview:
### The entrypoint that generates the image
It always returns the generated PIL.Image
  
<details><summary>Available parameters</summary>

```python
palette: list[Settings | Color] | list[Settings | list[Color]]
# The palette of colors to generate an image for
# The long type hint is because of the two Usage modes
show: bool = True
# Whether to display the generated image to the user
save: bool = False
# Whether to save the image to disk
```
</details>

## Reverse:
### Regenerate the code
Take an image and get back the code used to generate it

<details><summary>Available parameters</summary>

```python
image: Image | str
# The image generated with this tool (or compatible) or a path to it
changes: tuple[int, int] = (0, 1)
# The amount of color changes in the x/y axis to ignore per tile (for the darker bar)
# This is always the default in my program, but can be adjusted for other generators
# Most commonly (0, 0) if the palette doesn't have any flair colors
save: Literal['py', 'yml', 'json', 'toml'] | None = None
# If set, will save the file to reverse.<ext>
```
</details>

## PreviewSVG:
### The entrypoint that generates the image but in SVG format
it always returns the generated image (xml.etree.ElementTree)
  
<details><summary>Available parameters</summary>

```python
palette: list[Settings | Color] | list[Settings | list[Color]]
# The palette of colors to generate an image for
# The long type hint is because of the two Usage modes
show: bool = True
# Whether to display the generated image to the user
save: bool = False
# Whether to save the image to disk
# Saved temporarily regardless, just deleted if you don't want to keep it
# This is to allow opening with a browser, since everyone has one of those
```
</details>

## ReverseSVG:
### Regenerate the code
Take an image and get back the code used to generate it but in SVG

<details><summary>Available parameters</summary>

```python
image: str | xml.etree.ElementTree
# The image generated with this tool (or compatible) or a path to it
save: Literal['py', 'yml', 'json', 'toml'] | None = None
# If set, will save the file to reverseSvg.<ext>
```
</details>

## YAML, JSON, TOML:
### Configuration file readers
The internal configuration is a Python dictionary, but it can be saved in any of these formats with the use of the corresponding class

<details><summary>Available parameters</summary>

```python
palette: list[Settings | list[Color]]
# the Usage 2 representation of the palette
```
</details>
<details><summary>Available methods</summary>

`.read(file)` -> read a file into the Python representation  
`.write()` -> save to a formatted file
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
If you change the example, it will be saved to gui.py  
It also returns the image, just in case you wanted it  
I don't expect people to use it,  
but if you only have a notepad - this at least has syntax highlighting