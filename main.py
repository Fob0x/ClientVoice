
import socket
import threading
import pyaudio
import tkinter as tk

HOST = '127.0.0.1'
PORT = 12345
BUFFER_SIZE = 1024

CHUNK_SIZE = 1024
FORMAT = pyaudio.paInt32
CHANNELS = 1
RATE = 44100

audio = pyaudio.PyAudio()
mic_enabled = True
client_socket = None

def connect():
    global client_socket

    if client_socket:
        disconnect()

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        client_socket.connect((HOST, PORT))
    except ConnectionRefusedError:
        print('Connection refused')
        client_socket = None
        return

    send_thread = threading.Thread(target=send_audio)
    send_thread.daemon = True
    send_thread.start()

    receive_thread = threading.Thread(target=receive_audio)
    receive_thread.daemon = True
    receive_thread.start()

def disconnect():
    global client_socket

    if client_socket:
        client_socket.close()
        client_socket = None

def send_audio():
    stream = audio.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK_SIZE)

    while client_socket:
        if mic_enabled:
            audio_data = stream.read(CHUNK_SIZE)
            client_socket.sendall(audio_data)

    stream.stop_stream()
    stream.close()

def receive_audio():
    stream = audio.open(format=FORMAT, channels=CHANNELS, rate=RATE, output=True, frames_per_buffer=CHUNK_SIZE)

    while client_socket:
        data = client_socket.recv(BUFFER_SIZE)
        stream.write(data)

    stream.stop_stream()
    stream.close()

def toggle_mic():
    global mic_enabled
    mic_enabled = not mic_enabled
    print(f'Microphone enabled: {mic_enabled}')

def create_gui():
    root = tk.Tk()
    root.title('Voice chat')

    tk.Label(root, text='Server Address').grid(row=0, column=0, sticky=tk.W)
    address_entry = tk.Entry(root, width=15)
    address_entry.grid(row=0, column=1, sticky=tk.W)
    address_entry.insert(0, HOST)

    tk.Label(root, text='Server Port').grid(row=1, column=0, sticky=tk.W)
    port_entry = tk.Entry(root, width=5)
    port_entry.grid(row=1, column=1, sticky=tk.W)
    port_entry.insert(0, PORT)

    connect_button = tk.Button(root, text='Connect', command=connect)
    connect_button.grid(row=0, column=2)

    disconnect_button = tk.Button(root, text='Disconnect', command=disconnect)
    disconnect_button.grid(row=1, column=2)

    tk.Button(root, text='Toggle Mic', command=toggle_mic).grid(row=2, column=0)

    root.mainloop()

if __name__ == '__main__':
    create_gui()
