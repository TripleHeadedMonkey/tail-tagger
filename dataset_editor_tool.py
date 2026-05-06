#!/usr/bin/env python3
import os
import sys
import math
import subprocess
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk

IMG_EXTS = ('.png', '.jpg', '.jpeg', '.webp')

class DatasetEditor(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('Tail Tagger Dataset Editor')
        self.geometry('1450x900')

        self.current_directory = ''
        self.items_per_page = 50
        self.page_num = 0
        self.file_pairs = []
        self.current_items = []
        self.active_row_index = None

        self._build_ui()

    def _build_ui(self):
        top = tk.Frame(self, padx=8, pady=8)
        top.pack(fill=tk.X)

        tk.Button(top, text='📂 Load Directory', command=self.load_directory).pack(side=tk.LEFT, padx=4)
        tk.Button(top, text='🤖 Auto-Caption Folder', command=self.run_bulk_caption).pack(side=tk.LEFT, padx=4)

        self.prev_btn = tk.Button(top, text='<', command=lambda: self.change_page(-1), state=tk.DISABLED)
        self.prev_btn.pack(side=tk.LEFT, padx=4)
        self.page_ent = tk.Entry(top, width=5, justify='center')
        self.page_ent.pack(side=tk.LEFT)
        self.page_ent.bind('<Return>', self.jump_page)
        self.page_lbl = tk.Label(top, text='/ 0')
        self.page_lbl.pack(side=tk.LEFT, padx=4)
        self.next_btn = tk.Button(top, text='>', command=lambda: self.change_page(1), state=tk.DISABLED)
        self.next_btn.pack(side=tk.LEFT, padx=4)

        main = tk.PanedWindow(self, orient=tk.HORIZONTAL, sashwidth=4)
        main.pack(fill=tk.BOTH, expand=True)

        left = tk.Frame(main, bg='white')
        main.add(left, minsize=800, stretch='always')

        self.canvas = tk.Canvas(left, bg='white')
        self.vsb = tk.Scrollbar(left, orient='vertical', command=self.canvas.yview)
        self.frame = tk.Frame(self.canvas, bg='white')
        self.window = self.canvas.create_window((0, 0), window=self.frame, anchor='nw')
        self.frame.bind('<Configure>', lambda e: self.canvas.configure(scrollregion=self.canvas.bbox('all')))
        self.canvas.bind('<Configure>', lambda e: self.canvas.itemconfig(self.window, width=e.width))
        self.canvas.configure(yscrollcommand=self.vsb.set)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.vsb.pack(side=tk.RIGHT, fill=tk.Y)

        right = tk.Frame(main, bg='#f0f0f0', width=320)
        main.add(right, minsize=280, stretch='never')
        tk.Label(right, text='Selected Image Tags', bg='#e1e1e1', font=('Arial', 10, 'bold')).pack(fill=tk.X, padx=4, pady=4)
        self.tags_list = tk.Listbox(right)
        self.tags_list.pack(fill=tk.BOTH, expand=True, padx=6, pady=6)

        self.status = tk.StringVar(value='Ready.')
        tk.Label(self, textvariable=self.status, bd=1, relief=tk.SUNKEN, anchor=tk.W).pack(side=tk.BOTTOM, fill=tk.X)

    def _parse_tags(self, text):
        return [t.strip() for t in text.replace('\n', ',').split(',') if t.strip()]

    def _show_tags_for_row(self, index):
        if index < 0 or index >= len(self.current_items):
            return
        self.active_row_index = index
        for i, item in enumerate(self.current_items):
            bg = '#dfefff' if i == index else 'white'
            item['row'].config(bg=bg)
            item['img_lbl'].config(bg=bg)

        text_val = self.current_items[index]['txt'].get('1.0', tk.END).strip()
        tags = self._parse_tags(text_val)
        self.tags_list.delete(0, tk.END)
        for t in tags:
            self.tags_list.insert(tk.END, t)

    def load_directory(self):
        d = filedialog.askdirectory()
        if not d:
            return
        self.load_directory_from_path(d)

    def load_directory_from_path(self, path):
        self.current_directory = path
        files = os.listdir(path)
        images = sorted([f for f in files if f.lower().endswith(IMG_EXTS)])
        self.file_pairs = [(img, os.path.splitext(img)[0] + '.txt') for img in images]
        self.page_num = 0
        self.load_page()

    def load_page(self):
        for w in self.frame.winfo_children():
            w.destroy()
        self.current_items = []
        self.canvas.yview_moveto(0)
        self.tags_list.delete(0, tk.END)

        total = len(self.file_pairs)
        if total == 0:
            self.page_lbl.config(text='/ 0')
            self.page_ent.delete(0, tk.END); self.page_ent.insert(0, '0')
            self.prev_btn.config(state=tk.DISABLED); self.next_btn.config(state=tk.DISABLED)
            self.status.set('No files.')
            return

        pages = math.ceil(total / self.items_per_page)
        self.page_num = max(0, min(self.page_num, pages - 1))
        s = self.page_num * self.items_per_page
        e = s + self.items_per_page
        data = self.file_pairs[s:e]

        self.page_ent.delete(0, tk.END); self.page_ent.insert(0, str(self.page_num + 1))
        self.page_lbl.config(text=f'/ {pages}  (Total: {total})')
        self.prev_btn.config(state=tk.NORMAL if self.page_num > 0 else tk.DISABLED)
        self.next_btn.config(state=tk.NORMAL if self.page_num < pages - 1 else tk.DISABLED)

        for i, (img_name, txt_name) in enumerate(data):
            self._add_row(i, img_name, txt_name)

        if self.current_items:
            self._show_tags_for_row(0)
        self.status.set(f'Showing {len(data)} items.')

    def _add_row(self, idx, img_name, txt_name):
        row = tk.Frame(self.frame, bg='white', pady=8)
        row.pack(fill=tk.X, padx=8)
        row.bind('<Button-1>', lambda e, i=idx: self._show_tags_for_row(i))

        img_path = os.path.join(self.current_directory, img_name)
        txt_path = os.path.join(self.current_directory, txt_name)

        img_lbl = tk.Label(row, bg='white')
        try:
            im = Image.open(img_path)
            thumb = im.copy(); thumb.thumbnail((180, 180))
            tkimg = ImageTk.PhotoImage(thumb)
            img_lbl.config(image=tkimg); img_lbl.image = tkimg
        except Exception:
            img_lbl.config(text='Error', bg='red')
        img_lbl.pack(side=tk.LEFT, padx=8, anchor='n')
        img_lbl.bind('<Button-1>', lambda e, i=idx: self._show_tags_for_row(i))
        img_lbl.bind('<Double-Button-1>', lambda e, p=img_path: self.open_external(p))

        txt = tk.Text(row, height=7, wrap=tk.WORD)
        try:
            with open(txt_path, 'r', encoding='utf-8') as f:
                txt.insert('1.0', f.read())
        except Exception:
            pass
        txt.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=8)
        txt.bind('<FocusIn>', lambda e, i=idx: self._show_tags_for_row(i))
        txt.bind('<KeyRelease>', lambda e, i=idx: self._show_tags_for_row(i) if self.active_row_index == i else None)

        self.current_items.append({'txt': txt, 'txt_path': txt_path, 'row': row, 'img_lbl': img_lbl})

    def open_external(self, img_path):
        try:
            if sys.platform.startswith('win'):
                os.startfile(img_path)
            elif sys.platform == 'darwin':
                subprocess.Popen(['open', img_path])
            else:
                subprocess.Popen(['xdg-open', img_path])
        except Exception as e:
            messagebox.showerror('Open Image', str(e))

    def run_bulk_caption(self):
        if not self.current_directory:
            messagebox.showinfo('No folder', 'Load a folder first.')
            return
        script = os.path.join(os.getcwd(), 'bulk_caption_tool.py')
        if not os.path.exists(script):
            messagebox.showerror('Missing tool', script)
            return
        cmd = [sys.executable, script, self.current_directory, '--overwrite-mode', 'auto']
        res = subprocess.run(cmd, capture_output=True, text=True)
        if res.returncode != 0:
            messagebox.showerror('Bulk caption failed', res.stdout + '\n' + res.stderr)
            return
        self.load_directory_from_path(self.current_directory)
        messagebox.showinfo('Bulk caption complete', res.stdout or 'Done')

    def change_page(self, delta):
        self.page_num += delta
        self.load_page()

    def jump_page(self, _evt=None):
        t = self.page_ent.get().strip()
        if t.isdigit():
            self.page_num = int(t) - 1
            self.load_page()

if __name__ == '__main__':
    DatasetEditor().mainloop()
