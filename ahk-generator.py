import tkinter as tk
from tkinter import ttk, messagebox
from typing import List, Dict, Any
import re

class Action:
    def __init__(self, action_type: str, parameter: str = ""):
        self.type = action_type
        self.parameter = parameter
    
    def __str__(self) -> str:
        if self.parameter:
            return f"{self.type}: {self.parameter}"
        return self.type

class KeyTranslator:
    SPECIAL_KEYS = {
        'ctrl': '^',
        'control': '^',
        'shift': '+',
        'alt': '!',
        'win': '#',
        'up': '{Up}',
        'down': '{Down}',
        'left': '{Left}',
        'right': '{Right}',
        'enter': '{Enter}',
        'tab': '{Tab}',
        'space': '{Space}',
        'backspace': '{Backspace}',
        'delete': '{Delete}',
        'esc': '{Esc}',
        'escape': '{Esc}',
    }

    @classmethod
    def translate_key_combination(cls, key_string: str) -> str:
        """Convert human-readable key combinations to AutoHotkey syntax."""
        # Split the key combination
        keys = [k.strip().lower() for k in key_string.split('+')]
        
        # Initialize result with modifiers
        result = ''
        remaining_keys = []
        
        # Process each key
        for key in keys:
            if key in cls.SPECIAL_KEYS:
                if cls.SPECIAL_KEYS[key].startswith('{'):
                    remaining_keys.append(cls.SPECIAL_KEYS[key])
                else:
                    result += cls.SPECIAL_KEYS[key]
            else:
                remaining_keys.append(key)
        
        # Add remaining keys
        result += ''.join(remaining_keys)
        return result

class AHKGeneratorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("AutoHotkey Script Generator")
        
        # Available hotkeys
        self.hotkeys = [
            "#+F1", "#+F2", "#+F3", "#+F4", "#+F5",  # Win+Shift+F1-F12
            "^!1", "^!2", "^!3", "^!4", "^!5",       # Ctrl+Alt+1-9
            "#1", "#2", "#3", "#4", "#5"              # Win+1-9
        ]
        
        # Available actions
        self.actions = [
            "Click Button", 
            "Cut Text", 
            "Paste Text", 
            "Switch Window",
            "Send Keys"  # New action type
        ]
        
        # Sequence of actions
        self.sequence: List[Action] = []
        
        self._create_widgets()
        
    def _create_widgets(self):
        # Hotkey selection
        hotkey_frame = ttk.LabelFrame(self.root, text="Hotkey Selection", padding=5)
        hotkey_frame.grid(row=0, column=0, columnspan=2, padx=5, pady=5, sticky="ew")
        
        self.hotkey_var = tk.StringVar()
        self.hotkey_var.set(self.hotkeys[0])
        ttk.Combobox(hotkey_frame, textvariable=self.hotkey_var, values=self.hotkeys).pack(fill="x")
        
        # Action builder
        action_frame = ttk.LabelFrame(self.root, text="Action Builder", padding=5)
        action_frame.grid(row=1, column=0, columnspan=2, padx=5, pady=5, sticky="ew")
        
        self.action_var = tk.StringVar()
        self.action_var.set(self.actions[0])
        action_combo = ttk.Combobox(action_frame, textvariable=self.action_var, values=self.actions)
        action_combo.pack(fill="x")
        action_combo.bind('<<ComboboxSelected>>', self._on_action_change)
        
        # Parameter label and entry
        self.param_label = ttk.Label(action_frame, text="Button/Window Name:")
        self.param_label.pack(fill="x", pady=(5,0))
        
        self.param_var = tk.StringVar()
        self.param_entry = ttk.Entry(action_frame, textvariable=self.param_var)
        self.param_entry.pack(fill="x", pady=(0,5))
        
        # Help text for key combinations
        self.help_text = ttk.Label(action_frame, text="", wraplength=300)
        self.help_text.pack(fill="x", pady=(0,5))
        
        ttk.Button(action_frame, text="Add Action", command=self._add_action).pack(fill="x")
        
        # Sequence list
        sequence_frame = ttk.LabelFrame(self.root, text="Action Sequence", padding=5)
        sequence_frame.grid(row=2, column=0, columnspan=2, padx=5, pady=5, sticky="nsew")
        
        self.sequence_listbox = tk.Listbox(sequence_frame, height=10)
        self.sequence_listbox.pack(fill="both", expand=True)
        
        button_frame = ttk.Frame(sequence_frame)
        button_frame.pack(fill="x", pady=5)
        
        ttk.Button(button_frame, text="Move Up", command=self._move_up).pack(side="left", padx=2)
        ttk.Button(button_frame, text="Move Down", command=self._move_down).pack(side="left", padx=2)
        ttk.Button(button_frame, text="Remove", command=self._remove_action).pack(side="left", padx=2)
        
        # Generate button
        ttk.Button(self.root, text="Generate Script", command=self._generate_script).grid(row=3, column=0, columnspan=2, pady=5)

    def _on_action_change(self, event=None):
        action = self.action_var.get()
        if action == "Send Keys":
            self.param_label.config(text="Key Combination:")
            self.help_text.config(text="Example: control+s, shift+tab, alt+f4\nSpecial keys: up, down, left, right, enter, tab, space, backspace, delete, esc")
        elif action in ["Click Button", "Switch Window"]:
            self.param_label.config(text="Button/Window Name:")
            self.help_text.config(text="")
        else:
            self.param_label.config(text="")
            self.help_text.config(text="")
            
    def _add_action(self):
        action_type = self.action_var.get()
        parameter = self.param_var.get()
        
        if action_type == "Send Keys" and parameter:
            # Validate and convert key combination
            try:
                translated = KeyTranslator.translate_key_combination(parameter)
                parameter = translated  # Store the AutoHotkey syntax version
            except Exception as e:
                messagebox.showerror("Error", f"Invalid key combination: {str(e)}")
                return
        
        if action_type in ["Click Button", "Switch Window", "Send Keys"] and not parameter:
            messagebox.showwarning("Warning", "Parameter required for this action type!")
            return
            
        action = Action(action_type, parameter)
        self.sequence.append(action)
        self.sequence_listbox.insert(tk.END, str(action))
        self.param_var.set("")  # Clear parameter field
        
    def _move_up(self):
        selected = self.sequence_listbox.curselection()
        if not selected or selected[0] == 0:
            return
            
        idx = selected[0]
        self.sequence[idx], self.sequence[idx-1] = self.sequence[idx-1], self.sequence[idx]
        self._refresh_listbox()
        self.sequence_listbox.selection_set(idx-1)
        
    def _move_down(self):
        selected = self.sequence_listbox.curselection()
        if not selected or selected[0] == len(self.sequence) - 1:
            return
            
        idx = selected[0]
        self.sequence[idx], self.sequence[idx+1] = self.sequence[idx+1], self.sequence[idx]
        self._refresh_listbox()
        self.sequence_listbox.selection_set(idx+1)
        
    def _remove_action(self):
        selected = self.sequence_listbox.curselection()
        if not selected:
            return
            
        idx = selected[0]
        del self.sequence[idx]
        self._refresh_listbox()
        
    def _refresh_listbox(self):
        self.sequence_listbox.delete(0, tk.END)
        for action in self.sequence:
            self.sequence_listbox.insert(tk.END, str(action))
            
    def _generate_script(self):
        if not self.sequence:
            messagebox.showwarning("Warning", "No actions in sequence!")
            return
            
        script = [
            "#SingleInstance Force",
            "#NoEnv",
            "",
            f"{self.hotkey_var.get()}::",
            "{",
            "    SetTitleMatchMode, 2",
            '    if WinExist("KoboldAI")',
            "    {",
            "        WinActivate",
        ]
        
        for action in self.sequence:
            if action.type == "Click Button":
                script.append(f'        Click, {action.parameter}')
            elif action.type == "Cut Text":
                script.append('        Send, ^x')
            elif action.type == "Paste Text":
                script.append('        Send, ^v')
            elif action.type == "Switch Window":
                script.append(f'        WinActivate, {action.parameter}')
            elif action.type == "Send Keys":
                script.append(f'        Send, {action.parameter}')
        
        script.extend([
            "    }",
            "    return",
            "}"
        ])
        
        try:
            with open("script.ahk", "w") as f:
                f.write("\n".join(script))
            messagebox.showinfo("Success", "Script generated successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save script: {str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = AHKGeneratorGUI(root)
    root.mainloop()
