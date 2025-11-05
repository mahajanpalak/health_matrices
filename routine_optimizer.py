# routine_optimizer.py
# Complete runnable routine optimizer implementing the detailed logic requested.
# Keep function names and signatures: generate_schedule, auto_mode, routine_optimizer_ui

import os
import random
from datetime import date
from typing import List, Dict, Any

import pandas as pd
import streamlit as st
import plotly.express as px

# -----------------------------
# Config / dataset paths
# -----------------------------
DATA_DIR = "data"
FOOD_PATH = os.path.join(DATA_DIR, "foods.csv") if os.path.exists(os.path.join(DATA_DIR, "foods.csv")) else "foods.csv"
EX_PATH = os.path.join(DATA_DIR, "exercises.csv") if os.path.exists(os.path.join(DATA_DIR, "exercises.csv")) else "exercises.csv"

# -----------------------------
# Small helpers
# -----------------------------
def _hour_to_int(h):
    """Accept '08:00' or '8' or int -> returns 0..23 int"""
    if isinstance(h, int):
        return max(0, min(23, int(h)))
    s = str(h).strip()
    if ":" in s:
        try:
            return max(0, min(23, int(s.split(":")[0])))
        except:
            return 0
    try:
        return max(0, min(23, int(s)))
    except:
        return 0

def hour_label(i: int) -> str:
    return f"{i:02d}:00"

def clamp(x, a, b):
    return max(a, min(b, x))

# -----------------------------
# Load datasets (robust)
# -----------------------------
def load_foods():
    if not os.path.exists(FOOD_PATH):
        return None
    try:
        df = pd.read_csv(FOOD_PATH)
        df.columns = [c.strip() for c in df.columns]
        return df
    except Exception:
        try:
            df = pd.read_excel(FOOD_PATH)
            df.columns = [c.strip() for c in df.columns]
            return df
        except Exception:
            return None

def load_exercises():
    if not os.path.exists(EX_PATH):
        return None
    try:
        df = pd.read_csv(EX_PATH)
        df.columns = [c.strip() for c in df.columns]
        return df
    except Exception:
        try:
            df = pd.read_excel(EX_PATH)
            df.columns = [c.strip() for c in df.columns]
            return df
        except Exception:
            return None

FOODS_DF = load_foods()
EX_DF = load_exercises()

# -----------------------------
# Constants: preference names and mapping
# -----------------------------
PREFERENCE_SET = [
    "Mindfulness/Relaxation",
    "Nap/Sleep",
    "Exercise",
    "Meal/Snack",
    "Hydration",
    "Outdoor/Social",
    "College/Office Work"
]

# Compatibility groups (used for merging preferences)
COMPATIBLE = {
    "Nap/Sleep": ["Mindfulness/Relaxation"],
    "Mindfulness/Relaxation": ["Nap/Sleep", "Hydration"],
    "Exercise": ["Hydration", "Mindfulness/Relaxation"],
    "Meal/Snack": ["Hydration", "Mindfulness/Relaxation"],
    "Outdoor/Social": ["Hydration"],
    "College/Office Work": ["Hydration", "Mindfulness/Relaxation"]
}

# Natural windows
WINDOWS = {
    "Sleep": (0, 6),
    "Breakfast": (8, 10),
    "Lunch": (13, 15),
    "Coffee/Snack": (16, 18),
    "Dinner": (19, 21),
    "Exercise_pref": (16, 19),
    "Exercise_fallback": (7, 21),
    "Mindfulness_pref": (6, 12),
    "Mindfulness_fallback_night": (0, 6),
    "Outdoor_allowed": (11, 22),
    "Work_allowed": (11, 22)
}

# -----------------------------
# Utility: picks from datasets
# -----------------------------
def pick_mindfulness_example():
    """Pick yoga/breathing low-to-moderate intensity example from EX_DF"""
    df = EX_DF
    if df is None or df.empty:
        fallbacks = ["3-minute breathing exercise", "Child's Pose - 5 min", "Guided body-scan - 10 min"]
        return random.choice(fallbacks)
    cols = [c.lower() for c in df.columns]
    # heuristics to detect name, category, intensity columns
    name_col = next((c for c in df.columns if "name" in c.lower() or "exercise" in c.lower()), df.columns[0])
    cat_col = next((c for c in df.columns if "category" in c.lower()), None)
    int_col = next((c for c in df.columns if "intensity" in c.lower()), None)
    pool = df.copy()
    if cat_col:
        pool = pool[pool[cat_col].str.lower().isin(["yoga", "breathing", "meditation", "flexibility"]) | pool[cat_col].str.lower().str.contains("yoga|breath|meditat|flex", na=False)]
    if int_col:
        pool = pool[pool[int_col].str.lower().isin(["low", "moderate", "medium"]) | pool[int_col].str.lower().str.contains("low|moderate|medium", na=False)]
    if pool.empty:
        pool = df
    return str(pool.sample(1)[name_col].iloc[0])

