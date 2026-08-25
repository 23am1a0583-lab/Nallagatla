# ============================================================
# BLOOD BANK MANAGEMENT SYSTEM
# ============================================================
# Python + Tkinter + SQLite3
#
# Features:
# 1. Add Donor
# 2. View All Donors
# 3. Search by ONE PARTICULAR Blood Group
# 4. Update Donor
# 5. Delete Donor
# 6. Clear Form
# 7. Stock Summary
# ============================================================

import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime


# ============================================================
# 1. DATABASE SETUP
# ============================================================

DB_NAME = "blood_bank.db"


def connect_db():
    """Create a connection to the SQLite database."""
    return sqlite3.connect(DB_NAME)


def create_table():
    """Create donors table if it does not already exist."""

    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS donors (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            age INTEGER NOT NULL,
            blood_group TEXT NOT NULL,
            phone TEXT NOT NULL,
            city TEXT NOT NULL,
            donation_count INTEGER NOT NULL DEFAULT 0,
            last_donation_date TEXT
        )
    """)

    conn.commit()

    # ---- Migration: add columns if an older DB already exists ----

    cursor.execute("PRAGMA table_info(donors)")

    existing_columns = [row[1] for row in cursor.fetchall()]

    if "donation_count" not in existing_columns:

        cursor.execute("""
            ALTER TABLE donors
            ADD COLUMN donation_count INTEGER NOT NULL DEFAULT 0
        """)

        conn.commit()

    if "last_donation_date" not in existing_columns:

        cursor.execute("""
            ALTER TABLE donors
            ADD COLUMN last_donation_date TEXT
        """)

        conn.commit()

    conn.close()


# ============================================================
# 2. DATABASE OPERATIONS
# ============================================================

def add_donor(name, age, blood_group, phone, city, donation_count=0):
    """Add a new donor."""

    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO donors
        (name, age, blood_group, phone, city, donation_count)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (name, age, blood_group, phone, city, donation_count))

    conn.commit()
    conn.close()


def get_all_donors():
    """Get all donor records."""

    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT * FROM donors
        ORDER BY id
    """)

    rows = cursor.fetchall()

    conn.close()

    return rows


def search_by_blood_group(blood_group):
    """
    Search donors using EXACT blood group.

    Example:
    If blood_group = 'O+'
    only O+ donors will be returned.
    """

    conn = connect_db()
    cursor = conn.cursor()

    # Exact match using =
    cursor.execute("""
        SELECT *
        FROM donors
        WHERE blood_group = ?
        ORDER BY id
    """, (blood_group,))

    rows = cursor.fetchall()

    conn.close()

    return rows


def update_donor(donor_id, name, age, blood_group, phone, city, donation_count):
    """Update selected donor."""

    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE donors
        SET name = ?,
            age = ?,
            blood_group = ?,
            phone = ?,
            city = ?,
            donation_count = ?
        WHERE id = ?
    """, (name, age, blood_group, phone, city, donation_count, donor_id))

    conn.commit()
    conn.close()


def increment_donation(donor_id):
    """Increase a donor's donation count by 1 and stamp the current
    date/time as their last donation (records a new donation).

    Returns a tuple: (updated_donation_count, last_donation_date_str)
    """

    conn = connect_db()
    cursor = conn.cursor()

    now_str = datetime.now().strftime("%d-%b-%Y %I:%M %p")

    cursor.execute("""
        UPDATE donors
        SET donation_count = donation_count + 1,
            last_donation_date = ?
        WHERE id = ?
    """, (now_str, donor_id))

    conn.commit()

    cursor.execute("""
        SELECT donation_count, last_donation_date
        FROM donors
        WHERE id = ?
    """, (donor_id,))

    new_count, last_donation_date = cursor.fetchone()

    conn.close()

    return new_count, last_donation_date


def delete_donor(donor_id):
    """Delete selected donor."""

    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
        DELETE FROM donors
        WHERE id = ?
    """, (donor_id,))

    conn.commit()
    conn.close()


