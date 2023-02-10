## Palette
### The colors you want to convert to an image
<details><summary>Usage 1 - "It just works"</summary>

(1d list) place colors in the order you want them to appear in the generated image  
the program will make a rectangle big enough to fit them all  
</details>
<details><summary>Usage 2 - "Do what I say"</summary>

(2d list) each inner list will be treated as a single row of colors, left-to-right  
use this for full control over the placement of colors in the final image  
\- you can even leave entire rows transparent if you pass an empty list  
</details>

with either option you can put `None` in the table to leave one field transparent  

## Color
### An object that represents a single color  
<details><summary>Available parameters</summary>

```python
color: str | tuple[float, float, float] | tuple[int, int, int]
# The color value to assign, you need to include this value
name: str | None = None
# The name to display
desc_left: str | None = None
# Left corner description
desc_right: str | None = None
# Right corner description
mode: Literal['rgb', 'hsv', 'hls', 'yiq'] = 'rgb'
# Specifies type of color to convert from
```
</details>
<details><summary>you can change the mode by specifying the type of color you want</summary>

```python
Color((0.2, 0.4, 0.7))              # RGB is the default
Color((0.2, 0.4, 0.7), mode='hsv')  # other supported modes are HSV, HLS and YIQ
Color((0.2, 0.4, 0.7), mode='hls')
Color((0.2, 0.4, 0.7), mode='yiq')
```
</details>
<details><summary>all the modes support normalized and denormalized values</summary>

but make sure to look at the ranges of values if you want to use denormalized ones  
```python
(R: 0-255,  G: 0-255,  B: 0-255)
(H: 0-179,  S: 0-255,  V: 0-255)
(H: 0-360,  S: 0-100,  L: 0-100)
(Y: 0-255,  I: 0-255,  Q: 0-255)
```
</details>
<details><summary>you can also specify a name for a color or not</summary>

```python
Color((200, 100, 235), 'purple')    # RGB with name
Color((0.2, 0.4, 0.7), mode='hsv')  # HSV without name
```
</details>
<details><summary>HEX works regardless of mode specified</summary>
    
```python
Color('#52c7a7', 'mint', mode='hls') # HEX with name (mode ignored)
```
</details>

## Settings:
### An object that controls the behavior of the program  
\- if you don't want to overwrite any settings just omit it  

<details><summary>Available parameters</summary>

```python
file_name: str = 'result'
# File name to save into (no extension - png)
font: str | None = None
# Font used (no extension - true type) - if none, will use bundled
grid_height: int = 168
# Height of each individual color tile
grid_width: int = 224
# Width of each individual color tile
bar_height: int = 10
# Height of the darkened bar at the bottom of each tile
name_offset: int = -10
# Vertical offset of the color name printed within the tile
hex_offset: int = 35
# Vertical offset of the hex value printed below color name
hex_offset_noname: int = 0
# Vertical offset of the hex value printed if no name given
desc_offset_x: int = 15
# Horizontal offset of the corner descriptions
desc_offset_y: int = 20
# Vertical offset of the corner descriptions
name_size: int = 40
# Text size of the color name
hex_size: int = 26
# Text size of the hex value printed under the color name
hex_size_noname: int = 34
# Text size of the hex value printed if no name given
desc_size: int = 26
# Text size of the corner descriptions
bar_col_fn: Callable[[Color], Color] = (default omitted)
# Function to determine bar color from background color
# You probably shouldn't touch this
text_col_fn: Callable[[Color], Color] = (default omitted)
# Function to determine text color from background color
# You probably shouldn't touch this
```
</details>

## Preview:
### The entrypoint that generates the image
it always returns the generated image, even if you choose to also save it  
  
<details><summary>Available parameters</summary>

```python
palette: list[None | Settings | Color] | list[None | Settings | list[None | Color]]
# The palette of colors to generate an image for, you need to include this value
# The stupid type hint is because of the two Usage modes
save: bool = False
# Whether to save the image to disk
show: bool = False
# Whether to display the generated image to the user
```
</details>

## GUI:
### An interactive editor
it also returns the image, just in case you wanted it  
if you change the example, it will be saved to gui.py

```python
# this is how you use it
from prev_gen import GUI
GUI()
```
