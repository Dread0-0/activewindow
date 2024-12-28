import Xlib
import Xlib.display
import asyncio
from websockets.server import serve
import sqlite3
import time
import os

home = os.getenv("HOME")

disp = Xlib.display.Display()
root = disp.screen().root

NET_ACTIVE_WINDOW = disp.intern_atom('_NET_ACTIVE_WINDOW')
NET_WM_NAME = disp.intern_atom('_NET_WM_NAME')
last_seen = {'xid': None, 'name': None}

def get_active_window():
    """
    Get the currently active window ID.
    """
    try:
        window_id = root.get_full_property(NET_ACTIVE_WINDOW, Xlib.X.AnyPropertyType).value[0]
    except (AttributeError, IndexError):
        window_id = None
    return window_id

def get_window_name(window_id):
    """
    Get the name (title) of the specified window.
    """
    try:
        window_obj = disp.create_resource_object('window', window_id)
        window_name = window_obj.get_full_property(NET_WM_NAME, 0).value.decode('utf-8')
    except (Xlib.error.XError, AttributeError):
        window_name = None
    return window_name

async def winname(websocket):
    """
    WebSocket handler to send window details.
    """
    while True:
        await websocket.send(str(last_seen))
        await asyncio.sleep(1)

async def track_active_window():
    """
    Track changes in the active window and update the global state.
    """
    global last_seen
    root.change_attributes(event_mask=Xlib.X.PropertyChangeMask)

    while True:
        win = get_active_window()
        if win:
            window_name = get_window_name(win)
            if window_name != last_seen['name']:
                last_seen = {'xid': win, 'name': window_name}
                con = sqlite3.connect(f"{home}/.local/window.db")
                cur = con.cursor()
                cur.execute("INSERT INTO windows(winname, epoch) VALUES(?, ?)", (window_name, time.time()))
                con.commit()
                con.close()

        while disp.pending_events():
            event = disp.next_event()
            if event.type == Xlib.X.PropertyNotify and event.atom == NET_ACTIVE_WINDOW:
                break

        await asyncio.sleep(0.1)

async def main():
    """
    Main entry point to start the WebSocket server and window tracking.
    """
    websocket_server = serve(winname, "localhost", 8765)
    asyncio.ensure_future(websocket_server)
    await track_active_window()

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Exiting...")




















# barely wrote any of this code bro, i stole the window detection code from stackoverflow, used the websocket code from the documentation and fixed bugs with chatgpt im such a fraud T_T
