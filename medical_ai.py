import tkinter as tk
from tkinter import messagebox
import datetime
import os

# ==============================================================================
# MEDICAL KNOWLEDGE BASE & EXPERT SYSTEM DATA
# ==============================================================================
SYMPTOMS = {
    "fever": "Fever (High Temperature)",
    "cough": "Dry or Wet Cough",
    "headache": "Severe Headache",
    "body_pain": "Body & Muscle Aches",
    "rash": "Skin Rash or Redness",
    "nausea": "Nausea or Vomiting",
    "chest_pain": "Chest Pain / Tightness",
    "sore_throat": "Sore Throat",
    "shortness_breath": "Shortness of Breath",
    "fatigue": "Extreme Fatigue & Weakness",
    "runny_nose": "Runny or Stuffy Nose",
    "loss_taste_smell": "Loss of Taste or Smell"
}

DISEASES = {
    "COVID-19": {
        "symptoms": {
            "fever": 0.8,
            "cough": 0.9,
            "loss_taste_smell": 1.0,
            "shortness_breath": 0.9,
            "fatigue": 0.7,
            "body_pain": 0.5,
            "sore_throat": 0.5
        },
        "description": "A highly contagious respiratory illness caused by the SARS-CoV-2 virus. It can range from mild cases to severe respiratory distress.",
        "precautions": [
            "Self-isolate immediately in a well-ventilated room.",
            "Monitor blood oxygen levels (SpO2) using a pulse oximeter.",
            "Wear a high-filtering mask (N95) to protect household members.",
            "Stay hydrated, rest, and contact medical services."
        ],
        "urgency": "High"
    },
    "Dengue Fever": {
        "symptoms": {
            "fever": 1.0,
            "body_pain": 1.0,
            "headache": 0.8,
            "rash": 0.7,
            "nausea": 0.6,
            "fatigue": 0.7
        },
        "description": "A mosquito-borne viral infection causing severe flu-like illness. It can sometimes progress to a severe bleeding complication.",
        "precautions": [
            "Rest completely and prevent physical strain.",
            "Maintain high fluid intake (water, ORS, fruit juice) to combat dehydration.",
            "Use Paracetamol for fever; strictly avoid Ibuprofen/Aspirin due to bleeding risk.",
            "Seek immediate care if you experience abdominal pain or nose/gum bleeding."
        ],
        "urgency": "High"
    },
    "Chest Infection (Pneumonia/Bronchitis)": {
        "symptoms": {
            "cough": 0.9,
            "chest_pain": 1.0,
            "shortness_breath": 0.8,
            "fever": 0.5,
            "fatigue": 0.6
        },
        "description": "An infection of the lungs or bronchial tubes, leading to breathing difficulties and painful coughing.",
        "precautions": [
            "Seek a doctor's evaluation as antibiotics or inhalers might be required.",
            "Perform steam inhalation twice daily to loosen chest congestion.",
            "Elevate your head while sleeping to ease breathing.",
            "Avoid cold drinks, smoking, and dusty environments."
        ],
        "urgency": "High"
    },
    "Flu (Influenza)": {
        "symptoms": {
            "fever": 1.0,
            "cough": 0.8,
            "body_pain": 0.9,
            "fatigue": 0.8,
            "headache": 0.6,
            "sore_throat": 0.5
        },
        "description": "A common contagious respiratory virus that affects the nose, throat, and lungs, with rapid onset of symptoms.",
        "precautions": [
            "Stay at home, rest in bed, and avoid physical strain.",
            "Drink plenty of warm liquids (teas, broth, warm water) to soothe the airway.",
            "Take over-the-counter fever reducers if temperature exceeds 101°F.",
            "Cover your mouth when coughing and sanitize hands frequently."
        ],
        "urgency": "Medium"
    },
    "Common Cold": {
        "symptoms": {
            "cough": 0.6,
            "runny_nose": 1.0,
            "sore_throat": 0.8,
            "fatigue": 0.4,
            "headache": 0.3
        },
        "description": "A mild, self-limiting viral infection of the nose, sinuses, and throat causing congestion and sneezing.",
        "precautions": [
            "Get sufficient sleep and stay warm.",
            "Use a saline nasal wash or drops to clear nasal passages.",
            "Gargle warm salt water to relieve throat irritation.",
            "Stay hydrated by drinking plenty of water."
        ],
        "urgency": "Low"
    },
    "Migraine": {
        "symptoms": {
            "headache": 1.0,
            "nausea": 0.8,
            "fatigue": 0.3
        },
        "description": "A neurological condition characterized by intense, pulsing headache episodes, often with sensory sensitivities.",
        "precautions": [
            "Lie down in a dark, silent, and cool room.",
            "Apply a cold compress to the forehead or back of the neck.",
            "Avoid sensory triggers such as strong lights, loud sounds, and screen time.",
            "Stay hydrated and try to rest or sleep."
        ],
        "urgency": "Low"
    },
    "Gastroenteritis (Stomach Flu)": {
        "symptoms": {
            "nausea": 1.0,
            "body_pain": 0.4,
            "fever": 0.3,
            "fatigue": 0.5
        },
        "description": "An inflammation of the stomach and intestines, commonly presenting as nausea, vomiting, or stomach cramps.",
        "precautions": [
            "Sip clear fluids or electrolyte solutions constantly to avoid dehydration.",
            "Eat small, bland meals (rice, toast, crackers) when ready.",
            "Avoid dairy, caffeine, spicy foods, and carbonated beverages.",
            "Wash hands thoroughly to prevent contamination."
        ],
        "urgency": "Medium"
    },
    "Allergies": {
        "symptoms": {
            "runny_nose": 0.8,
            "cough": 0.3,
            "headache": 0.2
        },
        "description": "An immune response triggered by airborne allergens like pollen, dust, or pet dander.",
        "precautions": [
            "Minimize outdoor exposure during high pollen days.",
            "Keep indoor spaces clean and wash linens in hot water.",
            "Consider non-drowsy over-the-counter antihistamines.",
            "Use a nasal saline rinse to clear out allergens."
        ],
        "urgency": "Low"
    },
    "Common Fever": {
        "symptoms": {
            "fever": 1.0
        },
        "description": "A temporary spike in body temperature, usually indicating the body is fighting off a minor infection.",
        "precautions": [
            "Drink plenty of water and rest.",
            "Wear light, breathable clothing to help heat escape.",
            "Take a lukewarm bath or use damp washcloths on the forehead.",
            "Consult a doctor if the fever exceeds 103°F or lasts more than 3 days."
        ],
        "urgency": "Low"
    }
}

