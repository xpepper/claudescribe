import threading
import webbrowser

import uvicorn


def open_browser() -> None:
    webbrowser.open("http://localhost:8000")


if __name__ == "__main__":
    threading.Timer(1.5, open_browser).start()
    uvicorn.run("backend.app:app", host="0.0.0.0", port=8000, reload=False)
