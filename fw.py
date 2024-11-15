import os

def focus_window(window_title):
    os.system(f'wmctrl -a "{window_title}"')

# Beispielaufruf
if __name__ == "__main__":
    window_name = "Smolit"
    focus_window(window_name)
