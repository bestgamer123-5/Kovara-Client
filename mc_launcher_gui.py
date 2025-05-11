import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
import json
import requests
from minecraft_launcher_lib import command, install, utils, fabric
import subprocess
import platform

# Function to get the user's home directory and Minecraft directory
def get_minecraft_directory():
    if platform.system() == "Windows":
        # Default Windows path for Minecraft
        return os.path.join(os.getenv('APPDATA'), '.minecraft')
    elif platform.system() == "Darwin":
        # macOS path for Minecraft
        return os.path.expanduser('~/Library/Application Support/minecraft')
    else:
        # Linux path for Minecraft
        return os.path.expanduser('~/.minecraft')

# Function to get the mods folder (a custom folder inside the project)
def get_mods_folder():
    return os.path.join(os.getcwd(), "mods")

# Function to get settings file location (in the project directory)
def get_settings_file():
    return os.path.join(os.getcwd(), "settings.json")

# Auto-locate the directories
minecraft_directory = get_minecraft_directory()
mods_folder = get_mods_folder()
settings_file = get_settings_file()

# Ensure the mods folder exists
os.makedirs(mods_folder, exist_ok=True)

default_settings = {
    "ram": "2048",
    "fps_limit": True,
    "vsync": False,
    "fullscreen": True,
    "username": "Player123"
}

# Function to save settings
def save_settings():
    data = {
        "ram": ram_entry.get(),
        "fps_limit": fps_var.get(),
        "vsync": vsync_var.get(),
        "fullscreen": fullscreen_var.get(),
        "username": username_entry.get().strip()
    }
    with open(settings_file, "w") as f:
        json.dump(data, f)
    messagebox.showinfo("Settings", "Settings saved!")

# Function to load settings
def load_settings():
    if os.path.exists(settings_file):
        with open(settings_file, "r") as f:
            return json.load(f)
    return default_settings.copy()

# Function to get all available versions of Minecraft
def get_all_versions():
    return [v["id"] for v in utils.get_available_versions(minecraft_directory)]

# Function to get installed versions of Minecraft
def get_installed_versions():
    return [v["id"] for v in utils.get_installed_versions(minecraft_directory)]

# Function to install selected Minecraft versions
def install_selected_versions():
    selected = version_listbox.curselection()
    selected_versions = [all_versions[i] for i in selected]

    if not os.path.exists(minecraft_directory):
        os.makedirs(minecraft_directory)
        print(f"Created Minecraft directory at {minecraft_directory}")
    
    for version in selected_versions:
        try:
            print(f"Attempting to install version: {version}")
            install.install_minecraft_version(version, minecraft_directory)
            print(f"Successfully installed version: {version}")
            if fabric_var.get():
                fabric.install_fabric(version, minecraft_directory)
                print(f"Successfully installed Fabric for version: {version}")
        except Exception as e:
            print(f"Failed to install {version}: {e}")
            messagebox.showerror("Error", f"Failed to install version: {version}")
    
    messagebox.showinfo("Done", "Selected versions installed.")
    update_version_dropdown()

# Function to update the version dropdown
def update_version_dropdown():
    installed = get_installed_versions()
    version_box['values'] = installed
    if installed:
        version_box.set(installed[0])

# Function to launch Minecraft with the selected version
def launch_minecraft():
    selected_version = version_box.get()
    if not selected_version:
        messagebox.showerror("Error", "No version selected.")
        return

    user_username = username_entry.get().strip()
    if not user_username:
        messagebox.showerror("Missing Info", "Enter a username.")
        return

    if not os.path.exists(minecraft_directory):
        messagebox.showerror("Error", f"Minecraft directory not found: {minecraft_directory}")
        return

    version_path = os.path.join(minecraft_directory, "versions", selected_version)
    if not os.path.exists(version_path):
        messagebox.showerror("Error", f"Version directory not found: {version_path}")
        return

    java_path = "C:\\Program Files\\Java\\jdk-24\\bin\\java.exe"
    if not os.path.exists(java_path):
        messagebox.showerror("Error", f"Java executable not found: {java_path}")
        return

    settings = load_settings()
    ram = settings.get("ram", "2048")

    selected_mods = [mods_listbox.get(i) for i in mods_listbox.curselection()]
    for mod in selected_mods:
        mod_path = os.path.join(mods_folder, mod)
        if not os.path.exists(mod_path):
            messagebox.showerror("Mod Error", f"Mod file {mod} is missing!")
            return

    options = {
        "username": user_username,
        "uuid": "12345678969089067ACW890",
        "token": "dummy_token",
        "mods": selected_mods,
    }

    try:
        minecraft_command = command.get_minecraft_command(selected_version, minecraft_directory, options)
        print("Minecraft Command:", minecraft_command)

        java_args = [
            java_path,
            f"-Xmx{ram}M",
            f"-Xms{ram}M"
        ]
        if settings.get("fps_limit"):
            java_args.append("-Dfml.noDisplay=true")
        if settings.get("vsync"):
            java_args.append("-Dvsync=true")
        if settings.get("fullscreen"):
            java_args.append("-Dfullscreen=true")

        full_cmd = java_args + minecraft_command[1:]
        print("Full Command:", full_cmd)

        subprocess.run(full_cmd)
    except Exception as e:
        messagebox.showerror("Launch Error", f"Failed to launch: {e}")
        print(f"Launch Error: {e}")

