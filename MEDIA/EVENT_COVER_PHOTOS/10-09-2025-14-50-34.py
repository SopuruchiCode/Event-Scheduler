from pathlib import Path
import re
import shutil
from tkinter import *
from tkinter import messagebox


def separate_files(root_path_string, folder_path):
    pattern = r"\([0-9]+\)$"
    # root_path_string = "C:\\Users\\DELL\\Desktop\\AUDIO\\TRACKS\\2025-08-24 Sunday service swep"
    root_PATH = Path(root_path_string)
    # folder_path = "C:\\Users\\DELL\\Desktop\\AUDIO\\TRACKS\\2025-08-24 Sunday service swep\\Media"
    _dir = Path(folder_path)

    if not root_PATH.exists() or not _dir.exists():
        quit()

    for i in _dir.iterdir():
        match = re.search(pattern, i.stem)
        if match:
            print(i.stem)
            print(match.group(0))
            version = match.group(0)[1:-1]
            try:
                destination_path = root_PATH.joinpath(f"Media {version}")
                if not destination_path.exists():
                    destination_path.mkdir()
                shutil.copy2(str(i), str(destination_path.joinpath(str(i.name))))
            except Exception as e:
                print(e)
                
            else:
                print(f"{i.name} was copied successfully")

        else:
            try:
                print(i)
                destination_path = root_PATH.joinpath(f"Media Original")
                if not destination_path.exists():
                    destination_path.mkdir()
                shutil.copy2(str(i), str(destination_path.joinpath(str(i.name))))
            except Exception as e:
                print(e)
                messagebox.showerror(message="There was an error")

            else:
                print(f"{i.name} was copied successfully")
    messagebox.showinfo(message="All files have been sorted")

def submit():
    dest = root_folder_entry.get()
    source = source_folder_entry.get()
    separate_files(dest, source)

    root_folder_entry.delete(0, END)
    source_folder_entry.delete(0, END)

window = Tk()
window.geometry("1000x400")
window.title("Audio File Sorter")

root_folder_label = Label(window, text='Destination Folder Path')
root_folder_label.place(x=50, y=40)
root_folder_entry = Entry(window,width=60,
                 font=(15))
root_folder_entry.place(x=180, y=40)

source_folder_label = Label(window, text='Source Folder Path')
source_folder_label.place(x=40, y=80)
source_folder_entry = Entry(window, width=60,
                 font=(15))
source_folder_entry.place(x=150, y=80)

btn = Button(command=submit, text="submit")
btn.place(x=200, y=200)
window.mainloop()