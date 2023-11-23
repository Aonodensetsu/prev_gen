from __future__ import annotations

from inspect import currentframe, getabsfile
from PIL import Image, ImageTk, ImageOps
import idlelib.percolator as ip
import idlelib.colorizer as ic
from os.path import dirname
import tkinter as tk

from .settings import Settings
from .preview import Preview


class GUI:
    """
    Shows a graphical editor, I don't really expect anyone to use it,
    but if you only have a notepad or something,
    this at least has syntax highlighting and a semi-live preview
    """
    def __new__(cls) -> Image:
        def onEdit(_):
            editor.unbind('<Key>')
            editor.edited = True

        def preview():
            local = {}
            exec(editor.get('1.0', tk.END), None, local)
            p = local['palette']
            i = Preview(p, show=False)
            j = ImageOps.contain(i, (prev.winfo_width() - 10, prev.winfo_height() - 10))
            img = ImageTk.PhotoImage(j)
            prev.image = img
            prev.config(image=img)
            return i, p

        def save():
            i, p = preview()
            s = p[0]
            if not isinstance(s, Settings):
                s = Settings()
            i.save(s.fileName + '.png')

        def leave():
            _, p = preview()
            if editor.edited:
                with open('gui.py', 'w') as f:
                    f.write(editor.get('1.0', tk.END))
            exit()

        ui = tk.Tk()
        ui.title('Preview Generator GUI')
        ui.rowconfigure(0, weight=1)
        ui.rowconfigure(1, minsize=350)
        ui.columnconfigure(0, weight=1)
        ui.columnconfigure(1, minsize=100)
        ui.config(bg='#282828')
        ui.attributes('-fullscreen', True)
        fEdit = tk.Frame(ui, bg='#282828', border=10)
        fEdit.grid(row=0, column=0, sticky='nsew')
        editor = tk.Text(
            fEdit, bg='#282828', fg='#d4be98', insertbackground='#d4be98', borderwidth=0, font=('Verdana', 13)
        )
        with open(dirname(getabsfile(currentframe())) + '/example.txt', 'r') as f:
            editor.insert(tk.END, f.read())
        editor.pack(fill='both', expand=True)
        editor.edited = False
        editor.bind('<Key>', onEdit)
        col = ic.ColorDelegator()
        for i, j in zip(['STRING', 'COMMENT', 'KEYWORD', 'BUILTIN', 'DEFINITION'],
                        ['#a9b665', '#5a524c', '#ea6962', '#d8a657', '#7daea3']):
            col.tagdefs[i] = {'background': '#282828', 'foreground': j}
        ip.Percolator(editor).insertfilter(col)
        fCmd = tk.Frame(ui, bg='#282828')
        fCmd.grid(row=0, column=1, sticky='nsew')
        tk.Button(fCmd, text='Preview', command=preview, borderwidth=0, bg='#7daea3').pack(fill='x')
        tk.Button(fCmd, text='Save', command=save, borderwidth=0, bg='#7daea3').pack(fill='x')
        tk.Button(fCmd, text='Exit', command=leave, borderwidth=0, bg='#7daea3').pack(fill='x')
        fPrev = tk.Frame(ui, bg='#282828', border=10)
        fPrev.grid(row=1, column=0, columnspan=2, sticky='nsew')
        prev = tk.Label(fPrev, bg='#282828')
        prev.pack(fill='both', expand=True)
        ui.wait_visibility(prev)
        preview()
        ui.mainloop()
        return preview()[0]
