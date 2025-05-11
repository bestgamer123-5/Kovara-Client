import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
import json
import requests
from minecraft_launcher_lib import command, install, utils, fabric, forge
import subprocess

# Detect default Minecraft directory
minecraft_directory = utils.get_minecraft_directory()
launcher_version = "1.0.0"

# Paths
base_dir = os.path.dirname(os.path.abspath(__file__))
mods_folder = os.path.join(base_dir, "mods")
settings_file = os.path.join(base_dir, "settings.json")
os.makedirs(mods_folder, exist_ok=True)

# Default settings
default_settings = {
    "ram": "2048",
    "fps_limit": True,
    "vsync": False,
    "fullscreen": True,
    "username": "Player123"
}

# Load settings
def load_settings():
    if os.path.exists(settings_file):
        with open(settings_file, "r") as f:
            return json.load(f)
    return default_settings.copy()

# Save settings
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

# Get all and installed versions
def get_all_versions():
    return [v["id"] for v in utils.get_available_versions(minecraft_directory)]

def get_installed_versions():
    return [v["id"] for v in utils.get_installed_versions(minecraft_directory)]

# Update version dropdown
def update_version_dropdown():
    installed = get_installed_versions()
    version_box['values'] = installed
    if installed:
        version_box.set(installed[0])

# Install selected Minecraft versions
def install_selected_versions():
    selected = version_listbox.curselection()
    selected_versions = [all_versions[i] for i in selected]

    for version in selected_versions:
        try:
            install.install_minecraft_version(version, minecraft_directory)
            if fabric_var.get():
                fabric.install_fabric(version, minecraft_directory)
                print(f"Fabric installed for {version}")
            if forge_var.get():
                forge_version = forge.find_forge_version(version)
                if forge_version and forge.supports_automatic_install(forge_version):
                    forge.install_forge_version(forge_version, minecraft_directory)
                    print(f"Forge installed for {version}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to install {version}: {e}")
    update_version_dropdown()

# Launch Minecraft
def launch_minecraft():
    selected_version = version_box.get()
    username = username_entry.get().strip()
    if not selected_version or not username:
        messagebox.showerror("Error", "Missing version or username.")
        return

    version_path = os.path.join(minecraft_directory, "versions", selected_version)
    if not os.path.exists(version_path):
        messagebox.showerror("Error", f"Version not installed: {selected_version}")
        return

    java_path = "java"  # fallback to system Java
    settings = load_settings()
    ram = settings.get("ram", "2048")
    selected_mods = [mods_listbox.get(i) for i in mods_listbox.curselection()]

    options = {
        "username": username,
        "uuid": "1234567890",
        "token": "dummy_token",
    }

    try:
        cmd = command.get_minecraft_command(selected_version, minecraft_directory, options)
        java_args = [java_path, f"-Xmx{ram}M", f"-Xms{ram}M"]
        if settings.get("fullscreen"):
            java_args.append("-Dfullscreen=true")
        full_cmd = java_args + cmd[1:]
        subprocess.run(full_cmd)
    except Exception as e:
        messagebox.showerror("Launch Error", str(e))

# Download mod
def download_mod():
    mod_url = mod_url_entry.get()
    if not mod_url:
        messagebox.showerror("Missing URL", "Please enter a mod URL.")
        return
    try:
        mod_name = mod_url.split("/")[-1]
        mod_path = os.path.join(mods_folder, mod_name)
        with open(mod_path, "wb") as f:
            f.write(requests.get(mod_url).content)
        mods_listbox.insert(tk.END, mod_name)
        messagebox.showinfo("Success", f"{mod_name} downloaded.")
    except Exception as e:
        messagebox.showerror("Mod Error", str(e))

# Upload skin
def upload_skin():
    file = filedialog.askopenfilename(filetypes=[("PNG Files", "*.png")])
    if file:
        dest = os.path.join(minecraft_directory, "custom_skin.png")
        with open(file, "rb") as src, open(dest, "wb") as dst:
            dst.write(src.read())
        messagebox.showinfo("Skin", "Skin uploaded!")

# Update check (placeholder logic)
def check_for_update():
    latest_version = "1.0.1"  # pretend this is fetched online
    if latest_version != launcher_version:
        messagebox.showinfo("Update Available", f"New version {latest_version} available.")
    else:
        messagebox.showinfo("Up To Date", "You're on the latest version.")

