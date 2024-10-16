## Create a palette preview image by using a simple config file

![size](https://img.shields.io/github/languages/code-size/aonodensetsu/prev_gen) ![files](https://img.shields.io/github/directory-file-count/aonodensetsu/prev_gen)   
![python](https://img.shields.io/pypi/pyversions/prev-gen) [![version](https://img.shields.io/pypi/v/prev-gen)](https://pypi.org/project/prev-gen/5.1.0/)  
![license](https://img.shields.io/pypi/l/prev-gen) [![releases](https://img.shields.io/badge/releases-here-green?logo=pypi)](https://pypi.org/project/prev-gen/#history)  
[![wiki](https://img.shields.io/badge/wiki-here-pink)](https://github.com/Aonodensetsu/prev_gen/blob/main/WIKI.md) [![changelog](https://img.shields.io/badge/changelog-here-pink)](https://github.com/Aonodensetsu/prev_gen/blob/main/CHANGELOG.md)  
[![ko-fi](https://img.shields.io/badge/show-support-555599?style=for-the-badge&logo=kofi)](https://ko-fi.com/aonodensetsu)

## Big changes from v5 to v6!
This repository contains the v6 release candidate version of the code.  
Check out the [migration](MIGRATION6.md) guide before upgrading.  
v6 will be released to PyPi after final testing.

# Usage:
1. `pip install prev_gen`
2. Open up [the wiki](https://github.com/Aonodensetsu/prev_gen/blob/main/WIKI.md) to see how everything works
3. Create a file based on instructions (or just edit the [python](https://github.com/Aonodensetsu/prev_gen/blob/main/example.py), [yaml](https://github.com/Aonodensetsu/prev_gen/blob/main/example.yml), [json](https://github.com/Aonodensetsu/prev_gen/blob/main/example.json), or [toml](https://github.com/Aonodensetsu/prev_gen/blob/main/example.toml) examples)
4. ```python
   # in a python file
   palette = [...]
   from prev_gen import Previewer
   Previewer(palette)
   ```
   or use the cli tool `prev_gen` for conversions with no code

# Example:
Inspired by the great [Gruvbox](https://github.com/morhetz/gruvbox) theme, where even the preview is impressive  
And so, below is the Gruvbox palette preview recreated with this app (click for selectable text)  
[![example](https://raw.githubusercontent.com/Aonodensetsu/prev_gen/main/gruvbox.png)](https://raw.githubusercontent.com/Aonodensetsu/prev_gen/main/gruvbox.svg)
