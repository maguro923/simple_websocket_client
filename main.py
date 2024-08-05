import asyncio
import threading
import tkinter as tk
from tkinter import scrolledtext
from websocket import WebSocketApp
import json
from config import URL, CHECK_MESSAGE_TYPE

class WebSocketClient:
    def __init__(self, uri):
        self.uri = uri
        self.window = tk.Tk()
        self.window.title(f"WebSocket Client")

        self.uritext = tk.Label(self.window, text=uri)
        self.uritext.grid(column=0, row=0, padx=0, pady=5)

        self.username_input_field = tk.Entry(self.window, width=20)
        self.username_input_field.grid(column=1, row=0, padx=0, pady=5)
        self.username_input_field.insert(0, "username")

        self.clear_button = tk.Button(self.window, text="Clear", command=self.clear_message_area)
        self.clear_button.grid(column=4, row=0, padx=10, pady=5)

        self.message_area = scrolledtext.ScrolledText(self.window, wrap=tk.WORD, width=100, height=20, state='disabled')
        self.message_area.grid(column=0, row=1, padx=10, pady=10, columnspan=5)
        self.message_area.tag_config("error", foreground="red", background="yellow")
        self.message_area.tag_config("info", foreground="blue")
        self.message_area.tag_config("warning", foreground="red")

        self.input_field = scrolledtext.ScrolledText(self.window, wrap=tk.WORD, width=60, height=5)
        self.input_field.grid(column=0, row=2, padx=10, pady=10, columnspan=2)

        self.send_button = tk.Button(self.window, text="Send", command=self.send_message)
        self.send_button.grid(column=2, row=2, padx=10, pady=10)

        self.reconnect_button = tk.Button(self.window, text="Reconnect", command=self.reconnect)
        self.reconnect_button.grid(column=3, row=2, padx=10, pady=10)

        self.disconnect_button = tk.Button(self.window, text="Disconnect", command=self.disconnect)
        self.disconnect_button.grid(column=4, row=2, padx=10, pady=10)
        self.window.protocol("WM_DELETE_WINDOW", self.on_close_window)
        self.websocket = None
        self.loop = asyncio.new_event_loop()

    def on_message(self, ws, message):
        self.display_message(f"Server: {message}")

    def on_error(self, ws, error):
        self.display_message(f"Error: {error}", "error")

    def on_close(self, ws, close_status_code, close_msg):
        self.display_message("Connection closed", "info")

    def on_open(self, ws):
        self.display_message("Connected", "info")

    def connect(self):
        self.websocket = WebSocketApp(self.uri+self.username_input_field.get(),
                                      on_open=self.on_open,
                                      on_message=self.on_message,
                                      on_error=self.on_error,
                                      on_close=self.on_close)
        self.websocket.run_forever()

    def reconnect(self):
        if self.websocket:
            self.websocket.close()
        threading.Thread(target=self.connect, daemon=True).start()

    def disconnect(self):
        if not self.websocket.sock or not self.websocket.sock.connected:
            self.display_message("Already disconnected", "warning")
            return
        self.message_area.delete(0.0, tk.END)
        if self.websocket:
            self.websocket.close()

    def clear_message_area(self):
        self.message_area.config(state='normal')
        self.message_area.delete(0.0, tk.END)
        self.message_area.config(state='disabled')

    def send_message(self):
        if not self.websocket or not self.websocket.sock or not self.websocket.sock.connected:
            self.display_message("Not connected", "warning")
            return
        message = self.input_field.get(0.0, tk.END).replace("\n", "")
        print(message)
        if CHECK_MESSAGE_TYPE:
            try:
                json.loads(message)
            except json.JSONDecodeError as e:
                print(e)
                self.display_message("Invalid JSON", "warning")
                return
        if message:
            self.websocket.send(message)
            self.display_message(f"You: {message}")

    def display_message(self, message, state=None):
        self.message_area.config(state='normal')
        if state is None:
            self.message_area.insert(tk.END, message + '\n')
        else:
            self.message_area.insert(tk.END, message + '\n', state)
        self.message_area.config(state='disabled')
        self.message_area.yview(tk.END)

    def on_close_window(self):
        if self.websocket:
            self.websocket.close()
        self.window.destroy()

    def start(self):
        threading.Thread(target=self.connect, daemon=True).start()
        self.window.mainloop()

if __name__ == "__main__":
    client = WebSocketClient(URL)
    client.start()