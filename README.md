# Flask_microblog
Flask Tutorial Microblog

## Uruchamianie
 * Pierwszą rzeczą, jaką należy zrobić, to zainstalować Python w wersji co najmniej 3.7,
 * Należy pobrać repozytorium, wpisując w terminal komendę 
 `git clone https://github.com/Lioheart/Flask_microblog.git`
 * Następnie przechodzimy do katalogu `cd .\Flask_mikroblog`
 * W danym folderze uruchamiamy komendę, aby zainicjować utworzenie venv `python3 -m venv venv`
 * Następnie tworzymy venv za pomocą komendy `virtualenv venv`
 * Należy teraz aktywować venv za pomocą komendy (tylko linux i macOS) `source venv/bin/activate`
 * W przypadku, gdy używamy Microsoft Windows należy użyć komendy `venv\Scripts\activate`

### Uwaga 
W przypadku, gdy uruchamiamy to poprzez Windows PowerShell należy wykonać poniższe kroki:
 * Uruchom Windows PowerShell w trybie administratora i wprowadź poniższą komendę, zgadzając się na zmiany 
 
 ```
 Set-ExecutionPolicy RemoteSigned
```
 * Następnie uruchom Windows PowerShell bez uprawnień, przejdź do katalogu z projektem, po czym użyj komendy 
 ```
 venv\Scripts\activate
```
 * Przejdź ponownie do Windows PowerShell w trybie administratora i wycofaj zmiany, za pomocą komendy 
 ```
 Set-ExecutionPolicy Restricted
```
 
## Instalacja pakietów
Aby zainstalować niezbędne pakiety, wystarczy użyć poniższej komendy:
 * ```python setup.py install```
 
## Uruchamianie
Aby uruchomić naszą aplikację, użyjemy komendy ```flask run```