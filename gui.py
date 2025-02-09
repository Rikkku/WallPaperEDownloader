import json
import subprocess
import threading
from tkinter import Tk, Canvas, Text, Entry, Button, Label, StringVar, filedialog, messagebox
import os
import sys


def initialize_location_json():
    if not os.path.exists("location.json"):
        default_config = {"steamcmd_path": "", "last_location": ""}
        with open("location.json", "w") as file:
            json.dump(default_config, file)


initialize_location_json()


def load_location_data():
    try:
        with open("location.json", "r") as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"steamcmd_path": "", "last_location": ""}

location_data = load_location_data()


screen_width = window.winfo_screenwidth()
screen_height = window.winfo_screenheight()
x_position = (screen_width - 750) // 2
y_position = (screen_height - 400) // 2
window.geometry(f"750x400+{x_position}+{y_position}")


def on_paste(event):
    try:
        clipboard_content = window.clipboard_get().strip()
        current_text = workshop_link_text.get("1.0", "end").strip()


        existing_links = [link.strip() for link in current_text.split(",") if link.strip()]


        if clipboard_content in existing_links:
            return "break"


        if existing_links:
            workshop_link_text.insert("end", f",{clipboard_content}")
        else:
            workshop_link_text.insert("end", clipboard_content)

        return "break"
    except:
        pass

workshop_link_text.bind("<Control-v>", on_paste)

def select_steamcmd():
    filepath = filedialog.askopenfilename(filetypes=[("Executable Files", "*.exe")])
    if filepath:
        steamcmd_entry.delete(0, "end")
        steamcmd_entry.insert(0, filepath)
        save_location()


def set_download_location():
    location = filedialog.askdirectory()
    if location:
        download_location_entry.delete(0, "end")
        download_location_entry.insert(0, location)
        save_location()

set_location_button = Button(window, text="Browse", command=set_download_location, bg="#A8C4F4", font=("Arial", 12))
set_location_button.place(x=630, y=300, width=100, height=30)

def save_location():
    location_config = {"steamcmd_path": steamcmd_entry.get().strip(), "last_location": download_location_entry.get().strip()}
    with open("location.json", "w") as file:
        json.dump(location_config, file)

def download_workshop_thread():
    links = workshop_link_text.get("1.0", "end").strip().split(",")
    download_location = download_location_entry.get().strip()
    steamcmd_path = steamcmd_entry.get().strip()

    if not steamcmd_path or not links or not download_location:
        messagebox.showerror("Error", "Please provide all required fields.")
        return

    links = [link.strip() for link in links if link.strip()]

    workshop_link_text.config(state="disabled")
    download_button.config(state="disabled")
    set_location_button.config(state="disabled")
    steamcmd_browse_button.config(state="disabled")
    status_var.set("Downloading...")

    try:
        for link in links:
            if "id=" not in link:
                raise ValueError(f"Invalid Workshop link: {link}")

            workshop_id = link.split("id=")[-1].split("&")[0]

            creation_flags = 0
            if sys.platform == "win32":
                creation_flags = subprocess.CREATE_NO_WINDOW

            process = subprocess.Popen(
                [
                    steamcmd_path,
                    "+login", STEAM_USER, STEAM_PASS,
                    "+force_install_dir", download_location,
                    "+workshop_download_item", "431960", workshop_id,
                    "+quit"
                ],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE,
                text=True, shell=False, creationflags=creation_flags
            )

            stdout, stderr = process.communicate()
            if process.returncode != 0:
                raise subprocess.CalledProcessError(process.returncode, process.args, output=stdout, stderr=stderr)

        status_var.set("Complete")
        messagebox.showinfo("Success", "All workshop items downloaded successfully!")

        workshop_link_text.config(state="normal")
        workshop_link_text.delete("1.0", "end")

    except Exception as e:
        status_var.set("Error")
        messagebox.showerror("Error", f"An error occurred: {e}")

    finally:
        workshop_link_text.config(state="normal")
        download_button.config(state="normal")
        set_location_button.config(state="normal")
        steamcmd_browse_button.config(state="normal")
        status_var.set("Idle")



window.resizable(False, False)
window.mainloop()
