from __future__ import annotations

from inspect import currentframe, getabsfile
from PIL import Image, ImageTk, ImageOps
import idlelib.percolator as ip
import idlelib.colorizer as ic
from os.path import dirname
import tkinter as tk

from .previewer import Previewer
from .settings import Settings


class GUI:
    """
    Shows a graphical editor, I don't really expect anyone to use it,
    but if you only have a notepad or something,
    this at least has syntax highlighting and a semi-live preview
    """
    def __new__(cls) -> Image:
        def on_edit(_):
            editor.unbind('<Key>')
            editor.edited = True

        def preview():
            local = {}
            exec(editor.get('1.0', tk.END), None, local)
            p = local['palette']
            pr = Previewer(p, show=False)
            io = ImageOps.contain(pr, (prev.winfo_width() - 10, prev.winfo_height() - 10))
            img = ImageTk.PhotoImage(io)
            prev.image = img
            # noinspection PyTypeChecker
            prev.config(image=img)
            return pr, p

        def save():
            im, p = preview()
            s = p[0]
            if not isinstance(s, Settings):
                s = Settings()
            im.save(s.file_name + '.png')

        def leave():
            _ = preview()
            if editor.edited:
                with open('gui.py', 'w') as g:
                    g.write(editor.get('1.0', tk.END))
            exit()

        ui = tk.Tk()
        ui.title('Preview Generator GUI')
        ui.rowconfigure(0, weight=1)
        ui.rowconfigure(1, minsize=350)
        ui.columnconfigure(0, weight=1)
        ui.columnconfigure(1, minsize=100)
        ui.config(bg='#282828')
        ui.attributes('-fullscreen', True)
        f_edit = tk.Frame(ui, bg='#282828', border=10)
        f_edit.grid(row=0, column=0, sticky='nsew')
        editor = tk.Text(
            f_edit, bg='#282828', fg='#d4be98', insertbackground='#d4be98', borderwidth=0, font=('Verdana', 13)
        )
        with open(dirname(getabsfile(currentframe())) + '/example.txt', 'r') as f:
            editor.insert(tk.END, f.read())
        editor.pack(fill='both', expand=True)
        editor.edited = False
        editor.bind('<Key>', on_edit)
        col = ic.ColorDelegator()
        for i, j in zip(['STRING', 'COMMENT', 'KEYWORD', 'BUILTIN', 'DEFINITION'],
                        ['#a9b665', '#5a524c', '#ea6962', '#d8a657', '#7daea3']):
            col.tagdefs[i] = {'background': '#282828', 'foreground': j}
        ip.Percolator(editor).insertfilter(col)
        f_cmd = tk.Frame(ui, bg='#282828')
        f_cmd.grid(row=0, column=1, sticky='nsew')
        tk.Button(f_cmd, text='Preview', command=preview, borderwidth=0, bg='#7daea3').pack(fill='x')
        tk.Button(f_cmd, text='Save', command=save, borderwidth=0, bg='#7daea3').pack(fill='x')
        tk.Button(f_cmd, text='Exit', command=leave, borderwidth=0, bg='#7daea3').pack(fill='x')
        f_prev = tk.Frame(ui, bg='#282828', border=10)
        f_prev.grid(row=1, column=0, columnspan=2, sticky='nsew')
        prev = tk.Label(f_prev, bg='#282828')
        prev.pack(fill='both', expand=True)
        ui.wait_visibility(prev)
        preview()
        ui.mainloop()
        return preview()[0]
