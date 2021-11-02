import bluetooth_utils
import time

if input("Close test? ") == 'y':
    bluetooth_utils.start(1)
    time.sleep(1)
    bluetooth_utils.stop()
    print("Close test complete.\n")

num_players = int(input("Number of Players: "))
bluetooth_utils.start(num_players)
print("Here we go.")
currently_displayed = ""
while True:
    num_connected = bluetooth_utils.number_of_devices()
    to_display = f"Connected: {num_connected}/{num_players}   Input: "
    for player in range(num_players):
        to_display += f"({player + 1}, {bluetooth_utils.get_direction(player)}) "
    if currently_displayed != to_display:
        currently_displayed = to_display
        print('\r', to_display, (' ' * 10), end='')

