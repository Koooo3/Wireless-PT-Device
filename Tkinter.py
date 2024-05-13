import subprocess
import os
import time
import threading 
import signal
import select
import tkinter as tk
import tkinter.font as tkFont
import csv
from queue import Queue

from PIL import Image, ImageTk
from tkinter import ttk
from tkinter import messagebox


unified_bg_color = "#282828"
unified_fg_color = "#FFFFFF"


###############################################This is the functions space #####################################
def create_file(freq):
    directory = "/home/kali/signals"
    max_files = 9
    for num in range(1, max_files + 1):
        filename = f"Signal_{num}_{freq}.complex16s"
        filepath = os.path.join(directory, filename)
        # If file does not exist, or we're cycling back to start overwriting
        if not os.path.exists(filepath) or num == max_files:
            return filepath
    # If all files exist and max is reached, start overwriting from the first file
    return os.path.join(directory, f"Signal_1_{freq}.complex16s")

def receive_signal(output_file, frequency, sample_rate, if_gain, gain, timeout=None):
    command = [
        'hackrf_transfer',
        '-r', output_file,
        '-f', str(frequency),
        '-s', str(sample_rate),
        '-l', str(if_gain),
        '-g', str(gain)
    ]
    try:
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate(timeout=3)
        if process.returncode != 0:
            print("Error in receive signal:", stderr.decode())
        else:
            print("Receive signal success", stdout.decode())
    except subprocess.TimeoutExpired:
        print("Receive operation timed out.")
        process.kill()
        process.communicate()
    except Exception:
        pass

def transmit_signal(input_file, frequency, sample_rate, antenna_gain, tx_gain):
    command = [
        'hackrf_transfer',
        '-t', input_file,
        '-f', str(frequency),
        '-s', str(sample_rate),
        '-a', str(antenna_gain),
        '-x', str(tx_gain)
    ]
    try:
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()
        if process.returncode != 0:
            print("Error in transmit signal:", stderr.decode())
        else:
            print("Transmit signal success")
    except Exception as e:
        print(f"An error occurred during transmission: {e}")


###############################################This is the functions space #####################################

def weight_setup(r, c):
    max_dimension = 12  # Maximum for both rows and columns
    # Set the specified rows and columns to weight 1
    for i in range(max_dimension):
        if i < r:
            content_frame.grid_rowconfigure(i, weight=1)
        else:
            content_frame.grid_rowconfigure(i, weight=0)  # Set all other rows to weight 0
        
        if i < c:
            content_frame.grid_columnconfigure(i, weight=1)
        else:
            content_frame.grid_columnconfigure(i, weight=0)  # Set all other columns to weight 0

def main_page():
    # Page and Font Setup.
    new_frame(content_frame)
    weight_setup(2,3)
    content_frame.grid_rowconfigure(0,weight=0)
    unified_button_font = tkFont.Font(family="Helvetica", size=36, weight="bold")
    unified_title_font = tkFont.Font(family="Helvetica", size=48, weight="bold")

    # Title label
    title_label = tk.Label(content_frame, text="Attack Vector", bg=unified_bg_color, fg=unified_fg_color, font=unified_title_font)
    title_label.grid(row=0, column=0, columnspan=3, padx=10, pady=10, sticky="nsew")

    # Create buttons with specified size and font, and center them in the grid
    wifi_button = tk.Button(content_frame, text="WIFI",
                            bg=unified_bg_color, fg=unified_fg_color, font=unified_button_font, command=wifi_page)
    wifi_button.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

    rfid_button = tk.Button(content_frame, text="RFID",
                            bg=unified_bg_color, fg=unified_fg_color, font=unified_button_font, command=rfid_page)
    rfid_button.grid(row=1, column=1, padx=10, pady=10, sticky="nsew")

    sub_ghz_button = tk.Button(content_frame, text="SUB-GHz",
                               bg=unified_bg_color, fg=unified_fg_color, font=unified_button_font, command=sub_ghz_page)
    sub_ghz_button.grid(row=1, column=2, padx=10, pady=10, sticky="nsew")