# GUI Setup
root = tk.Tk()
root.title("Custom Minecraft Launcher")
root.geometry("1000x700")
root.configure(bg="#1e1e1e")
notebook = ttk.Notebook(root)
notebook.pack(fill='both', expand=True)

# Home Tab
home_tab = tk.Frame(notebook, bg="#1e1e1e")
notebook.add(home_tab, text='Home')

tk.Label(home_tab, text="Enter Username:", bg="#1e1e1e", fg="white").pack()
username_entry = tk.Entry(home_tab)
username_entry.insert(0, load_settings()["username"])
username_entry.pack()

tk.Label(home_tab, text="Select Version:", bg="#1e1e1e", fg="white").pack()
version_box = ttk.Combobox(home_tab, state="readonly")
version_box.pack(pady=5)
update_version_dropdown()

tk.Button(home_tab, text="Launch", command=launch_minecraft).pack(pady=10)

# Versions Tab
versions_tab = tk.Frame(notebook, bg="#1e1e1e")
notebook.add(versions_tab, text='Versions')

all_versions = get_all_versions()
version_listbox = tk.Listbox(versions_tab, selectmode=tk.MULTIPLE, height=20)
for v in all_versions:
    version_listbox.insert(tk.END, v)
version_listbox.pack(pady=10, fill='both', expand=True)

fabric_var = tk.BooleanVar()
forge_var = tk.BooleanVar()

tk.Checkbutton(versions_tab, text="Install Fabric", variable=fabric_var, bg="#1e1e1e", fg="white").pack()
tk.Checkbutton(versions_tab, text="Install Forge", variable=forge_var, bg="#1e1e1e", fg="white").pack()

tk.Button(versions_tab, text="Download Selected Versions", command=install_selected_versions).pack(pady=5)

# Settings Tab
settings_tab = tk.Frame(notebook, bg="#1e1e1e")
notebook.add(settings_tab, text='Settings')

loaded_settings = load_settings()
tk.Label(settings_tab, text="RAM (MB):", bg="#1e1e1e", fg="white").pack()
ram_entry = tk.Entry(settings_tab)
ram_entry.insert(0, loaded_settings["ram"])
ram_entry.pack()

fps_var = tk.BooleanVar(value=loaded_settings["fps_limit"])
tk.Checkbutton(settings_tab, text="Limit FPS", variable=fps_var, bg="#1e1e1e", fg="white").pack()
vsync_var = tk.BooleanVar(value=loaded_settings["vsync"])
tk.Checkbutton(settings_tab, text="Enable VSync", variable=vsync_var, bg="#1e1e1e", fg="white").pack()
fullscreen_var = tk.BooleanVar(value=loaded_settings["fullscreen"])
tk.Checkbutton(settings_tab, text="Fullscreen Mode", variable=fullscreen_var, bg="#1e1e1e", fg="white").pack()
tk.Button(settings_tab, text="Save Settings", command=save_settings).pack(pady=10)

# Mods Tab
mods_tab = tk.Frame(notebook, bg="#1e1e1e")
notebook.add(mods_tab, text='Mods')

tk.Label(mods_tab, text="Available Mods:", bg="#1e1e1e", fg="white").pack()
mods_listbox = tk.Listbox(mods_tab, selectmode=tk.MULTIPLE)
mods_listbox.pack(pady=5, fill='both', expand=True)

for file in os.listdir(mods_folder):
    if file.endswith(".jar"):
        mods_listbox.insert(tk.END, file)

tk.Label(mods_tab, text="Mod URL (.jar):", bg="#1e1e1e", fg="white").pack()
mod_url_entry = tk.Entry(mods_tab, width=60)
mod_url_entry.pack()
tk.Button(mods_tab, text="Download Mod", command=download_mod).pack(pady=5)

# Cosmetics Tab
cosmetics_tab = tk.Frame(notebook, bg="#1e1e1e")
notebook.add(cosmetics_tab, text='Cosmetics')

tk.Label(cosmetics_tab, text="Upload Skin (.png):", bg="#1e1e1e", fg="white").pack()
tk.Button(cosmetics_tab, text="Upload Skin", command=upload_skin).pack(pady=5)

# Update Tab
update_tab = tk.Frame(notebook, bg="#1e1e1e")
notebook.add(update_tab, text='Updates')

tk.Label(update_tab, text=f"Launcher Version: {launcher_version}", bg="#1e1e1e", fg="white").pack(pady=10)
tk.Button(update_tab, text="Check for Updates", command=check_for_update).pack()

# Launch GUI
root.mainloop()
