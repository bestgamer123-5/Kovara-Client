import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
import json
import subprocess
import requests
from minecraft_launcher_lib import command, install, utils, fabric
import urllib.request
import time

# Paths
minecraft_directory = r"C:\Users\masym\AppData\Roaming\.minecraft"
mods_folder = os.path.join("C:/Users/masym/Desktop/mc_launcher_gui", "mods")
settings_file = os.path.join("C:/Users/masym/Desktop/mc_launcher_gui", "settings.json")
os.makedirs(mods_folder, exist_ok=True)

# Default settings
default_settings = {
    "ram": "2048",
    "fps_limit": True,
    "vsync": False,
    "fullscreen": True,
    "username": "SUB TO SPYLEGEND"
}

# Launcher Version
current_launcher_version = "1.0.0"  # Define the current launcher version here

# Check for updates from a source
def check_for_updates():
    try:
        # Simulate fetching a version from an external source (for example, a GitHub release or a version file).
        latest_version_url = "https://example.com/latest_launcher_version.txt"  # Replace with actual URL
        with urllib.request.urlopen(latest_version_url) as response:
            latest_version = response.read().decode("utf-8").strip()

        # Compare versions
        if latest_version > current_launcher_version:
            messagebox.showinfo("Update Available", f"A new version {latest_version} is available!")
            update_button.config(state=tk.NORMAL)
        else:
            messagebox.showinfo("No Update", "You are already using the latest version!")
            update_button.config(state=tk.DISABLED)

    except Exception as e:
        print(f"Error checking for updates: {e}")
        messagebox.showwarning("Update Check Error", "Could not check for updates. Please try again later.")

# Simulate the update process
def update_launcher():
    try:
        # You can modify this section to actually download the latest version of the launcher
        # For example, download a new script or unzip the latest files.
        messagebox.showinfo("Updating", "Updating the launcher...")

        # Simulate a delay for the update process
        time.sleep(2)
        
        # After updating, ask the user to restart the launcher
        messagebox.showinfo("Update Complete", "The launcher has been updated. Please restart the program.")
        root.quit()  # Close the application after updating

    except Exception as e:
        print(f"Error updating launcher: {e}")
        messagebox.showerror("Update Error", "An error occurred while updating the launcher.")

# Save settings function
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

# Load settings function
def load_settings():
    if os.path.exists(settings_file):
        with open(settings_file, "r") as f:
            return json.load(f)
    return default_settings.copy()

# Get all available versions
def get_all_versions():
    return [v["id"] for v in utils.get_available_versions(minecraft_directory)]

# Get installed versions
def get_installed_versions():
    return [v["id"] for v in utils.get_installed_versions(minecraft_directory)]

# Update the version dropdown
def update_version_dropdown():
    installed = get_installed_versions()
    version_box['values'] = installed
    if installed:
        version_box.set(installed[0])

# Install selected versions
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
            if forge_var.get():
                install_forge(version)
        except Exception as e:
            print(f"Failed to install {version}: {e}")
            messagebox.showerror("Error", f"Failed to install version: {version}")
    
    messagebox.showinfo("Done", "Selected versions installed.")
    update_version_dropdown()

# Install Forge (simulate manual download)
def install_forge(version):
    forge_installer_path = os.path.join(minecraft_directory, "versions", version, "forge-installer.jar")
    if not os.path.exists(forge_installer_path):
        print(f"Forge installer not found for {version}.")
        prompt_user_to_download_forge(version)
    else:
        print(f"Forge installer found for {version}.")
        # Continue with launching Minecraft or whatever needs to happen

