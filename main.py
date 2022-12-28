# This is simple mp3-player

from tkinter import *
from tkinter import filedialog
from tkinter import messagebox
from mutagen.mp3 import MP3
import os
import sys
import pygame
import time
import tkinter.ttk as ttk
import re
import json
import platform


paused = False
stopped = False
playlist_songs = {}
current_song = ""

os.chdir(os.path.dirname(__file__))

# Application class
class App(Tk):
    def __init__(self):
        super().__init__()
        pygame.mixer.init()

        self.title("MP3-плеер")
        self.geometry("920x670+290+85")
        self.resizable(False, False)
        self.config(bg="#0f1a2b")
        icon = PhotoImage(
            file=f"{os.path.dirname(__file__)}\\images\\logo.png")
        self.iconphoto(False, icon)

        # Main_frame
        container = Frame(self, bg="#0f1a2b")
        container.pack(fill=BOTH, expand=True)

        self.Top = PhotoImage(
            file=f"{os.path.dirname(__file__)}\\images\\top.png")
        top = Label(container, image=self.Top, bg="#0f1a2b", relief=FLAT)
        top.pack(side="top", fill=BOTH)
        

        self.playlistbox = Listbox(
            container,
            bg="white",
            fg="green",
            width=63,
            height=15,
            font="AzeretMono 8 bold",
            selectbackground="#0f1a2b",
            selectmode = EXTENDED,
            selectforeground="green")
        self.playlistbox.pack(anchor="s", pady=12, padx=10)
       
        self.frames = {}
        frame = Frame(container, bg="#0f1a2b")
        frame.pack(fill=BOTH, anchor="center")

        self.backbtnimg = PhotoImage(
            file=f"{os.path.dirname(__file__)}\\images\\back50.png")
        self.forwardbtnimg = PhotoImage(
            file=f"{os.path.dirname(__file__)}\\images\\forward50.png")
        self.playbtnimg = PhotoImage(
            file=f"{os.path.dirname(__file__)}\\images\\play50.png")
        self.pausebtnimg = PhotoImage(
            file=f"{os.path.dirname(__file__)}\\images\\pause50.png")
        self.stopbtnimg = PhotoImage(
            file=f"{os.path.dirname(__file__)}\\images\\stop50.png")

        back_button = Button(
            frame,
            bg="#0f1a2b",
            image=self.backbtnimg,
            borderwidth=0,
            activebackground="#0f1a2b",
            command=self.previous_song)
        forward_button = Button(
            frame,
            bg="#0f1a2b",
            image=self.forwardbtnimg,
            borderwidth=0,
            activebackground="#0f1a2b",
            command=self.next_song)
        play_button = Button(
            frame,
            bg="#0f1a2b",
            image=self.playbtnimg,
            borderwidth=0,
            activebackground="#0f1a2b",
            command=self.play)
        pause_button = Button(
            frame,
            bg="#0f1a2b",
            image=self.pausebtnimg,
            borderwidth=0,
            activebackground="#0f1a2b",
            command=lambda: self.pause(paused))
        stop_button = Button(
            frame,
            bg="#0f1a2b",
            image=self.stopbtnimg,
            borderwidth=0,
            activebackground="#0f1a2b",
            command=self.stop)
        empy_button = Button(
            frame,
            bg="#0f1a2b",
            text="",
            borderwidth=0,
            activebackground="#0f1a2b")

        empy_button.pack(pady=7, side="left", padx=123)
        back_button.pack(pady=7, side="left", padx=15)
        forward_button.pack(pady=7, side="left", padx=15)
        play_button.pack(pady=7, side="left", padx=15)
        pause_button.pack(pady=7, side="left", padx=15)
        stop_button.pack(pady=7, side="left", padx=15)

        self.song_slider = ttk.Scale(
            container,
            from_=0,
            to=100,
            orient=HORIZONTAL,
            length=366,
            value=1,
            command=self.slide)
        self.song_slider.pack(side="bottom", pady=20)

        volume_frame = LabelFrame(
            container,
            bg="#0f1a2b",
            text="Громкость",
            fg="red",
            bd=0,
            font="JetBrainsMono 11 ",
            labelanchor="n")
        volume_frame.place(relx=0.73, rely=0.43)

        self.volume_slider = ttk.Scale(
            volume_frame,
            from_=0,
            to=1,
            orient=VERTICAL,
            length=125,
            value=1,
            command=self.volume)
        self.volume_slider.pack(anchor="sw", pady=20, padx=50)
        
        self.bind('<Control-o>', self.add_song)
        self.bind('<Control-k>', self.add_many_songs)
        self.bind('<Delete>', self.delete_song)
        self.bind('<Control-a>', self.select_all)
        self.bind('<space>', self.bindf)
        self.bind('<End>',self.delete_all_songs)
        
        self.__create_widgets()
        self.__create_menu()
        self.load_playlist()
    
    def bindf(self, event=None):
        self.pause(paused)
    
    def select_all(self,event=None):
        self.playlistbox.selection_set(ALL)
    
    def load_playlist(self):
        if os.path.exists("songs.json"):
            with open("songs.json", "r") as file:
                songs = json.load(file)
                global playlist_songs
                playlist_songs = songs
                for s in playlist_songs.keys():
                    self.playlistbox.insert(END,s)
        else:
            with open("songs.json","w") as file:
                json.dump(playlist_songs,file)

    def __create_menu(self):
        self.menu = Menu()
        self.config(menu=self.menu)

        self.add_song_menu = Menu(self.menu, tearoff=0)
        self.menu.add_cascade(
            label="Добавление музыки",
            menu=self.add_song_menu)
        self.add_song_menu.add_command(
            label="Добавить одну песню в плейлиcт", accelerator="Ctrl-O",
            command=self.add_song)
        self.add_song_menu.add_command(
            label="Добавить много песен в плейлист", accelerator="Ctrl-K",
            command=self.add_many_songs)
        self.add_song_menu.add_separator()
        self.add_song_menu.add_command(label="Закрыть", command=self.exit, accelerator="Alt-F4")
        

        self.remove_song_menu = Menu(self.menu, tearoff=0)
        self.menu.add_cascade(
            label="Удаление музыки",
            menu=self.remove_song_menu)
        self.remove_song_menu.add_command(
            label="Удаление песни из плейлиста", accelerator="Del",
            command=self.delete_song)
        self.remove_song_menu.add_command(
            label="Удаление всех песен из плейлиста", accelerator="End",
            command=self.delete_all_songs)

        self.help_menu = Menu(self.menu, tearoff=0)
        self.menu.add_cascade(label="Справка", menu=self.help_menu)
        self.help_menu.add_command(
            label="О программе",
            command=self.about_program)
        self.help_menu_sub = Menu(self.help_menu, tearoff=0)

    def __create_widgets(self):
        self.Logo = PhotoImage(
            file=f"{os.path.dirname(__file__)}\\images\\logo.png")
        self.logo = Label(image=self.Logo, bg="#0f1a2b", borderwidth=0)
        self.logo.place(
            relx=0.075,
            rely=0.165,
            relwidth=0.195,
            relheight=0.28)
        
        self.status_bar = Label(text='', relief=GROOVE, bd=1, anchor=E)
        self.columnconfigure(0, weight=3)
        self.rowconfigure(6, weight=4)
        self.status_bar.pack(fill=X, anchor="nw", ipady=2)

    def about_program(self, event=None):
        messagebox.showinfo(
            title='ПC "MP3-плеер"',
            message=f'''Версия: 1.0
        \nАвтор: Плакхин Даниил
        \nOC: {platform.system()} {platform.release()}
        \nПрограмма была написана на Python 3.10.6 ''')
    
    def exit(self, event=None):
        answer = messagebox.askokcancel('Выход', 'Вы точно хотите выйти?')
        if answer:
            self.quit()

    def add_song(self, event=None):
        song = filedialog.askopenfilename(
            title="Выберите трек", filetypes=(
                ("MP3 Файлы ", "*.mp3"),))
        song_name = re.sub(r"[\w+:]+/", "", song)
        song_name = song_name.replace(".mp3","")
        if song_name in self.playlistbox.get(0, END):
            messagebox.showwarning(
                title="Ошибка добавления песни",
                message="Песня уже существует в плейлисте")
        else:
            if song not in [None,"",]:
                playlist_songs[song_name] = song
                self.playlistbox.insert(END, song_name)
                with open('songs.json', 'w') as file:
                    json.dump(playlist_songs, file)
        
    def add_many_songs(self, event=None):
        songs = filedialog.askopenfilenames(
            title="Выберите треки", filetypes=(
                ("MP3 Файлы ", "*.mp3"),), multiple=True)
        for song in songs:
            song_name = re.sub(r"[\w+:]+/", "", song)
            song_name = song_name.replace(".mp3","")
            if song_name in self.playlistbox.get(0, END):
                messagebox.showwarning(
                    title="Ошибка добавления песни",
                    message="Одна или несколько песен уже существует в плейлисте")
                break
            else:
                if song not in [None,"",]:
                    playlist_songs[song_name] = song
                    self.playlistbox.insert(END, song_name)
        with open('songs.json', 'w') as file:
            json.dump(playlist_songs,file)

    def delete_song(self, event=None):
        selection = self.playlistbox.curselection()
        for i in range(len(selection)):
            playlist_songs.pop(self.playlistbox.get(selection[i]))
        self.playlistbox.delete(selection[0])
        with open('songs.json', 'w') as file:
            json.dump(playlist_songs, file)

    def delete_all_songs(self, event=None):
        self.playlistbox.delete(0, END)
        playlist_songs.clear()
        with open('songs.json', 'w') as file:
            json.dump(playlist_songs, file)

    # Dealing with time
    def play_time(self):
        if stopped:
            return

        # Get song time
        current_time = pygame.mixer.music.get_pos() / 1000
        # Convert to time format
        converted_current_time = time.strftime(
            "%M:%S", time.gmtime(current_time))

        song = self.playlistbox.get(ACTIVE)
        # Find song length
        song_mut = MP3(playlist_songs[current_song])
        global song_length
        song_length = song_mut.info.length
        # Convert song length
        converted_song_length = time.strftime(
            "%M:%S", time.gmtime(song_length))

        if int(self.song_slider.get()) == int(song_length):
            self.stop()
        elif paused:
            pass
        else:
            # Change time 
            next_time = int(self.song_slider.get()) + 1
            self.song_slider.config(to=song_length, value=next_time)

            # Convert slider 
            converted_current_time = time.strftime(
                "%M:%S", time.gmtime(int(self.song_slider.get())))

            # To status bar
            self.status_bar.config(
                text=f"{current_song}: {converted_current_time} из {converted_song_length}  ")

        # Add current time
        if current_time > 0:
            self.status_bar.config(
                text=f"{current_song}: {converted_current_time} из {converted_song_length}  ")

        # Loop to see evry second
        self.status_bar.after(1000, self.play_time)

    def play(self, event=None):
        global stopped
        stopped = False

        song = self.playlistbox.get(ACTIVE)
        global current_song
        current_song = song

        # Load song
        pygame.mixer.music.load(playlist_songs[song])
        pygame.mixer.music.play(loops=0)
        self.status_bar.config(text="")
        self.song_slider.config(value=0)

        # Get time
        self.play_time()

    def stop(self, event=None):
        pygame.mixer.music.stop()
        self.playlistbox.selection_clear(ACTIVE)

        self.status_bar.config(text="")
        self.song_slider.config(value=0)

        global stopped
        stopped = True

    def previous_song(self):
        self.status_bar.config(text="")
        self.song_slider.config(value=0)

        previous = self.playlistbox.curselection()
        previous = previous[0] - 1

        # Previous song
        song = self.playlistbox.get(previous)
        global current_song
        current_song = song

        pygame.mixer.music.load(playlist_songs[song])
        pygame.mixer.music.play(loops=0)

        # Clear
        self.playlistbox.selection_clear(0, END)
        self.playlistbox.activate(previous)
        self.playlistbox.selection_set(previous)

    def next_song(self):
        self.status_bar.config(text="")
        self.song_slider.config(value=0)

        next = self.playlistbox.curselection()
        next = next[0] + 1

        # Next song
        song = self.playlistbox.get(next)
        global current_song
        current_song = song

        pygame.mixer.music.load(playlist_songs[song])
        pygame.mixer.music.play(loops=0)

        self.playlistbox.selection_clear(0, END)
        self.playlistbox.activate(next)
        self.playlistbox.selection_set(next, last=None)

    def pause(self, is_paused, event=None):
        global paused
        paused = is_paused
        if paused:
            pygame.mixer.music.unpause()
            paused = False
        else:
            pygame.mixer.music.pause()
            paused = True

    def volume(self, x):
        pygame.mixer.music.set_volume(self.volume_slider.get())

    def slide(self, x):
        song = self.playlistbox.get(ACTIVE)

        # Load song with pygame mixer
        pygame.mixer.music.load(playlist_songs[song])
        # Play song with pygame mixer
        pygame.mixer.music.play(loops=0, start=self.song_slider.get())


# Run the application
if __name__ == "__main__":
    app = App()
    app.mainloop()