# ==============================================================================
# HELPER FUNCTIONS FOR RENDERING FLAT SHAPES
# ==============================================================================
def draw_pill(canvas, x1, y1, x2, y2, fill, outline=""):
    h = y2 - y1
    r = h / 2
    canvas.create_oval(x1, y1, x1 + h, y2, fill=fill, outline=outline)
    canvas.create_oval(x2 - h, y1, x2, y2, fill=fill, outline=outline)
    canvas.create_rectangle(x1 + r, y1, x2 - r, y2, fill=fill, outline=outline)

# ==============================================================================
# CUSTOM TOGGLE SWITCH (CHECKBOX)
# ==============================================================================
class ModernCheckbox(tk.Frame):
    def __init__(self, parent, text, variable, command=None, bg="#1e293b", fg="#cbd5e1", active_color="#0d9488"):
        super().__init__(parent, bg=bg)
        self.variable = variable
        self.command = command
        self.active_color = active_color
        self.inactive_color = "#475569"
        
        # Canvas for the toggle pill switch
        self.canvas = tk.Canvas(self, width=44, height=24, bg=bg, highlightthickness=0, cursor="hand2")
        self.canvas.pack(side="left", pady=3)
        
        # Label for toggle text
        self.label = tk.Label(self, text=text, font=("Segoe UI", 10), bg=bg, fg=fg, cursor="hand2")
        self.label.pack(side="left", padx=10)
        
        self.draw_switch()
        
        # Bind mouse clicks
        self.canvas.bind("<Button-1>", self.toggle)
        self.label.bind("<Button-1>", self.toggle)
        
    def draw_switch(self):
        self.canvas.delete("all")
        val = self.variable.get()
        if val:
            draw_pill(self.canvas, 2, 2, 42, 22, fill=self.active_color)
            self.canvas.create_oval(23, 3, 41, 21, fill="#ffffff", outline="")
        else:
            draw_pill(self.canvas, 2, 2, 42, 22, fill=self.inactive_color)
            self.canvas.create_oval(3, 3, 21, 21, fill="#cbd5e1", outline="")

    def toggle(self, event=None):
        self.variable.set(not self.variable.get())
        self.draw_switch()
        if self.command:
            self.command()

