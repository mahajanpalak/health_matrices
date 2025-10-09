import pandas as pd

PROFILE_FILE = "profile.csv"

def save_profile(profile):
    profile_copy = profile.copy()

    # Ensure multi-select fields have at least "None"
    for key in ['Allergies', 'Injuries']:
        if key in profile_copy:
            if not profile_copy[key]:  # empty list
                profile_copy[key] = ["None"]
            profile_copy[key] = ','.join(profile_copy[key])  # convert to CSV string

    # Save single-value fields as-is
    df = pd.DataFrame([profile_copy])
    df.to_csv(PROFILE_FILE, index=False)

def load_profile():
    try:
        df = pd.read_csv(PROFILE_FILE)

        # Convert multi-value fields back to list
        for key in ['Allergies', 'Injuries']:
            if key in df.columns:
                df[key] = df[key].apply(lambda x: x.split(',') if pd.notna(x) else ["None"])

        return df
    except FileNotFoundError:
        return pd.DataFrame()
