import sys
import requests
from pynput import keyboard
from urllib3.exceptions import MaxRetryError, NewConnectionError


def key_press(key):
    if key == keyboard.Key.esc:
        exit(0)
        return False  # stop listener


if __name__ == '__main__':
    numClass = int(input("Number of Class: "))
    classLabels = [0] * numClass
    classNames = [""] * numClass
    classDict = {}
    for i in range(1, numClass + 1):
        classLabels[i - 1] = (i % 10) if (i < 11) else (ord('a') + i - 11)
        classNames[i - 1] = input(str(classLabels[i - 1] if (i < 11) else chr(classLabels[i - 1])) + ") ")
        classDict[str(classLabels[i - 1])] = str(classNames[i - 1])

    listener = keyboard.Listener(on_press=key_press)
    listener.start()  # start to listen on a separate thread

    print("Type class-label (1 to ", classLabels[-1],
          ') followed by `y` & press ENTER to confirm action.\nPress `ESC` or type `END` to Exit.')
    while True:
        label = input("Next-action's class-label: ")

        if label == 'END':
            exit(0)

        try:
            intLabel = int(label[0])
        except ValueError:
            intLabel = ord(label[0])
        except IndexError:
            intLabel = -1

        # Discard any unconfirmed / invalid input
        if len(label) != 2 \
                or (label[1] != 'y' and label[1] != 'Y') \
                or (intLabel < 0
                    or (numClass < 10 and (intLabel <= 0 or intLabel > numClass))
                    or (numClass == 10 and (intLabel < 0 or intLabel > 9))
                    or (numClass > 10 and (intLabel < 0 or 9 < intLabel < ord('a')))):
            print("Invalid Input! Ignoring ...\n")
            continue
        className = classDict[label[0]]
        # put CURL request: "curl --location --request POST \
        #                   'http://<PI_HOSTNAME>.local:8080/annotation?value=<ACTION_OR_MEASUREMENT_VALUE>'"
        params = (('value', className),)
        try:
            response = requests.post('http://0.0.0.0:8080/annotation', params=params)  # better way to specify the host?
        except (ConnectionError, ConnectionRefusedError, NewConnectionError, MaxRetryError, Exception) as err:
            response = None
            sys.stderr.write(str(err) + "\n")
            pass
        if response is not None and response.status_code == 200:
            print("Successfully posted action to the CSI-Pi service. Collecting data for action `", className, "`...\n")
        else:
            sys.stderr.write("Bad Service!\nResponse Code: "
                             + str(response.status_code if response is not None else "NULL")
                             + "\nResponse: " + str(response.text if response is not None else "NULL\n"))