def wifi_page():
    # Page and Font Setup.
    new_frame(content_frame)
    weight_setup(7, 1)
    unified_button_font = tkFont.Font(family="Helvetica", size=24, weight="bold")
    unified_title_font = tkFont.Font(family="Helvetica", size=48, weight="bold")

    # Title label
    title_label = tk.Label(content_frame, text="Select Attack", bg=unified_bg_color, fg=unified_fg_color, font=unified_title_font)
    title_label.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

    # Create and arrange buttons for different Wi-Fi attack methods
    button_texts = ["Scan Targets", "Deauthentication Attack", "Password Crack Attempt", "Beacon Frame Flooding", "Evil Twin"]
    button_commands = [scan_targets, deauth_page, password_crack, beacon_flooding, evil_twin]
    
    for index, (text, command) in enumerate(zip(button_texts, button_commands)):
        button = tk.Button(content_frame, text=text, font=unified_button_font, bg=unified_bg_color, fg=unified_fg_color, command=command)
        button.grid(row=1 + index, column=0, padx=10, pady=10, sticky="nsew")

    # Back button
    return_button = tk.Button(content_frame, text="Back", font=unified_button_font, bg=unified_bg_color, fg=unified_fg_color, command=main_page)
    return_button.grid(row=6, column=0, padx=10, pady=10, sticky="nsew")

def scan_targets():
    """Displays WLAN interfaces as selectable buttons and navigates to the scanning page."""
    new_frame(content_frame)
    weight_setup(4, 1) 
    unified_button_font = tkFont.Font(family="Helvetica", size=36, weight="bold")
    unified_title_font = tkFont.Font(family="Helvetica", size=48, weight="bold")

    # Title label
    title_label = tk.Label(content_frame, text="Select an Interface", bg=unified_bg_color, fg=unified_fg_color, font=unified_title_font)
    title_label.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

    # Get the available WLAN interfaces
    result = subprocess.run(["iwconfig"], stdout=subprocess.PIPE, text=True)
    interfaces = [line.split()[0] for line in result.stdout.splitlines() if "IEEE 802.11" in line]

    # Create a button for each WLAN interface
    for index, interface in enumerate(interfaces, start=1):
        interface_button = tk.Button(content_frame, text=interface, font=unified_button_font, bg=unified_bg_color, fg=unified_fg_color,
                                     command=lambda iface=interface: on_interface_button_click(iface))
        interface_button.grid(row=index, column=0, padx=10, pady=10, sticky="nsew")

    # Back button
    return_button = tk.Button(content_frame, text="Back", font=unified_button_font, bg=unified_bg_color, fg=unified_fg_color, command=wifi_page)
    return_button.grid(row=len(interfaces) + 1, column=0, padx=10, pady=10, sticky="nsew")


# Global variable to hold the selected monitor mode interface
monitor_interface = ""

def on_interface_button_click(interface):
    """Handles the selection of a WLAN interface and initiates monitor mode setup."""
    global monitor_interface
    monitor_interface = set_monitor_mode(interface)
    if monitor_interface:
        scanning()

def set_monitor_mode(interface):
    """Set the given WLAN interface into monitor mode and return the new interface name."""
    try:
        # Stop conflicting processes that can interfere with airmon-ng using airmon-ng check kill
        subprocess.run(["sudo", "airmon-ng", "check", "kill"], check=True)

        # Place the interface into monitor mode using airmon-ng
        subprocess.run(["sudo", "airmon-ng", "start", interface], check=True)

        # Restart NetworkManager after setting the monitor mode
        subprocess.run(["sudo", "systemctl", "restart", "NetworkManager"], check=True)

        # Retrieve the new monitor mode interface name
        result = subprocess.run(["iwconfig"], stdout=subprocess.PIPE, text=True)
        for line in result.stdout.splitlines():
            if "Mode:Monitor" in line:
                return line.split()[0]
    except subprocess.CalledProcessError as e:
        print(f"Error enabling monitor mode: {e}")
        return None


