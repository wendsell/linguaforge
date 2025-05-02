import customtkinter as ctk

class ToolTip:
    def __init__(self, parent, widget, text, offset=(20, 10)):
        self.text = text
        self.parent = parent
        self.widget = widget
        self.offset = offset
        self.tip = ctk.CTkLabel(parent, text=text, font=("Segoe UI", 10),
                                text_color="#888888", fg_color="transparent")
        self.tip.place_forget()

        self.widget.bind("<Enter>", self.show_tip)
        self.widget.bind("<Leave>", self.hide_tip)

    def show_tip(self, event):
        x = event.x_root - self.parent.winfo_rootx() + self.offset[0]
        y = event.y_root - self.parent.winfo_rooty() + self.offset[1]
        self.tip.place(x=x, y=y)

    def hide_tip(self, _):
        self.tip.place_forget()
