# SecuScan AI

SecuScan AI is a tool that uses AI to assist in automated penetration testing. This tool employs cutting-edge algorithms of GPT-4 to conduct security assessments, enhancing the efficiency and effectiveness of the testing process.

## Caution

This software is designed strictly for authorized and ethical use. It is suitable for sanctioned security assessments and learning purposes. The creators are not responsible for any misuse or damage resulting from the use of this tool.

## Prerequisites

- Python version 3.12 or higher
- Required Python libraries specified in `requirements.txt`

## Installation Guide

Ensure Python 3.12 or newer is installed. Follow these steps to prepare your environment:

1. Download the source code:

   ```
   git clone https://github.com/PorePranav/SecuScanAI.git
   cd SecuScanAI 
   ```

2. Install dependencies:

   ```
   pip install -r requirements.txt
   ```

3. Configure OpenAI API Key:
   - Create a file named `.env` in the main directory.
   - Insert your OpenAI API key in the `.env` file:

     ```
     OPENAI_API_KEY=<your_api_key>
     ```
   - Replace `<your_api_key>` with your actual OpenAI API key.

## Execution

Launch the tool with the following command in the project's main directory:

```
python start.py
```

Use the interactive prompts to specify your penetration testing tasks.

## Sample Task

You can check my samples in the examples folder of this repo.

Example of a task you might input:

> Perform an SQL injection test on the URL http://localhost:5000/users/v1/John.Smith and retrieve all usernames and passwords from the database.