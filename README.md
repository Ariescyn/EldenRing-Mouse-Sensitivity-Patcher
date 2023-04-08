# EldenRing-Mouse-Sensitivity-Patcher
Increase your mouse movement speed beyond allowed values


## How to use
- Select "Change Directory" and set it to the path of your game save directory.
- This is usually something like C:\Users\{YOUR_USERNAME}\AppData\Roaming\EldenRing\76543210987654321
- Enter a speed value. Normal range is 1-10, but you can now go as high as 99.
- Click "Patch" and launch the game!

### Note:
When you're in-game and go to system settings, if you visit the tab that shows your mouse sensitivity option, it will reset the changes. Just make sure to avoid that menu while your playing, otherwise you will have to re-patch it.

#### Windows
[Download Latest Release](https://github.com/Ariescyn/EldenRing-Save-Manager/releases/latest)

#### Linux / Proton / SteamDeck

Dependencies
```
python3 -m pip install Pillow
```
Fedora/DNF for 'ImageTk' from 'PIL'
```
sudo dnf install python3-pillow-tk.x86_64 python3-pillow.x86_64
```
Run
```
python3 main.py
```

Compile to EXE with Pyinstaller
```
pyinstaller --onefile --windowed --icon=./data/icon.ico ./main.py
```
