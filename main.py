import tkinter as tk
from gui import CitationCheckerApp
import ctypes
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
except Exception as e:
    print("Tidak dapat mengatur DPI awareness: ", e)

def main():
    root = tk.Tk()
    app = CitationCheckerApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()