import os
import threading
import webbrowser

import uvicorn

PORT = int(os.environ.get("PORT", 8000))


def open_browser() -> None:
    webbrowser.open(f"http://localhost:{PORT}")


if __name__ == "__main__":
    threading.Timer(1.5, open_browser).start()
    uvicorn.run("backend.app:app", host="0.0.0.0", port=PORT, reload=False)