def scanning():
    """Set up the scanning page, start airodump-ng in a thread, and display scanning status."""
    global scanning_process, scanning_output_label

    new_frame(content_frame)
    weight_setup(4, 1)
    unified_title_font = tkFont.Font(family="Helvetica", size=48, weight="bold")

    title_label = tk.Label(content_frame, text="Scanning", bg=unified_bg_color, fg=unified_fg_color, font=unified_title_font)
    title_label.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

    scanning_output_label = tk.Label(content_frame, text="Scanning in progress...", bg=unified_bg_color, fg=unified_fg_color, font=tkFont.Font(size=18))
    scanning_output_label.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

    stop_scanning_button = tk.Button(content_frame, text="Stop Scanning", font=tkFont.Font(size=24), bg=unified_bg_color, fg=unified_fg_color, command=stop_scanning)
    stop_scanning_button.grid(row=2, column=0, padx=10, pady=10, sticky="nsew")

    # Start the airodump-ng command in a separate thread to avoid blocking the GUI
    #threading.Thread(target=run_airodump, args=(monitor_interface,), daemon=True).start()
    thread = threading.Thread(target=run_airodump, args=(monitor_interface,))
    thread.start()   

def run_airodump(interface):
    global scanning_process  # Make sure to define this as global to modify it
    command = ['sudo', 'airodump-ng', interface, '-w', '/tmp/airodump_output', '--output-format', 'csv']
    scanning_process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

def stop_scanning():
    global scanning_process  # Make sure to access the global variable
    if scanning_process:
        scanning_process.terminate()  # This sends SIGTERM, you could also send SIGINT if needed
        scanning_process.wait()       # Wait for the process to terminate
        scanning_process = None       # Reset the global variable
    results_page()  # Proceed to results page

def results_page():
    """Read results from the CSV file and display them as buttons in a 4x5 grid."""
    new_frame(content_frame)
    weight_setup(6, 5)  # Adjust grid weights (rows, columns)
    small_button_font = tkFont.Font(family="Helvetica", size=8, weight="bold")
    unified_title_font = tkFont.Font(family="Helvetica", size=36, weight="bold")

    # Title label
    title_label = tk.Label(content_frame, text="Results", bg=unified_bg_color, fg=unified_fg_color, font=unified_title_font)
    title_label.grid(row=0, column=0, columnspan=5, padx=10, pady=10, sticky="nsew")
    
    # Read results using the read_csv_results function
    results = read_csv_results('/tmp/airodump_output-01.csv')
    
    # Limit to 20 entries and create buttons in a 4x5 grid
    for index, (bssid, essid) in enumerate(results[:20]):
        # Determine row and column positions based on index
        row_position = index // 5 + 1  # Starts at 1 since the title is at row 0
        column_position = index % 5
        
        button_text = f"Target {index + 1}: {essid or 'N/A'} ({bssid})"
        result_button = tk.Button(content_frame, text=button_text, font=small_button_font, bg=unified_bg_color, fg=unified_fg_color, command=lambda b=bssid, e=essid: choose_attack_page(b, e))
        result_button.grid(row=row_position, column=column_position, padx=5, pady=5, sticky="nsew")
    
    # Add a back button spanning all columns
    back_button = tk.Button(content_frame, text="Back", font=unified_title_font, bg=unified_bg_color, fg=unified_fg_color, command=wifi_page)
    back_button.grid(row=5, column=0, columnspan=5, padx=10, pady=10, sticky="nsew")


def read_csv_results(file_path):
    # Read the entire file content
    with open(file_path, 'r', encoding='utf-8') as file:
        data = file.read()
    # Split the data into lines and initialize the list for results
    lines = data.splitlines()
    results = []
    # Start reading the lines
    for line in lines:
        # Ignore empty lines and header rows
        if (line == '') or (line.startswith("Station MAC,")) or (line.startswith("BSSID,")):
            continue

        fields = line.split(',')

        if len(fields) >= 13:
            bssid = fields[0].strip()
            essid = fields[13].strip()
            results.append((bssid, essid))

    return results

