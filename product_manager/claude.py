
import os
import anthropic
import tkinter as tk
from tkinter import scrolledtext, ttk
import markdown
import threading
import re
from pygments import highlight
from pygments.lexers import get_lexer_by_name
from pygments.formatters import HtmlFormatter
from pygments.styles import get_style_by_name
import html

def read_file(file_path):
    with open(file_path, 'r') as file:
        return file.read()

def collect_project_files(project_dir, file_extensions=('.py', '.html')):
    project_contents = []
    for root, _, files in os.walk(project_dir):
        for file in files:
            if file.endswith(file_extensions):
                file_path = os.path.join(root, file)
                content = read_file(file_path)
                project_contents.append(f"File: {file_path}\n\n{content}\n\n")
                print(f"File: {file_path} Added to project contents\n\n")
    return "\n".join(project_contents)

class ClaudeGUI:
    def __init__(self, master):
        self.master = master
        master.title("Claude AI Chat")
        master.geometry("800x600")

        self.chat_frame = tk.Frame(master)
        self.chat_frame.pack(fill=tk.BOTH, expand=True)

        self.chat_display = tk.Text(self.chat_frame, wrap=tk.WORD, state=tk.DISABLED)
        self.chat_display.pack(fill=tk.BOTH, expand=True)

        self.scrollbar = tk.Scrollbar(self.chat_frame, command=self.chat_display.yview)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.chat_display.config(yscrollcommand=self.scrollbar.set)

        self.input_frame = tk.Frame(master)
        self.input_frame.pack(fill=tk.X, side=tk.BOTTOM)

        self.input_box = scrolledtext.ScrolledText(self.input_frame, height=3)
        self.input_box.pack(fill=tk.X, side=tk.LEFT, expand=True)
        self.input_box.bind("<Return>", self.send_message)

        self.send_button = ttk.Button(self.input_frame, text="Send", command=self.send_message)
        self.send_button.pack(side=tk.RIGHT)

        self.chat_display.tag_configure("bold", font=("TkDefaultFont", 10, "bold"))
        self.chat_display.tag_configure("italic", font=("TkDefaultFont", 10, "italic"))
        self.chat_display.tag_configure("code", font=("Courier", 10), background="#f0f0f0", wrap="none")
        self.chat_display.tag_configure("code_block", font=("Courier", 10), background="#e6f3ff", wrap="none")

        style = get_style_by_name("default")
        self.code_formatter = HtmlFormatter(style=style)

        self.client = anthropic.Anthropic(api_key="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")
        project_dir = "/Users/bitcraze/Desktop/testebot/marcacao/product_manager"
        project_content = collect_project_files(project_dir)

        self.system_prompt = "You are Claude, an AI assistant created by Anthropic. You have been provided with the contents of a Python project for context. Always answer with the full code and a very simple guide to help the user understand the code."
        self.conversation = []
        if project_content:
            self.conversation.append({"role": "user", "content": project_content})
        self.conversation.append({"role": "assistant", "content": "Hello! I'm ready to assist you with your Python project. What would you like to know or discuss?"})

        self.update_chat_display()

    def send_message(self, event=None):
        user_input = self.input_box.get("1.0", tk.END).strip()
        if user_input:
            self.conversation.append({"role": "user", "content": user_input})
            self.update_chat_display()
            self.input_box.delete("1.0", tk.END)
            threading.Thread(target=self.get_claude_response).start()
        return "break"

    def get_claude_response(self):
        try:
            response = self.client.messages.create(
                model="claude-3-sonnet-20240229",
                max_tokens=1000,
                temperature=0,
                system=self.system_prompt,
                messages=self.conversation
            )

            claude_response = response.content[0].text
            self.conversation.append({"role": "assistant", "content": claude_response})
            self.update_chat_display()
        except Exception as e:
            error_message = f"An error occurred: {str(e)}"
            self.conversation.append({"role": "assistant", "content": error_message})
            self.update_chat_display()

    def update_chat_display(self):
        self.chat_display.config(state=tk.NORMAL)
        self.chat_display.delete("1.0", tk.END)
        self.chat_display.insert(tk.END, "Chat with Claude\n\n", "bold")
        for message in self.conversation:
            if message['role'] == 'user':
                self.chat_display.insert(tk.END, "You: ", "bold")
                self.chat_display.insert(tk.END, f"{message['content']}\n\n")
            elif message['role'] == 'assistant':
                self.chat_display.insert(tk.END, "Claude: ", "bold")
                self.insert_formatted_text(message['content'])
                self.chat_display.insert(tk.END, "\n\n")
        self.chat_display.config(state=tk.DISABLED)
        self.chat_display.see(tk.END)

    def insert_formatted_text(self, text):
        html_content = markdown.markdown(text, extensions=['fenced_code', 'codehilite'])
        
        parts = re.split(r'(<[^>]+>|```[\s\S]*?```)', html_content)
        inside_code_block = False
        for part in parts:
            if part.startswith('<code>') and part.endswith('</code>'):
                code = html.unescape(part[6:-7])
                self.chat_display.insert(tk.END, code, "code")
            elif part.startswith('```') and part.endswith('```'):
                inside_code_block = True
                lines = part.split('\n')
                lang = lines[0][3:].strip() or 'text'
                code = '\n'.join(lines[1:-1])
                code = html.unescape(code)
                lexer = get_lexer_by_name(lang, stripall=True)
                highlighted_html = highlight(code, lexer, self.code_formatter)
                self.chat_display.insert(tk.END, highlighted_html, "code_block")
            elif part.startswith('<strong>'):
                self.chat_display.insert(tk.END, html.unescape(part[8:-9]), "bold")
            elif part.startswith('<em>'):
                self.chat_display.insert(tk.END, html.unescape(part[4:-5]), "italic")
            elif not part.startswith('<'):
                if not inside_code_block:
                    self.chat_display.insert(tk.END, html.unescape(part))
            
            if part.endswith('```'):
                inside_code_block = False

def main():
    root = tk.Tk()
    gui = ClaudeGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()