def get_blood_group_summary():
    """Get donor count for each blood group."""

    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT blood_group, COUNT(*)
        FROM donors
        GROUP BY blood_group
        ORDER BY blood_group
    """)

    rows = cursor.fetchall()

    conn.close()

    return rows


# ============================================================
# 3. BLOOD GROUPS
# ============================================================

BLOOD_GROUPS = [
    "A+",
    "A-",
    "B+",
    "B-",
    "AB+",
    "AB-",
    "O+",
    "O-"
]


# ============================================================
# 4. MAIN APPLICATION
# ============================================================

class BloodBankApp:

    def __init__(self, root):

        self.root = root

        self.root.title("Blood Bank Management System")

        self.root.geometry("900x600")

        self.root.resizable(False, False)

        # Stores selected donor ID
        self.selected_id = None

        # Build GUI
        self.build_form()
        self.build_buttons()
        self.build_table()

        # Display all donors initially
        self.refresh_table()


    # ========================================================
    # FORM
    # ========================================================

    def build_form(self):

        frame = tk.LabelFrame(
            self.root,
            text="Donor Details",
            padx=10,
            pady=10
        )

        frame.place(
            x=10,
            y=10,
            width=880,
            height=175
        )

        # ---------------- NAME ----------------

        tk.Label(
            frame,
            text="Name:"
        ).grid(
            row=0,
            column=0,
            sticky="w",
            padx=5,
            pady=5
        )

        self.name_var = tk.StringVar()

        tk.Entry(
            frame,
            textvariable=self.name_var,
            width=25
        ).grid(
            row=0,
            column=1,
            padx=5
        )


        # ---------------- AGE ----------------

        tk.Label(
            frame,
            text="Age:"
        ).grid(
            row=0,
            column=2,
            sticky="w",
            padx=5
        )

        self.age_var = tk.StringVar()

        tk.Entry(
            frame,
            textvariable=self.age_var,
            width=10
        ).grid(
            row=0,
            column=3,
            padx=5
        )


        # ---------------- BLOOD GROUP ----------------

        tk.Label(
            frame,
            text="Blood Group:"
        ).grid(
            row=0,
            column=4,
            sticky="w",
            padx=5
        )

        self.bg_var = tk.StringVar()

        self.blood_group_combo = ttk.Combobox(
            frame,
            textvariable=self.bg_var,
            values=BLOOD_GROUPS,
            width=10,
            state="readonly"
        )

        self.blood_group_combo.grid(
            row=0,
            column=5,
            padx=5
        )


        # ---------------- PHONE ----------------

        tk.Label(
            frame,
            text="Phone:"
        ).grid(
            row=1,
            column=0,
            sticky="w",
            padx=5,
            pady=5
        )

        self.phone_var = tk.StringVar()

        tk.Entry(
            frame,
            textvariable=self.phone_var,
            width=25
        ).grid(
            row=1,
            column=1,
            padx=5
        )


        # ---------------- CITY ----------------

        tk.Label(
            frame,
            text="City:"
        ).grid(
            row=1,
            column=2,
            sticky="w",
            padx=5
        )

        self.city_var = tk.StringVar()

        tk.Entry(
            frame,
            textvariable=self.city_var,
            width=25
        ).grid(
            row=1,
            column=3,
            columnspan=2,
            padx=5
        )


        # ---------------- DONATIONS ----------------

        tk.Label(
            frame,
            text="Donations:"
        ).grid(
            row=1,
            column=5,
            sticky="w",
            padx=5
        )

        self.donation_var = tk.StringVar(value="0")

        tk.Entry(
            frame,
            textvariable=self.donation_var,
            width=10
        ).grid(
            row=1,
            column=6,
            padx=5
        )


        # ---------------- LAST DONATION (read-only) ----------------

        tk.Label(
            frame,
            text="Last Donation:"
        ).grid(
            row=2,
            column=0,
            sticky="w",
            padx=5,
            pady=5
        )

        self.last_donation_var = tk.StringVar(value="Not recorded")

        tk.Entry(
            frame,
            textvariable=self.last_donation_var,
            width=40,
            state="readonly"
        ).grid(
            row=2,
            column=1,
            columnspan=4,
            sticky="w",
            padx=5
        )


    # ========================================================
    # BUTTONS AND SEARCH
    # ========================================================

    def build_buttons(self):

        frame = tk.Frame(self.root)

        frame.place(
            x=10,
            y=195,
            width=880,
            height=75
        )


        # ---------------- ADD ----------------

        tk.Button(
            frame,
            text="Add Donor",
            width=13,
            bg="#4CAF50",
            fg="white",
            command=self.handle_add
        ).pack(
            side="left",
            padx=3
        )


        # ---------------- UPDATE ----------------

        tk.Button(
            frame,
            text="Update Selected",
            width=15,
            bg="#2196F3",
            fg="white",
            command=self.handle_update
        ).pack(
            side="left",
            padx=3
        )


        # ---------------- DELETE ----------------

        tk.Button(
            frame,
            text="Delete Selected",
            width=15,
            bg="#f44336",
            fg="white",
            command=self.handle_delete
        ).pack(
            side="left",
            padx=3
        )


        # ---------------- CLEAR ----------------

        tk.Button(
            frame,
            text="Clear Form",
            width=12,
            command=self.clear_form
        ).pack(
            side="left",
            padx=3
        )


        # ---------------- SHOW ALL ----------------

        tk.Button(
            frame,
            text="Show All",
            width=12,
            command=self.show_all
        ).pack(
            side="left",
            padx=3
        )


        # ---------------- STOCK SUMMARY ----------------

        tk.Button(
            frame,
            text="Stock Summary",
            width=14,
            bg="#9C27B0",
            fg="white",
            command=self.show_summary
        ).pack(
            side="left",
            padx=3
        )


        # ---------------- RECORD DONATION ----------------

        tk.Button(
            frame,
            text="Record Donation +1",
            width=16,
            bg="#E91E63",
            fg="white",
            command=self.handle_record_donation
        ).pack(
            side="left",
            padx=3
        )


        # ====================================================
        # SEARCH SECTION
        # ====================================================

        search_frame = tk.Frame(self.root)

        search_frame.place(
            x=10,
            y=275,
            width=880,
            height=50
        )


        tk.Label(
            search_frame,
            text="Search ONE Blood Group:",
            font=("Arial", 10, "bold")
        ).pack(
            side="left",
            padx=5
        )


        self.search_var = tk.StringVar()


        self.search_combo = ttk.Combobox(
            search_frame,
            textvariable=self.search_var,
            values=BLOOD_GROUPS,
            width=12,
            state="readonly"
        )

        self.search_combo.pack(
            side="left",
            padx=5
        )


        # Search button

        tk.Button(
            search_frame,
            text="🔍 Search",
            width=12,
            bg="#FF9800",
            fg="white",
            command=self.handle_search
        ).pack(
            side="left",
            padx=5
        )


        # Clear search button

        tk.Button(
            search_frame,
            text="Clear Search",
            width=12,
            command=self.clear_search
        ).pack(
            side="left",
            padx=5
        )


    # ========================================================
    # TABLE
    # ========================================================

    def build_table(self):

        columns = (
            "id",
            "name",
            "age",
            "blood_group",
            "phone",
            "city",
            "donation_count",
            "last_donation_date"
        )

        self.tree = ttk.Treeview(
            self.root,
            columns=columns,
            show="headings",
            height=13
        )


        headings = [
            "ID",
            "Name",
            "Age",
            "Blood Group",
            "Phone",
            "City",
            "Donations",
            "Last Donation"
        ]


        widths = [
            40,
            140,
            40,
            90,
            110,
            120,
            80,
            140
        ]


        for col, heading, width in zip(
            columns,
            headings,
            widths
        ):

            self.tree.heading(
                col,
                text=heading
            )

            self.tree.column(
                col,
                width=width,
                anchor="center"
            )


        self.tree.place(
            x=10,
            y=330,
            width=880,
            height=250
        )


        # When a row is selected

        self.tree.bind(
            "<<TreeviewSelect>>",
            self.on_row_select
        )


    # ========================================================
    # ADD DONOR
    # ========================================================

    def handle_add(self):

        name, age, bg, phone, city, donations = self.get_form_values()


        if not self.validate(
            name,
            age,
            bg,
            phone,
            city,
            donations
        ):
            return


        add_donor(
            name,
            int(age),
            bg,
            phone,
            city,
            int(donations)
        )


        messagebox.showinfo(
            "Success",
            "Donor added successfully!"
        )


        self.clear_form()

        self.refresh_table()


    # ========================================================
    # UPDATE DONOR
    # ========================================================

    def handle_update(self):

        if self.selected_id is None:

            messagebox.showwarning(
                "No Selection",
                "Please select a donor from the table first."
            )

            return


        name, age, bg, phone, city, donations = self.get_form_values()


        if not self.validate(
            name,
            age,
            bg,
            phone,
            city,
            donations
        ):
            return


        update_donor(
            self.selected_id,
            name,
            int(age),
            bg,
            phone,
            city,
            int(donations)
        )


        messagebox.showinfo(
            "Success",
            "Donor updated successfully!"
        )


        self.clear_form()

        self.refresh_table()


    # ========================================================
    # DELETE DONOR
    # ========================================================

    def handle_delete(self):

        if self.selected_id is None:

            messagebox.showwarning(
                "No Selection",
                "Please select a donor from the table first."
            )

            return


        confirm = messagebox.askyesno(
            "Confirm Delete",
            "Are you sure you want to delete this donor?"
        )


        if confirm:

            delete_donor(
                self.selected_id
            )


            messagebox.showinfo(
                "Deleted",
                "Donor deleted successfully!"
            )


            self.clear_form()

            self.refresh_table()


    # ========================================================
    # RECORD DONATION (+1)
    # ========================================================

    def handle_record_donation(self):

        if self.selected_id is None:

            messagebox.showwarning(
                "No Selection",
                "Please select a donor from the table first."
            )

            return


        new_count, last_donation_date = increment_donation(
            self.selected_id
        )


        times_word = "time" if new_count == 1 else "times"

        messagebox.showinfo(
            "Donation Recorded",
            f"Donation recorded successfully!\n"
            f"This donor has now donated {new_count} {times_word}.\n"
            f"Recorded on: {last_donation_date}"
        )


        self.clear_form()

        self.refresh_table()


    # ========================================================
    # SEARCH ONE PARTICULAR BLOOD GROUP
    # ========================================================

    def handle_search(self):

        # Get selected blood group
        blood_group = self.search_var.get().strip()


        # Check whether user selected a group

        if not blood_group:

            messagebox.showwarning(
                "Search",
                "Please select ONE blood group."
            )

            return


        # Search exact blood group

        rows = search_by_blood_group(
            blood_group
        )


        # If no donor found, show "No data found" inside the table

        if not rows:

            self.show_no_data_row()

            messagebox.showinfo(
                "Search Result",
                f"No donors found for blood group: {blood_group}"
            )

            return


        # Otherwise, load the matching rows into the table

        self.load_rows_into_table(rows)


        # Highlight (select) all matching rows so they show
        # with the blue selection bar

        self.tree.selection_set(
            self.tree.get_children()
        )


        # Show number of matching donors

        messagebox.showinfo(
            "Search Result",
            f"{len(rows)} donor(s) found for blood group: {blood_group}"
        )


    # ========================================================
    # CLEAR SEARCH
    # ========================================================

    def clear_search(self):

        self.search_var.set("")

        self.refresh_table()


    # ========================================================
    # SHOW ALL DONORS
    # ========================================================

    def show_all(self):

        self.search_var.set("")

        self.refresh_table()


    # ========================================================
    # STOCK SUMMARY
    # ========================================================

    def show_summary(self):

        data = get_blood_group_summary()


        if not data:

            messagebox.showinfo(
                "Stock Summary",
                "No donor records available."
            )

            return


        # Create dictionary from database results

        summary = dict(data)


        # Display ALL blood groups, including groups with 0 donors

        message = ""

        for group in BLOOD_GROUPS:

            count = summary.get(group, 0)

            message += f"{group} : {count} donor(s)\n"


        messagebox.showinfo(
            "Blood Group-wise Donor Count",
            message
        )


    # ========================================================
    # SELECT ROW
    # ========================================================

    def on_row_select(self, event):

        selected = self.tree.focus()


        if not selected:
            return


        values = self.tree.item(
            selected,
            "values"
        )


        if not values:
            return


        # Ignore clicks on the "No data found" placeholder row

        if not str(values[0]).strip():
            return


        self.selected_id = int(values[0])


        self.name_var.set(values[1])

        self.age_var.set(values[2])

        self.bg_var.set(values[3])

        self.phone_var.set(values[4])

        self.city_var.set(values[5])

        # values[6] is displayed as "X time(s)" — pull out just the number

        donation_digits = "".join(
            ch for ch in str(values[6]) if ch.isdigit()
        )

        self.donation_var.set(donation_digits if donation_digits else "0")


        # values[7] is the last donation date/time (already formatted)

        self.last_donation_var.set(str(values[7]))


    # ========================================================
    # GET FORM VALUES
    # ========================================================

    def get_form_values(self):

        return (
            self.name_var.get().strip(),
            self.age_var.get().strip(),
            self.bg_var.get().strip(),
            self.phone_var.get().strip(),
            self.city_var.get().strip(),
            self.donation_var.get().strip()
        )


    # ========================================================
    # VALIDATION
    # ========================================================

    def validate(
        self,
        name,
        age,
        blood_group,
        phone,
        city,
        donations
    ):

        # Check empty fields

        if not name:

            messagebox.showerror(
                "Missing Field",
                "Please enter donor name."
            )

            return False


        if not age:

            messagebox.showerror(
                "Missing Field",
                "Please enter donor age."
            )

            return False


        if not blood_group:

            messagebox.showerror(
                "Missing Field",
                "Please select blood group."
            )

            return False


        if not phone:

            messagebox.showerror(
                "Missing Field",
                "Please enter phone number."
            )

            return False


        if not city:

            messagebox.showerror(
                "Missing Field",
                "Please enter city."
            )

            return False


        # Age validation

        if not age.isdigit():

            messagebox.showerror(
                "Invalid Age",
                "Age must contain numbers only."
            )

            return False


        age_number = int(age)


        if age_number < 18 or age_number > 100:

            messagebox.showerror(
                "Invalid Age",
                "Age must be between 18 and 100."
            )

            return False


        # Phone validation

        if not phone.isdigit():

            messagebox.showerror(
                "Invalid Phone",
                "Phone number must contain numbers only."
            )

            return False


        if len(phone) != 10:

            messagebox.showerror(
                "Invalid Phone",
                "Phone number must contain exactly 10 digits."
            )

            return False


        # Donations validation

        if not donations.isdigit():

            messagebox.showerror(
                "Invalid Donations",
                "Donations must contain numbers only (0 or more)."
            )

            return False


        return True


    # ========================================================
    # CLEAR FORM
    # ========================================================

    def clear_form(self):

        self.name_var.set("")

        self.age_var.set("")

        self.bg_var.set("")

        self.phone_var.set("")

        self.city_var.set("")

        self.donation_var.set("0")

        self.last_donation_var.set("Not recorded")

        self.selected_id = None


        # Remove selected table row

        for item in self.tree.selection():

            self.tree.selection_remove(item)


    # ========================================================
    # LOAD ROWS INTO TABLE
    # ========================================================

    def load_rows_into_table(self, rows):

        # Delete old rows

        for item in self.tree.get_children():

            self.tree.delete(item)


        # Insert new rows

        for row in rows:

            row = list(row)

            # Format donation count as "X time(s)" for readability

            count = row[-2]

            times_word = "time" if count == 1 else "times"

            row[-2] = f"{count} {times_word}"


            # Format last donation date (blank if never donated)

            last_date = row[-1]

            row[-1] = last_date if last_date else "Not recorded"

            self.tree.insert(
                "",
                "end",
                values=row
            )


    # ========================================================
    # SHOW "NO DATA FOUND" IN TABLE
    # ========================================================

    def show_no_data_row(self):

        # Delete old rows

        for item in self.tree.get_children():

            self.tree.delete(item)


        # Insert a single placeholder row so the table itself
        # visibly communicates that nothing was found

        self.tree.insert(
            "",
            "end",
            values=("", "", "", "No data found", "", "", "", "")
        )


    # ========================================================
    # REFRESH TABLE
    # ========================================================

    def refresh_table(self):

        rows = get_all_donors()

        self.load_rows_into_table(rows)


# ============================================================
# 5. MAIN PROGRAM
# ============================================================

if __name__ == "__main__":

    # Create database and table
    create_table()

    # Create Tkinter window
    root = tk.Tk()

    # Create application
    app = BloodBankApp(root)

    # Start application
    root.mainloop()