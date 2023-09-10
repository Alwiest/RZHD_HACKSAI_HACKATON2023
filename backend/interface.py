from tkinter import *
from tkinter import messagebox
from PIL import Image, ImageTk
from api_wrapper import get_recomendations

window = Tk()
window.title('Контроль вагонопотока')
window.geometry('1920x1080')
window.state('zoomed')

def get_and_show():
    stat_names = [
        'Златоуст',
        'Кыштым',
        'Миасс',
        'Муслюмово',
        'Челябинск',
        'Полетаево',
        'Еманжелинск',
    ]

    x = entry1.get()
    tm = get_recomendations(x)['recommended_stations']
    text = f'1) Станция {stat_names[tm[0]+1]}\n2) Станция {stat_names[tm[1]+1]}\n3) Станция {stat_names[tm[2]+1]}'
    lbl3['text'] = text

img = Image.open('../backend/templates/Untitled-4_page-0002.jpg')
img = img.resize((1920, 1022), Image.LANCZOS)
image = ImageTk.PhotoImage(img)
lb = Label(
    image = image,
    height = 1280,
    width = 1980
)
lb.pack(side="top", fill="both", expand=1)

entry1 = Entry(window, width=14, font=('Times New Roman', 36, "bold"))
entry1.place(x=195, y=314)

butall = Button(height = 2, width = 20, text='Выполнить поиск', font=('Times New Roman', 24, "bold"), bg="red", command=get_and_show)
butall.place(x=195, y=720)

lab1 = Label(
    text='Введите нужный номер вагона:',
    font=('Times New Roman', 17, "bold"),
    bg='#d8d8d8'
)
lab1.place(x=195, y=380)

lab2 = Label(
    text='Рекомендованный маршрут:',
    font=('Times New Roman', 17, "bold"),
    bg='#d8d8d8'
)
lab2.place(x=195, y=450)

lbl3 = Label(
    font=('Times New Roman', 17, "bold"),
    bg='#d8d8d8',
    justify='left'
)
lbl3.place(x=195, y=480)

window.mainloop()
