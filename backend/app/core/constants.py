# Camera Network Constants representing the City Model Graph

# Transition Graph Structure: Camera ID -> Dict of Target Cameras with Distance (meters),
# Travel Time (seconds), and default Transition Probability.
CAMERA_GRAPH = {
    "Camera_A": {
        "Camera_B": {"distance": 100, "travel_time": 5, "transition_probability": 0.8},
    },
    "Camera_B": {
        "Camera_C": {"distance": 150, "travel_time": 8, "transition_probability": 0.5},
        "Camera_D": {"distance": 120, "travel_time": 6, "transition_probability": 0.4},
    },
    "Camera_C": {
        "Camera_E": {"distance": 80, "travel_time": 4, "transition_probability": 0.9},
    },
    "Camera_D": {
        "Blind_Spot_1": {"distance": 50, "travel_time": 3, "transition_probability": 0.6},
    },
    "Camera_E": {
        "Blind_Spot_2": {"distance": 60, "travel_time": 3, "transition_probability": 0.7},
    }
}

# Crime rate statistics by area for risk factor analysis (multiplier/adder)
HIGH_CRIME_AREAS = {"Zone_B", "Zone_D", "Blind_Spot_1"}

# Default travel time limits before a prediction marks "MISSED" (seconds)
TIMEOUT_GRACE_PERIOD = 8.0  # Added on top of standard travel time