def pick_exercise_for_goal_and_mood(goal: str, mood: str):
    """Pick an exercise example depending on goal (lose/gain/maintain) and mood"""
    df = EX_DF
    goal = (goal or "maintain").lower()
    mood = (mood or "").lower()
    if df is None or df.empty:
        # fallback examples tailored by goal
        if goal == "lose":
            return random.choice(["Burpees - 10 min", "HIIT circuit - 20 min", "Brisk run - 20 min"]), "High-intensity cardio like burpees is great for burning calories."
        if goal == "gain":
            return random.choice(["Dumbbell full-body - 30 min", "Resistance band routine - 20 min"]), "Strength training focusing on progressive overload helps muscle gain."
        return random.choice(["Mixed circuit - 25 min", "Moderate jog + bodyweight - 25 min"]), "Balanced mix to maintain fitness."
    # find name/category/intensity columns
    name_col = next((c for c in df.columns if "name" in c.lower() or "exercise" in c.lower()), df.columns[0])
    cat_col = next((c for c in df.columns if "category" in c.lower()), None)
    int_col = next((c for c in df.columns if "intensity" in c.lower()), None)

    def sample_by(categories=None, intensities=None):
        p = df
        if categories and cat_col:
            cats = [c.lower() for c in categories]
            p = p[p[cat_col].str.lower().isin(cats) | p[cat_col].str.lower().str.contains("|".join(cats), na=False)]
        if intensities and int_col:
            ints = [i.lower() for i in intensities]
            p = p[p[int_col].str.lower().isin(ints) | p[int_col].str.lower().str.contains("|".join(ints), na=False)]
        if p.empty:
            return None
        return str(p.sample(1)[name_col].iloc[0])

    if goal == "lose":
        # prefer cardio/strength high/moderate intensity
        ex = sample_by(categories=["Cardio", "HIIT", "Circuit", "Strength"], intensities=["High", "Moderate"])
        if ex: return f"{ex} (high/mod intensity)", "Try cardio or strength work like " + ex
        # fallback
        ex = sample_by(categories=["Cardio", "Strength"], intensities=["Moderate"])
        if ex: return ex, "Try high-effort cardio or circuit training."
    elif goal == "gain":
        # prefer strength low->moderate and flexibility/yoga as supportive
        ex = sample_by(categories=["Strength", "Resistance"], intensities=["Low", "Moderate"])
        if ex: return ex, "Focus on strength with controlled moderate intensity."
        ex = sample_by(categories=["Yoga", "Flexibility"], intensities=["Low", "Moderate", "High"])
        if ex: return ex, "Include flexibility/yoga for recovery."
    else:
        # maintain: mix of all categories
        ex = sample_by(categories=["Cardio", "Strength", "Yoga", "Flexibility", "Circuit"], intensities=["Low", "Moderate", "High"])
        if ex: return ex, "A balanced mix across cardio, strength and flexibility keeps you fit."
    # ultimate fallback
    return random.choice(["Brisk Walk - 20 min", "Bodyweight circuit - 20 min"]), "Try a short mixed session."

def pick_meals(goal: str, meal_type: str, used=set()):
    """Pick 1-2 healthy foods from FOODS_DF for goal and meal_type.
       goal mapping: 'lose'->'Weight loss', 'gain'->'Weight gain', 'maintain'->any
       meal_type: 'Breakfast', 'Lunch', 'Dinner', 'Snack'
    """
    df = FOODS_DF
    goal = (goal or "maintain").lower()
    meal_type = meal_type or ""
    if df is None or df.empty:
        fallback = {
            "gain": ["Oats + Peanut Butter", "Banana + Nuts"],
            "lose": ["Grilled Veg Salad", "Quinoa & Chickpeas"],
            "maintain": ["Mixed Grain Bowl", "Yogurt + Fruit"]
        }
        choices = fallback.get(goal, fallback["maintain"])
        picks = [p for p in choices if p not in used][:2]
        return picks or choices[:1]
    # detect columns
    name_col = next((c for c in df.columns if "food" in c.lower() or "name" in c.lower()), df.columns[0])
    weight_col = next((c for c in df.columns if "weight" in c.lower()), None)
    healthy_col = next((c for c in df.columns if "healthy" in c.lower() or "junk" in c.lower() or "healthy/junk" in c.lower()), None)
    meal_col = next((c for c in df.columns if "meal" in c.lower()), None)

    pool = df.copy()
    # filter healthy
    if healthy_col:
        pool = pool[pool[healthy_col].astype(str).str.lower().str.contains("healthy", na=False)]
    # filter weight
    if weight_col:
        if goal == "lose":
            pool = pool[pool[weight_col].astype(str).str.lower().str.contains("loss|weight loss|weightloss", na=False)]
        elif goal == "gain":
            pool = pool[pool[weight_col].astype(str).str.lower().str.contains("gain|weight gain|weightgain", na=False)]
        # maintain: keep all
    # filter meal type
    if meal_col and meal_type:
        pool2 = pool[pool[meal_col].astype(str).str.lower().str.contains(meal_type.lower(), na=False)]
        if not pool2.empty:
            pool = pool2

    if pool.empty:
        pool = df.copy()
        if healthy_col:
            pool = pool[pool[healthy_col].astype(str).str.lower().str.contains("healthy", na=False)]
    # pick up to 2 unique items
    names = pool[name_col].astype(str).tolist()
    if not names:
        return ["Fruit Salad"]
    random.shuffle(names)
    picks = []
    for n in names:
        if n not in used:
            picks.append(n)
        if len(picks) >= 2:
            break
    if not picks:
        picks = names[:1]
    return picks

