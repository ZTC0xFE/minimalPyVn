import os
import pickle
from settings import SAVE_FILE

def load_progress():
    """
    Loads progress from SAVE_FILE if it exists and is a valid dict.
    Returns an empty dict otherwise.
    Expected structure:
      {
        "chapter1.yml": {"last_page": 0, "completed": False},
        ...
      }
    """
    if os.path.exists(SAVE_FILE):
        try:
            with open(SAVE_FILE, "rb") as f:
                data = pickle.load(f)
                if isinstance(data, dict):
                    return data
                else:
                    return {}
        except Exception:
            return {}
    return {}

def save_progress(progress_data):
    """
    Saves the given progress dict to SAVE_FILE.
    """
    try:
        with open(SAVE_FILE, "wb") as f:
            pickle.dump(progress_data, f)
    except Exception as e:
        print(f"[save_manager] Error saving progress: {e}")
