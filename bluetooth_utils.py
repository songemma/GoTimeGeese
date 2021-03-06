import bluetooth
import threading

_SERVER_UUID = "2cafd5f6-ea6c-44c4-99bf-5629bdbcab1d"
_SERVER_NAME = "Go Time Geese"
_SERVER_BACKLOG = 10
_SERVER_GAME_FULL_RESPONSE = 255

_CLIENT_ACTION_PAUSE = 200

DIR_UP = 1
DIR_DOWN = 2
DIR_LEFT = 3
DIR_RIGHT = 4
DIR_NONE = 5


class _AtomicBool:
    """Internally used to manage the paused/resumed state in a thread-safe manner."""
    def __init__(self, value=False):
        self._lock = threading.Lock()
        self._value = value

    def set(self, value: bool):
        with self._lock:
            self._value = value

    def get(self) -> bool:
        return self._value

    def switch(self) -> bool:
        with self._lock:
            new_value = not self._value
            self._value = new_value
            return new_value


class _DeviceArray:
    """Internally used to manage device information in a thread-safe manner."""
    def __init__(self, n: int):
        self._length = n
        self._devices = 0
        self._arr = ["" for _ in range(n)]
        self._lock = threading.Lock()

    def number_of_devices(self) -> int:
        return self._devices

    def add_device(self, mac_address: str) -> int:
        with self._lock:
            for i in range(self._length):
                if self._arr[i] == "":
                    self._arr[i] = mac_address
                    self._devices += 1
                    return i
        return -1

    def remove_device(self, index: int) -> bool:
        with self._lock:
            if self._arr[index] != "":
                self._arr[index] = ""
                self._devices -= 1
                return True
        return False


# Global variables used to deliver the functionality advertised by the module.
# Declared here to maintain compatibility with Python 3.7.
_devices: _DeviceArray
_serverSocket: bluetooth.BluetoothSocket
_playerDirs: list
_paused: _AtomicBool


class _PlayerThread(threading.Thread):
    """In charge of receiving bytes from the supplied socket and appropriately
    updating the relevant playerDir field. If player == -1, the thread will
    simply wait for the client to disconnect and close the socket."""
    def __init__(self, player, socket):
        super().__init__()
        self._player = player
        self._socket = socket

    def run(self):
        global _devices, _playerDirs, _paused

        # We wrap the logic for receiving data from the client in try-except so
        # that the thread gracefully terminates when _serverSocket is closed.
        try:
            while True:
                data = self._socket.recv(1)
                if not data:
                    break
                if self._player != -1:
                    user_in = data[0]
                    if user_in == _CLIENT_ACTION_PAUSE:
                        _paused.switch()
                    else:
                        _playerDirs[self._player] = user_in
        except OSError:
            pass

        # The connection has ended. Reset the player's direction and remove the
        # device from _devices. Then, close the socket.
        if self._player != -1:
            _playerDirs[self._player] = DIR_NONE
            _devices.remove_device(self._player)
        self._socket.close()


class _ConnectionThread(threading.Thread):
    """The main connection thread that indefinitely accepts oncoming connections
    and sends the appropriate response before handing the client socket over to
    a _PlayerThread."""
    def __init__(self, socket):
        super().__init__()
        self._socket = socket

    def run(self):
        global _devices
        while True:
            # Accept a connection from an oncoming client. If this fails, the socket is closed,
            # and we must gracefully exit the loop.
            try:
                client_socket, client_info = self._socket.accept()
            except OSError:
                self._socket.close()
                break

            # We wrap the code for sending the appropriate response to the client within a
            # try-except in case the client crashes or closes the connection.
            try:
                index = _devices.add_device(client_info[0])
                if index == -1:
                    client_socket.send(bytes([_SERVER_GAME_FULL_RESPONSE]))
                else:
                    client_socket.send(bytes([index + 1]))
                _PlayerThread(index, client_socket).start()
            except OSError:
                client_socket.close()


def start(num_players: int) -> None:
    """Starts the bluetooth_utils module. Call this function after a stop() call or at the
    beginning of the program to start allowing players to connect to the game. You MUST
    call this function before calling any of the other functions available in the module."""
    global _devices, _serverSocket, _playerDirs, _paused

    # Call stop() first to fool-proof against repeated calls.
    stop()

    # Prepare the server socket and advertise with _SERVER_UUID.
    _serverSocket = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
    _serverSocket.bind(("", bluetooth.PORT_ANY))
    _serverSocket.listen(_SERVER_BACKLOG)
    bluetooth.advertise_service(_serverSocket, _SERVER_NAME,
                                service_classes=[_SERVER_UUID, bluetooth.SERIAL_PORT_CLASS],
                                profiles=[bluetooth.SERIAL_PORT_PROFILE],
                                service_id=_SERVER_UUID)

    # Initialize the other globals.
    _devices = _DeviceArray(num_players)
    _playerDirs = [DIR_NONE for _ in range(num_players)]
    _paused = _AtomicBool()

    # Start a _ConnectionThread to begin accepting client connections.
    _ConnectionThread(_serverSocket).start()


def number_of_devices() -> int:
    """Returns the number of devices that are currently connected to the game.
    The returned value will be between 0 and the total number of players."""
    global _devices
    return _devices.number_of_devices()


def get_paused() -> bool:
    """Returns True if one of the players has paused the game."""
    global _paused
    return _paused.get()


def clear_paused_status() -> None:
    """Resets the paused status of the game to False. Useful to call after
    all the players are joined so that the game doesn't start paused if someone
    had accidentally touched pause on their controller."""
    global _paused
    _paused.set(False)


def get_direction(player: int) -> int:
    """Returns the directional input currently supplied by the specified player.
    The returned value is one of DIR_UP, DIR_DOWN, DIR_LEFT, DIR_RIGHT, DIR_NONE.
    Note: Player numbering starts from 0."""
    global _playerDirs
    return _playerDirs[player]


def stop() -> None:
    """Stops the bluetooth_utils module and cleans up system resources. After you
    call this function, you must not call any of the other functions in the module
    unless you start it again. Note: This function is idempotent."""
    global _devices, _serverSocket, _playerDirs, _paused
    try:
        _serverSocket.close()
        del _serverSocket
        del _devices
        del _playerDirs
        del _paused
    except NameError:
        pass
