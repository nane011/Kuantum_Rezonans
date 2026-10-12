import tkinter as tk
from QuantumApp import QuantumSonifierGUI

def main():
    """
    Kuantum Rezonans Ana Başlatıcı sınıfı.
    """
    root = tk.Tk()
    app = QuantumSonifierGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()