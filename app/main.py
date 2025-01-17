import sys
import argparse
import uuid
from .agents.user_input_agent import UserInputAgent
from .agents.command_agent import CommandAgent
from .agents.pentest_agent import PentestAgent
from .agents.chat_agent import ChatAgent
from openai import OpenAI
from rich.console import Console
from rich.panel import Panel
from rich.style import Style
from rich.text import Text
from prompt_toolkit import print_formatted_text
from prompt_toolkit.formatted_text import FormattedText
import os
from dotenv import load_dotenv
import pyfiglet
import time

# Initialize OpenAI API client
load_dotenv()
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))


# Directory to store the data
DATA_DIR = "./logs/"


class PentestPilot:
    """
    Main class for bugtester application.
    Handles the overall workflow and interactions between different agents.
    """
    def __init__(self):
        self.console = Console()
        self.user_agent = UserInputAgent(data_dir=DATA_DIR)
        self.pentest_agent = None
        self.command_agent = None
        self.chat_agent = ChatAgent(client=client, data_dir=DATA_DIR)

    def print_banner(self):
        self.console.clear()
        banner = pyfiglet.figlet_format("SecuScan AI", font="slant")
        self.console.print(banner, style="bold blue")
        time.sleep(0.5)

    def run(self):
        self.print_banner()
        parser = argparse.ArgumentParser(description="SecuScan AI Application")
        parser.add_argument('mode', nargs='?', default='action', help="Start mode of the application: 'chat' or 'action' (default)")
        args = parser.parse_args()

        # Choose between chat mode or action mode
        if args.mode == 'chat':
            task_id = str(uuid.uuid4())
            self.chat_agent.set_task_id(task_id)
            self.chat_agent.start_chat_session()
        else:    
            while True:
                task_id = str(uuid.uuid4())
                self.user_agent.set_task_id(task_id)
                self.pentest_agent = PentestAgent(client=client, data_dir=DATA_DIR, task_id=task_id)
                self.command_agent = CommandAgent(data_dir=DATA_DIR, task_id=task_id)
                self.run_action_mode()

    def run_action_mode(self):
        # Get user input
        task = self.user_agent.get_task()
        if not task:
            sys.exit()

        # Process the task, handle ctrl+c to stop the process and go back to user input
        try:
            self.pentest_agent.set_task(task)
            while True:
                try:
                    # Generate a thought about next step
                    thought = self.pentest_agent.generate_thought()
                    # Generate an action (command line code) based on the thought
                    action, status = self.pentest_agent.determine_next_action(thought)
                    if status=='success':
                        self.console.print("I have successfully completed the task. Below is a summary of the steps taken:\n", style="green")
                        # Generate a summary of the steps taken
                        self.pentest_agent.generate_summary(success=True)
                        break
                    elif status=='failure':
                            self.console.print("Unfortunately, I couldn't complete the task successfully, and I'm uncertain about the next step. To assist further, please provide additional details about the task, or allow me to attempt it again. Below are the steps I've undertaken so far:\n", style="red")
                            # Generate a summary of the steps tried
                            self.pentest_agent.generate_summary(success=False)
                            response_style = Style(color="yellow", bold=True)
                            prompt_text = Text("\nWould you like me to try again? [yes/no] ", style=response_style)
                            response = self.console.input(prompt_text)
                            response = (response.strip().lower()) if response else "no"
                            if response == 'yes':
                                # Generate a new task ID
                                task_id = str(uuid.uuid4())
                                self.pentest_agent = PentestAgent(client=client, data_dir=DATA_DIR, task_id=task_id)
                                self.command_agent = CommandAgent(data_dir=DATA_DIR, task_id=task_id)

                                # Rerun the previous user input
                                task = self.user_agent.get_last_task()
                                self.pentest_agent.set_task(task)
                                continue
                            else:
                                break                    
                    else:
                        # Execute the action
                        execution_response = self.command_agent.execute_action(action)

                        # Print the output
                        if len(execution_response['output']) > 0:
                            # You can use a Panel for large outputs
                            if len(execution_response['output']) > 1000:
                                execution_response['output'] = execution_response['output'][:500] + "\n\n...\n\n" + execution_response['output'][-500:]
                            self.console.print(Text("System Output", style="bold magenta"))
                            output_panel = Panel(execution_response['output'], expand=False, border_style="magenta")
                            self.console.print(output_panel)
                        if len(execution_response['error']) > 0:
                            if len(execution_response['error']) > 1000:
                                execution_response['error'] = execution_response['error'][:500] + "\n\n...\n\n" + execution_response['error'][-500:]
                            self.console.print(Text("System Error", style="bold red"))
                            error_panel = Panel(execution_response['error'], expand=False, border_style="red")
                            self.console.print(error_panel)                        

                        # Save the result
                        self.command_agent.save_result(execution_response)
                except KeyboardInterrupt:
                    print_formatted_text(FormattedText([("bold yellow", "\nGeneration stopped. Please input additional feedback to the AI.")]))
                    feedback = self.user_agent.get_additional_feedback()
                    if feedback:
                        continue
                    else:
                        break
        except KeyboardInterrupt:
            print_formatted_text(FormattedText([("bold yellow", "\nGeneration stopped. Going back to user input.")]))
            return
        
    def run_chat_mode(self):
        self.chat_agent.run()


def main():
    app = PentestPilot()
    app.run()

if __name__ == "__main__":
    main()