def choose_attack_page(bssid, essid):
    """Display a page to choose an attack type for the given target."""
    new_frame(content_frame)
    weight_setup(4, 1)  # Adjust grid weights
    unified_title_font = tkFont.Font(family="Helvetica", size=36, weight="bold")
    unified_button_font = tkFont.Font(family="Helvetica", size=24, weight="bold")

    # Title label showing the target information
    title_text = f"Choose Attack for {essid or 'N/A'} ({bssid})"
    title_label = tk.Label(content_frame, text=title_text, bg=unified_bg_color, fg=unified_fg_color, font=unified_title_font)
    title_label.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

    # Deauthentication attack button
    deauth_button = tk.Button(content_frame, text="Deauthentication Attack", font=unified_button_font, bg=unified_bg_color, fg=unified_fg_color)
    deauth_button.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

    # Password cracking attack button
    crack_button = tk.Button(content_frame, text="Password Cracking Attack", font=unified_button_font, bg=unified_bg_color, fg=unified_fg_color)
    crack_button.grid(row=2, column=0, padx=10, pady=10, sticky="nsew")

    # Back button to return to results page
    back_button = tk.Button(content_frame, text="Back", font=unified_button_font, bg=unified_bg_color, fg=unified_fg_color, command=results_page)
    back_button.grid(row=3, column=0, padx=10, pady=10, sticky="nsew")
def deauth_page():
    # Page and Font Setup.
    new_frame(content_frame)
    weight_setup(4, 1)
    unified_button_font = tkFont.Font(family="Helvetica", size=36, weight="bold")
    unified_title_font = tkFont.Font(family="Helvetica", size=48, weight="bold")
    
    # Title label
    title_label = tk.Label(content_frame, text="Select a Target", bg=unified_bg_color, fg=unified_fg_color, font=unified_title_font)
    title_label.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

    # Text box to display targets
    text_font = tkFont.Font(family="Helvetica", size=16)
    text_box = tk.Text(content_frame, font=text_font, height=10, width=50, bg=unified_bg_color, fg=unified_fg_color)
    text_box.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
    text_box.insert(tk.END, "Target 1: Example Network\nTarget 2: Another Network\nTarget 3: More Networks\n")  # Example targets

    # Entry box for number input
    entry_font = tkFont.Font(family="Helvetica", size=20)
    number_entry = tk.Entry(content_frame, font=entry_font, justify='center',  bg=unified_bg_color, fg=unified_fg_color)
    number_entry.grid(row=3, column=0, padx=10, pady=10, sticky="nsew")

    # Number pad buttons
    pad_frame = tk.Frame(content_frame, bg=unified_bg_color)
    pad_frame.grid(row=2, column=0, padx=10, pady=10, sticky="nsew")
    btn_texts = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "0", "Clear"]
    r = 0
    c = 0
    for btn_text in btn_texts:
        button = tk.Button(pad_frame, text=btn_text, font=entry_font, bg=unified_bg_color, fg=unified_fg_color,
                           command=lambda b=btn_text: number_pad_action(b, number_entry))
        button.grid(row=r, column=c, padx=5, pady=5, sticky="nsew")
        c += 1
        if c > 2:
            c = 0
            r += 1

    # Configure pad_frame grid weights
    for i in range(4):
        pad_frame.grid_rowconfigure(i, weight=1)
    for i in range(3):
        pad_frame.grid_columnconfigure(i, weight=1)

    # Back button
    
    back_button = tk.Button(content_frame, text="Back", font=unified_button_font, bg=unified_bg_color, fg=unified_fg_color, command=wifi_page)
    back_button.grid(row=4, column=0, padx=10, pady=10, sticky="nsew")

def number_pad_action(value, entry_widget):
    if value == "Clear":
        entry_widget.delete(0, tk.END)
    else:
        entry_widget.insert(tk.END, value)

def password_crack():
    print("Attempting password crack...")  # Placeholder for actual function

def beacon_flooding():
    print("Flooding with beacon frames...")  # Placeholder for actual function

def evil_twin():
    print("Setting up Evil Twin...")  # Placeholder for actual function

