#!/usr/bin/python3
import subprocess
import sys


choice = input("1. Wi-Fi\n2. Sub-GHz\n3. RFID\nTechnology:  ")
choice = int(choice)

##Wi-Fi Implementation
if (choice == 1):
	print("\nWi-Fi Options:\n1. Evil twin\n2. De-Auth\n3. Probe Request Flooding")




##SubGHz Implementation
elif (choice == 2):
	print("\n1. Receive\n2. Transmit")
	def receive_signal(output_file, frequency, sample_rate, if_gain, gain):
	    command = [
	        'hackrf_transfer',
	        '-r', output_file,       # Output file for the received data
	        '-f', str(frequency),    # Frequency in Hz
	        '-s', str(sample_rate),  # Sample rate in Hz
	        '-l', str(if_gain),      # IF gain
	        '-g', str(gain)          # RX VGA gain
	    ]
	    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	    stdout, stderr = process.communicate()
	    if process.returncode != 0:
	        print("Error in receive signal:", stderr.decode())
	    else:
	        print("Receive signal success:", stdout.decode())

	def transmit_signal(input_file, frequency, sample_rate, antenna_gain, tx_gain):
	    command = [
	        'hackrf_transfer',
	        '-t', input_file,        # Input file for the data to transmit
	        '-f', str(frequency),    # Frequency in Hz
	        '-s', str(sample_rate),  # Sample rate in Hz
	        '-a', str(antenna_gain), # Antenna power amplifier (0 or 1)
	        '-x', str(tx_gain)       # TX VGA gain
	    ]
	    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	    stdout, stderr = process.communicate()
	    if process.returncode != 0:
	        print("Error in transmit signal:", stderr.decode())
	    else:
	        print("Transmit signal success:", stdout.decode())

	if __name__ == "__main__":
	    if len(sys.argv) < 2:
	        print("Usage: python hackrf_script.py mode [args]")
	        sys.exit(1)

	    mode = sys.argv[1]
	    if mode == "receive":
	        if len(sys.argv) != 7:
	            print("Receive mode usage: python hackrf_script.py receive output_file frequency sample_rate if_gain gain")
	            sys.exit(1)
	        _, _, output_file, frequency, sample_rate, if_gain, gain = sys.argv
	        receive_signal(output_file, frequency, sample_rate, if_gain, gain)
	    elif mode == "transmit":
	        if len(sys.argv) != 7:
	            print("Transmit mode usage: python hackrf_script.py transmit input_file frequency sample_rate antenna_gain tx_gain")
	            sys.exit(1)
	        _, _, input_file, frequency, sample_rate, antenna_gain, tx_gain = sys.argv
	        transmit_signal(input_file, frequency, sample_rate, antenna_gain, tx_gain)
	    else:
	        print("Invalid mode. Use 'receive' or 'transmit'.")
	        sys.exit(1)



##RFID Implementation
elif (choice == 3):
	print("\n1. Read\n2. Write") 





else:
	print("Invalid Option")