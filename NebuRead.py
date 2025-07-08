"""
Python code to read serial data from USSolid USS-DBS28-50 Analytical scale.
Time in sec since program start and current scale weight in scale units displayed.
Also saved to file data_log.csv.

Change sampling rate with last argument to animation.FuncAnimation. 
 - Actual sample rate is about 200 ms slower than setpoint.

 [7/8/25]: Ported code for Ohouse scale.  Max baud = 9600.
 Fixed bug where negative sign was not captured.  Need to reflect this back 
 to main branch for US Solid scale.

"""
import serial
import csv
import time
import re
from datetime import datetime
import matplotlib.pyplot as plt
import matplotlib.animation as animation

# Serial port configuration
PORT = 'COM9'
BAUDRATE = 9600
TIMEOUT = 1

# CSV output file
CSV_FILENAME = 'nebuData_'
timestamp = datetime.now().strftime("%d%b%y_%I_%M%p").lower()
CSV_FILENAME += timestamp + ".csv"

# Initialize data lists
timestamps = []
values = []

start_time = time.time()

def extract_number(text):
    """Extracts the first float or int from a string."""
    pattern = r'([+-])\s*(\d*\.?\d+(?:[eE][+-]?\d+)?)'
    match = re.sub(pattern, r'\1\2', text)
    return float(match) if match else None

def read_serial_line(ser):
    """Flushes input buffer and reads a line from serial."""
    try:
        ser.reset_input_buffer()  # FLUSH the buffer
        line = ser.readline().decode(errors='ignore').strip()
#        line = ser.readline().decode(errors='ignore').strip() #read 2x to clear potential garbage line'
        if line:
            value = extract_number(line)
            if value is not None:
                elapsed = time.time() - start_time
                value = round(value, 2)
                timestamps.append(elapsed)
                values.append(value)
                with open(CSV_FILENAME, mode='a', newline='') as csvfile:
                    writer = csv.writer(csvfile)
                    writer.writerow([f"{elapsed:.2f}", f"{value:.2f}"])
                print(f"{elapsed:.2f}, {value:.2f}")
            else:
                print(f"Skipped non-numeric: {line}")
    except Exception as e:
        print(f"Error reading line: {e}")

def update_plot(frame):
    read_serial_line(ser)
    ax.clear()
    ax.plot(timestamps, values, marker='o',markersize=3,linewidth=1)
    ax.set_title('Real-Time Data Plot')
    ax.set_xlabel('Time (s)')
    ax.set_ylabel('Value')
    ax.grid(True)

# Set up serial connection
try:
    ser = serial.Serial(PORT, BAUDRATE, timeout=TIMEOUT)
    print(f"Connected to {PORT} at {BAUDRATE} bps.")
except serial.SerialException as e:
    print(f"Could not open {PORT}: {e}")
    exit()

# Initialize CSV with header
with open(CSV_FILENAME, mode='w', newline='') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(['Time (s)', 'Value'])

# Set up real-time plot
fig, ax = plt.subplots()
ani = animation.FuncAnimation(fig, update_plot, interval=200)  #  interval timing
plt.tight_layout()

try:
    plt.show()
except KeyboardInterrupt:
    print("\nPlot closed by user.")
finally:
    ser.close()
    print("Serial port closed.")
