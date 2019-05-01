# Swarmbot-simulator
A simulation of robots moving using swarm algorithms

# Instalation to use program needs cairocffi library


link to installation: https://sourceforge.net/projects/gtk-win/
install pycario from wheel: https://www.lfd.uci.edu/~gohlke/pythonlibs/#pycairo
pip install "C:\Users\splmcu\Downloads\pycairo-1.18.0-cp37-cp37m-win32.whl"

pip install psutil

install shapely from wheel: https://www.lfd.uci.edu/~gohlke/pythonlibs/#shapely
pip install "C:\Users\Nexon\Downloads\Shapely-1.6.4.post1-cp37-cp37m-win_amd64.whl"

add mosquitto.exe to path variable
setx path "%path%;E:\mosquitto"




pip install simple-pid


--------------------------- outdated ------------------------------  
Installing cairo on Windows

cairocffi needs a libcairo-2.dll file in a directory that is listed in the PATH environment variable.

Alexander Shaduri’s GTK+ installer works. (Make sure to leave the Set up PATH environment variable checkbox checked.)
Pycairo on Windows is sometimes compiled statically against cairo and may not provide a .dll file that cairocffi can use.  

pip install slycot
pip install control

-------------------------------------------------------------------