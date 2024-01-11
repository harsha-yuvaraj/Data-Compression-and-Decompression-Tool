import tkinter as tk
from tkinter import ttk, filedialog
from PIL import ImageTk, Image
from os import stat
from compress_file import HuffFile

# background color - hex format
bgColor = "#e4e8f0"

# Create the main window
mainWin = tk.Tk()
mainWin.title("HuffCompress - Lossless Compression Tool")
mainWin.geometry("400x200")  # Set the size of the window
mainWin.iconbitmap('./images/logo.ico') # Set the icon logo of HuffCompress
mainWin.configure(bg=bgColor)  # Set the background color to a shade of royal blue
mainWin.resizable(False, False)  # Lock the window size

# Loading our logo and placing it in the main window
logo = ImageTk.PhotoImage(Image.open('./images/logo.png').resize((120,90)))
logoContainer = tk.Label(image=logo)
logoContainer.configure(bg=bgColor, height="60")  # Set the background color to a shade of royal blue
logoContainer.pack(side="top", anchor="nw") # Position the logo top-left side of the main window

# Styles for buttons
style1 = ttk.Style() # For compress button
style2 = ttk.Style() # For decompress button
style1.configure('W.TButton', font=('Helvetica', 16, 'bold italic'), foreground='#5dbea3')
style2.configure('C.TButton', font=('Helvetica', 16, 'bold italic'), foreground='#4681f4')

# Listener for compress button
def compressFile():
    target_file =  filedialog.askopenfilename(title="Choose a file to compress", filetypes=((".txt","*.txt"),))
    original_size = stat(target_file)
    hf = HuffFile()
    hf.compress_file(target_file)
    compressed_size = stat(target_file+".huff")
    print(f'OS: {original_size.st_size}, CS: {compressed_size.st_size}')
    

# Listener for decompress button
def decompressFile():
    target_file =  filedialog.askopenfilename(title="Choose a file to decompress", filetypes=((".huff","*.huff"),))
    original_size = stat(target_file)
    hf = HuffFile()
    hf.decompress_file(target_file)
    compressed_size = stat(target_file)
    print(f'OS: {original_size.st_size}, CS: {compressed_size.st_size}')


# Create the buttons for compression & decompression
compressBtn = ttk.Button(mainWin, text="Compress a File", width=20, style='W.TButton', command=compressFile)
compressBtn.pack(padx=(100,0), pady=(10,0))
decompressBtn = ttk.Button(mainWin, text="Decompress a File", width=20, style='C.TButton', command=decompressFile)
decompressBtn.pack(padx=(100,0), pady=(10,0))


# Run the Tkinter event loop
mainWin.mainloop()