# -----------------------------
# Core rule engine: generate_schedule
# -----------------------------
def generate_schedule(free_hours: List[str], prefs: List[str], user: Dict[str, Any], energy: str, hunger: str, mood: str):
    """
    Returns ordered dict-like (python dict) mapping hour string -> list of subslot dicts:
      { "hour_label": [ {"pref": "...", "activity": "...", "duration": "xx", "reason": "..."} ] }
    Implements the full logic user requested.
    """
    # normalize
    free_hours = sorted(list(dict.fromkeys(free_hours)), key=lambda x: _hour_to_int(x))
    if not free_hours:
        return {}

    # simplify user fields
    goal = (user.get("goal") or "maintain").lower()
    # normalize preferences to canonical set
    prefs = [p for p in prefs if p in PREFERENCE_SET]

    hour_ints = [_hour_to_int(h) for h in free_hours]

    schedule = {h: [] for h in free_hours}
    used_examples = set()   # avoid duplicated dataset items
    used_main_types = set() # avoid duplicate heavy activity types (exercise/meal/nap/work/outdoor)
    hydration_append = {}   # track hours where hydration was appended

    # Helper: check if a preference must be placed in night (00-06)
    night_hours = [h for h in free_hours if 0 <= _hour_to_int(h) < 6]

    # Rule 1: Night (00-06) => Sleep priority
    # Sleep should be first preference in night window unless user explicitly 'dislikes' sleep.
    # Since we don't have per-activity 'like/dislike' here, interpret 'prefs' list presence as desire.
    # If user explicitly added "Nap/Sleep" in prefs, we will honor it; otherwise we will assign Sleep by default.
    # ALSO: we will only override Sleep if user's provided preferences cannot fit outside 00-06 even after splitting (see below)
    # Implementation: tentatively place Sleep in night hours, then check if preferences count > available non-night slots such that
    # they cannot be accommodated, if so we will reassign some preferences into night slots.
    non_night_hours = [h for h in free_hours if not (0 <= _hour_to_int(h) < 6)]

    # Quick capacity check: count 'must-include' preferences (all prefs except Hydration which is supportive)
    required_prefs = [p for p in prefs if p != "Hydration"]
    # capacity outside night if we want to keep Sleep in every night slot: number of non-night hours
    # There is also the special rule: night-sleep logic can be overpowered only if number of selected preferences are more such
    # that they can not be accomodated outside 00-06 even after dividing the selected hours in half for each preference.
    # We'll compute if preferences > 2 * non_night_slots then we must place some preferences into night.
    if non_night_hours:
        max_pref_outside = len(non_night_hours) * 2  # "after dividing selected hours in half for each preference"
    else:
        max_pref_outside = 0

    force_place_prefs_in_night = False
    if len(required_prefs) > max_pref_outside:
        force_place_prefs_in_night = True

    # Assign sleep to night hours (initially)
    for h in night_hours:
        # If user explicitly disliked sleep? (we don't have dislike per-activity in this function) --
        # we interpret presence of "Nap/Sleep" in prefs as *liking* it, absence doesn't necessarily mean dislike.
        schedule[h].append({
            "pref": "Nap/Sleep",
            "activity": "Sleep",
            "duration": "Full night (when possible)",
            "reason": "Night hours are best used for sleep."
        })
        used_main_types.add("sleep")

    # We will prepare an ordered list of preference items to place.
    # Ordering logic:
    #  - user preferences first (in order they provided)
    #  - then energy-level based defaults appended if not present
    #  - mood adjustments (e.g., if mood tired/stressed -> prefer nap/mindfulness)
    # Keep duplicates removed but preserve order.
    def energy_base_pattern(energy_level):
        energy_level = energy_level or "Moderate"
        if energy_level in ["Very Low", "Low"]:
            return ["Mindfulness/Relaxation", "Meal/Snack", "Nap/Sleep"]
        if energy_level in ["Moderate"]:
            return ["Mindfulness/Relaxation", "Meal/Snack", "Nap/Sleep", "College/Office Work", "Exercise"]
        return ["College/Office Work", "Exercise", "Meal/Snack"]

    base_order = energy_base_pattern(energy)

    # mood adjustments
    if mood in ["Tired", "Stressed"]:
        # bump Nap and Mindfulness to top if not already
        base_order = ["Nap/Sleep", "Mindfulness/Relaxation"] + [p for p in base_order if p not in ["Nap/Sleep", "Mindfulness/Relaxation"]]
    elif mood == "Motivated":
        base_order = ["College/Office Work", "Exercise"] + [p for p in base_order if p not in ["College/Office Work", "Exercise"]]
    elif mood == "Relaxed":
        if "Mindfulness/Relaxation" not in base_order:
            base_order.append("Mindfulness/Relaxation")

    # Merge: user prefs first, then base_order extras
    ordered_prefs = []
    for p in prefs:
        if p not in ordered_prefs:
            ordered_prefs.append(p)
    for p in base_order:
        if p not in ordered_prefs:
            ordered_prefs.append(p)

    # If hydration is present in prefs, we do not allocate a full slot for hydration;
    # instead we append hydration note to whichever slot is related.
    want_hydration = "Hydration" in ordered_prefs
    if want_hydration and "Hydration" in ordered_prefs:
        ordered_prefs.remove("Hydration")

    # Now compress ordered_prefs if more prefs than slots
    slots = len(free_hours)
    def compress_preferences(lst, slots_available):
        """Compress by merging compatible preferences using COMPATIBLE map until <= slots_available"""
        out = lst.copy()
        # if already fits
        if len(out) <= slots_available:
            return out
        # repeatedly merge compatible pairs with highest compatibility
        # greedily try to merge pairs where COMPATIBLE lists overlap
        while len(out) > slots_available:
            merged = False
            # attempt to merge any compatible pair
            for i in range(len(out)):
                a = out[i]
                comps = COMPATIBLE.get(a, [])
                for j in range(i + 1, len(out)):
                    b = out[j]
                    if b in comps or a in COMPATIBLE.get(b, []):
                        # merge a+b into "a+b"
                        out[i] = f"{a}+{b}"
                        out.pop(j)
                        merged = True
                        break
                if merged:
                    break
            if not merged:
                # no compatible pairs; merge last two as a forced merge (still keep order)
                if len(out) >= 2:
                    out[-2] = f"{out[-2]}+{out[-1]}"
                    out.pop(-1)
                else:
                    break
        return out

    compressed = compress_preferences(ordered_prefs, slots if slots > 0 else 1)

    # Assignment strategy:
    # We'll try to place preferences into natural windows if possible:
    # - Meal/Snack: within breakfast/lunch/dinner/snack windows depending on free hour
    # - Outdoor/Social or College/Office Work: try any 11..22 free hour
    # - Exercise: preferred 16..19 else 7..21
    # - Mindfulness: preferred 6..12 else night fallback
    # - Nap: use gap heuristic: if there is a gap of >=5 hours between two free hours, allow nap; else short nap.
    # Place items round-robin across available free_hours while respecting above windows and avoiding duplicate heavy types.
    hour_pool = free_hours.copy()
    # prefer filling non-night hours first for user prefs unless forced to place into night
    place_order_hours = [h for h in hour_pool if not (0 <= _hour_to_int(h) < 6)] + [h for h in hour_pool if (0 <= _hour_to_int(h) < 6)]

    # If force_place_prefs_in_night True, we allow placing preferences into night hours as needed; otherwise avoid placing heavy prefs into night.
    # We'll map each compressed pref -> chosen hour(s)
    pref_to_hours = {}
    used_hour_set = set()
    # Round robin assignment with window heuristics
    def find_hour_for_pref(pref_label):
        parts = [p.strip() for p in str(pref_label).split("+")]
        # we try candidate hours in preference order:
        # - for Meal/Snack: choose hour in the meal window
        # - for Outdoor/Social, College/Office Work: choose hour between 11..22
        # - for Exercise: choose 16..19 first, else 7..21
        # - for Mindfulness: choose 6..12 first, else use night fallback (0..6) or other hours
        # - for Nap: try to find a gap or quiet early afternoon 13..17
        # - otherwise pick next available hour
        # Return hour string or None.
        # We'll exclude already used_hour_set unless multiple prefs share the same hour (allowed if merged).
        for attempt in range(2):
            for h in place_order_hours:
                if (h in used_hour_set) and attempt == 0:
                    # prefer unused hours first
                    continue
                h_i = _hour_to_int(h)
                # if pref_label includes Meal
                if any("Meal" in p or "Snack" in p for p in parts):
                    # only choose breakfast/lunch/dinner/snack windows
                    if 8 <= h_i <= 10:
                        return h
                    if 13 <= h_i <= 15:
                        return h
                    if 19 <= h_i <= 21:
                        return h
                    if 16 <= h_i <= 18:
                        return h
                    # else skip first attempt
                    continue
                if any("Outdoor" in p or "Social" in p for p in parts):
                    if 11 <= h_i <= 22:
                        return h
                    continue
                if any("College/Office" in p or "College" in p or "Office" in p for p in parts):
                    if 11 <= h_i <= 22:
                        return h
                    continue
                if any("Exercise" in p or "Workout" in p or "Strength" in p for p in parts):
                    # prefer 16-19 then 7-21
                    if 16 <= h_i <= 19:
                        return h
                    if 7 <= h_i <= 21:
                        return h
                    continue
                if any("Mindfulness" in p or "Relaxation" in p or "Meditation" in p for p in parts):
                    if 6 <= h_i <= 12:
                        return h
                    if 0 <= h_i <= 6:
                        return h
                    continue
                if any("Nap" in p or "Sleep" in p for p in parts):
                    if 13 <= h_i <= 17:
                        return h
                    # accept night only if forced
                    if 0 <= h_i <= 6 and force_place_prefs_in_night:
                        return h
                    continue
                # default fallback - any hour
                return h
        # if nothing matched, return any free hour (prefer unused)
        for h in place_order_hours:
            if h not in used_hour_set:
                return h
        return place_order_hours[0] if place_order_hours else free_hours[0]

    # Assign compressed prefs to hours
    # We will assign in input order to attempt to respect user order
    for pref in compressed:
        # allow merged prefs to occupy the same hour (we intentionally will allow this)
        chosen_hour = find_hour_for_pref(pref)
        if chosen_hour is None:
            chosen_hour = place_order_hours[0]
        # If this chosen_hour already has a sleep assigned and pref is heavy, consider moving pref if sleep should be preserved
        if chosen_hour in schedule and schedule[chosen_hour]:
            # If schedule has Sleep and pref is heavy and not forced to go into night, try to find alternate hour
            if any(s.get("activity", "").lower() == "sleep" for s in schedule[chosen_hour]):
                # try other hours first
                alt = None
                for h in place_order_hours:
                    if h == chosen_hour:
                        continue
                    # prefer hours outside night for heavy prefs
                    if pref and "Nap/Sleep" not in pref:
                        if 0 <= _hour_to_int(h) < 6 and not force_place_prefs_in_night:
                            continue
                    if h not in used_hour_set:
                        alt = h
                        break
                if alt:
                    chosen_hour = alt
        # Reserve the chosen hour (but multiple prefs can share same hour if merged)
        used_hour_set.add(chosen_hour)
        pref_to_hours.setdefault(chosen_hour, []).append(pref)

    # Now for each hour we have one or more pref labels assigned (merged or single).
    # Create concrete activities for each pref label using dataset pickers & heuristics.
    def choose_activity_for_pref_label(pref_label, hour):
        # returns a dict with fields pref, activity, duration, reason
        parts = [p.strip() for p in pref_label.split("+")]
        hour_i = _hour_to_int(hour)
        subparts = []
        # For each part, pick an appropriate example or label
        for p in parts:
            if p == "Mindfulness/Relaxation":
                ex = pick_mindfulness_example()
                subparts.append({
                    "pref": "Mindfulness/Relaxation",
                    "activity": f"Mindfulness: {ex}",
                    "duration": "10-20 min",
                    "reason": "Short yoga/breathing practice to restore calm and focus."
                })
                # if we used an example, mark it used
                used_examples.add(ex)
                used_main_types.add("mindfulness")
                continue
            if p == "Nap/Sleep":
                # if hour in night -> sleep else short nap
                if 0 <= hour_i < 6:
                    subparts.append({
                        "pref": "Nap/Sleep",
                        "activity": "Sleep (night)",
                        "duration": "as night sleep",
                        "reason": "Night period — recommended to sleep if possible."
                    })
                    used_main_types.add("sleep")
                else:
                    # check gap heuristic - use longer nap if big gap, otherwise short rest
                    gap_available = False
                    # simple heuristic: if there exists a gap >=5 between consecutive selected hours including this hour
                    hi = sorted(hour_ints)
                    for idx in range(1, len(hi)):
                        if abs(hi[idx] - hi[idx - 1]) >= 5:
                            gap_available = True
                            break
                    if gap_available:
                        subparts.append({
                            "pref": "Nap/Sleep",
                            "activity": "Nap",
                            "duration": "20-30 min",
                            "reason": "A short nap to restore energy."
                        })
                    else:
                        subparts.append({
                            "pref": "Nap/Sleep",
                            "activity": "Short Rest",
                            "duration": "10-15 min",
                            "reason": "Short rest to recharge when long nap not possible."
                        })
                    used_main_types.add("nap")
                continue
            if p == "Meal/Snack":
                # Determine meal type by hour
                if 8 <= hour_i <= 10:
                    meal_type = "Breakfast"
                elif 13 <= hour_i <= 15:
                    meal_type = "Lunch"
                elif 19 <= hour_i <= 21:
                    meal_type = "Dinner"
                elif 16 <= hour_i <= 18:
                    meal_type = "Snack"
                else:
                    # any other slot -> snack
                    meal_type = "Snack"
                # hunger rule: only suggest full meal if hunger is above Slightly Hungry
                if hunger in ["Very Hungry", "Hungry"]:
                    picks = pick_meals(goal, meal_type, used_examples)
                elif hunger == "Slightly Hungry":
                    # snack only
                    picks = pick_meals(goal, "Snack", used_examples)
                else:
                    # Not hungry -> avoid meal if possible -> propose light snack only if user explicitly requested Meal/Snack
                    if "Meal/Snack" not in prefs:
                        picks = []
                    else:
                        picks = pick_meals(goal, meal_type, used_examples)
                if picks:
                    for pk in picks:
                        used_examples.add(pk)
                    text = " + ".join(picks)
                    reason = f"Suggested {meal_type} aligned with your goal ({goal}). Example: {text}."
                    subparts.append({
                        "pref": "Meal/Snack",
                        "activity": text,
                        "duration": "20-45 min",
                        "reason": reason
                    })
                    used_main_types.add("meal")
                else:
                    # user not hungry – fill with alternative light activity
                    alt_choices = [
                        "Read a book or an article",
                        "Write a short journal entry",
                        "Plan your next day or set tomorrow’s goals",
                        "Do a 5-minute breathing exercise",
                        "Light stretching or posture correction"
                    ]
                    alt_pick = random.choice(alt_choices)
                    subparts.append({
                        "pref": "Mindful/Light Activity",
                        "activity": alt_pick,
                        "duration": "15–30 min",
                        "reason": "You're not hungry — instead, use this time for self-growth or relaxation."
                    })

                continue
            if p == "Exercise":
                # special rule: if Mindfulness also included and mood/tiredness indicate, prefer mindfulness and skip exercise
                if "Mindfulness/Relaxation" in pref_label and (mood in ["Tired", "Stressed"] or energy in ["Low", "Very Low"]):
                    # pick mindfulness instead of heavy exercise
                    ex = pick_mindfulness_example()
                    subparts.append({
                        "pref": "Mindfulness/Relaxation",
                        "activity": f"Mindfulness: {ex}",
                        "duration": "10-20 min",
                        "reason": "We prioritize light mindfulness when tired/stressed."
                    })
                    used_examples.add(ex)
                    used_main_types.add("mindfulness")
                    continue
                ex, rationale = pick_exercise_for_goal_and_mood(goal, mood)
                # duration depends on goal and energy
                dur = "30-45 min"
                if goal == "gain":
                    dur = "30-45 min (strength focus)"
                elif goal == "lose":
                    dur = "30-45 min (cardio/hiit)"
                if energy in ["Low", "Very Low"]:
                    # lower intensity suggestion text
                    subparts.append({
                        "pref": "Exercise",
                        "activity": f"Light Exercise: {ex}",
                        "duration": "10-20 min",
                        "reason": "Energy low — keep exercise light and focused on movement."
                    })
                    used_main_types.add("exercise")
                else:
                    subparts.append({
                        "pref": "Exercise",
                        "activity": f"{ex}",
                        "duration": dur,
                        "reason": rationale
                    })
                    used_main_types.add("exercise")
                # mark the example used
                used_examples.add(ex)
                continue
            if p == "Outdoor/Social":
                # map examples like "meet friends", "play", "walk outside"
                options = ["Go for a walk with a friend", "Play a short game (e.g. badminton)", "Meet a friend for coffee", "Outdoor walk/jog"]
                pick = random.choice(options)
                subparts.append({
                    "pref": "Outdoor/Social",
                    "activity": pick,
                    "duration": "30-60 min",
                    "reason": "Social/outdoor time improves mood and energy."
                })
                used_main_types.add("outdoor")
                continue
            if p == "College/Office Work":
                subparts.append({
                    "pref": "College/Office Work",
                    "activity": "Focused work/session (use Pomodoro)",
                    "duration": "45-90 min",
                    "reason": "Good slot for concentrated productive work."
                })
                used_main_types.add("work")
                continue
            # fallback generic
            subparts.append({
                "pref": p,
                "activity": p,
                "duration": "20-30 min",
                "reason": "Suggested activity."
            })
        # combine subparts into a single block if multiple
        if not subparts:
            return {
                "pref": pref_label,
                "activity": "Relaxation",
                "duration": "15 min",
                "reason": "Default short relaxation."
            }
        if len(subparts) == 1:
            return subparts[0]
        # merge multiple subparts into combined activity for the hour
        combined_activity = " + ".join([s["activity"] for s in subparts])
        combined_duration = ", ".join([s["duration"] for s in subparts])
        combined_reason = " ".join([s["reason"] for s in subparts])
        return {
            "pref": pref_label,
            "activity": combined_activity,
            "duration": combined_duration,
            "reason": combined_reason
        }

    # Build schedule entries for assigned hours
    for h, pref_labels in pref_to_hours.items():
        # ensure chronological order inside hour by preference
        for pl in pref_labels:
            block = choose_activity_for_pref_label(pl, h)
            # append hydration note if user asked hydration
            if want_hydration:
                # append only once per hour and only if activity supports hydration (Meals/Exercise/Outdoor/Work)
                if any(k in block["pref"] for k in ["Meal", "Exercise", "Outdoor", "College", "Nap", "Mindfulness", "Relaxation"]):
                    # friendly hydration note
                    block["reason"] = block["reason"] + " 💧 And remember to stay hydrated — sip water regularly!"
                    hydration_append[h] = True
            schedule[h].append(block)

    # Fill remaining free hours that don't have assigned prefs with auto picks
    for h in free_hours:
        if not schedule[h]:
            # if hour is nightly 0..6, we should prefer Sleep unless user disliked (we assume not)
            h_i = _hour_to_int(h)
            if 0 <= h_i < 6:
                schedule[h].append({
                    "pref": None,
                    "activity": "Sleep",
                    "duration": "Night sleep",
                    "reason": "Night — recommended sleep."
                })
                continue
            # otherwise create a human-like sensible pick depending on energy
            if energy in ["Very Low", "Low"]:
                ex = pick_mindfulness_example()
                schedule[h].append({
                    "pref": None,
                    "activity": f"Mindfulness: {ex}",
                    "duration": "10-20 min",
                    "reason": "Short mindfulness to restore energy."
                })
            elif energy == "Moderate":
                # put either quick work or short exercise
                if mood == "Motivated":
                    schedule[h].append({
                        "pref": None,
                        "activity": "Focused work session (25-45 min)",
                        "duration": "25-45 min",
                        "reason": "Good time for focused productive work."
                    })
                else:
                    ex, rationale = pick_exercise_for_goal_and_mood(goal, mood)
                    schedule[h].append({
                        "pref": None,
                        "activity": ex,
                        "duration": "20-30 min",
                        "reason": rationale
                    })
            else:
                # energy high -> work or exercise
                ex, rationale = pick_exercise_for_goal_and_mood(goal, mood)
                schedule[h].append({
                    "pref": None,
                    "activity": ex,
                    "duration": "30-45 min",
                    "reason": rationale
                })

    # Final cleanup:
    # - Ensure no duplicate main heavy types: prioritize first occurrence and convert duplicates to supportive activity
    seen_main = set()
    final_schedule = {}
    def main_type_of_activity(a):
        la = a.lower()
        if any(x in la for x in ["sleep", "nap", "rest"]):
            return "sleep"
        if any(x in la for x in ["breakfast", "lunch", "dinner", "snack", "meal"]):
            return "meal"
        if any(x in la for x in ["burpee", "hiit", "workout", "strength", "circuit", "run", "brisk"]):
            return "exercise"
        if any(x in la for x in ["mindfulness", "meditation", "breathing", "yoga", "child's"]) or "mindfulness:" in la:
            return "mindfulness"
        if any(x in la for x in ["work session", "focused", "study", "office", "college"]):
            return "work"
        if any(x in la for x in ["walk", "meet", "play", "outdoor", "social"]):
            return "outdoor"
        return "other"

    for h in sorted(schedule.keys(), key=lambda x: _hour_to_int(x)):
        blocks = schedule[h]
        filtered = []
        for b in blocks:
            m = main_type_of_activity(b["activity"])
            if m in seen_main and m not in ["other", "mindfulness"]:
                # convert to supportive activity to avoid repeating heavy thing
                if m == "meal":
                    newb = b.copy()
                    newb["activity"] = "Healthy Snack"
                    newb["duration"] = "10-15 min"
                    newb["reason"] = "Converted to a light snack to avoid repeating full meals."
                    filtered.append(newb)
                elif m == "exercise":
                    # convert duplicate exercise to light stretching / walk
                    newb = b.copy()
                    newb["activity"] = "Light walk or stretching"
                    newb["duration"] = "10-15 min"
                    newb["reason"] = "Short movement break instead of repeating a full workout."
                    filtered.append(newb)
                else:
                    # skip duplicates of same main type
                    continue
            else:
                filtered.append(b)
                if m not in ["other", "mindfulness"]:
                    seen_main.add(m)
        if filtered:
            final_schedule[h] = filtered

    # Ensure chronological order (by hour int)
    ordered = dict(sorted(final_schedule.items(), key=lambda x: _hour_to_int(x[0])))
    return ordered

