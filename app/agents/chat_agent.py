import os
from prompt_toolkit import PromptSession
from prompt_toolkit import print_formatted_text
from prompt_toolkit.formatted_text import FormattedText
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.markdown import Markdown
from rich.live import Live
from openai import OpenAI
import json

class ChatAgent:
    def __init__(self, client, data_dir):
        self.client = client
        self.data_dir = data_dir
        self.history = []
        self.console = Console()

    def get_history_file_path(self):
        return os.path.join(self.data_dir, f"chat_{self.task_id}.json")

    def save_history(self, history):
        history_file = self.get_history_file_path()
        with open(history_file, "w") as file:
            json.dump(history, file, indent=4)

    def set_task_id(self, task_id):
        self.task_id = task_id

    def start_chat_session(self):
        """
        Start the main chat session loop. Continuously gets user input, generates responses, and updates the history.
        """
        # Initial message in a panel
        self.console.print(Text("────────────────────────────────────────────────────────────────\n", style="magenta"), end="")
        self.console.print(Text("SecuScan AI:", style="bold blue"))
        welcome_panel = Panel("Hi, how can I help you?", border_style="blue", expand=False)
        self.console.print(welcome_panel)

        while True:
            user_input = self.get_user_input()
            if user_input is None: # Exit the chat session
                break

            self.generate_response()


    def get_user_input(self):
        """
        Get the input from the user.
        """
        session = PromptSession()

        try:
            prompt_text = FormattedText([
                ("bold blue", "Enter your message (multiple lines allowed).\n"),
                ("", "Type "),
                ("bold green", "'done'"),
                ("", " to finish, "),
                ("bold yellow", "'cancel'"),
                ("", " to restart, "),
                ("bold red", "'exit'"),
                ("", " to exit:\n"),
            ])
            print_formatted_text(prompt_text)
            lines = []
            while True:
                line = session.prompt("")
                if line.strip().lower() == 'done':
                    break
                elif line.strip().lower() == 'cancel':
                    print_formatted_text(FormattedText([("bold yellow", "Input cancelled. Restarting user input.")]))
                    return self.get_user_input()
                elif line.strip().lower() == 'exit':
                    print_formatted_text(FormattedText([("bold red", "Exiting the current chat.")]))
                    return None
                else:
                    lines.append(line) 

            user_input = "\n".join(lines)
            self.history.append({"role": "user", "content": user_input})
            self.save_history(self.history)
            return user_input
        except KeyboardInterrupt:
            if lines:
                print_formatted_text(FormattedText([("bold yellow", "\nInput cancelled. Restarting user input.")]))
                return self.get_user_input()
            else:
                print_formatted_text(FormattedText([("bold red", "\nNo input given. Exiting the current chat.")]))
                return None
        except Exception as e:
            print_formatted_text(FormattedText([("bold red", f"Error occurred while getting user input: {e}")]))
            return None

    def generate_response(self):
        """
        Generate a response based on the conversation history, updating the output live as the response is received.
        """
        from app.prompts import CHAT_AGENT_PROMPT
        instruction = CHAT_AGENT_PROMPT

        messages = [{"role": "system", "content": instruction}] + self.history

        # Initialize a panel with no content for live display
        self.console.print(Text("SecuScan AI:", style="bold blue"))
        response_panel = Panel("", border_style="blue", expand=False)

        full_message_content = ''

        try:
            with Live(response_panel, console=self.console, refresh_per_second=10) as live:
                # Begin the streaming completion with OpenAI
                completion = self.client.chat.completions.create(
                    model="gpt-4-1106-preview",
                    messages=messages,
                    stream=True
                )

                for chunk in completion:
                    if chunk.choices and chunk.choices[0].delta:
                        delta = chunk.choices[0].delta
                        message_content = delta.content
                        if message_content:
                            # Update the full message content
                            full_message_content += message_content

                            # Update the live output with the new content
                            response_markdown = Markdown(full_message_content)
                            live.update(Panel(response_markdown, border_style="blue", expand=False))
        except KeyboardInterrupt:
            print_formatted_text(FormattedText([("bold yellow", "\nGeneration stopped. Returning to user input.")]))
            # Save to history
            self.history.append({"role": "assistant", "content": full_message_content})
            self.save_history(self.history)
            return

        # Save to history
        self.history.append({"role": "assistant", "content": full_message_content})
        self.save_history(self.history)

        return
