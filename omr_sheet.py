import tkinter as tk
from tkinter import simpledialog, messagebox

# --- CONFIG ---
OPTIONS = ["A", "B", "C", "D"]
MAX_QUESTIONS = 200
OVAL_WIDTH = 40
OVAL_HEIGHT = 30
OVAL_PADDING = 10
COLUMN_SIZE = 10  # number of answers per column in display

# --- Ask user for number of questions ---
root = tk.Tk()
root.withdraw()  # hide main window while asking

while True:
    try:
        num_questions = simpledialog.askinteger(
            "Number of Questions",
            f"Enter number of questions (1-{MAX_QUESTIONS}):",
            minvalue=1,
            maxvalue=MAX_QUESTIONS
        )
        if num_questions is None:
            exit()  # user cancelled
        break
    except Exception:
        continue

root.deiconify()  # show main window
root.title("Interactive OMR Sheet")
root.attributes('-topmost', True)
root.geometry("300x750")
root.resizable(True, True)

# --- Store responses ---
responses = {}

# --- Functions ---
def select_option(q_num, opt):
    responses[q_num] = opt
    draw_omr()  # redraw to update colors
    update_display()

def update_display():
    """Display answers in columns of 10 vertically per column."""
    output_text.delete(1.0, tk.END)
    col_size = COLUMN_SIZE
    num_cols = (num_questions + col_size - 1) // col_size

    # Build a 2D list of answers
    columns = []
    for c in range(num_cols):
        col = []
        for i in range(1 + c*col_size, min((c+1)*col_size + 1, num_questions + 1)):
            ans = responses.get(i, "-")
            col.append(f"{i}.{ans}")
        columns.append(col)

    # Print row by row
    for row in range(col_size):
        line = ""
        for col in columns:
            if row < len(col):
                line += f"{col[row]:<8}"  # pad each column
        output_text.insert(tk.END, line + "\n")

def save_to_file():
    """Save answers in columns like the display."""
    col_size = COLUMN_SIZE
    num_cols = (num_questions + col_size - 1) // col_size
    columns = []
    for c in range(num_cols):
        col = []
        for i in range(1 + c*col_size, min((c+1)*col_size + 1, num_questions + 1)):
            ans = responses.get(i, "-")
            col.append(f"{i}.{ans}")
        columns.append(col)

    with open("omr_responses.txt", "w") as f:
        for row in range(col_size):
            line = ""
            for col in columns:
                if row < len(col):
                    line += f"{col[row]:<8}"
            f.write(line + "\n")
    messagebox.showinfo("Saved", "Responses saved to omr_responses.txt")

def reset_all():
    responses.clear()
    draw_omr()
    update_display()

def toggle_answers():
    if answer_frame.winfo_ismapped():
        answer_frame.pack_forget()
        toggle_btn.config(text="📜 Show Answers")
    else:
        answer_frame.pack(pady=5, fill="x")
        toggle_btn.config(text="🔽 Hide Answers")


# --- GUI Setup ---
title = tk.Label(root, text=f"OMR Sheet ({num_questions} Questions)", font=("Arial", 12, "bold"))
title.pack(pady=10)

# Scrollable Canvas
canvas_frame = tk.Frame(root)
canvas_frame.pack(fill="both", expand=True)

canvas = tk.Canvas(canvas_frame, bg="white")
canvas.pack(side="left", fill="both", expand=True)

scrollbar = tk.Scrollbar(canvas_frame, orient="vertical", command=canvas.yview)
scrollbar.pack(side="right", fill="y")
canvas.configure(yscrollcommand=scrollbar.set)

inner_frame = tk.Frame(canvas, bg="white")
canvas.create_window((0, 0), window=inner_frame, anchor="nw")

# Enable scrolling with mouse wheel
def _on_mousewheel(event):
    canvas.yview_scroll(int(-1*(event.delta/120)), "units")
canvas.bind_all("<MouseWheel>", _on_mousewheel)

# Drag scrolling
def scroll_start(event):
    canvas.scan_mark(event.x, event.y)
def scroll_move(event):
    canvas.scan_dragto(event.x, event.y, gain=1)
canvas.bind("<ButtonPress-1>", scroll_start)
canvas.bind("<B1-Motion>", scroll_move)

# --- Draw OMR --- 
def draw_omr():
    for widget in inner_frame.winfo_children():
        widget.destroy()
    for q in range(1, num_questions + 1):
        row_frame = tk.Frame(inner_frame, bg="white")
        row_frame.pack(anchor="w", pady=5, padx=10)

        q_label = tk.Label(row_frame, text=f"{q}.", width=4, bg="white")
        q_label.pack(side="left")

        # Create a canvas for oval options
        opt_canvas = tk.Canvas(row_frame, width=(OVAL_WIDTH+OVAL_PADDING)*len(OPTIONS), height=OVAL_HEIGHT, bg="white", highlightthickness=0)
        opt_canvas.pack(side="left")
        
        for i, opt in enumerate(OPTIONS):
            x0 = i*(OVAL_WIDTH+OVAL_PADDING)
            y0 = 0
            x1 = x0 + OVAL_WIDTH
            y1 = OVAL_HEIGHT
            fill_color = "#4CAF50" if responses.get(q)==opt else "white"
            outline_color = "black"
            text_color = "white" if fill_color=="#4CAF50" else "black"
            oval_id = opt_canvas.create_oval(x0, y0, x1, y1, fill=fill_color, outline=outline_color, width=2)
            text_id = opt_canvas.create_text(x0+OVAL_WIDTH/2, y0+OVAL_HEIGHT/2, text=opt, fill=text_color, font=("Arial", 10, "bold"))

            # Bind click to select
            def make_callback(q=q, opt=opt):
                return lambda e: select_option(q, opt)
            opt_canvas.tag_bind(oval_id, "<Button-1>", make_callback())
            opt_canvas.tag_bind(text_id, "<Button-1>", make_callback())

draw_omr()

# --- Answer Frame (Hidden by Default) ---
toggle_btn = tk.Button(root, text="📜 Show Answers", command=toggle_answers, bg="#2196F3", fg="white")
toggle_btn.pack(pady=5)

answer_frame = tk.Frame(root)

tk.Label(answer_frame, text="Your Selected Answers:", font=("Arial", 11, "bold")).pack(pady=5)
output_text = tk.Text(answer_frame, height=12, width=80, font=("Consolas", 11))
output_text.pack()


# Buttons
btn_frame = tk.Frame(root)
btn_frame.pack(pady=5)
save_button = tk.Button(btn_frame, text="💾 Save Responses", command=save_to_file, bg="#2196F3", fg="white")
save_button.pack(side="left", padx=10)
reset_button = tk.Button(btn_frame, text="🔄 Reset All", command=reset_all, bg="#f44336", fg="white")
reset_button.pack(side="left", padx=10)

# Update scroll region
inner_frame.update_idletasks()
canvas.config(scrollregion=canvas.bbox("all"))

update_display()
root.mainloop()
