from config import SYSTEM_PROMPT
from chat_engine import ChatEngine
from ui import ChatUI

def main():
    engine = ChatEngine(SYSTEM_PROMPT)
    ui = ChatUI(engine)
    ui.run()

if __name__ == "__main__":
    main()