# Function to download mods from URL
def download_mod():
    mod_url = mod_url_entry.get()
    if mod_url:
        try:
            mod_name = mod_url.split("/")[-1]
            mod_path = os.path.join(mods_folder, mod_name)

            if not os.path.exists(mods_folder):
                os.makedirs(mods_folder)

            if os.path.exists(mod_path):
                os.remove(mod_path)

            response = requests.get(mod_url)
            with open(mod_path, "wb") as f:
                f.write(response.content)
            messagebox.showinfo("Download", f"Mod {mod_name} downloaded successfully!")
            mods_listbox.insert(tk.END, mod_name)
        except Exception as e:
            messagebox.showerror("Download Error", f"Failed to download the mod: {e}")
    else:
        messagebox.showerror("Invalid URL", "Please enter a valid mod URL.")

# UI
root = tk.Tk()
root.title("Kovara Client")
root.geometry("1000x700")
root.configure(bg="#1e1e1e")

notebook = ttk.Notebook(root)
notebook.pack(fill='both', expand=True)

# Home Tab
home_tab = tk.Frame(notebook, bg="#1e1e1e")
notebook.add(home_tab, text='Home')

tk.Label(home_tab, text="Enter Username:", bg="#1e1e1e", fg="white").pack(pady=5)
username_entry = tk.Entry(home_tab)
username_entry.insert(0, load_settings().get("username", "Player123"))
username_entry.pack(pady=5)

tk.Label(home_tab, text="Select Installed Version to Launch:", bg="#1e1e1e", fg="white").pack(pady=5)

version_box = ttk.Combobox(home_tab, state="readonly")
version_box.pack(pady=5)
update_version_dropdown()

tk.Button(home_tab, text="Launch Minecraft", command=launch_minecraft, bg="#0078D7", fg="white").pack(pady=10)

# Versions Tab
versions_tab = tk.Frame(notebook, bg="#1e1e1e")
notebook.add(versions_tab, text='Versions')

all_versions = get_all_versions()
version_listbox = tk.Listbox(versions_tab, selectmode=tk.MULTIPLE, height=20)
for v in all_versions:
    version_listbox.insert(tk.END, v)
version_listbox.pack(pady=10, fill='both', expand=True)

fabric_var = tk.BooleanVar()
tk.Checkbutton(versions_tab, text="Install with Fabric", variable=fabric_var, bg="#1e1e1e", fg="white").pack(pady=5)

tk.Button(versions_tab, text="Download Selected Versions", command=install_selected_versions, bg="#0078D7", fg="white").pack(pady=5)

# Settings Tab
settings_tab = tk.Frame(notebook, bg="#1e1e1e")
notebook.add(settings_tab, text='Settings')

loaded_settings = load_settings()

tk.Label(settings_tab, text="RAM Allocation (MB):", bg="#1e1e1e", fg="white").pack(pady=10)
ram_entry = tk.Entry(settings_tab)
ram_entry.insert(0, loaded_settings["ram"])
ram_entry.pack(pady=5)

fps_var = tk.BooleanVar(value=loaded_settings["fps_limit"])
tk.Checkbutton(settings_tab, text="Limit FPS", variable=fps_var, bg="#1e1e1e", fg="white").pack()

vsync_var = tk.BooleanVar(value=loaded_settings["vsync"])
tk.Checkbutton(settings_tab, text="Enable VSync", variable=vsync_var, bg="#1e1e1e", fg="white").pack()

fullscreen_var = tk.BooleanVar(value=loaded_settings["fullscreen"])
tk.Checkbutton(settings_tab, text="Fullscreen Mode", variable=fullscreen_var, bg="#1e1e1e", fg="white").pack()

tk.Button(settings_tab, text="Save Settings", command=save_settings, bg="#0078D7", fg="white").pack(pady=10)

# Mods Tab
mods_tab = tk.Frame(notebook, bg="#1e1e1e")
notebook.add(mods_tab, text='Mods')

tk.Label(mods_tab, text="Available Mods:", bg="#1e1e1e", fg="white").pack(pady=10)

mods_listbox = tk.Listbox(mods_tab, selectmode=tk.MULTIPLE)
mods_listbox.pack(pady=5, fill='both', expand=True)

for file in os.listdir(mods_folder):
    if file.endswith(".jar"):
        mods_listbox.insert(tk.END, file)

tk.Label(mods_tab, text="Enter Mod URL (Download .jar):", bg="#1e1e1e", fg="white").pack(pady=10)
mod_url_entry = tk.Entry(mods_tab)
mod_url_entry.pack(pady=5)

tk.Button(mods_tab, text="Download Mod", command=download_mod, bg="#0078D7", fg="white").pack(pady=10)
# Cosmetics aka skins Tab
cosmetics_tab = tk.Frame(notebook, bg="#1e1e1e")
notebook.add(cosmetics_tab, text='Cosmetics')

skin_label = tk.Label(cosmetics_tab, text="Custom Skins coming soon!", bg="#1e1e1e", fg="white")
skin_label.pack(pady=10)

root.mainloop()

