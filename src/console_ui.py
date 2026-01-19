import sys
import time
import os
import shutil

class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    GREY = '\033[90m'

class ConsoleUI:
    def __init__(self):
        self.typing_speed = 0.02 # Seconds per char
        self.enable_colors = True
        if sys.platform == 'win32':
            os.system('color') # Enable ANSI colors on Windows

    def clear(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def colored(self, text, color):
        if not self.enable_colors:
            return text
        return f"{color}{text}{Colors.ENDC}"

    def slow_print(self, text, speed=None, color=None, end='\n'):
        if speed is None:
            speed = self.typing_speed

        if color and self.enable_colors:
            sys.stdout.write(color)

        for char in text:
            sys.stdout.write(char)
            sys.stdout.flush()
            if speed > 0:
                time.sleep(speed)

        if color and self.enable_colors:
            sys.stdout.write(Colors.ENDC)

        sys.stdout.write(end)
        sys.stdout.flush()

    def print_header(self, text):
        width = shutil.get_terminal_size().columns
        print(self.colored("=" * width, Colors.HEADER))
        print(self.colored(text.center(width), Colors.HEADER + Colors.BOLD))
        print(self.colored("=" * width, Colors.HEADER))

    def print_separator(self):
        width = shutil.get_terminal_size().columns
        print(self.colored("-" * width, Colors.GREY))

    def print_error(self, text):
        print(self.colored(f"Error: {text}", Colors.RED))

    def print_success(self, text):
        print(self.colored(text, Colors.GREEN))

    def print_warning(self, text):
        print(self.colored(text, Colors.YELLOW))

    def print_info(self, text):
        print(self.colored(text, Colors.BLUE))

    def print_dialogue(self, name, text):
        self.slow_print(f"{name}: ", speed=0.01, color=Colors.CYAN, end="")
        self.slow_print(f"\"{text}\"", speed=0.03, color=Colors.ENDC)

    def menu_choice(self, options, prompt="Select an option"):
        print(f"\n{prompt}:")
        for i, opt in enumerate(options):
            print(f"{self.colored(str(i+1) + '.', Colors.YELLOW)} {opt}")

        while True:
            try:
                choice = input(self.colored("> ", Colors.YELLOW)).strip()
                if not choice: continue
                idx = int(choice) - 1
                if 0 <= idx < len(options):
                    return idx
            except ValueError:
                pass
            print(self.colored("Invalid selection.", Colors.RED))

    def print_combat_log(self, text):
        # Heuristic to colorize combat text
        color = Colors.ENDC
        if "damage" in text.lower() or "hit" in text.lower():
            color = Colors.RED
        elif "healed" in text.lower():
            color = Colors.GREEN
        elif "gained" in text.lower():
            color = Colors.YELLOW
        elif "used" in text.lower():
            color = Colors.CYAN

        print(self.colored(text, color))

    def loading_effect(self, text="Loading", duration=1.0):
        chars = "/-\\|"
        end_time = time.time() + duration
        idx = 0
        sys.stdout.write(text + " ")
        while time.time() < end_time:
            sys.stdout.write(chars[idx % len(chars)] + "\b")
            sys.stdout.flush()
            idx += 1
            time.sleep(0.1)
        print("Done.")

# Global instance
ui = ConsoleUI()
