def log_event(message):
    # Intentionally unsafe: interprets escape sequences
    unsafe_message = message.encode().decode('unicode_escape')

    with open("app.log", "a") as f:
        f.write(unsafe_message + "\n")

#no sanitization → attacker can inject fake logs