# Use this code to scan Digikey Bar Codes and store the data in a text file with ; separated fields
# Input parameter is the location of the bag with components. Ex "Box 1"
# py adddigikeybarcodedata.py "Box 1"

import msvcrt
import sys
import logging

# Enable or disable debugging. Change to False to disable debug messages.
DEBUG_ENABLED = False

# Configure logging
logging.basicConfig(level=logging.DEBUG if DEBUG_ENABLED else logging.INFO)

def read_valid_locations(filename='component_locations.txt'):
    # Read valid locations from a text file
    with open(filename, 'r') as f:
        locations = [line.strip() for line in f.readlines()]
    logging.debug(f"Read valid locations: {locations}")
    return locations

def read_from_keyboard():
    # Read a byte string from the keyboard
    input_str = b""
    
    while True:
        if msvcrt.kbhit():
            ch = msvcrt.getch()
            if ch == b'\r':  # Check for Enter key
                break
            input_str += ch
    
    logging.debug(f"Received keyboard input: {input_str}")
    return input_str

def extract_substrings(input_str):
    # Extract substrings from a byte string by splitting based on the '\x1d' separator
    substrings = [substr.decode('utf-8') for substr in input_str.split(b'\x1d') if substr]
    logging.debug(f"Extracted substrings: {substrings}")
    return substrings

def append_to_text(substrings, location, filename='output.txt'):
    # Append the extracted substrings to a text file
    if substrings and substrings[0] == "[)>\x1e06":
        # Define prefixes that need to be removed from the substrings
        prefixes_to_remove = {
            1: 'P',   # Part number
            2: '1P',  # MFG Part number
            3: 'K',   # Purchase Order
            4: '1K',  # Sales Order ID
            5: '10K', # Invoice Order
            6: '11K', # Picklist ID
            7: '4L',  # Country of Origin
            8: 'Q',   # Quantity
            9: '11Z',
            10: '12Z',
            11: '13Z'
        }

        for i, prefix in prefixes_to_remove.items():
            if len(substrings) > i and substrings[i].startswith(prefix):
                substrings[i] = substrings[i][len(prefix):]
        
        # Filter out specific substrings that start with '20Z0'
        filtered_substrings = [s for s in substrings[1:] if not s.startswith('20Z0')]

        # Write to the output file
        with open(filename, 'a') as f:
            f.write(location + ';' + ';'.join(filtered_substrings) + '\n')
        logging.debug(f"Appended data to file {filename}")
    else:
        print("Invalid data string. Ignored.")
        logging.debug("Received invalid data string")

def main():
    # Print welcome message
    print("Digikey bar code data parser V1.0")
    print("Press Crtl-C or Type 'exit' and press Enter to exit the program) ")
    # Check command-line arguments
    if len(sys.argv) < 2:
        print("Usage: python adddigikeybarcodedata.py <location> [output_file]")
        sys.exit(1)

    location = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else 'digikey_items.txt'  # Use specified filename or default to 'digikey_items.txt'

    valid_locations = read_valid_locations()

    if location not in valid_locations:
       if location not in valid_locations:
        print(f"Invalid location: '{location}'. Valid locations are {', '.join(valid_locations)}. Exiting.")
        sys.exit(1)
    try:
        while True:
            print("Ready for a new scan:")
            received_str = read_from_keyboard()

            if received_str.lower() == b'exit':
                print("Exiting program.")
                break

            logging.debug(f"Received from keyboard: {received_str.decode('utf-8')}")

            extracted_substrings = extract_substrings(received_str)
            print("Extracted substrings:")
            for i, substring in enumerate(extracted_substrings):
                print(f"{i+1}. {substring}")

            append_to_text(extracted_substrings, location, output_file)  # Pass the output_file as an argument
    except KeyboardInterrupt:
        print("\nCtrl+C detected. Exiting program.")

if __name__ == '__main__':
    main()
