import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image
import numpy as np
import os

# --- Image operations ---
def load_image(path):
    try:
        img = Image.open(path).convert('RGB')
        data = np.array(img, dtype=np.uint8)
        return data, img.size
    except Exception as e:
        messagebox.showerror("Error", f"Failed to load image:\n{e}")
        raise

def save_image(data, size, path):
    try:
        img = Image.fromarray(data.astype('uint8'))
        img.save(path)
    except Exception as e:
        messagebox.showerror("Error", f"Failed to save image:\n{e}")
        raise

def xor_operation(data, key):
    # Ensure key is within 0–255 and use bitwise XOR (self-inverse)
    return np.bitwise_xor(data, key % 256)

def swap_pixels(data):
    # Self-inverse diagonal swap: apply twice to restore original
    swapped = data.copy()
    h, w, _ = swapped.shape
    for i in range(0, h, 2):
        for j in range(0, w, 2):
            if i + 1 < h and j + 1 < w:
                swapped[i, j], swapped[i + 1, j + 1] = swapped[i + 1, j + 1], swapped[i, j]
    return swapped

def process_image(path, output_path, key, method, mode):
    data, size = load_image(path)
    if method == 'xor':
        result = xor_operation(data, key)
    elif method == 'swap':
        result = swap_pixels(data)
    else:
        messagebox.showerror("Error", "Unsupported method")
        return
    save_image(result, size, output_path)
    messagebox.showinfo("Success", f"Image {mode}ed using {method} and saved to:\n{output_path}")

# --- GUI actions ---
def browse_file():
    chosen = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg *.png *.bmp")])
    if chosen:
        file_path.set(chosen)

def on_method_change(*_):
    m = method_var.get()
    # Disable key when swap is selected
    key_entry.configure(state=('normal' if m == 'xor' else 'disabled'))

def run_process(mode):
    path = file_path.get()
    if not path:
        messagebox.showerror("Error", "Please select an image file.")
        return
    method = method_var.get()
    try:
        key = int(key_entry.get()) if method == 'xor' else 0
    except ValueError:
        messagebox.showerror("Error", "Key must be an integer.")
        return
    suffix = "_encrypt" if mode == "encrypt" else "_decrypt"
    output = os.path.splitext(path)[0] + f"{suffix}.png"
    process_image(path, output, key, method, mode)

# --- GUI setup ---
root = tk.Tk()
root.title("Image Encryption Tool")

file_path = tk.StringVar()
method_var = tk.StringVar(value='xor')
method_var.trace_add('write', on_method_change)

tk.Label(root, text="Select Image:").grid(row=0, column=0, sticky='e', padx=5, pady=5)
tk.Entry(root, textvariable=file_path, width=40).grid(row=0, column=1, padx=5, pady=5)
tk.Button(root, text="Browse", command=browse_file).grid(row=0, column=2, padx=5, pady=5)

tk.Label(root, text="Method:").grid(row=1, column=0, sticky='e', padx=5, pady=5)
tk.OptionMenu(root, method_var, 'xor', 'swap').grid(row=1, column=1, sticky='w', padx=5, pady=5)

tk.Label(root, text="Key (for XOR):").grid(row=2, column=0, sticky='e', padx=5, pady=5)
key_entry = tk.Entry(root)
key_entry.insert(0, "123")
key_entry.grid(row=2, column=1, sticky='w', padx=5, pady=5)

tk.Button(root, text="Encrypt", command=lambda: run_process('encrypt')).grid(row=3, column=0, pady=10)
tk.Button(root, text="Decrypt", command=lambda: run_process('decrypt')).grid(row=3, column=1, pady=10)

on_method_change()  # Initialize key field state
root.mainloop()
