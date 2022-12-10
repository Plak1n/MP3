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
from shutil import move


# Основа приложения
root = Tk()
root.title("MP3-плеер")
icon = PhotoImage(file=f"{os.path.dirname(__file__)}\images\logo.png")
root.iconphoto(False,icon)
root.geometry("920x670+290+85")
root.resizable(False,False)


# Инициализация pygame
pygame.mixer.init()


def about_program():
    messagebox.showinfo(
        title='ПC "MP3-плеер"',
        message=f'''Версия: 1.0
        \nАвтор: Плакхин Даниил
        \nOC: {sys.platform}
        \nПрограмма была написана на Python 3.10.6 ''')


# Функция для взаимодействия с временем
def play_time():
    # Проверка если песня остановлена
    if stopped:
        return
    
    # Узнаем время песни
    current_time = pygame.mixer.music.get_pos() / 1000
    # Конвертиурем песню в корректный формат
    converted_current_time = time.strftime("%M:%S", time.gmtime(current_time))    


    
    song = playlistbox.get(ACTIVE)
    song = f"{os.path.dirname(__file__)}\\music\\{song}"
    
    # Найти длину трека
    song_mut = MP3(song)
    global song_length
    song_length = song_mut.info.length
    # Конвертиурем в временной формат
    converted_song_length = time.strftime("%M:%S", time.gmtime(song_length))
    
    # Проверка закончилась ли песня
    if int(song_slider.get()) == int(song_length):
        stop()
    elif paused:
        # Проверка на паузе трек или нет
        pass
    else:
        # Передвинуть на 1 секунду
        next_time = int(song_slider.get()) +1
        song_slider.config(to=song_length, value=next_time)
        
        # Конвертируем ползунок в временной формат
        converted_current_time = time.strftime("%M:%S", time.gmtime(int(song_slider.get())))
        
        # Данные на статус бар
        status_bar.config(text=f"Time Elapsed: {converted_current_time} of {converted_song_length}  ")
        
    # Добавляем текущее время в статус бар
    if current_time > 0:
        status_bar.config(text=f"TIme Elapsed: {converted_current_time} of {converted_song_length}  ")
    
    # Создаем цикл чтобы видеть время каждую секунду
    status_bar.after(1000,play_time)
    

# Добавить песню
def add_song(event=None):
    song = filedialog.askopenfilename(title="Выберите трек", filetypes=(("MP3 Файлы ","*.mp3"),))
    if song.find(os.path.dirname(__file__)) != -1: 
        move(song, f"{os.path.dirname(__file__)}\music", )
    song_name = re.sub(r"[\w+:]+/","",song)
    playlistbox.insert(END, song_name)

    
# Добавить много песен
def add_many_songs(event=None):
    songs = filedialog.askopenfilenames(title="Выберите треки", filetypes=(("MP3 Файлы ","*.mp3"),), multiple=True)
    for song in songs:
        if song.find(os.path.dirname(__file__)) != -1:
            move(song, f"{os.path.dirname(__file__)}\music", )
        song_name = re.sub(r"[\w+:]+/","",song)
        playlistbox.insert(END, song_name)


# Удаление песни из плейлиста
def delete_song(event=None):
    playlistbox.delete(ANCHOR)


# Удаление всех песен
def delete_all_songs(event=None):
    playlistbox.delete(0, END)

    
# Запустить трек
def play(event=None):
    global stopped
    stopped = False

    song = playlistbox.get(ACTIVE)
    song = f'{os.path.dirname(__file__)}\\music\\{song}'
	
	# Загрузка песню с pygame.mixer
    pygame.mixer.music.load(song)
	# Запуск песни с pygame.mixer
    pygame.mixer.music.play(loops=0)
    
	# Получить время песни
    play_time()


global stopped
stopped = False


# Остановка песни
def stop(event= None):
    # Остановить песню
    pygame.mixer.music.stop()
    playlistbox.selection_clear(ACTIVE)
    
    status_bar.config(text="")
    song_slider.config(value=0)
    
    global stopped
    stopped = True

    
# Cледующая песня
def next_song():
    status_bar.config(text="")
    song_slider.config(value=0)

    next = playlistbox.curselection()
    next = next[0]+1    

    # Название следующей песни
    song = playlistbox.get(next)
    
    #song = f'C:/mp3/audio/{song}.mp3'
	
    # Загрузка и запуск песни
    pygame.mixer.music.load(song)
    pygame.mixer.music.play(loops=0)

    # Очистка и выделение следующего трека
    playlistbox.selection_clear(0, END)
    playlistbox.activate(next)
    playlistbox.selection_set(next, last=None)


