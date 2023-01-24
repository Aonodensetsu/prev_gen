# Palette preview generator

Creates a palette preview image by using given color values  
Based on the great gruvbox theme, where even the preview is impressive:  
![gruvbox theme](https://camo.githubusercontent.com/410b3ab80570bcd5b470a08d84f93caa5b4962ccd994ebceeb3d1f78364c2120/687474703a2f2f692e696d6775722e636f6d2f776136363678672e706e67)

# Usage:
You need **Python** with modules: **os**, **pillow**, **math**, **colorsys**, **typing**  
1. Open up [pallete.py](palette.py) and set up the colors how you want (instruction in the file)  
2. Run [main.py](main.py) with Python to generate a PNG with those colors
3. result.png is where your palette lives - a preview window will open as well

Simple as can be!

# Changelog:
Version 8 - changed hex to uppercase, file name to save into is a setting now
![Current version](result.png)

Archive of past results - to laugh or cry:  
[Version 7](version7.png) - added little corner descriptions as in gruvbox, repositioned text a bit
[Version 6](version6.png) - the rewrite update, the project is rewritten from scratch to fix any bugs and improve usability  
Version 5 - the README update, finally added the Usage section (no image)  
[Version 4](version4.png) - the little darker strip at the bottom goes a long way in making this look good  
[Version 3](version3.png) - finally fixed the font, arial was making me angry, had to fix contrast again  
[Version 2](version2.png) - made in a day, got text contrast to about where I want it  
[Version 1](version1.png) - made in an hour, quality confirms it :p