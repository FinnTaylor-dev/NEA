import json
import os
import tkinter as tk
from tkinter import ttk

import customtkinter as ctk

# Constants
PROFILE_PATH = "data/profile.json"
ACTIVITY_MULTIPLIERS = {
    "Sedentary": 1.2,
    "Lightly Active": 1.375,
    "Moderately Active": 1.55,
    "Very Active": 1.725,
}


def profile_exists():
    if not os.path.exists(PROFILE_PATH):
        return False
    if os.path.getsize(PROFILE_PATH) == 0:
        return False
    try:
        with open(PROFILE_PATH) as f:
            data = json.load(f)
        return isinstance(data, dict) and "gender" in data
    except (json.JSONDecodeError, OSError):
        return False


def load_profile():
    with open(PROFILE_PATH) as f:
        return json.load(f)


class App:
    def __init__(self, root):
        self.root = root
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

        self.frames = {}

        for F in (SetupPage, MainPage, SettingPage):
            frame = F(self.root, self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        if profile_exists():
            self.show_frame(MainPage)
        else:
            self.show_frame(SetupPage)

    def show_frame(self, cont):
        self.frames[cont].tkraise()

    def refresh_main_page(self):
        main = self.frames[MainPage]

        if profile_exists():
            main.load_and_show_profile()
        else:
            main.info_label.config(text="No profile found. Please complete setup.")


class SetupPage(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.parent = app

        # Title
        label = ctk.CTkLabel(self, text="Setup", justify="center")
        label.grid(row=0, column=0, columnspan=3, sticky="ew", pady=10)

        # Gender
        self.gender_var = tk.StringVar(value="Male")
        ttk.Label(self, text="Gender:").grid(
            row=1, column=0, sticky="w", padx=5, pady=5
        )
        ctk.CTkRadioButton(
            self, text="Male", variable=self.gender_var, value="Male"
        ).grid(row=1, column=1, sticky="w")
        ctk.CTkRadioButton(
            self, text="Female", variable=self.gender_var, value="Female"
        ).grid(row=1, column=2, sticky="w")

        # Weight
        ttk.Label(self, text="Weight (kg):").grid(
            row=2, column=0, sticky="w", padx=5, pady=5
        )
        self.weight_entry = ttk.Entry(self, state="normal")
        self.weight_entry.grid(
            row=2, column=1, columnspan=2, sticky="ew", padx=5, pady=5
        )
        self.weight_entry.insert(0, "67")

        # Height
        ttk.Label(self, text="Height (cm):").grid(
            row=3, column=0, sticky="w", padx=5, pady=5
        )
        self.height_entry = ttk.Entry(self)
        self.height_entry.grid(
            row=3, column=1, columnspan=2, sticky="ew", padx=5, pady=5
        )
        self.height_entry.insert(0, "178")

        # Age
        ttk.Label(self, text="Age:").grid(row=4, column=0, sticky="w", padx=5, pady=5)
        self.age_entry = ttk.Entry(self)
        self.age_entry.grid(row=4, column=1, columnspan=2, sticky="ew", padx=5, pady=5)
        self.age_entry.insert(0, "17")

        # Body Fat
        ttk.Label(self, text="Body Fat (%) (leave at 0 if unknown):").grid(
            row=5, column=0, sticky="w", padx=5, pady=5
        )
        self.bodyfat_entry = ttk.Entry(self)
        self.bodyfat_entry.grid(
            row=5, column=1, columnspan=2, sticky="ew", padx=5, pady=5
        )
        self.bodyfat_entry.insert(0, "0")

        # Activity level
        tk.Label(self, text="Activity Level:").grid(
            row=6, column=0, sticky="w", padx=5, pady=5
        )
        levels = ["Sedentary", "Lightly Active", "Moderately Active", "Very Active"]
        self.activity_var = tk.StringVar(value=levels[0])
        self.activity_entry = tk.OptionMenu(
            self, self.activity_var, *levels, command=self._update_activity_desc
        )
        self.activity_entry.grid(
            row=6, column=1, columnspan=2, sticky="ew", padx=5, pady=5
        )

        ACTIVITY_DESC = {
            "Sedentary": "Sedentary is a desk job, a drive to work, and evenings on the couch. Under 5,000 steps a day, no regular exercise. Most office workers without a training habit are here, whether it feels that way or not.",
            "Lightly Active": "Lightly active is someone who walks the dog daily and hits the gym once or twice. Five to seven thousand steps, a short daily walk, a couple of casual workouts a week.",
            "Moderately Active": "Moderately active is where most recreational athletes actually belong. Three to five real training sessions a week, or a job that keeps you on your feet. Seven to ten thousand steps. A cyclist who commutes and lifts on weekends. A parent chasing young kids around a playground.",
            "Very Active": "Very active means six or seven training sessions a week plus a physically demanding day. Ten to twelve thousand steps. Construction workers, personal trainers who demonstrate all day, people deep in marathon training. A desk job with four gym sessions is not very active, no matter how hard the sessions felt.",
        }
        self.ACTIVITY_DESC = ACTIVITY_DESC

        description = ACTIVITY_DESC.get(
            self.activity_var.get(),
            "Sedentary is a desk job, a drive to work, and evenings on the couch. Under 5,000 steps a day, no regular exercise. Most office workers without a training habit are here, whether it feels that way or not.",
        )
        self.desc_label = tk.Label(
            self, text=description, justify="center", wraplength=400
        )
        self.desc_label.grid(
            row=7, column=0, columnspan=3, sticky="ew", padx=5, pady=10
        )
        # submit button
        submit_btn = ctk.CTkButton(self, text="Submit", command=self.submit)
        submit_btn.grid(row=8, column=0, columnspan=3, pady=10)

        # Result
        self.result_label = ttk.Label(self, text="", justify="center")
        self.result_label.grid(row=9, column=0, columnspan=3, sticky="w", pady=5)

    def _update_activity_desc(self, _value=None):
        level = self.activity_var.get()
        default = (
            "Sedentary is a desk job, a drive to work, and evenings on the couch. "
            "Under 5,000 steps a day, no regular exercise. Most office workers "
            "without a training habit are here, whether it feels that way or not."
        )
        description = self.ACTIVITY_DESC.get(level, default)
        self.desc_label.config(text=description)

    def submit(self):
        gender_val = self.gender_var.get()
        try:
            weight_val = float(self.weight_entry.get())
            height_val = float(self.height_entry.get())
            age_val = int(self.age_entry.get())
            bodyfat_val = float(self.bodyfat_entry.get())
        except ValueError:
            self.result_label.config(  # ty:ignore[unresolved-attribute]
                text="Please enter valid numbers for weight, height, age, and body fat."
            )
            return

        activity_val = self.activity_var.get()

        profile = {
            "gender": gender_val,
            "weight_kg": weight_val,
            "height_cm": height_val,
            "age": age_val,
            "bodyfat_percent": bodyfat_val,
            "activity_level": activity_val,
        }

        self.save_profile(profile)

        self.result_label.config(text="Profile saved.\n\n")
        self.parent.refresh_main_page()
        self.parent.show_frame(MainPage)

    def save_profile(self, data: dict):
        os.makedirs(os.path.dirname(PROFILE_PATH), exist_ok=True)

        with open(PROFILE_PATH, "w") as f:
            json.dump(data, f, indent=2)


class MainPage(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.parent = app
        self.title_label = tk.Label(self, text="Main Page", justify="center")
        self.title_label.pack(fill="x", pady=10)

        self.info_label = tk.Label(self, text="", justify="left")
        self.info_label.pack(fill="both", expand=True, padx=10, pady=10)

        self.reset_btn = ttk.Button(
            self, text="Reset profile", command=self.reset_profile
        )
        self.reset_btn.pack(pady=10)

        self.setting_btn = ctk.CTkButton(self, text="Settings", command=self.settings)
        self.setting_btn.pack(pady=10)

        # Only load and show profile if it exists
        if profile_exists():
            self.load_and_show_profile()
        else:
            self.info_label.config(text="No profile found. Please complete setup.")

    def load_and_show_profile(self):
        profile = load_profile()
        gender = profile["gender"]
        weight = profile["weight_kg"]
        height = profile["height_cm"]
        age = profile["age"]
        bodyfat = profile["bodyfat_percent"]
        activity_level = profile["activity_level"]

        bmr, tdee = calculate_bmr_tdee(
            gender, weight, height, age, bodyfat, activity_level
        )
        info = (
            f"Gender: {gender}\n"
            f"Weight: {weight} kg\n"
            f"Height: {height} cm\n"
            f"Age: {age}\n"
            f"Body Fat: {bodyfat} %\n\n"
            f"BMR: {bmr:.1f} kcal/day\n"
            f"TDEE: {tdee:.1f} kcal/day"
        )
        self.info_label.config(text=info)

    def reset_profile(self):
        if os.path.exists(PROFILE_PATH):
            os.remove(PROFILE_PATH)

        self.info_label.config(text="")
        self.parent.show_frame(SetupPage)

    def settings(self):
        self.parent.show_frame(SettingPage)


class SettingPage(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.parent = app

        self.title_label = tk.Label(self, text="Settings", justify="center")
        self.title_label.pack(fill="x", pady=10)

        self.info_label = tk.Label(self, text="", justify="left")
        self.info_label.pack(fill="both", expand=True, padx=10, pady=10)

        # Only load and show profile if it exists
        if profile_exists():
            profile = load_profile()
        else:
            self.info_label.config(text="No profile found. Please complete setup.")

        # print(profile)


# calculations


# bmr - resting metabolism - mifflin st jeor equation (used when no bf entered)
def calculate_bmr_tdee(gender, weight, height, age, bodyfat, activity_level):
    bmr = 0
    if bodyfat == 0:
        if gender == "male":
            bmr = (10 * weight) + (6.25 * height) - (5 * age) + 5
        elif gender == "female":
            bmr = (10 * weight) + (6.25 * height) - (5 * age) - 161
    else:
        # Katch-McArdle equation
        LBM = weight * (1 - bodyfat / 100.0)  # bodyfat as percent
        bmr = 370 + 21.6 * LBM

    multiplier = ACTIVITY_MULTIPLIERS.get(activity_level, 1.2)
    TDEE = bmr * multiplier
    return bmr, TDEE


# macronutrient split
def calculate_macro(tdee, protein, fat, carbs):
    PROTEIN_ENERGY, CARB_ENERGY = 4, 4  # 4 kcal per gram
    FAT_ENERGY = 9  # 9 kcal per gram

    protein_grams = (tdee * protein) / PROTEIN_ENERGY
    fat_grams = (tdee * fat) / FAT_ENERGY
    carb_grams = (tdee * carbs) / CARB_ENERGY

    return protein_grams, fat_grams, carb_grams


if __name__ == "__main__":
    root = ctk.CTk()
    root.title("NutriTracker")
    root.minsize(500, 500)
    root.geometry("500x500")
    app = App(root)
    root.mainloop()
