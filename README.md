## Create a palette preview image by using a simple config file

![size](https://img.shields.io/github/languages/code-size/aonodensetsu/prev_gen) ![files](https://img.shields.io/github/directory-file-count/aonodensetsu/prev_gen)   
![py dep](https://img.shields.io/pypi/pyversions/prev-gen) [![version](https://img.shields.io/pypi/v/prev-gen)](https://pypi.org/project/prev-gen/4.5.0/)  
![license](https://img.shields.io/pypi/l/prev-gen) [![downloads](https://img.shields.io/badge/releases-here-green?logo=pypi)](https://pypi.org/project/prev-gen/#history)  
[![downloads](https://img.shields.io/badge/wiki-here-pink)](https://github.com/Aonodensetsu/prev_gen/blob/main/WIKI.md) [![downloads](https://img.shields.io/badge/changelog-here-pink)](https://github.com/Aonodensetsu/prev_gen/blob/main/CHANGELOG.md)  

# Usage:
1. `pip install prev_gen`
2. Open up [the wiki](https://github.com/Aonodensetsu/prev_gen/blob/main/WIKI.md) to see how everything works
3. Create a file based on instructions (or just edit [the example](https://github.com/Aonodensetsu/prev_gen/blob/main/example.py))
4. ```python
   # in a python file
   palette = [...]
   from prev_gen import Preview
   Preview(palette)
   ```

# Example:
Inspired by the great [Gruvbox](https://github.com/morhetz/gruvbox) theme, where even the preview is impressive  
And so, below is the Gruvbox palette preview recreated with this app (click for selectable text)  
[![example](https://raw.githubusercontent.com/Aonodensetsu/prev_gen/main/gruvbox.png)](https://raw.githubusercontent.com/Aonodensetsu/prev_gen/main/gruvbox.svg)
