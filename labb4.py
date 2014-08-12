#!/usr/bin/python
#-*- coding: utf-8 -*-
import Tkinter as tk, pygame, json, sys
from PIL import Image, ImageTk

""" Beskrivning av lösning till labb 4:

    Datan hämtas från en JSON-fil och läses in i en lista (self.items) i metoden get_items(). Innan listan returneras
    ersätts sträng-sökvägarna till bild- och ljudfilerna med bild- och ljudobjekt med hjälp av ImageTk och Pygame.
    Om inte bild eller ljud är angivet i JSON-filen, eller om den angivna sökvägen är felaktig, kastas ett undantag
    som inte genererar något fel utan ersätter sökvägen till bilden med en placeholder-bild, och sökvägen till
    ljudfilen med "None". 

    Applikationsfönstret (self.root) skapas i metoden create_window(). 
    update_content() är metoden som fyller fönstrets olika delar med innehåll och uppdaterar detta när byte av
    sida görs.

    show_prev() och show_next() stegar genom listan med data genom att ändra värdet på det aktuella 
    "self.item_nr_current" beroende på om man klickar framåt eller bakåt. Metoderna håller också reda på att man 
    kommer till början/slutet om man är på väg utanför listans gräns.

    play_sound() spelar ljudet för den aktulla sida om ett ljud finns. Finns inget ljud, d.v.s. det är satt till
    "None" i listan, inaktiveras "Spela igen"-knappen och metoden försöker inte spela ljudet.

    set_audio_status() fungerar som en mute-funktion, där man kan välja att slå av allt ljud.

    Applikationen kan även navigeras till fullo genom tangentbordet. De aktuella tangenter beskrivs här:
        Esc: Avsluta.
        Pil-vänster: Föregående sida.
        Pil-höger: Nästa sida.
        Pil-upp: Spela igen.
        Pil-ned: Ljud på/av.
        0-9: Hoppa mellan sidorna från sida 0 (intro), upp till sida 9, om denna finns.


    Gjord av: Per Magnusson (pema3616@student.su.se)

    Version: Python 2.7.2
    Dator: Mac
    OS: OS X 10.8.4

"""

