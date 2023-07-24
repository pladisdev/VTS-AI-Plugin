import tkinter as tk
from tkinter import ttk
import asyncio 

class GUI:

    def __init__(self, expressions = [] ):
        self.expressions = expressions
        self.expressions.insert(0, "None")
        self.value_change = True
        self.new_expression = False
        self.exit = False

        self.expression = ""

        self.head_state = "Still"
        self.head_target_speed_min = 0.5
        self.head_target_speed_max = 0.5
        self.head_x_min = 0.5
        self.head_x_max = 0.5
        self.head_y_min = 0.5
        self.head_y_max = 0.5
        self.head_z_min = 0.5
        self.head_z_max = 0.5

        self.eyes_state = "Still"
        self.eyes_target_speed_min = 0.5
        self.eyes_target_speed_max = 0.5
        self.eyes_x_min = 0.5
        self.eyes_x_max = 0.5
        self.eyes_y_min = 0.5
        self.eyes_y_max = 0.5

        self.eye_lids = "Blink"

        self.window = tk.Tk()
        self.window.title("GUI Example")

        self.sliders = []
        slider_labels = ["Next Pos (0->5:0->5)", "     X (-30->0:0->30)", "     Y (-30->0:0->30)", "     Z (-90->0:0->90)", "Next Pos (0->5:0->5)", "     X (-1->0:0->1)", "     Y (-1->0:0->1)"]
        for i in range(7):

            if (i == 0):
                slider_head_label = tk.Label(self.window, text="Head Movement:")
                slider_head_label.pack()
                self.selector1 = ttk.Combobox(self.window, values=["Still", "Random"], )
                self.selector1.bind("<<ComboboxSelected>>", self.__handle_head_selection)
                self.selector1.pack()
            elif (i == 4):
                selector1_label = tk.Label(self.window, text="Eye Movement:")
                selector1_label.pack()
                self.selector2 = ttk.Combobox(self.window, values=["Still", "Random"])
                self.selector2.bind("<<ComboboxSelected>>", self.__handle_eyes_selection)
                self.selector2.pack()

            slider_frame = tk.Frame(self.window)
            slider_frame.pack()
            
            slider_label = tk.Label(slider_frame, text=slider_labels[i])
            slider_label.pack(side=tk.LEFT)

            slider_min = ttk.Scale(slider_frame, from_=0, to=1, length=100, orient=tk.HORIZONTAL, value=.5)
            slider_min.bind("<ButtonRelease-1>", self.__handle_slider_release)
            slider_min.pack(side=tk.LEFT)
            
            slider = ttk.Scale(slider_frame, from_=0, to=1, length=100, orient=tk.HORIZONTAL, value=.5)
            slider.bind("<ButtonRelease-1>", self.__handle_slider_release)
            slider.pack(side=tk.LEFT)

            self.sliders.append(slider_min)
            self.sliders.append(slider)

        self.selector3_label = tk.Label(self.window, text="Eye lids control:")
        self.selector3_label.pack()

        eye_lids_frame = tk.Frame(self.window)
        eye_lids_frame.pack()

        blink_button = ttk.Button(eye_lids_frame, text="Blink", command=lambda: self.__eye_lids_selection("Blink"))
        blink_button.pack(side=tk.LEFT)

        blink_button = ttk.Button(eye_lids_frame, text="Open", command=lambda: self.__eye_lids_selection("Open"))
        blink_button.pack(side=tk.LEFT)

        blink_button = ttk.Button(eye_lids_frame, text="Close", command=lambda: self.__eye_lids_selection("Close"))
        blink_button.pack(side=tk.LEFT)

        blink_button = ttk.Button(eye_lids_frame, text="Wink", command=lambda: self.__eye_lids_selection("Wink"))
        blink_button.pack(side=tk.LEFT)
     
        self.selector3_label = tk.Label(self.window, text="Select Expression:")
        self.selector3_label.pack()
        self.selector3 = ttk.Combobox(self.window, values=self.expressions)
        self.selector3.bind("<<ComboboxSelected>>", self.__handle_expression_selection)
        self.selector3.pack()

        # Error box
        self.error_label = tk.Label(self.window, text="Error:")
        self.error_label.pack()
        self.error_box = tk.Text(self.window, height=4, width=30)
        self.error_box.pack()

        self.task = asyncio.create_task(self.__update_gui())

        exit_button = ttk.Button(self.window, text="Exit", command=self.__handle_exit)
        exit_button.pack()

    async def __update_gui(self):
        while self.window:
            self.window.update()
            await asyncio.sleep(0.01)  # Adjust the sleep duration as needed

    async def close_gui(self):
        self.task.cancel()
        await asyncio.gather(*self.task, return_exceptions=True)

    def __handle_head_selection(self, event):
        self.head_state = self.selector1.get()
        print("Selected value:", self.head_state)
        self.value_change = True

    def __handle_eyes_selection(self, event):
        self.eyes_state = self.selector2.get()
        print("Selected value:", self.eyes_state)
        self.value_change = True

    def __eye_lids_selection(self, action):
        self.eye_lids = action
        self.value_change = True

    def __handle_expression_selection(self, event):
        self.expression = self.selector3.get()
        print("Selected value:", self.expression)
        self.new_expression = True
    
    def __update_error(self, text):
        self.error_box.delete("1.0", tk.END)
        self.error_box.insert(tk.END, text)

    def __handle_slider_release(self, event):
        # Get the current values of the sliders

        self.head_target_speed_min = self.sliders[0].get()
        self.head_target_speed_max = self.sliders[1].get()
        self.head_x_min = self.sliders[2].get()
        self.head_x_max = self.sliders[3].get()
        self.head_y_min = self.sliders[4].get()
        self.head_y_max = self.sliders[5].get()
        self.head_z_min = self.sliders[6].get()
        self.head_z_max = self.sliders[7].get()

        self.eyes_target_speed_min = self.sliders[8].get()
        self.eyes_target_speed_max = self.sliders[9].get()
        self.eyes_x_min = self.sliders[10].get()
        self.eyes_x_max = self.sliders[11].get()
        self.eyes_y_min = self.sliders[12].get()
        self.eyes_y_max = self.sliders[13].get()

        self.value_change = True

    def __handle_exit(self):
        self.window.destroy()  # Close the main window and exit the application
        self.exit = True

    async def end(self):
        self.task.cancel()