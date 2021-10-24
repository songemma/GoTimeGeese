import bluetooth

# Set up a server-type BluetoothSocket.
server_socket = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
server_socket.bind(("", bluetooth.PORT_ANY))
server_socket.listen(1)

# Advertise the server.
MY_UUID = "2cafd5f6-ea6c-44c4-99bf-5629bdbcab1d"
bluetooth.advertise_service(server_socket, "My Lovely Server",
                            service_classes=[MY_UUID, bluetooth.SERIAL_PORT_CLASS],
                            profiles=[bluetooth.SERIAL_PORT_PROFILE],
                            service_id=MY_UUID)

# Connect to the client device.
print(f"Awaiting connection...")
client_socket, client_info = server_socket.accept()
print(f"Accepted connection!")

# Depending on user input, accept the client into the game or indicate that the game is full.
user_in = input("Let them join the game? ")
if user_in in ["y", "Y"]:
    client_socket.send(bytes([1]))
else:
    client_socket.send(bytes([255]))

try:
    while True:
        data = client_socket.recv(1)
        if not data:
            break
        print(data)
except OSError as err:
    print("Error:", err)

# Close the connection.
print("Disconnected.")
client_socket.close()
server_socket.close()
print("All done!")
