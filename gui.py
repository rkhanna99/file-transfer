import helpers, os
from tkinter import Tk, Label, Entry, Button, filedialog, StringVar, messagebox, ttk, Toplevel, PhotoImage, Frame
from tkcalendar import Calendar
from datetime import datetime
from file_transfer import copy_files
from PIL import Image, ImageTk
from collections import defaultdict

def browse_folder(entry_var, creation_dates=None):
    """
    Opens a folder selection dialog and updates the associated entry field.
    Optionally collects file creation dates for highlighting.
    """
    folder = filedialog.askdirectory()
    if folder:
        entry_var.set(folder)
        if creation_dates is not None:
            creation_dates.clear()
            for file in os.listdir(folder):
                file_path = os.path.join(folder, file)
                if os.path.isfile(file_path):
                    creation_date = helpers.extract_file_date(file_path).split(" ")[0]  # Only use the date part
                    if creation_date:
                        creation_dates.setdefault(creation_date, []).append(file)
            print("Updated creation_dates:", creation_dates)


def open_calendar(entry_var, creation_dates=None):
    """
    Opens a pop-up calendar and updates the entry field with the selected date upon click.
    Highlights dates based on the creation_dates dictionary.
    """
    def select_date(event):
        selected_date = cal.selection_get()
        entry_var.set(selected_date.strftime("%Y-%m-%d"))
        top.destroy()

    def highlight_dates():
        """Highlight dates with files created on those dates."""
        for date, files in creation_dates.items():
            try:
                # Parse the date from the string
                parsed_date = datetime.strptime(date, "%Y-%m-%d").date()
                cal.calevent_create(parsed_date, "Files Exist", "highlight")
            except ValueError:
                print(f"Error parsing date: {date}")

    # Create a top-level window for the calendar
    top = Toplevel(root)
    top.title("Select Date")

    cal = Calendar(
        top, font="Arial 14", selectmode='day', cursor="hand1", date_pattern="y-mm-dd"
    )
    cal.pack(fill="both", expand=True, padx=10, pady=10)

    # Apply the highlighting
    if creation_dates:
        highlight_dates()

    # Bind date selection to update the entry
    cal.bind("<<CalendarSelected>>", select_date)



def create_date_entry(parent, label_text, entry_var, creation_dates):
    """
    Creates a labeled entry with a resized calendar icon.
    """
    frame = Frame(parent)
    frame.grid(sticky="w", padx=10, pady=5)

    Label(frame, text=label_text).pack(side="left", padx=(0, 5))

    # Entry widget for the date
    entry = Entry(frame, textvariable=entry_var, width=20)
    entry.pack(side="left", padx=(0, 5))

    # Load the calendar icon and resize it to fit the entry box
    calendar_icon = Image.open("calendar.png")
    icon_width, icon_height = 20, 20
    calendar_icon = calendar_icon.resize(size=(icon_width, icon_height))
    calendar_icon = ImageTk.PhotoImage(calendar_icon)

    # Button with the resized calendar icon
    Button(frame, image=calendar_icon, command=lambda: open_calendar(entry_var, creation_dates)).pack(side="left")
    
    # Keep reference to prevent garbage collection
    frame.calendar_icon = calendar_icon  


def start_copy():
    source = source_var.get()
    destination = destination_var.get()
    workers = int(workers_var.get())
    file_type = file_type_var.get() if file_type_var.get() else None
    start_date = datetime.strptime(start_date_var.get(), "%Y-%m-%d") if start_date_var.get() else None
    end_date = datetime.strptime(end_date_var.get(), "%Y-%m-%d") if end_date_var.get() else None

    # Make sure we have a source and destination folder
    if not source or not destination:
        messagebox.showerror("Error", "Source and Destination folders are required!")
        return
    
    # Make sure the source and destination folders aren't the same
    if source == destination:
        messagebox.showerror("Error", "Source and Destination folders cannot be the same location")
        return

    # Make sure the start date isn't greater than the end date
    if start_date > end_date:
        messagebox.showerror("Error", "Start Date cannot be greater than the End Date")
        return

    try:
        file_count = copy_files(source, destination, workers, file_type, start_date, end_date)
        messagebox.showinfo("Success", f"Transferred {file_count} files successfully!")
    except Exception as e:
        messagebox.showerror("Error", str(e))

# Tkinter GUI setup
root = Tk()
root.title("File Transfer Tool")
root.geometry("400x300")

style = ttk.Style(root)
style.theme_use('aqua')

# Initialize variables
source_var = StringVar()
destination_var = StringVar()
workers_var = StringVar(value="4")
file_type_var = StringVar()
start_date_var = StringVar()
end_date_var = StringVar()
creation_dates = defaultdict(list)

# Layout
Label(root, text="Source Folder:").grid(row=0, column=0, sticky="w", padx=10, pady=5)
Entry(root, textvariable=source_var, width=30).grid(row=0, column=1, padx=10, pady=5)
Button(root, text="Browse", command=lambda: browse_folder(source_var, creation_dates)).grid(row=0, column=2, padx=5)

Label(root, text="Destination Folder:").grid(row=1, column=0, sticky="w", padx=10, pady=5)
Entry(root, textvariable=destination_var, width=30).grid(row=1, column=1, padx=10, pady=5)
Button(root, text="Browse", command=lambda: browse_folder(destination_var)).grid(row=1, column=2, padx=5)

Label(root, text="Number of Workers:").grid(row=2, column=0, sticky="w", padx=10, pady=5)
Entry(root, textvariable=workers_var, width=10).grid(row=2, column=1, sticky="w", padx=10, pady=5)

Label(root, text="File Type (e.g., .txt):").grid(row=3, column=0, sticky="w", padx=10, pady=5)
Entry(root, textvariable=file_type_var, width=10).grid(row=3, column=1, sticky="w", padx=10, pady=5)

# Create date entries with calendar icons
create_date_entry(root, "Start Date:", start_date_var, creation_dates)
create_date_entry(root, "End Date:", end_date_var, creation_dates)

Button(root, text="Start Copy", command=start_copy, bg="green", fg="white").grid(row=6, column=1, pady=20)

if __name__ == "__main__":
    root.mainloop()
