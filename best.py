import random
import time
from prompt_toolkit import PromptSession
from prompt_toolkit.completion import Completer, Completion

# List of random responses
responses = [
    "Hello there!",
    "How can I assist you today?",
    "That's interesting!",
    "I see...",
    "Tell me more!",
    "Goodbye!"
]

class ChatCompleter(Completer):
    def __init__(self):
        self.commands = ["exit"]

    def get_completions(self, document, complete_event):
        text = document.text_before_cursor
        if text:
            for command in self.commands:
                if command.startswith(text):
                    yield Completion(command, -len(text))

def chat():
    session = PromptSession("Enter your message: ", completer=ChatCompleter())

    while True:
        user_input = session.prompt()
        if user_input.lower() == "exit":
            print("Exiting chat...")
            break

        # Random response
        response = random.choice(responses)
        print(f"Bot: {response}")
        time.sleep(1)

if __name__ == "__main__":
    print("""
         ;        ______ _             ____             _     _          _
         ;;       |_   _| |__   ___   | __ )  ___  __ _| |_  | |    __ _| |__
         ;';.       | | | '_ \\ / _ \\  |  _ \\ / _ \\/ _` | __| | |   / _` | '_ \\
         ;  ;;      | | | | | |  __/  | |_) |  __/ (_| | |_  | |__| (_| | |_) |
         ;   ;;     |_| |_| |_|\\___|  |____/ \\___|\\__,_|\\__| |_____\\__,_|_.__/
         ;   ;'
         ;  '
    ,;;;,;             🤖 LLM music assistant - With ❤️  to the community
    ;;;;;;
    `;;;;'
    """)
    print("Welcome to the terminal chat. Type 'exit' to quit.")
    chat()
