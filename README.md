# Flask_microblog
Flask Tutorial Microblog

## Uruchamianie
 * Pierwszą rzeczą, jaką należy zrobić, to zainstalować [Python](https://www.python.org/downloads/) w wersji co
  najmniej 3.7 (koniecznie zaznacz pole add to PATH), oraz [git](https://git-scm.com/downloads).
 * Aby uruchomić PowerShell w systemie Windows 10, kliknij prawym przyciskiem myszy w start, następnie wybierz
  Program Windows PowerShell.
 * Należy pobrać repozytorium, wpisując w terminal komendę 
 `git clone https://github.com/Lioheart/Flask_microblog.git`
 * Następnie przechodzimy do katalogu `cd Flask_mikroblog` lub dla PowerShell `cd .\Flask_mikroblog`
 * W danym folderze uruchamiamy komendę, aby zainicjować utworzenie venv `python -m venv venv`
 * Uruchom drugie okno konsoli lub PowerShella w trybie administratora.
 * Zainstaluj paczkę (tylko z uprawnieniami administratora), dzięki której utworzysz wirtualne środowisko `pip install
  virtualenv`
 * Przejdź do pierwszego okna i utwórz virtual env za pomocą komendy `virtualenv venv`
 * Należy teraz aktywować virtual env za pomocą komendy (tylko linux i macOS) `source venv/bin/activate`
 * W przypadku, gdy używamy konsoli cmd Microsoft Windows należy użyć komendy `venv\Scripts\activate`

### Uwaga 
W przypadku, gdy wykonujemy komendy poprzez Windows PowerShell należy wykonać poniższe kroki:
 * Uruchom Windows PowerShell w trybie administratora i wprowadź poniższą komendę, zgadzając się na zmiany 
 
 ```
 Set-ExecutionPolicy RemoteSigned
```
 * Następnie przejdź do okna Windows PowerShell, w którym wykonywałeś poprzednie polecenia, przejdź do katalogu z
  projektem, po czym użyj komendy 
 ```
 venv\Scripts\activate
```
 * Przejdź ponownie do Windows PowerShell w trybie administratora i wycofaj zmiany, za pomocą komendy 
 ```
 Set-ExecutionPolicy Restricted
```
 
## Instalacja pakietów
Aby zainstalować niezbędne pakiety, wystarczy użyć poniższej komendy:
```
pip install -r requirements.txt
```
 
## Uruchamianie
Aby uruchomić naszą aplikację, użyjemy komendy ```flask run```