def rfid_page():
    # Page and Font Setup.
    new_frame(content_frame)
    weight_setup(3, 4)
    unified_button_font = tkFont.Font(family="Helvetica", size=36, weight="bold")
    unified_title_font = tkFont.Font(family="Helvetica", size=48, weight="bold")

    # Title label
    title_label = tk.Label(content_frame, text="Select Operation", bg=unified_bg_color, fg=unified_fg_color, font=unified_title_font)
    title_label.grid(row=0, column=0, columnspan=4, padx=10, pady=10, sticky="nsew")

    # Create Read and Write buttons
    read_button = tk.Button(content_frame, text="Read", font=unified_button_font, bg=unified_bg_color, fg=unified_fg_color, command=read_card)
    read_button.grid(row=1, column=0, columnspan=2,padx=10, pady=10, sticky="nsew")

    write_button = tk.Button(content_frame, text="Write", font=unified_button_font, bg=unified_bg_color, fg=unified_fg_color, command=write_card)
    write_button.grid(row=1, column=2, columnspan=2,padx=10, pady=10, sticky="nsew")

    # Back button
    return_button = tk.Button(content_frame, text="Back", font=unified_button_font, bg=unified_bg_color, fg=unified_fg_color, command=main_page)
    return_button.grid(row=2, column=0, columnspan=4, padx=10,pady=10, sticky="nsew")

def read_card():
    new_frame(content_frame)

def write_card():
    new_frame(content_frame)

