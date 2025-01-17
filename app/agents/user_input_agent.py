from rich.console import Console
from rich.prompt import Prompt
from rich.text import Text
import sys
from prompt_toolkit import PromptSession
from prompt_toolkit import print_formatted_text
from prompt_toolkit.formatted_text import FormattedText
import os
import json

class UserInputAgent:
    """
    Agent to handle user input.
    """
    def __init__(self, data_dir="./pentest_data/", task_id=None):
        self.data_dir = data_dir
        self.task_id = task_id
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)        
        self.console = Console()
        self.input_history = []

    def set_task_id(self, task_id):
        self.task_id = task_id
        
    def get_history_file_path(self):
        return os.path.join(self.data_dir, f"history_{self.task_id}.json")

    def load_history(self):
        history_file = self.get_history_file_path()
        if not os.path.exists(history_file):
            return []

        with open(history_file, "r") as file:
            return json.load(file)

    def save_history(self, history):
        history_file = self.get_history_file_path()
        with open(history_file, "w") as file:
            json.dump(history, file, indent=4)

    def get_last_task(self):
        """
        Get the last task from user input history.
        """
        if self.input_history:
            return self.input_history[-1]
        else:
            return None

    def get_task(self):
        """
        Get the task from user input using prompt_toolkit for advanced input handling.
        """
        session = PromptSession()

        try:
            if len(self.input_history) == 0:
                prompt_text = FormattedText([
                    ("magenta", "────────────────────────────────────────────────────────────────\n"),
                    ("bold blue", "Enter your task (multiple lines allowed).\n"),
                    ("magenta", "────────────────────────────────────────────────────────────────\n"),
                    ("bold blue", "Made by Pranav\n"),
                    ("magenta", "────────────────────────────────────────────────────────────────\n"),
                    ("", "Type "),
                    ("bold green", "'done'"),
                    ("", " to finish, "),
                    ("bold yellow", "'cancel'"),
                    ("", " to restart, "),
                    ("bold red", "'exit'"),
                    ("", " to exit:\n"),
                    ("magenta", "────────────────────────────────────────────────────────────────\n")
                ])
            else:
                prompt_text = FormattedText([
                    ("magenta", "────────────────────────────────────────────────────────────────\n"),
                    ("bold blue", "Enter your task (multiple lines allowed).\n"),
                    ("", "Type "),
                    ("bold green", "'done'"),
                    ("", " to finish, "),
                    ("bold yellow", "'cancel'"),
                    ("", " to restart, or "),
                    ("bold red", "'exit'"),
                    ("", " to exit, "),
                    ("bold blue", "'repeat'"),
                    ("", " to repeat the previous task:\n"),
                    ("magenta", "────────────────────────────────────────────────────────────────\n")
                ])
            print_formatted_text(prompt_text)

            lines = []
            while True:
                line = session.prompt("")
                if line.strip().lower() == 'done':
                    print_formatted_text(FormattedText([("bold green", "Saving input...")]))
                    self.input_history.append("\n".join(lines))
                    break
                elif line.strip().lower() == 'cancel':
                    print_formatted_text(FormattedText([("bold yellow", "Input cancelled. Restarting input.")]))
                    return self.get_task()
                elif line.strip().lower() == 'exit':
                    print_formatted_text(FormattedText([("bold red", "Exiting application.")]))
                    sys.exit()
                elif line.strip().lower() == 'repeat' and len(self.input_history) > 0:
                    print_formatted_text(FormattedText([("bold blue", "Repeating previous task...")]))
                    history = self.load_history()
                    history.append({"role": "user", "content": self.input_history[-1]})
                    self.save_history(history)
                    return self.input_history[-1]
                else:
                    lines.append(line)
            

            task = "\n".join(lines)
            self.input_history.append(task)
            
            return task
        except KeyboardInterrupt:
            if lines:
                print_formatted_text(FormattedText([("bold yellow", "\nInput cancelled. Restarting input.")]))
                return self.get_task()
            else:
                print_formatted_text(FormattedText([("bold red", "\nNo input given. Exiting application.")]))
                sys.exit()
        except Exception as e:
            print_formatted_text(FormattedText([("bold red", f"Error occurred while getting user input: {e}")]))
            return None
    
    def get_additional_feedback(self):
        """
        Get the task from user input using prompt_toolkit for advanced input handling.
        """
        session = PromptSession()

        try:
            prompt_text = FormattedText([
                ("", "Type "),
                ("bold green", "'done'"),
                ("", " to finish, "),
                ("bold yellow", "'cancel'"),
                ("", " to restart, "),
                ("bold red", "'exit'"),
                ("", " to exit the current task:\n"),
            ])
            print_formatted_text(prompt_text)

            lines = []
            while True:
                line = session.prompt("")
                if line.strip().lower() == 'done':
                    print_formatted_text(FormattedText([("bold green", "Saving feedback...")]))
                    break
                elif line.strip().lower() == 'cancel':
                    print_formatted_text(FormattedText([("bold yellow", "Input cancelled. Restarting input.")]))
                    return self.get_additional_feedback()
                elif line.strip().lower() == 'exit':
                    print_formatted_text(FormattedText([("bold red", "Exiting current task.")]))
                    return None
                else:
                    lines.append(line)            

            feedback = "\n".join(lines)
            history = self.load_history()
            history.append({"role": "user", "content": feedback})
            self.save_history(history)

            return feedback
        except KeyboardInterrupt:
            if lines:
                print_formatted_text(FormattedText([("bold yellow", "\nInput cancelled. Restarting input.")]))
                return self.get_additional_feedback()
            else:
                print_formatted_text(FormattedText([("bold yellow", "\nNo input given. Exiting current task.")]))
                return None
        except Exception as e:
            print_formatted_text(FormattedText([("bold red", f"Error occurred while getting user input: {e}")]))
            return None