# ==============================================================================
# CUSTOM GRAPHICAL PROGRESS BAR
# ==============================================================================
class ConfidenceBar(tk.Frame):
    def __init__(self, parent, label_text, percent, urgency="Low", bg="#1e293b", width=340, height=28):
        super().__init__(parent, bg=bg)
        self.label_text = label_text
        self.percent = percent
        self.width = width
        self.height = height
        
        # Color based on urgency
        if urgency == "High":
            self.fill_color = "#ef4444"  # Red
        elif urgency == "Medium":
            self.fill_color = "#f59e0b"  # Amber
        else:
            self.fill_color = "#06b6d4"  # Teal / Cyan
            
        self.canvas = tk.Canvas(self, width=width, height=height, bg=bg, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        self.draw()
        
    def update_percent(self, new_percent):
        self.percent = new_percent
        self.draw()
        
    def draw(self):
        self.canvas.delete("all")
        # Background track
        draw_pill(self.canvas, 2, 2, self.width-2, self.height-2, fill="#334155")
        
        # Fill proportion
        fill_width = int((self.width - 4) * (self.percent / 100))
        h = self.height - 4
        if fill_width > h:
            draw_pill(self.canvas, 2, 2, fill_width, self.height-2, fill=self.fill_color)
        elif fill_width > 0:
            self.canvas.create_oval(2, 2, 2 + fill_width, self.height-2, fill=self.fill_color, outline="")
            
        # Label
        self.canvas.create_text(12, self.height/2, text=self.label_text, fill="#ffffff", anchor="w", font=("Segoe UI", 9, "bold"))
        # Percentage
        self.canvas.create_text(self.width-12, self.height/2, text=f"{int(self.percent)}%", fill="#f8fafc", anchor="e", font=("Segoe UI", 9, "bold"))

# ==============================================================================
# ECG SIMULATION SCREEN WIDGET
# ==============================================================================
class ECGVisualizer(tk.Canvas):
    def __init__(self, parent, width=510, height=80, bg="#1e293b", color="#0d9488"):
        super().__init__(parent, width=width, height=height, bg=bg, highlightthickness=0)
        self.width = width
        self.height = height
        self.color = color
        self.points = [height / 2] * (width // 4)
        self.index = 0
        
        # Heartbeat shape sequence
        self.template = [0, 0, 0, 2, -2, 0, 0, 4, -4, 0, 0, -8, 28, -15, 0, 0, 6, 8, 4, 0, 0, 0, 0]
        self.template_len = len(self.template)
        
        self.animate()
        
    def animate(self):
        phase = self.index % 35
        val = self.template[phase] if phase < self.template_len else 0
            
        baseline = self.height / 2
        y = baseline - (val * 1.5)
        self.points.pop(0)
        self.points.append(y)
        
        self.delete("all")
        
        # Grid lines background
        for x in range(0, self.width, 20):
            self.create_line(x, 0, x, self.height, fill="#334155", width=1, dash=(2, 4))
        for y_grid in range(0, self.height, 20):
            self.create_line(0, y_grid, self.width, y_grid, fill="#334155", width=1, dash=(2, 4))
            
        # Draw background thicker glow
        bg_points = []
        for x, y_val in enumerate(self.points):
            bg_points.extend([x * 4, y_val])
        self.create_line(bg_points, fill="#042f2e", width=4, smooth=True)
        
        # Draw active line
        self.create_line(bg_points, fill=self.color, width=2, smooth=True)
        
        # Draw scanning bead
        self.create_oval(self.width - 6, self.points[-1] - 3, self.width, self.points[-1] + 3, fill="#14b8a6", outline="")
        
        # Monitoring status in top corner
        self.create_text(15, 15, text="● ECG MONITOR: STABLE", fill="#10b981", anchor="w", font=("Segoe UI", 8, "bold"))
        self.create_text(self.width - 15, 15, text="AI ENGINE ACTIVE", fill="#64748b", anchor="e", font=("Segoe UI", 8, "bold"))
        
        self.index += 1
        self.after(50, self.animate)

# ==============================================================================
# MAIN APPLICATION INTERFACE
# ==============================================================================
class ModernMedicalAIApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Aegis AI - Smart Medical Expert System")
        self.root.configure(bg="#0f172a")
        
        # Center the window
        width, height = 950, 700
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        root.geometry(f"{width}x{height}+{x}+{y}")
        root.resizable(False, False)
        
        self.emergency_active = False
        self.top_condition = None
        self.diagnoses = []
        
        self.create_variables()
        self.build_ui()
        self.update_diagnoses()  # Run initial screen update
        
    def create_variables(self):
        self.symptom_vars = {}
        for sym_key in SYMPTOMS.keys():
            self.symptom_vars[sym_key] = tk.BooleanVar(value=False)
            
    def build_ui(self):
        # ----------------------------------------------------
        # LEFT COLUMN (SIDEBAR - SYMPTOM SELECTOR)
        # ----------------------------------------------------
        sidebar = tk.Frame(self.root, bg="#1e293b", width=380, height=700)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)
        
        # Logo section
        logo_frame = tk.Frame(sidebar, bg="#1e293b")
        logo_frame.pack(fill="x", pady=(20, 15))
        
        logo_canvas = tk.Canvas(logo_frame, width=32, height=32, bg="#1e293b", highlightthickness=0)
        logo_canvas.pack(side="left", padx=(25, 0))
        logo_canvas.create_rectangle(12, 4, 20, 28, fill="#0d9488", outline="")
        logo_canvas.create_rectangle(4, 12, 28, 20, fill="#0d9488", outline="")
        
        logo_label = tk.Label(logo_frame, text="Aegis Medical AI", font=("Segoe UI", 16, "bold"), bg="#1e293b", fg="#f8fafc")
        logo_label.pack(side="left", padx=10)
        
        # Subtitle
        sub_title = tk.Label(sidebar, text="Interactive Symptoms Selection", font=("Segoe UI", 9), bg="#1e293b", fg="#64748b", anchor="w")
        sub_title.pack(fill="x", padx=25, pady=(0, 10))
        
        # Scrollable / Container Frame for categories
        symptoms_container = tk.Frame(sidebar, bg="#1e293b", padx=25)
        symptoms_container.pack(fill="both", expand=True)
        
        # Group symptoms by category
        categories = [
            ("CARDIO-RESPIRATORY SYMPTOMS", ["cough", "chest_pain", "shortness_breath", "runny_nose", "sore_throat"]),
            ("SYSTEMIC SYMPTOMS", ["fever", "headache", "body_pain", "fatigue"]),
            ("OTHER SYMPTOMS", ["rash", "nausea", "loss_taste_smell"])
        ]
        
        self.checkbox_widgets = {}
        for cat_name, keys in categories:
            # Header
            tk.Label(symptoms_container, text=cat_name, font=("Segoe UI", 8, "bold"), bg="#1e293b", fg="#38bdf8", anchor="w").pack(fill="x", pady=(10, 5))
            for key in keys:
                cb = ModernCheckbox(symptoms_container, text=SYMPTOMS[key], variable=self.symptom_vars[key], command=self.update_diagnoses, bg="#1e293b", fg="#cbd5e1", active_color="#0d9488")
                cb.pack(fill="x", pady=2)
                self.checkbox_widgets[key] = cb
                
        # Action Buttons frame in sidebar
        btn_frame = tk.Frame(sidebar, bg="#1e293b", padx=25, pady=15)
        btn_frame.pack(side="bottom", fill="x")
        
        # Reset button
        self.reset_btn = tk.Button(btn_frame, text="Reset Symptoms", font=("Segoe UI", 10, "bold"), bg="#ef4444", fg="#ffffff", activebackground="#dc2626", activeforeground="#ffffff", bd=0, pady=8, cursor="hand2", command=self.reset_symptoms)
        self.reset_btn.pack(side="left", fill="x", expand=True, padx=(0, 5))
        self.make_button_interactive(self.reset_btn, "#dc2626", "#ef4444")
        
        # Save report button
        self.save_btn = tk.Button(btn_frame, text="Export Report", font=("Segoe UI", 10, "bold"), bg="#10b981", fg="#ffffff", activebackground="#059669", activeforeground="#ffffff", bd=0, pady=8, cursor="hand2", command=self.save_report)
        self.save_btn.pack(side="right", fill="x", expand=True, padx=(5, 0))
        self.make_button_interactive(self.save_btn, "#059669", "#10b981")
        
        # Status Bar
        self.status_bar = tk.Label(sidebar, text="System Ready", font=("Segoe UI", 9), bg="#1e293b", fg="#64748b", anchor="w", padx=25, pady=5)
        self.status_bar.pack(side="bottom", fill="x")

        # ----------------------------------------------------
        # RIGHT COLUMN (DASHBOARD)
        # ----------------------------------------------------
        dashboard = tk.Frame(self.root, bg="#0f172a", width=570, height=700)
        dashboard.pack(side="right", fill="both", expand=True)
        dashboard.pack_propagate(False)
        
        # ECG visualizer
        self.ecg = ECGVisualizer(dashboard, width=540, height=90, bg="#0f172a", color="#0d9488")
        self.ecg.pack(fill="x", padx=15, pady=(15, 5))
        
        # Real-time reports header
        report_header = tk.Frame(dashboard, bg="#0f172a", padx=15)
        report_header.pack(fill="x", pady=5)
        
        tk.Label(report_header, text="REAL-TIME DIAGNOSTIC REPORT", font=("Segoe UI", 12, "bold"), bg="#0f172a", fg="#f8fafc").pack(anchor="w")
        tk.Label(report_header, text="Expert System confidence match for symptoms checked:", font=("Segoe UI", 9), bg="#0f172a", fg="#64748b").pack(anchor="w")
        
        # Results frame containing dynamic progress bars
        self.results_frame = tk.Frame(dashboard, bg="#0f172a", padx=15)
        self.results_frame.pack(fill="x", pady=10)
        
        # Empty placeholder label inside results frame
        self.empty_label = tk.Label(self.results_frame, text="No symptoms selected.\nChoose symptoms on the left sidebar to initiate diagnostics.", font=("Segoe UI", 11, "italic"), bg="#0f172a", fg="#475569", pady=30)
        self.empty_label.pack(fill="both")
        
        # Progress bars list reference
        self.progress_widgets = []
        
        # Card detailing top matched condition
        self.card_frame = tk.Frame(dashboard, bg="#1e293b", padx=20, pady=15)
        self.card_frame.pack(fill="both", expand=True, padx=15, pady=(5, 15))
        
        # Disclaimer Card elements (shown initially)
        self.disclaimer_title = tk.Label(self.card_frame, text="Medical Disclaimer & Information", font=("Segoe UI", 11, "bold"), bg="#1e293b", fg="#38bdf8", anchor="w")
        self.disclaimer_title.pack(fill="x", pady=(0, 5))
        
        disclaimer_text = ("This software is a rule-based expert system designed for educational, preliminary screening, "
                           "and demonstration purposes only. It is NOT a diagnostic tool and does NOT provide medical advice.\n\n"
                           "• Consult a certified physician or healthcare professional for actual diagnostic services.\n"
                           "• In case of emergency or severe symptoms, visit the nearest medical emergency center immediately.\n"
                           "• The computed scores are statistical probabilities based on weighted rules.")
        self.disclaimer_body = tk.Label(self.card_frame, text=disclaimer_text, font=("Segoe UI", 10), bg="#1e293b", fg="#cbd5e1", justify="left", wraplength=490, anchor="nw")
        self.disclaimer_body.pack(fill="both", expand=True, pady=10)
        
        # Detail Condition Elements (hidden initially, packed when diagnosis matches)
        self.detail_header = tk.Frame(self.card_frame, bg="#1e293b")
        self.detail_title = tk.Label(self.detail_header, text="COVID-19 Detected", font=("Segoe UI", 13, "bold"), bg="#1e293b", fg="#ffffff")
        self.detail_title.pack(side="left")
        
        self.urgency_tag = tk.Label(self.detail_header, text="HIGH URGENCY", font=("Segoe UI", 8, "bold"), bg="#ef4444", fg="#ffffff", padx=8, pady=2)
        self.urgency_tag.pack(side="left", padx=10)
        
        self.detail_desc = tk.Label(self.card_frame, text="Description of the disease goes here...", font=("Segoe UI", 10), bg="#1e293b", fg="#cbd5e1", justify="left", wraplength=490, anchor="w")
        self.detail_pre_header = tk.Label(self.card_frame, text="Recommended Precautions / Self-Care:", font=("Segoe UI", 10, "bold"), bg="#1e293b", fg="#38bdf8", anchor="w")
        
        self.detail_bullets = []
        for i in range(4):
            bullet = tk.Label(self.card_frame, text="• Precaution step", font=("Segoe UI", 10), bg="#1e293b", fg="#cbd5e1", justify="left", wraplength=480, anchor="w")
            self.detail_bullets.append(bullet)
            
        # Glowing Emergency Warning Banner (hidden initially)
        self.warning_banner = tk.Frame(dashboard, bg="#b91c1c", pady=10)
        self.warning_label = tk.Label(self.warning_banner, text="⚠️ EMERGENCY WARNING: Severe symptoms detected (Chest Pain / Shortness of Breath).\nPlease consult emergency medical services immediately.", font=("Segoe UI", 10, "bold"), bg="#b91c1c", fg="#ffffff", justify="center")
        self.warning_label.pack()

    def make_button_interactive(self, button, hover_bg, normal_bg):
        button.bind("<Enter>", lambda e: button.config(bg=hover_bg))
        button.bind("<Leave>", lambda e: button.config(bg=normal_bg))
        
    def reset_symptoms(self):
        for var in self.symptom_vars.values():
            var.set(False)
            
        for cb in self.checkbox_widgets.values():
            cb.draw_switch()
            
        self.update_diagnoses()
        self.show_status("Symptoms reset complete", "#38bdf8")
        
    def show_status(self, text, color="#64748b"):
        self.status_bar.config(text=text, fg=color)
        self.root.after(3500, lambda: self.status_bar.config(text="System Active", fg="#64748b"))

    def update_diagnoses(self):
        # Extract active symptom keys
        active_symptoms = [key for key, var in self.symptom_vars.items() if var.get()]
        
        # Check for emergency triggers (Chest Pain, Shortness of Breath)
        is_emergency = "chest_pain" in active_symptoms or "shortness_breath" in active_symptoms
        self.manage_emergency_state(is_emergency)
        
        # Clear current progress bars
        for bar in self.progress_widgets:
            bar.pack_forget()
            bar.destroy()
        self.progress_widgets.clear()
        
        # If no symptoms are selected, revert to default disclaimer view
        if not active_symptoms:
            self.empty_label.pack(fill="both", pady=30)
            self.show_disclaimer_view()
            self.diagnoses = []
            self.top_condition = None
            return
            
        self.empty_label.pack_forget()
        
        # Calculate diagnoses
        self.diagnoses = self.calculate_probabilities(active_symptoms)
        
        if not self.diagnoses:
            # Symptoms selected but matching score yields 0% for everything
            self.empty_label.pack(fill="both", pady=30)
            self.empty_label.config(text="Symptoms selected, but matching scores are too low.\nConsult a professional if you feel unwell.")
            self.show_disclaimer_view()
            self.top_condition = None
            return
            
        # Draw top matching bars (limit to top 3 matches)
        top_matches = self.diagnoses[:3]
        for item in top_matches:
            bar = ConfidenceBar(self.results_frame, label_text=item["disease"], percent=item["confidence"], urgency=item["urgency"], bg="#0f172a", width=530, height=26)
            bar.pack(pady=4, fill="x")
            self.progress_widgets.append(bar)
            
        # Show top matched disease details
        self.top_condition = top_matches[0]
        self.show_condition_detail_view(self.top_condition)

    def calculate_probabilities(self, active_symptoms):
        results = []
        for d_name, info in DISEASES.items():
            d_symptoms = info["symptoms"]
            
            # Sum of active symptom weights for this disease
            match_weight = 0.0
            for sym in active_symptoms:
                if sym in d_symptoms:
                    match_weight += d_symptoms[sym]
                    
            # Total weight of all symptoms of this disease
            total_weight = sum(d_symptoms.values())
            
            # Penalty for selecting symptoms not related to this disease (specificity penalty)
            mismatches = len([s for s in active_symptoms if s not in d_symptoms])
            penalty = 0.25 * mismatches  # 25% drop per irrelevant symptom selected
            
            raw_score = (match_weight / total_weight) if total_weight > 0 else 0.0
            confidence = max(0.0, raw_score - penalty) * 100
            
            if confidence > 0:
                results.append({
                    "disease": d_name,
                    "confidence": confidence,
                    "urgency": info["urgency"],
                    "description": info["description"],
                    "precautions": info["precautions"]
                })
                
        # Sort primarily by confidence, secondarily by urgency rating
        urgency_rank = {"High": 3, "Medium": 2, "Low": 1}
        results.sort(key=lambda x: (x["confidence"], urgency_rank[x["urgency"]]), reverse=True)
        return results

    def manage_emergency_state(self, active):
        self.emergency_active = active
        if active:
            if not self.warning_banner.winfo_manager():
                self.warning_banner.pack(side="bottom", fill="x", padx=15, pady=(0, 15))
                self.blink_warning()
        else:
            self.warning_banner.pack_forget()

    def blink_warning(self):
        if not self.emergency_active:
            return
        if not self.warning_banner.winfo_exists():
            return
        current_bg = self.warning_banner.cget("bg")
        # Toggle background color between bright warning red and dark warning red
        next_bg = "#7f1d1d" if current_bg == "#b91c1c" else "#b91c1c"
        self.warning_banner.config(bg=next_bg)
        self.warning_label.config(bg=next_bg)
        self.root.after(800, self.blink_warning)

    def show_disclaimer_view(self):
        # Hide detailed panels
        self.detail_header.pack_forget()
        self.detail_desc.pack_forget()
        self.detail_pre_header.pack_forget()
        for bullet in self.detail_bullets:
            bullet.pack_forget()
            
        # Show disclaimer
        self.disclaimer_title.pack(fill="x", pady=(0, 5))
        self.disclaimer_body.pack(fill="both", expand=True, pady=10)

    def show_condition_detail_view(self, condition):
        # Hide disclaimer panels
        self.disclaimer_title.pack_forget()
        self.disclaimer_body.pack_forget()
        
        # Show detailed panels
        self.detail_header.pack(fill="x", pady=(0, 5))
        self.detail_title.config(text=f"Primary Diagnosis Match: {condition['disease']}")
        
        # Style urgency tag
        urg_text = f"{condition['urgency'].upper()} URGENCY"
        if condition['urgency'] == "High":
            self.urgency_tag.config(text=urg_text, bg="#ef4444", fg="#ffffff")
        elif condition['urgency'] == "Medium":
            self.urgency_tag.config(text=urg_text, bg="#f59e0b", fg="#0f172a")
        else:
            self.urgency_tag.config(text=urg_text, bg="#0d9488", fg="#ffffff")
            
        self.detail_desc.config(text=condition['description'])
        self.detail_desc.pack(fill="x", pady=(5, 10))
        
        self.detail_pre_header.pack(fill="x", pady=(5, 2))
        
        # Load precautions
        precautions = condition['precautions']
        for idx, bullet in enumerate(self.detail_bullets):
            if idx < len(precautions):
                bullet.config(text=f"• {precautions[idx]}")
                bullet.pack(fill="x", pady=2)
            else:
                bullet.pack_forget()

    def save_report(self):
        active_symptoms = [SYMPTOMS[k] for k, v in self.symptom_vars.items() if v.get()]
        if not active_symptoms:
            self.show_status("Export failed: No symptoms selected", "#ef4444")
            messagebox.showwarning("Export Failed", "Please select at least one symptom to generate a report.")
            return
            
        # Compile report
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        report = []
        report.append("=" * 60)
        report.append("             AEGIS MEDICAL AI - DIAGNOSTIC REPORT")
        report.append(f"             Generated on: {timestamp}")
        report.append("=" * 60)
        report.append("\nPATIENT SYMPTOMS RECORDED:")
        for sym in active_symptoms:
            report.append(f" - {sym}")
            
        report.append("\n" + "-" * 60)
        report.append("AI DIAGNOSTIC PROBABILITIES:")
        if self.diagnoses:
            for idx, item in enumerate(self.diagnoses, 1):
                report.append(f"{idx}. {item['disease']}: {int(item['confidence'])}% Match [{item['urgency']} Urgency]")
        else:
            report.append("No matches found above threshold.")
            
        if self.top_condition:
            report.append("\n" + "-" * 60)
            report.append(f"PRIMARY DIAGNOSIS: {self.top_condition['disease']}")
            report.append(f"Description: {self.top_condition['description']}")
            report.append("\nRecommended Precautions:")
            for prec in self.top_condition['precautions']:
                report.append(f" • {prec}")
                
        if self.emergency_active:
            report.append("\n" + "!" * 60)
            report.append(" EMERGENCY WARNING: Severe symptoms (Chest Pain / Shortness of Breath)")
            report.append(" detected. Patient should seek immediate emergency medical care!")
            report.append("!" * 60)
            
        report.append("\n" + "=" * 60)
        report.append("IMPORTANT MEDICAL DISCLAIMER:")
        report.append("This report is generated by a rule-based expert system for preliminary")
        report.append("screening and educational purposes only. It is NOT a diagnostic report")
        report.append("from a certified medical practitioner. Always seek the advice of a")
        report.append("physician or other qualified health provider with any questions you")
        report.append("may have regarding a medical condition.")
        report.append("=" * 60)
        
        report_text = "\n".join(report)
        
        # Save to file
        filename = "diagnostic_report.txt"
        try:
            with open(filename, "w", encoding="utf-8") as f:
                f.write(report_text)
            self.show_status("Report saved to diagnostic_report.txt", "#10b981")
            
            # Show a nice confirmation box with location info
            messagebox.showinfo(
                "Report Saved Successfully",
                f"Your diagnostic report has been saved to:\n{os.path.abspath(filename)}\n\n"
                "Please review the document or print it for your next doctor's appointment."
            )
        except Exception as e:
            self.show_status(f"Export error: {str(e)}", "#ef4444")
            messagebox.showerror("Export Error", f"Could not write file: {str(e)}")

# ==============================================================================
# ENTRY POINT
# ==============================================================================
if __name__ == "__main__":
    root = tk.Tk()
    app = ModernMedicalAIApp(root)
    root.mainloop()