# -----------------------------
# Auto mode (keeps signature)
# -----------------------------
def auto_mode(hours: List[str], user: Dict[str, Any], energy: str, hunger: str, mood: str):
    """Simpler wrapper that uses generate_schedule with no preferences."""
    return generate_schedule(hours, [], user, energy, hunger, mood)

# -----------------------------
# Visualization helpers & feedback saving (simple)
# -----------------------------
def visualize_day_plan(schedule: Dict[str, Any]):
    if not schedule:
        st.info("No schedule to visualize.")
        return
    data = []
    for h, blocks in schedule.items():
        for b in blocks:
            data.append({
                "Hour": h,
                "Hour_Num": _hour_to_int(h),
                "Activity": b["activity"],
                "Reason": b.get("reason", "")
            })
    df = pd.DataFrame(data).sort_values("Hour_Num")
    fig = px.bar(df, x="Hour", y=[1]*len(df), color="Activity", hover_data=["Reason"], title="Your Day Plan")
    fig.update_yaxes(visible=False)
    fig.update_layout(showlegend=True, height=360, margin=dict(t=40, b=20, l=20, r=20))
    st.plotly_chart(fig, use_container_width=True)

def save_feedback_data(user_id, schedule, feedback_map):
    rows = []
    for hour, plans in schedule.items():
        for p in plans:
            rows.append({
                "user_id": user_id or 0,
                "date": date.today().isoformat(),
                "hour": hour,
                "activity": p.get("activity"),
                "feedback": feedback_map.get(hour)
            })
    if rows:
        df = pd.DataFrame(rows)
        file = "routine_feedback.csv"
        df.to_csv(file, mode="a", index=False, header=not os.path.exists(file))

