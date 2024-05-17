############################################### RFID Page #####################################

def rfid_page():
    # Page and Font Setup.
    new_frame(content_frame)
    weight_setup(4, 4)
    unified_button_font = tkFont.Font(family="Helvetica", size=36, weight="bold")
    unified_title_font = tkFont.Font(family="Helvetica", size=48, weight="bold")

    # Title label
    title_label = tk.Label(content_frame, text="Select Operation", bg=unified_bg_color, fg=unified_fg_color, font=unified_title_font)
    title_label.grid(row=0, column=0, columnspan=4, padx=10, pady=10, sticky="nsew")

    # Create Read, Write, and Simulate buttons
    read_button = tk.Button(content_frame, text="Read", font=unified_button_font, bg=unified_bg_color, fg=unified_fg_color, command=read_card)
    read_button.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

    write_button = tk.Button(content_frame, text="Write", font=unified_button_font, bg=unified_bg_color, fg=unified_fg_color, command=write_card)
    write_button.grid(row=1, column=1, padx=10, pady=10, sticky="nsew")
    
    simulate_button = tk.Button(content_frame, text="Simulate", font=unified_button_font, bg=unified_bg_color, fg=unified_fg_color, command=simulate_card)
    simulate_button.grid(row=1, column=2, padx=10, pady=10, sticky="nsew")

    # Back button
    return_button = tk.Button(content_frame, text="Back", font=unified_button_font, bg=unified_bg_color, fg=unified_fg_color, command=main_page)
    return_button.grid(row=2, column=0, columnspan=4, padx=10,pady=10, sticky="nsew")


def read_card():
    new_frame(content_frame)
    loading_label = tk.Label(content_frame, text="Scanning in progress...", bg=unified_bg_color, fg=unified_fg_color, font=tkFont.Font(size=18))
    loading_label.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
    
    # Back button
    back_button = tk.Button(content_frame, text="Back", bg=unified_bg_color, fg=unified_fg_color, command=rfid_page)
    back_button.grid(row=2, column=0, columnspan=4, padx=10, pady=10, sticky="nsew")
    
    content_frame.update()
    
    # Execute pm3 -c 'auto' command
    result = subprocess.run(["pm3", "-c", "auto"], capture_output=True, text=True)
    output = result.stdout
    
    # Check if a valid ISO 14443-A tag is found
    if "[+] Valid ISO 14443-A tag found" in output:
        # Extracting UID
        uid = None
        for line in output.split("\n"):
            if line.startswith("[+]  UID:"):
                uid = line.split(":")[1].replace(" ", "").strip()
                break
        
        if uid:
            keys_file = "hf-mf-{}-key.bin".format(uid)
            
            # Check if keys file already exists
            if os.path.exists(keys_file):
                loading_label.config(text="Card already saved.")
            else:
                loading_label.config(text="Valid Mifare card found, dumping its content...")
                content_frame.update()
                
                # Dump keys
                subprocess.run(["pm3", "-c", "hf mf chk --dump"], capture_output=True, text=True)
                
                # Generate filename for card content
                saved_cards = [file for file in os.listdir() if file.startswith("card") and file.endswith(".bin")]
                
                if len(saved_cards) >= 8:
                    # Remove the first card to overwrite
                    os.remove(saved_cards[0])
                
                i = 1
                while os.path.exists("card{}.bin".format(i)):
                    i += 1
                content_file = "card{}.bin".format(i)
                
                subprocess.run(["pm3", "-c", "hf mf dump --keys {} -f {}".format(keys_file, content_file)], capture_output=True, text=True)
                
                loading_label.config(text="Card{} saved".format(i))
        
    else:
        loading_label.config(text="No card found")


def write_card():
    new_frame(content_frame)
    
    # Back button
    back_button = tk.Button(content_frame, text="Back", bg=unified_bg_color, fg=unified_fg_color, command=rfid_page)
    back_button.grid(row=2, column=0, columnspan=4, padx=10, pady=10, sticky="nsew")
    
    content_frame.update()
    
    # Get a list of saved cards
    saved_cards = [file for file in os.listdir() if file.startswith("card") and file.endswith(".bin")]
    
    if saved_cards:
        for i, card in enumerate(saved_cards):
            card_button = tk.Button(content_frame, text=card, bg=unified_bg_color, fg=unified_fg_color, command=lambda c=card: write_selected_card(c))
            card_button.grid(row=i+1, column=0, columnspan=4, padx=10, pady=10, sticky="nsew")
    else:
        no_cards_label = tk.Label(content_frame, text="No cards saved yet.", bg=unified_bg_color, fg=unified_fg_color, font=tkFont.Font(size=18))
        no_cards_label.grid(row=1, column=0, columnspan=4, padx=10, pady=10, sticky="nsew")

def write_selected_card(card):
    new_frame(content_frame)
    write_label = tk.Label(content_frame, text="Writing card...", bg=unified_bg_color, fg=unified_fg_color, font=tkFont.Font(size=18))
    write_label.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
    
    # Back button
    back_button = tk.Button(content_frame, text="Back", bg=unified_bg_color, fg=unified_fg_color, command=rfid_page)
    back_button.grid(row=2, column=0, columnspan=4, padx=10, pady=10, sticky="nsew")
    
    content_frame.update()
    
    # Execute pm3 -c 'hf mf cload card{num}.eml' command
    result = subprocess.run(["pm3", "-c", "hf mf cload {}".format(card[:-4] + ".eml")], capture_output=True, text=True)
    print("hf mf cload {}".format(card[:-4] + ".eml"))
    write_label.config(text="Writing finished")

def simulate_card():
    new_frame(content_frame)
    
    # Back button
    back_button = tk.Button(content_frame, text="Back", bg=unified_bg_color, fg=unified_fg_color, command=rfid_page)
    back_button.grid(row=2, column=0, columnspan=4, padx=10, pady=10, sticky="nsew")
    
    content_frame.update()
    
    # Get a list of saved cards
    saved_cards = [file for file in os.listdir() if file.startswith("card") and file.endswith(".bin")]
    
    if saved_cards:
        for i, card in enumerate(saved_cards):
            card_button = tk.Button(content_frame, text=card, bg=unified_bg_color, fg=unified_fg_color, command=lambda c=card: simulate_selected_card(c))
            card_button.grid(row=i+1, column=0, columnspan=4, padx=10, pady=10, sticky="nsew")
    else:
        no_cards_label = tk.Label(content_frame, text="No cards saved yet.", bg=unified_bg_color, fg=unified_fg_color, font=tkFont.Font(size=18))
        no_cards_label.grid(row=1, column=0, columnspan=4, padx=10, pady=10, sticky="nsew")

def simulate_selected_card(card):
    new_frame(content_frame)
    simulate_label = tk.Label(content_frame, text="Simulating card...", bg=unified_bg_color, fg=unified_fg_color, font=tkFont.Font(size=18))
    simulate_label.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
    
    # Back button
    back_button = tk.Button(content_frame, text="Back", bg=unified_bg_color, fg=unified_fg_color, command=rfid_page)
    back_button.grid(row=2, column=0, columnspan=4, padx=10, pady=10, sticky="nsew")
    
    content_frame.update()
    
    # Load the card into the device memory
    result_load = subprocess.run(["pm3", "-c", "hf mf eload -f {}".format(card)], capture_output=True, text=True)
    
    # Simulate the card
    result_simulate = subprocess.run(["pm3", "-c", "hf mf sim --1k"], capture_output=True, text=True)
    
    simulate_label.config(text="Simulation finished")


