import tkinter as tk
from PIL import Image, ImageTk

# Create the main window
root = tk.Tk()
root.title("HuffCompress - Lossless Compression Tool")
root.geometry("400x300")  # Set the size of the window
root.configure(bg="black")  # Set the background color to black
root.resizable(False, False)  # Lock the window size

# Placeholder for a small image logo at the top-left side
# You can replace 'your_logo.png' with the path to your actual image file
logo_path = './images/logo.png'
try:
    pil_image = Image.open(logo_path)
    logo_image = ImageTk.PhotoImage(pil_image) if pil_image else None
except Exception as e:
    print(f"Error loading image: {e}")
    logo_image = None

# Create a label for the logo
logo_label = tk.Label(root, image=logo_image, bg="black")
logo_label.grid(row=0, column=0, padx=10, pady=10, sticky="nw")  # Adjust padx, pady, and sticky as needed

# Run the Tkinter event loop
root.mainloop()