# -----------------------------
# UI: keep routine_optimizer_ui signature
# -----------------------------
def routine_optimizer_ui(user):
    st.subheader("🧘 Intelligent Routine Optimizer (v4) — Dataset-driven")
    st.write("Select free hours, energy, hunger, mood and (optionally) preferences. The optimizer will return a human-like plan with real examples picked from datasets where possible.")

    # Load profile (compatibility)
    user_id = st.session_state.get("user_id", None)
    # keep existing profile loader if available in your project; otherwise use passed user
    profile = user or {}
    if isinstance(user, dict):
        profile = user

    # controls
    hours = [f"{h:02d}:00" for h in range(24)]
    free_hours = st.multiselect("🕒 Select your free hours (24h):", hours)

    energy = st.select_slider("⚡ Energy Level", ["Very Low", "Low", "Moderate", "High"], value="Moderate")
    hunger = st.select_slider("🍽 Hunger Level", ["Not Hungry", "Slightly Hungry", "Hungry", "Very Hungry"], value="Slightly Hungry")
    mood = st.selectbox("🙂 Mood", ["Tired", "Motivated", "Relaxed", "Stressed"], index=2)

    prefs = st.multiselect("🎯 Preferences (optional):", PREFERENCE_SET)

    col1, col2 = st.columns([2, 1])
    with col1:
        if st.button("✨ Generate My Optimized Routine", use_container_width=True):
            if not free_hours:
                st.warning("Please select at least one free hour.")
            else:
                schedule = generate_schedule(free_hours, prefs, profile or {}, energy, hunger, mood)
                st.session_state["routine_schedule"] = schedule
    with col2:
        if st.button("♻️ Reset Feedback File", use_container_width=True):
            try:
                if os.path.exists("routine_feedback.csv"):
                    os.remove("routine_feedback.csv")
                st.success("Feedback cleared.")
            except Exception as e:
                st.error(f"Could not clear feedback: {e}")

    schedule = st.session_state.get("routine_schedule")
    if schedule:
        st.markdown("## 🎯 Suggested Plan")
        for hour, blocks in schedule.items():
            st.markdown(f"### 🕒 {hour}")
            for b in blocks:
                pref_label = f" ({b.get('pref')})" if b.get("pref") else ""
                st.markdown(
                    f"<div style='background:#111827;padding:12px;border-radius:10px;margin-bottom:6px;color:white'>"
                    f"<b>{b.get('duration','')}</b> – {b.get('activity')}{pref_label}<br>"
                    f"<small style='color:#d1d5db'>{b.get('reason','')}</small></div>",
                    unsafe_allow_html=True
                )
            like_col, dislike_col = st.columns(2)
            with like_col:
                if st.button(f"👍 Like ({hour})", key=f"like_{hour}"):
                    save_feedback_data(user_id or 0, {hour: blocks}, {hour: "like"})
                    st.success("Saved like.")
            with dislike_col:
                if st.button(f"👎 Dislike ({hour})", key=f"dislike_{hour}"):
                    save_feedback_data(user_id or 0, {hour: blocks}, {hour: "dislike"})
                    st.warning("Saved dislike.")
        st.markdown("---")
        visualize_day_plan(schedule)
    else:
        st.info("No plan generated yet. Select hours and click Generate.")

# -----------------------------
# If used as script for quick local tests (optional)
# -----------------------------
if __name__ == "__main__":
    # quick CLI test sample (not used by Streamlit)
    fh = ["07:00", "08:00", "12:00", "16:00", "20:00"]
    prefs = ["Exercise", "Meal/Snack", "Mindfulness/Relaxation", "Hydration"]
    print(generate_schedule(fh, prefs, {"goal": "lose"}, energy="Moderate", hunger="Hungry", mood="Motivated"))
