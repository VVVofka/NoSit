import tkinter as tk
import pystray
from PIL import Image


class MyApp(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("System Tray App")
        self.geometry('500x250')
        self.protocol('WM_DELETE_WINDOW', self.minimize_to_tray)
    
    def minimize_to_tray(self):
        self.withdraw()
        image = Image.open("app.ico")
        menu = (pystray.MenuItem('Quit',  self.quit_window), 
                pystray.MenuItem('Show',self.show_window))
        icon = pystray.Icon("name", image, "My App", menu)
        icon.run()

    def quit_window(self, icon):
        icon.stop()
        self.destroy()

    def show_window(self, icon):
        icon.stop()
        self.after(0,self.deiconify)

if __name__ == "__main__":
    app = MyApp()
    app.mainloop()