from tkinter import *
from socket import *
import threading, time, pickle

SERVER_HOST = gethostname()
# SERVER_HOST = 'SERVER IP ADDRESS'
SERVER_PORT = 40404

cl = socket(AF_INET, SOCK_STREAM)
name = input('Enter your name: ')
cl.connect((SERVER_HOST, SERVER_PORT))
cl.send(name.encode())
connections = []

def lstn():
    while True:
        data = cl.recv(1024)
        print(data)
        dec = False
        if data.startswith(b'[NEW CONNECTION]:') or data.startswith(b'[DISCONNECTED]:'):
            data, _, connections = data.partition(b'\n')
            data = data.decode() + '\n'
            connections = pickle.loads(connections)
            usr.delete(0, END)
            for each in connections:
                usr.insert(END, each)
            dec = True

        if data:
            msgs.configure(state='normal')
            if dec:
                msgs.config(font=('Courier',12))
            msgs.insert(END, data)
            msgs.configure(state='disabled')
            msgs.config(font=('Helvetica', 14))
            chat_canvas.update()

def send_text():
    rcvd = text_input.get(1.0, END)
    print(rcvd)
    text_input.delete(1.0, END)
    cl.send(rcvd.encode())


root = Tk()
root.wm_title(f'user: {name}')

chat_canvas = Canvas(root, height=0, width=500)
chat_canvas.pack(side=TOP, fill=BOTH, expand=1)
chat_canvas.update()

msgs = Text(chat_canvas)
msgs.configure(state='disabled')
msgs.config(font=('Helvetica', 14))
msgs.pack(side=LEFT, fill=BOTH, expand=1)

actv = Frame(chat_canvas, height=chat_canvas.winfo_height(), width=200)
actv.config(bg='#eeeeee')
ac = Label(actv, text='ACTIVE CONNECTIONS')
ac.config(justify=CENTER, bg='#eeeeee', underline=True, relief=GROOVE, width=20)
ac.pack(side=TOP)
usr = Listbox(actv)
usr.config(borderwidth=0)
usr.pack(fill=Y, expand=1)
for each in connections:
    usr.insert(END, each)
actv.pack(side=RIGHT, fill=Y, expand=0)

sender = Canvas(height=100, width=600)
sender.pack(fill=X, side=BOTTOM)

text_input = Text(sender)
text_input.config(bg='#cccccc', height=3, font=('Helvetica', 15),)
text_input.pack(side=LEFT, fill=X, expand=1)

send_image = PhotoImage(file='send.png').subsample(12, 12)
send_button = Button(sender, image=send_image, command=send_text)
send_button.pack(side=RIGHT, expand=0)
sender.update()

try:
    t = threading.Thread(target=lstn)
    t.start()
    root.mainloop()

except KeyboardInterrupt:
    print('quitting')

finally:
    cl.close()
    root.destroy()