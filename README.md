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

# Instalacja oprogramowania na Intel Edison
Aby przygotować oprogramowanie na przenośnym układzie "Intel Edison", należy najpierw wyczyścić pamięc korzystając z 
programu "flashall.bat". Do pakietu porbranego ze strony intel-developer należy dodatkowo pobrać pliki .dll. Następnie
po pobraniu należy następnie korzystając z programu putty uzyskać komunikacje z komputerem intel edison za pomocą portu
COM. Na systemie operacyjnym Windows uruchamiamy program "menedżer urządzeń". Płytkę "Base block" podłączoną do 
komputera "Intel Edison" do portu OTG podłączamy micro-usb, który następnie podłączamy do komputera. Następnie 
uruchamiamy skrypt flashall.bat i czekamy na zakończenie programu.

Korzystając z programu "Menedżer urządzeń" znajdujemy port "USB Serial Port" zapisujemy numer portu. I po 
uruchomieniu programu Putty wybieramy połączenie przez "Serial Port". W polu "Serial Port" wpisujemy zapisany numer 
portu. W polu "Baud rate" należy wpisać wartość "115200" i uruchomić połączenie z płytką. Po włączeniu terminalu należy 
rozpocząć konfiguracje "Intel Edison"

Pierwszym krokiem jest konfiguracja Wi-Fi poprzez polecenie:

    configure_edison --setup

Następnie należy wpisać hasło, które może być dowolne, ale w pracy stosowane jest uniwersalne hasło "swarm_bot".
W kolejnym kroku konfiguracji użytkownik jest proszony o podanie nazwy rozróżniającej robota. W pracy zostało 
zastosowane nazewnictwo swarm_bot# - gdzie # - jest unikalnym numerem ID identyfikującym robota.
Postępując zgodnie z instrukcjami należy wpisać "Y" aby potwierdzić ustawienia. Następnie ponownie wprowadzane jest "Y",
aby ustawić połączenie Wi-Fi. Po zakończeniu skanowania należy wybrać sieć i wprowadzić dane dostępowe sieci, która 
będzie wykorzystana przez roboty do komunikacji.

Po sukcesywnym podłączeniu do sieci należy zainstalować obsługę git:
Na urządzeniu włączamy wykonujemy polecenie 
       
    opkg install git

Następnie należy przeprowadzić instalacje języka python:
To install Python 3.6 on your Intel® Edison, follow the steps below:

Powrót do katalogu domowego:
    
    cd ~

Pobranie źródeł:

    wget --no-check-certificate https://www.python.org/ftp/python/3.6.0/Python-3.6.0.tgz

Rozpakowanie źródeł:

    tar -xvf Python-3.6.0.tgz

Przejście do katalogu python, konfiguracja i kompilacja:

    cd Python-3.6.0/
    ./configure --with-pydebug
    make -s -j4
    sudo make install

Sprawdzenie czy Python 3.6 jest zainstalowany poprawnie:

    # python

Powinno się wyświetlć:

        Python 3.6.0 (default, Feb  1 2017, 05:35:57)
        [GCC 4.9.1] on linux
        Type "help", "copyright", "credits" or "license" for more information.

Usunięcie katalogów roboczych

        # rm -rf Python-3.6.0.tgz

Instalacja modułów potrzebnych przy projekcie:

###Bibliografia

https://www.intel.com/content/dam/support/us/en/documents/edison/sb/edison-module_HG_331189.pdf

--------------------------- outdated ------------------------------  
Installing cairo on Windows

cairocffi needs a libcairo-2.dll file in a directory that is listed in the PATH environment variable.

Alexander Shaduri’s GTK+ installer works. (Make sure to leave the Set up PATH environment variable checkbox checked.)
Pycairo on Windows is sometimes compiled statically against cairo and may not provide a .dll file that cairocffi can use.  

    pip install slycot
    pip install control

-------------------------------------------------------------------