# Прошлая песня
def previous_song():
    status_bar.config(text="")
    song_slider.config(value=0)
    
    previous = playlistbox.curselection()
    previous = previous[0]-1
    
    # Название прошлой песни
    song = playlistbox.get(previous)
    
    # Загрузка и проигрывание
    pygame.mixer.music.load(song)
    pygame.mixer.music.play(loops=0)
    
    # Очистка и выбор прошлого трека
    playlistbox.selection_clear(0,END)
    playlistbox.activate(previous)
    playlistbox.selection_set(previous)


global paused
paused = False


# Пауза
def pause(is_paused):
    global paused
    paused = is_paused
    if paused:
        pygame.mixer.music.unpause()
        paused = False
    else:
        pygame.mixer.music.pause()
        paused = True


# Громкость
def volume(x):
    pygame.mixer.music.set_volume(volume_slider.get())


# Ползунок перемещения трека
def slide(x):
    song = playlistbox.get(ACTIVE)
	#song = f'C:/mp3/audio/{song}.mp3'
	
	#Load song with pygame mixer
    pygame.mixer.music.load(song)
	#Play song with pygame mixer
    pygame.mixer.music.play(loops=0, start=song_slider.get())


# Создание главного фрейма
main_frame = Frame(root)
main_frame.pack(pady=20)

# Создание плейлиста
playlistbox = Listbox(main_frame, bg="black", fg="green", width=60, height=16, selectbackground="green", selectforeground="black")
playlistbox.grid(row=0,column=0)

# Создание фрейм регулировки звука
volume_frame = LabelFrame(main_frame, text ="Volume")
volume_frame.grid(row=0, column=1, padx=20)

# Создание регулировку звука
volume_slider = ttk.Scale(volume_frame, from_=0, to=1, orient=VERTICAL, length=125, value=1, command=volume)
volume_slider.pack(pady=10)

# Создание регулировку песен
song_slider = ttk.Scale(main_frame, from_=0, to=100, orient=HORIZONTAL, length=360, value=0, command=slide)
song_slider.grid(row=2, column=0, pady=20)

# Создание фрейм для кнопок
control_frame = Frame(main_frame)
control_frame.grid(row=1, column=0, pady=20)

# Определение изображений кнопок

backbtnimg = PhotoImage(file=f"{os.path.dirname(__file__)}\\images\\back50.png")
forwardbtnimg = PhotoImage(file=f"{os.path.dirname(__file__)}\\images\\forward50.png")
playbtnimg = PhotoImage(file=f"{os.path.dirname(__file__)}\\images\\play50.png")
pausebtnimg = PhotoImage(file=f"{os.path.dirname(__file__)}\\images\\pause50.png")
stopbtnimg = PhotoImage(file=f"{os.path.dirname(__file__)}\\images\\stop50.png")

# Создание кнопок
back_button = Button(control_frame, image=backbtnimg, borderwidth=0, command=previous_song)
forward_button = Button(control_frame, image=forwardbtnimg, borderwidth=0, command=next_song)
play_button = Button(control_frame, image=playbtnimg, borderwidth=0, command=play)
pause_button = Button(control_frame, image=pausebtnimg, borderwidth=0, command=lambda:pause(paused))
stop_button = Button(control_frame, image=stopbtnimg, borderwidth=0, command=previous_song)


# Расположение кнопок
back_button.grid(row=0, column=0, padx=10)
forward_button.grid(row=0, column=1, padx=10)
play_button.grid(row=0, column=2, padx=10)
pause_button.grid(row=0, column=3, padx=10)
stop_button.grid(row=0, column=4, padx=10)

# Создание меню
my_menu = Menu(root)
root.config(menu=my_menu)

# Создание меню добавления
add_song_menu = Menu(my_menu, tearoff=0)
my_menu.add_cascade(label="Добавление музыки", menu=add_song_menu)
add_song_menu.add_command(label="Добавить одну песню в плейлиcт", command=add_song)
add_song_menu.add_command(label="Добавить много песен в плейлист", command=add_many_songs)

# Создание меню удаления песен
remove_song_menu = Menu(my_menu, tearoff=0)
my_menu.add_cascade(label="Удаление музыки", menu=remove_song_menu)
remove_song_menu.add_command(label="Удаление песни из плейлиста", command=delete_song)
remove_song_menu.add_command(label="Удаление всех песен из плейлиста", command=delete_all_songs)

# Создание меню справка
help_menu = Menu(my_menu, tearoff=0)
my_menu.add_cascade(label="Справка", menu=help_menu)
help_menu.add_command(label="О программе", command=about_program)

# Создание статус бара
status_bar = Label(root, text='', bd=1, relief=GROOVE, anchor=E)
status_bar.pack(fill=X, side=BOTTOM, ipady=2)

# Временное текствое поле
my_label = Label(root, text='')
my_label.pack(pady=20)


# Создание кнопки
if __name__ =="__main__":
    root.mainloop()
   