def sub_ghz_page():
    # Page and Font Setup.
    new_frame(content_frame)
    weight_setup(8,3)
    unified_button_font = tkFont.Font(family="Helvetica", size=36, weight="bold")
    unified_title_font = tkFont.Font(family="Helvetica", size=48, weight="bold")

    # Title label
    title_label = tk.Label(content_frame, text="Please Specify the Frequency: ", bg=unified_bg_color, fg=unified_fg_color, font=unified_title_font)
    title_label.grid(row=0, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")


    # Create a font object for dynamic scaling
    # Adjust size as needed
    entry_font = tkFont.Font(family="Helvetica", size=40, weight="bold")  # For the entry widget

    # Frequency entry at the top
    global freq_entry
    freq_entry = tk.Entry(content_frame, width=10, font=entry_font, bg=unified_bg_color, fg=unified_fg_color)
    freq_entry.grid(row=0, column=2, pady=10, sticky='nsew')
    freq_entry.config(justify="center")  # Center horizontally


    # Number pad buttons
    number_pad_values = [
        ('1', 0, 0), ('2', 0, 1), ('3', 0, 2),
        ('4', 1, 0), ('5', 1, 1), ('6', 1, 2),
        ('7', 2, 0), ('8', 2, 1), ('9', 2, 2),
        ('0', 3, 1), ('.', 3, 0), ('Clear', 3, 2)
    ]

    for (text, r, c) in number_pad_values:
        command = clear_freq if text == 'Clear' else lambda t=text: add_to_freq(t)
        btn = tk.Button(content_frame, text=text, font=unified_button_font, bg=unified_bg_color, fg=unified_fg_color, command=command)
        btn.grid(row=r + 1, column=c, padx=10, pady=10, sticky='nsew')

    # Capture and Transmit buttons below the number pad
    capture_button = tk.Button(content_frame, text="Capture", font=unified_button_font, bg=unified_bg_color, fg=unified_fg_color, command=capture_sub_ghz)
    capture_button.grid(row=5, column=0, columnspan=3, pady=10, sticky='nsew')
    transmit_button = tk.Button(content_frame, text="Transmit", font=unified_button_font, bg=unified_bg_color, fg=unified_fg_color, command=transmit_sub_ghz)
    transmit_button.grid(row=6, column=0, columnspan=3, pady=10, sticky='nsew')

    # Back button
    return_button = tk.Button(content_frame, text="Back", font=unified_button_font, bg=unified_bg_color, fg=unified_fg_color, command=main_page)
    return_button.grid(row=7, column=0, columnspan=3, pady=10, sticky='nsew')

def add_to_freq(char):
    freq_entry.insert(tk.END, char)

def clear_freq():
    freq_entry.delete(0, tk.END)

def new_frame(frame):
    # Clears all widgets from the given frame
    for widget in frame.winfo_children():
        widget.destroy()

#Implement getting the pid of the hackrf_transfer and killing it once u press back.
def capture_sub_ghz():
    global freq_entry
    if freq_entry is not None:
        freq = freq_entry.get()
        
        # Page and Font Setup.
        new_frame(content_frame)
        weight_setup(3,3)
        unified_button_font = tkFont.Font(family="Helvetica", size=36, weight="bold")
        unified_title_font = tkFont.Font(family="Helvetica", size=48, weight="bold")

        # Title label
        title_label = tk.Label(content_frame, text="Listening to Sub-GHz Frequency", bg=unified_bg_color, fg=unified_fg_color, font=unified_title_font)
        title_label.grid(row=0, column=0, columnspan=3, padx=10, pady=10, sticky="nsew")

        # Message label
        message_font = tkFont.Font(family="Helvetica", size=24, weight="normal")
        message_label = tk.Label(content_frame, text=f"Listening on {freq} MHz", bg=unified_bg_color, fg=unified_fg_color, font=unified_button_font)
        message_label.grid(row=1, column=0, columnspan=3, padx=10, pady=10, sticky="nsew")

        # Back button
        return_button = tk.Button(content_frame, text="Back", font=unified_button_font, bg=unified_bg_color, fg=unified_fg_color, command=sub_ghz_page)
        return_button.grid(row=2, column=0, columnspan=3, pady=10, sticky='nsew')

        thread = threading.Thread(target=receive_signal, args=(create_file(freq), int(float(freq) * 1000000), 2000000, 16, 14))
        thread.start()    
    else:
        messagebox.showerror("Error", "Frequency entry not found")

def transmit_sub_ghz():
    # Page and Font Setup
    new_frame(content_frame)
    weight_setup(4, 3)
    unified_button_font = tkFont.Font(family="Helvetica", size=36, weight="bold")
    unified_title_font = tkFont.Font(family="Helvetica", size=48, weight="bold")

    # Title label
    title_label = tk.Label(content_frame, text="Select signal", bg=unified_bg_color, fg=unified_fg_color, font=unified_title_font)
    title_label.grid(row=0, column=0, columnspan=3, padx=10, pady=10, sticky="nsew")

    # List signals from directory and create buttons
    directory = "/home/kali/signals/"
    files = [f for f in os.listdir(directory) if f.endswith('.complex16s')]
    files.sort()

    for index, filename in enumerate(files):
        file_path = os.path.join(directory, filename)
        # Extract frequency from the file name
        freq = filename.split('_')[2].replace('.complex16s', '')

        # Button to transmit signal
        btn = tk.Button(content_frame, text=filename, font=unified_button_font, bg=unified_bg_color, fg=unified_fg_color,
                        command=lambda fp=file_path, fr=freq: threading.Thread(
                            target=transmit_signal, args=(fp, int(float(fr) * 1000000), 2000000, 1, 23)).start())
        btn.grid(row=1 + index // 3, column=index % 3, padx=5, pady=5, sticky="nsew")

    # Back button
    return_button = tk.Button(content_frame, text="Back", font=unified_button_font, bg=unified_bg_color, fg=unified_fg_color, command=sub_ghz_page)
    return_button.grid(row=4, column=0, columnspan=3, pady=10, sticky='nsew')




root = tk.Tk()
root.title("Wireless Pentesting Toolkit")
root.attributes('-fullscreen', True)  # Fullscreen mode

# Main content frame
content_frame = tk.Frame(root, bg="#282828")
content_frame.pack(fill='both', expand=True)

# Control frame for exit button
exit_control_frame = tk.Frame(root, bg="#282828")
exit_control_frame.pack(side='bottom', fill='x')

# Exit button
exit_button = tk.Button(exit_control_frame, text="Exit", command=root.quit, bg='red', fg='white')
exit_button.pack(side='left', fill='x')

# Bind the escape key to exit
root.bind('<Escape>', lambda e: root.quit())

# Display main page
main_page()

root.mainloop()