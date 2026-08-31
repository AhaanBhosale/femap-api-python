import tkinter as tk
from tkinter import messagebox

def get_user_inputs(defaults):
    """
    Create a form with pre-filled values.
    
    Args:
        defaults: dict with variable names as keys and default values
    
    Returns:
        dict with variable names as keys and user-entered values

    Example usage:
    defaults = {
        'ply1_id1': 16000060,
        'n_vecs': 1,
        'gap': 500,
        'threshold': 0.5,
    }
    """
    result = {}
    
    root = tk.Tk()
    root.title("Input Form")
    
    # Create entry widgets for each variable
    entries = {}
    for i, (var_name, default_value) in enumerate(defaults.items()):
        # Label
        tk.Label(root, text=f"{var_name}:").grid(row=i, column=0, sticky='e', padx=5, pady=5)
        
        # Entry with pre-filled value
        entry = tk.Entry(root, width=30)
        entry.insert(0, str(default_value))  # Pre-fill the value
        entry.grid(row=i, column=1, padx=5, pady=5)
        entries[var_name] = entry
    
    def on_submit():
        nonlocal result
        # Get values from entries
        for var_name, entry in entries.items():
            try:
                # Try to convert to the same type as default
                if isinstance(defaults[var_name], int):
                    result[var_name] = int(entry.get())
                elif isinstance(defaults[var_name], float):
                    result[var_name] = float(entry.get())
                else:
                    result[var_name] = entry.get()
            except ValueError:
                messagebox.showerror("Error", f"Invalid value for {var_name}")
                return
        root.quit()
        root.destroy()
    
    def on_cancel():
        root.quit()
        root.destroy()
    
    # Buttons
    button_frame = tk.Frame(root)
    button_frame.grid(row=len(defaults), column=0, columnspan=2, pady=10)
    tk.Button(button_frame, text="Submit", command=on_submit, width=10).pack(side='left', padx=5)
    tk.Button(button_frame, text="Cancel", command=on_cancel, width=10).pack(side='left', padx=5)
    
    root.mainloop()
    return result