class Slideshow:

    # const string
    AUDIO_ON = 'Ljud på'
    AUDIO_OFF = 'Ljud av'
    PLAY_AGAIN = 'Spela igen'
    QUIT = 'Avsluta'

    
    def __init__(self):
        self.items = []
        self.items_count = 0
        self.item_nr_current = 0
        self.audio_play = True
        # tk objects
        self.root = None
        self.header = None
        self.image = None
        self.info = None
        self.button_play_again = None
        self.button_audio = None
        # start
        self.main()



    def main(self):
        try:
            self.root = tk.Tk()
            pygame.mixer.init(44100, -16, 2, 1024)
            self.items = self.get_items()
            self.items_count = len(self.items)
            self.create_window()
            # run
            self.root.mainloop()
        except:
            print 'Programmet avslutades.'



    def get_items(self):
        try:
            json_data = open('data.json')
            data = json.load(json_data)
            json_data.close()
        except IOError:
            sys.stderr.write('Fel inträffade när datan skulle hämtas.\n')
            sys.exit(1)

        for r in data:
            try:
                r['image'] = ImageTk.PhotoImage(Image.open(r['image']))
            except:
                r['image'] = ImageTk.PhotoImage(Image.open('./img/no_image.png'))

            try:
                r['audio'] = pygame.mixer.Sound(r['audio'])
            except:
                r['audio'] = None

        return data



    def create_window(self):
        # root window
        self.root.title('Monty Python')
        self.root.minsize(650, 670)
        self.root.maxsize(650, 670)
        # frame
        frame = tk.Frame(self.root, bg='white')
        frame.pack(fill=tk.BOTH, expand=tk.YES, padx=10, pady=10)
        #header
        self.header = tk.Label(frame, font=('Verdana', 22))
        self.header.pack()
        # image
        self.image = tk.Label(frame, width=500, height=350, bg='black', bd=9, relief=tk.FLAT)
        self.image.pack(padx=20, pady=20)
        # info
        self.info = tk.Text(frame, font=('Verdana', 14), border=2, bg='white', 
                            width=55, height=10, wrap=tk.WORD)
        self.info.pack()
        # prev
        button_prev = tk.Button(frame, text='«', command=self.show_prev)
        button_prev.pack(side=tk.LEFT, fill=tk.X, expand=tk.YES)
        # next
        button_next = tk.Button(frame, text='»', command=self.show_next)
        button_next.pack(side=tk.LEFT, fill=tk.X, expand=tk.YES)
        # play sound again
        self.button_play_again = tk.Button(frame, text=self.PLAY_AGAIN, 
                                           command=lambda:self.play_sound(self.items[self.item_nr_current]['audio']))
        self.button_play_again.pack(side=tk.LEFT)
        # audio status
        self.button_audio = tk.Button(frame, text=self.AUDIO_ON, width=7, command=self.set_audio_status)
        self.button_audio.pack(side=tk.LEFT)
        # quit
        button_quit = tk.Button(frame, text=self.QUIT, command=self.root.destroy)
        button_quit.pack(side=tk.RIGHT)
        # set content for intro page
        self.update_content()
        # bind key handlers
        self.bind_key_handlers()



    def show_prev(self, event=None):
        if self.item_nr_current <= 0:
            self.item_nr_current = self.items_count - 1
        else:
            self.item_nr_current = self.item_nr_current - 1
        self.update_content()



    def show_next(self, event=None):
        if self.item_nr_current >= self.items_count - 1:
            self.item_nr_current = 0
        else:
            self.item_nr_current = self.item_nr_current + 1
        self.update_content()



    def goto_page(self, event):
        key = event.keysym  # pressed key from event
        self.item_nr_current = int(key)
        self.update_content()



    def update_content(self):
        current = self.items[self.item_nr_current]
        if self.item_nr_current:
            header = '{0}. {1}'.format(self.item_nr_current, current['name'])
        else:
            header = current['name']

        # update image
        self.header.config(text=header)
        self.image.config(image=current['image'])
        # update info
        self.info.configure(state=tk.NORMAL)
        self.info.delete(1.0, tk.END)
        self.info.insert(1.0, current['info'])
        self.info.configure(state=tk.DISABLED)
        
        self.button_play_again.configure(state=tk.NORMAL)

        # play sound
        self.play_sound(current['audio'])



    def play_sound(self, audio):
        pygame.mixer.stop()
        if audio and self.audio_play:
            audio.play()
        else:
            self.button_play_again.configure(state=tk.DISABLED)



    def set_audio_status(self, event=None):
        if self.audio_play:
            self.audio_play = False
            pygame.mixer.stop()
            self.button_audio.configure(text=self.AUDIO_OFF)
            self.button_play_again.configure(state=tk.DISABLED)
        else:
            self.audio_play = True
            self.button_audio.configure(text=self.AUDIO_ON)
            if self.items[self.item_nr_current]['audio']:
                self.button_play_again.configure(state=tk.NORMAL)



    def bind_key_handlers(self):
        # bind keys
        self.root.bind('<Left>', self.show_prev)
        self.root.bind('<Right>', self.show_next)
        self.root.bind('<Up>', lambda a: self.play_sound(self.items[self.item_nr_current]['audio']))
        self.root.bind('<Down>', self.set_audio_status)
        self.root.bind('<Key-Escape>', lambda a: self.root.destroy())
        # bind nuber keys 0-9 to pages
        key_range = 10
        if self.items_count < 10:  # if pages less than 10
            key_range = self.items_count
        for i in xrange(key_range):
            self.root.bind(str(i), self.goto_page)



# init program
slideshow = Slideshow()