def prompt_user_to_download_forge(version):
    messagebox.showinfo("Manual Download", f"Please download the Forge installer for Minecraft {version} from the following link: \n\nhttps://files.minecraftforge.net/maven/net/minecraftforge/forge/{version}/forge-{version}-installer.jar")
    
    # Let the user manually select the downloaded file
    file_path = filedialog.askopenfilename(title="Select the Forge Installer", filetypes=[("Jar Files", "*.jar")])

    if file_path:
        try:
            print(f"Starting Forge installation from {file_path}...")
            process = subprocess.Popen(
                ["java", "-jar", file_path, "--installClient", minecraft_directory],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            stdout, stderr = process.communicate()  # Capture output and errors
            if process.returncode == 0:
                print(f"Successfully installed Forge from {file_path}.")
            else:
                print(f"Forge installation failed: {stderr.decode()}")
                messagebox.showerror("Forge Installation Error", f"Failed to install Forge: {stderr.decode()}")
        except Exception as e:
            print(f"Error running Forge installer: {e}")
            messagebox.showerror("Forge Installation Error", f"Error running Forge installer: {e}")

# UI Setup

root = tk.Tk()
root.title("Custom Minecraft Launcher")
root.geometry("1000x700")
root.configure(bg="#1e1e1e")

notebook = ttk.Notebook(root)
notebook.pack(fill='both', expand=True)

# Home Tab
home_tab = tk.Frame(notebook, bg="#1e1e1e")
notebook.add(home_tab, text='Home')

tk.Label(home_tab, text="Enter Username:", bg="#1e1e1e", fg="white").pack(pady=5)
username_entry = tk.Entry(home_tab)
username_entry.insert(0, load_settings().get("username", "SUB TO SPYLEGEND"))
username_entry.pack(pady=5)

tk.Label(home_tab, text="Select Installed Version to Launch:", bg="#1e1e1e", fg="white").pack(pady=5)

version_box = ttk.Combobox(home_tab, state="readonly")
version_box.pack(pady=5)
update_version_dropdown()

# Define the launch_minecraft function
def launch_minecraft():
    selected_version = version_box.get()
    username = username_entry.get().strip()
    if not selected_version:
        messagebox.showwarning("Error", "Please select a Minecraft version to launch.")
        return
    if not username:
        messagebox.showwarning("Error", "Please enter a username.")
        return
    try:
        options = {
            "username": username,
            "jvmArguments": [f"-Xmx{ram_entry.get()}M"]
        }
        command.run_minecraft(selected_version, minecraft_directory, options)
        print(f"Launching Minecraft version {selected_version} with username {username}.")
    except Exception as e:
        print(f"Error launching Minecraft: {e}")
        messagebox.showerror("Error", f"Failed to launch Minecraft: {e}")

tk.Button(home_tab, text="Launch Minecraft", command=launch_minecraft, bg="#0078D7", fg="white").pack(pady=10)


# Update Tab
update_tab = tk.Frame(notebook, bg="#1e1e1e")
notebook.add(update_tab, text='Update')

tk.Label(update_tab, text=f"Current Launcher Version: {current_launcher_version}", bg="#1e1e1e", fg="white").pack(pady=10)

update_button = tk.Button(update_tab, text="Check for Updates", command=check_for_updates, bg="#0078D7", fg="white")
update_button.pack(pady=10)

update_button.config(state=tk.DISABLED)  # Disable until an update check is made

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

forge_var = tk.BooleanVar()
tk.Checkbutton(versions_tab, text="Install with Forge", variable=forge_var, bg="#1e1e1e", fg="white").pack(pady=5)

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
mod_url_entry = tk.Entry(mods_tab, width=50)
mod_url_entry.pack(pady=5)

def download_mod():
    mod_url = mod_url_entry.get().strip()
    if not mod_url:
        messagebox.showwarning("Error", "Please enter a valid mod URL.")
        return

    try:
        mod_name = os.path.basename(mod_url)
        mod_path = os.path.join(mods_folder, mod_name)
        urllib.request.urlretrieve(mod_url, mod_path)
        mods_listbox.insert(tk.END, mod_name)
        messagebox.showinfo("Success", f"Mod '{mod_name}' downloaded successfully!")
    except Exception as e:
        print(f"Error downloading mod: {e}")
        messagebox.showerror("Error", "Failed to download the mod. Please check the URL and try again.")

tk.Button(mods_tab, text="Download Mod", command=download_mod, bg="#0078D7", fg="white").pack(pady=5)

# Cosmetics aka skins Tab
cosmetics_tab = tk.Frame(notebook, bg="#1e1e1e")
notebook.add(cosmetics_tab, text='Cosmetics')

skin_label = tk.Label(cosmetics_tab, text="Upload Skin (.png):", bg="#1e1e1e", fg="white")
skin_label.pack(pady=10)

def upload_skin():
    file = filedialog.askopenfilename(filetypes=[("PNG Files", "*.png")])
    if file:
        dest = os.path.join(minecraft_directory, "custom_skin.png")
        with open(file, "rb") as src, open(dest, "wb") as dst:
            dst.write(src.read())
        messagebox.showinfo("Skin", "Skin uploaded!")

tk.Button(cosmetics_tab, text="Upload Skin", command=upload_skin, bg="#0078D7", fg="white").pack(pady=5)

# Run the app
root.mainloop()
