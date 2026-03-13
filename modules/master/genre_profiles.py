"""
LongPlay Studio V5.0 — Genre Profiles Database
Pre-defined mastering parameter sets per music genre.
Each profile contains target values for all mastering modules.
"""

# IRC (Intelligent Release Control) Modes — Ozone 12 Style
# Each IRC mode has sub-modes for fine character control
# Maps to different limiter behavior characteristics via FFmpeg alimiter

IRC_MODES = {
    # --- IRC 1: Transparent, minimal coloration ---
    "IRC 1": {
        "name": "IRC 1",
        "description": "Transparent limiting. Minimal coloration, preserves dynamics. Best for acoustic/jazz.",
        "attack": 0.1,       # ms
        "release": 200,      # ms
        "lookahead": 5,      # ms
        "knee": 0.5,         # dB
        "level_in": 1.0,
        "sub_modes": [],     # no sub-modes
    },
    # --- IRC 2: Balanced all-purpose ---
    "IRC 2": {
        "name": "IRC 2",
        "description": "Balanced limiting. Good loudness and clarity. All-purpose mastering.",
        "attack": 0.5,
        "release": 100,
        "lookahead": 5,
        "knee": 1.0,
        "level_in": 1.0,
        "sub_modes": [],
    },
    # --- IRC 3: Musical with 4 sub-modes ---
    "IRC 3": {
        "name": "IRC 3",
        "description": "Musical limiting with character options.",
        "attack": 1.0,
        "release": 60,
        "lookahead": 3,
        "knee": 2.0,
        "level_in": 1.05,
        "sub_modes": ["Pumping", "Balanced", "Crisp", "Clipping"],
    },
    "IRC 3 - Pumping": {
        "name": "IRC 3 — Pumping",
        "description": "Rhythmic pumping character. Great for dance music and EDM.",
        "attack": 3.0,
        "release": 25,
        "lookahead": 3,
        "knee": 4.0,
        "level_in": 1.1,
        "parent": "IRC 3",
    },
    "IRC 3 - Balanced": {
        "name": "IRC 3 — Balanced",
        "description": "Even-handed limiting. Smooth and musical across all genres.",
        "attack": 1.0,
        "release": 60,
        "lookahead": 3,
        "knee": 2.0,
        "level_in": 1.05,
        "parent": "IRC 3",
    },
    "IRC 3 - Crisp": {
        "name": "IRC 3 — Crisp",
        "description": "Bright and detailed. Preserves transient clarity and air.",
        "attack": 0.5,
        "release": 80,
        "lookahead": 4,
        "knee": 1.5,
        "level_in": 1.05,
        "parent": "IRC 3",
    },
    "IRC 3 - Clipping": {
        "name": "IRC 3 — Clipping",
        "description": "Hard clipping style. Aggressive loudness with saturation edge.",
        "attack": 0.1,
        "release": 15,
        "lookahead": 1,
        "knee": 6.0,
        "level_in": 1.15,
        "parent": "IRC 3",
    },
    # --- IRC 4: Aggressive with 3 sub-modes ---
    "IRC 4": {
        "name": "IRC 4",
        "description": "Aggressive limiting with character control.",
        "attack": 0.3,
        "release": 30,
        "lookahead": 2,
        "knee": 3.0,
        "level_in": 1.1,
        "sub_modes": ["Classic", "Modern", "Transient"],
    },
    "IRC 4 - Classic": {
        "name": "IRC 4 — Classic",
        "description": "Classic aggressive limiter. Warm and punchy, vintage vibe.",
        "attack": 0.5,
        "release": 40,
        "lookahead": 3,
        "knee": 3.0,
        "level_in": 1.1,
        "parent": "IRC 4",
    },
    "IRC 4 - Modern": {
        "name": "IRC 4 — Modern",
        "description": "Modern aggressive limiting. Clean loudness for streaming.",
        "attack": 0.2,
        "release": 25,
        "lookahead": 2,
        "knee": 3.5,
        "level_in": 1.12,
        "parent": "IRC 4",
    },
    "IRC 4 - Transient": {
        "name": "IRC 4 — Transient",
        "description": "Transient-preserving aggression. Keeps punch while pushing loud.",
        "attack": 0.8,
        "release": 20,
        "lookahead": 2,
        "knee": 2.5,
        "level_in": 1.1,
        "parent": "IRC 4",
    },
    # --- IRC 5: Maximum loudness ---
    "IRC 5": {
        "name": "IRC 5",
        "description": "Maximum loudness. Heavy limiting for modern pop/EDM/trap.",
        "attack": 0.1,
        "release": 15,
        "lookahead": 1,
        "knee": 6.0,
        "level_in": 1.2,
        "sub_modes": [],
    },
    # --- IRC Low Latency: Real-time monitoring ---
    "IRC LL": {
        "name": "IRC Low Latency",
        "description": "Low latency mode for real-time monitoring. Minimal lookahead.",
        "attack": 0.1,
        "release": 50,
        "lookahead": 0.5,
        "knee": 1.5,
        "level_in": 1.0,
        "sub_modes": [],
    },
}

# Quick lookup: top-level IRC modes (for UI dropdown)
IRC_TOP_MODES = ["IRC 1", "IRC 2", "IRC 3", "IRC 4", "IRC 5", "IRC LL"]

# Tone Presets for Maximizer
TONE_PRESETS = {
    "Transparent": {
        "description": "No tonal coloration",
        "pre_eq": {},  # no pre-EQ
    },
    "Warm": {
        "description": "Gentle low-end warmth, smooth highs",
        "pre_eq": {
            "low_shelf": {"freq": 200, "gain": 1.5, "type": "lowshelf"},
            "high_shelf": {"freq": 8000, "gain": -1.0, "type": "highshelf"},
        },
    },
    "Bright": {
        "description": "Enhanced presence and air",
        "pre_eq": {
            "presence": {"freq": 3000, "gain": 1.5, "width": 1.5, "type": "equalizer"},
            "air": {"freq": 12000, "gain": 2.0, "type": "highshelf"},
        },
    },
    "Punchy": {
        "description": "Enhanced low-mid punch, slight high boost",
        "pre_eq": {
            "punch": {"freq": 100, "gain": 2.0, "width": 0.8, "type": "equalizer"},
            "presence": {"freq": 4000, "gain": 1.0, "width": 2.0, "type": "equalizer"},
        },
    },
    "Analog": {
        "description": "Vintage warmth, gentle saturation character",
        "pre_eq": {
            "sub_roll": {"freq": 30, "gain": -2.0, "type": "highpass"},
            "warmth": {"freq": 250, "gain": 1.0, "width": 1.0, "type": "equalizer"},
            "air_roll": {"freq": 14000, "gain": -1.5, "type": "highshelf"},
        },
    },
}

# Genre Mastering Profiles
GENRE_PROFILES = {
    # === Electronic ===
    "EDM": {
        "category": "Electronic",
        "target_lufs": -9.0,
        "true_peak_ceiling": -0.3,
        "irc_mode": "IRC 4",
        "tone": "Punchy",
        "eq": {
            "bands": [
                {"freq": 40, "gain": 2.0, "width": 0.7, "type": "equalizer"},
                {"freq": 150, "gain": -1.0, "width": 1.0, "type": "equalizer"},
                {"freq": 1000, "gain": -0.5, "width": 2.0, "type": "equalizer"},
                {"freq": 5000, "gain": 1.5, "width": 1.5, "type": "equalizer"},
                {"freq": 12000, "gain": 2.0, "type": "highshelf"},
            ],
        },
        "compressor": {
            "threshold": -12, "ratio": 4.0, "attack": 5, "release": 50,
            "makeup": 3.0,
        },
        "stereo_width": 130,  # percentage (100 = original)
        "intensity_default": 70,
    },
    "House": {
        "category": "Electronic",
        "target_lufs": -10.0,
        "true_peak_ceiling": -0.3,
        "irc_mode": "IRC 3",
        "tone": "Warm",
        "eq": {
            "bands": [
                {"freq": 60, "gain": 2.5, "width": 0.6, "type": "equalizer"},
                {"freq": 300, "gain": -1.0, "width": 1.5, "type": "equalizer"},
                {"freq": 3000, "gain": 1.0, "width": 2.0, "type": "equalizer"},
                {"freq": 10000, "gain": 1.5, "type": "highshelf"},
            ],
        },
        "compressor": {
            "threshold": -14, "ratio": 3.0, "attack": 10, "release": 80,
            "makeup": 2.0,
        },
        "stereo_width": 120,
        "intensity_default": 60,
    },
    "Techno": {
        "category": "Electronic",
        "target_lufs": -9.0,
        "true_peak_ceiling": -0.3,
        "irc_mode": "IRC 4",
        "tone": "Punchy",
        "eq": {
            "bands": [
                {"freq": 50, "gain": 3.0, "width": 0.5, "type": "equalizer"},
                {"freq": 200, "gain": -1.5, "width": 1.0, "type": "equalizer"},
                {"freq": 2000, "gain": 0.5, "width": 2.0, "type": "equalizer"},
                {"freq": 8000, "gain": 1.0, "width": 2.0, "type": "equalizer"},
            ],
        },
        "compressor": {
            "threshold": -10, "ratio": 5.0, "attack": 3, "release": 40,
            "makeup": 4.0,
        },
        "stereo_width": 110,
        "intensity_default": 75,
    },
    "Dubstep": {
        "category": "Electronic",
        "target_lufs": -8.0,
        "true_peak_ceiling": -0.1,
        "irc_mode": "IRC 5",
        "tone": "Punchy",
        "eq": {
            "bands": [
                {"freq": 35, "gain": 3.0, "width": 0.5, "type": "equalizer"},
                {"freq": 100, "gain": 2.0, "width": 0.8, "type": "equalizer"},
                {"freq": 500, "gain": -2.0, "width": 1.0, "type": "equalizer"},
                {"freq": 3000, "gain": 2.0, "width": 1.5, "type": "equalizer"},
                {"freq": 10000, "gain": 1.5, "type": "highshelf"},
            ],
        },
        "compressor": {
            "threshold": -8, "ratio": 6.0, "attack": 2, "release": 30,
            "makeup": 5.0,
        },
        "stereo_width": 140,
        "intensity_default": 85,
    },
    "Future Bass": {
        "category": "Electronic",
        "target_lufs": -9.0,
        "true_peak_ceiling": -0.3,
        "irc_mode": "IRC 4",
        "tone": "Bright",
        "eq": {
            "bands": [
                {"freq": 60, "gain": 2.0, "width": 0.7, "type": "equalizer"},
                {"freq": 400, "gain": -1.0, "width": 1.5, "type": "equalizer"},
                {"freq": 2500, "gain": 2.0, "width": 1.5, "type": "equalizer"},
                {"freq": 8000, "gain": 2.5, "type": "highshelf"},
            ],
        },
        "compressor": {
            "threshold": -12, "ratio": 3.5, "attack": 8, "release": 60,
            "makeup": 3.0,
        },
        "stereo_width": 135,
        "intensity_default": 70,
    },
    "Electropop": {
        "category": "Electronic",
        "target_lufs": -10.0,
        "true_peak_ceiling": -0.3,
        "irc_mode": "IRC 3",
        "tone": "Bright",
        "eq": {
            "bands": [
                {"freq": 80, "gain": 1.5, "width": 0.8, "type": "equalizer"},
                {"freq": 500, "gain": -0.5, "width": 2.0, "type": "equalizer"},
                {"freq": 3000, "gain": 1.5, "width": 2.0, "type": "equalizer"},
                {"freq": 10000, "gain": 2.0, "type": "highshelf"},
            ],
        },
        "compressor": {
            "threshold": -14, "ratio": 3.0, "attack": 10, "release": 80,
            "makeup": 2.0,
        },
        "stereo_width": 125,
        "intensity_default": 60,
    },
    "Hyperpop": {
        "category": "Electronic",
        "target_lufs": -7.0,
        "true_peak_ceiling": -0.1,
        "irc_mode": "IRC 5",
        "tone": "Bright",
        "eq": {
            "bands": [
                {"freq": 50, "gain": 3.0, "width": 0.5, "type": "equalizer"},
                {"freq": 800, "gain": -2.0, "width": 1.0, "type": "equalizer"},
                {"freq": 3000, "gain": 3.0, "width": 1.5, "type": "equalizer"},
                {"freq": 12000, "gain": 3.0, "type": "highshelf"},
            ],
        },
        "compressor": {
            "threshold": -6, "ratio": 8.0, "attack": 1, "release": 20,
            "makeup": 6.0,
        },
        "stereo_width": 150,
        "intensity_default": 90,
    },
    "Dance Pop": {
        "category": "Electronic",
        "target_lufs": -9.0,
        "true_peak_ceiling": -0.3,
        "irc_mode": "IRC 3",
        "tone": "Warm",
        "eq": {
            "bands": [
                {"freq": 60, "gain": 2.0, "width": 0.7, "type": "equalizer"},
                {"freq": 300, "gain": -0.5, "width": 1.5, "type": "equalizer"},
                {"freq": 2000, "gain": 1.0, "width": 2.0, "type": "equalizer"},
                {"freq": 10000, "gain": 1.5, "type": "highshelf"},
            ],
        },
        "compressor": {
            "threshold": -14, "ratio": 3.0, "attack": 8, "release": 60,
            "makeup": 2.5,
        },
        "stereo_width": 120,
        "intensity_default": 65,
    },

    # === Rock ===
    "Rock": {
        "category": "Rock",
        "target_lufs": -11.0,
        "true_peak_ceiling": -0.5,
        "irc_mode": "IRC 3",
        "tone": "Punchy",
        "eq": {
            "bands": [
                {"freq": 80, "gain": 1.5, "width": 0.8, "type": "equalizer"},
                {"freq": 300, "gain": -1.0, "width": 1.5, "type": "equalizer"},
                {"freq": 2500, "gain": 1.5, "width": 2.0, "type": "equalizer"},
                {"freq": 8000, "gain": 1.0, "type": "highshelf"},
            ],
        },
        "compressor": {
            "threshold": -16, "ratio": 3.0, "attack": 10, "release": 100,
            "makeup": 2.0,
        },
        "stereo_width": 110,
        "intensity_default": 55,
    },
    "Classic Rock": {
        "category": "Rock",
        "target_lufs": -12.0,
        "true_peak_ceiling": -0.5,
        "irc_mode": "IRC 2",
        "tone": "Analog",
        "eq": {
            "bands": [
                {"freq": 100, "gain": 1.0, "width": 1.0, "type": "equalizer"},
                {"freq": 500, "gain": -0.5, "width": 2.0, "type": "equalizer"},
                {"freq": 3000, "gain": 1.0, "width": 2.0, "type": "equalizer"},
                {"freq": 10000, "gain": -0.5, "type": "highshelf"},
            ],
        },
        "compressor": {
            "threshold": -18, "ratio": 2.5, "attack": 15, "release": 120,
            "makeup": 1.5,
        },
        "stereo_width": 105,
        "intensity_default": 45,
    },
    "Alt Rock": {
        "category": "Rock",
        "target_lufs": -11.0,
        "true_peak_ceiling": -0.5,
        "irc_mode": "IRC 3",
        "tone": "Warm",
        "eq": {
            "bands": [
                {"freq": 80, "gain": 1.5, "width": 0.8, "type": "equalizer"},
                {"freq": 400, "gain": -1.0, "width": 1.5, "type": "equalizer"},
                {"freq": 2000, "gain": 1.0, "width": 2.0, "type": "equalizer"},
                {"freq": 6000, "gain": 1.5, "width": 2.0, "type": "equalizer"},
            ],
        },
        "compressor": {
            "threshold": -15, "ratio": 3.0, "attack": 10, "release": 80,
            "makeup": 2.0,
        },
        "stereo_width": 115,
        "intensity_default": 55,
    },
    "Indie Rock": {
        "category": "Rock",
        "target_lufs": -12.0,
        "true_peak_ceiling": -1.0,
        "irc_mode": "IRC 2",
        "tone": "Warm",
        "eq": {
            "bands": [
                {"freq": 100, "gain": 1.0, "width": 1.0, "type": "equalizer"},
                {"freq": 800, "gain": 0.5, "width": 2.0, "type": "equalizer"},
                {"freq": 3000, "gain": 1.0, "width": 2.0, "type": "equalizer"},
                {"freq": 10000, "gain": 0.5, "type": "highshelf"},
            ],
        },
        "compressor": {
            "threshold": -18, "ratio": 2.5, "attack": 15, "release": 100,
            "makeup": 1.5,
        },
        "stereo_width": 115,
        "intensity_default": 45,
    },
    "Post Rock": {
        "category": "Rock",
        "target_lufs": -14.0,
        "true_peak_ceiling": -1.0,
        "irc_mode": "IRC 1",
        "tone": "Warm",
        "eq": {
            "bands": [
                {"freq": 60, "gain": 1.0, "width": 0.8, "type": "equalizer"},
                {"freq": 300, "gain": -0.5, "width": 2.0, "type": "equalizer"},
                {"freq": 2000, "gain": 0.5, "width": 3.0, "type": "equalizer"},
                {"freq": 8000, "gain": 1.0, "type": "highshelf"},
            ],
        },
        "compressor": {
            "threshold": -20, "ratio": 2.0, "attack": 20, "release": 150,
            "makeup": 1.0,
        },
        "stereo_width": 130,
        "intensity_default": 35,
    },
    "Punk Rock": {
        "category": "Rock",
        "target_lufs": -10.0,
        "true_peak_ceiling": -0.3,
        "irc_mode": "IRC 4",
        "tone": "Punchy",
        "eq": {
            "bands": [
                {"freq": 80, "gain": 2.0, "width": 0.7, "type": "equalizer"},
                {"freq": 400, "gain": -1.5, "width": 1.0, "type": "equalizer"},
                {"freq": 2500, "gain": 2.0, "width": 1.5, "type": "equalizer"},
                {"freq": 6000, "gain": 1.5, "width": 2.0, "type": "equalizer"},
            ],
        },
        "compressor": {
            "threshold": -12, "ratio": 4.0, "attack": 5, "release": 50,
            "makeup": 3.0,
        },
        "stereo_width": 105,
        "intensity_default": 75,
    },
    "Metal": {
        "category": "Rock",
        "target_lufs": -9.0,
        "true_peak_ceiling": -0.3,
        "irc_mode": "IRC 4",
        "tone": "Punchy",
        "eq": {
            "bands": [
                {"freq": 60, "gain": 2.5, "width": 0.6, "type": "equalizer"},
                {"freq": 300, "gain": -2.0, "width": 1.0, "type": "equalizer"},
                {"freq": 800, "gain": -1.0, "width": 1.5, "type": "equalizer"},
                {"freq": 3000, "gain": 2.0, "width": 1.5, "type": "equalizer"},
                {"freq": 8000, "gain": 1.5, "type": "highshelf"},
            ],
        },
        "compressor": {
            "threshold": -10, "ratio": 5.0, "attack": 3, "release": 40,
            "makeup": 4.0,
        },
        "stereo_width": 115,
        "intensity_default": 80,
    },

    # === Pop ===
    "Pop": {
        "category": "Pop",
        "target_lufs": -10.0,
        "true_peak_ceiling": -0.3,
        "irc_mode": "IRC 3",
        "tone": "Bright",
        "eq": {
            "bands": [
                {"freq": 80, "gain": 1.5, "width": 0.8, "type": "equalizer"},
                {"freq": 250, "gain": -1.0, "width": 1.5, "type": "equalizer"},
                {"freq": 2000, "gain": 1.0, "width": 2.0, "type": "equalizer"},
                {"freq": 5000, "gain": 1.5, "width": 2.0, "type": "equalizer"},
                {"freq": 12000, "gain": 1.5, "type": "highshelf"},
            ],
        },
        "compressor": {
            "threshold": -14, "ratio": 3.0, "attack": 10, "release": 80,
            "makeup": 2.5,
        },
        "stereo_width": 120,
        "intensity_default": 60,
    },
    "K-pop/J-pop": {
        "category": "Pop",
        "target_lufs": -9.0,
        "true_peak_ceiling": -0.3,
        "irc_mode": "IRC 4",
        "tone": "Bright",
        "eq": {
            "bands": [
                {"freq": 60, "gain": 2.0, "width": 0.7, "type": "equalizer"},
                {"freq": 300, "gain": -1.0, "width": 1.5, "type": "equalizer"},
                {"freq": 2500, "gain": 2.0, "width": 1.5, "type": "equalizer"},
                {"freq": 8000, "gain": 2.0, "width": 2.0, "type": "equalizer"},
                {"freq": 14000, "gain": 2.0, "type": "highshelf"},
            ],
        },
        "compressor": {
            "threshold": -12, "ratio": 4.0, "attack": 5, "release": 50,
            "makeup": 3.0,
        },
        "stereo_width": 130,
        "intensity_default": 75,
    },
    "Pop Country": {
        "category": "Pop",
        "target_lufs": -11.0,
        "true_peak_ceiling": -0.5,
        "irc_mode": "IRC 2",
        "tone": "Warm",
        "eq": {
            "bands": [
                {"freq": 100, "gain": 1.0, "width": 1.0, "type": "equalizer"},
                {"freq": 400, "gain": -0.5, "width": 2.0, "type": "equalizer"},
                {"freq": 2000, "gain": 1.0, "width": 2.0, "type": "equalizer"},
                {"freq": 5000, "gain": 1.0, "width": 2.0, "type": "equalizer"},
            ],
        },
        "compressor": {
            "threshold": -16, "ratio": 2.5, "attack": 15, "release": 100,
            "makeup": 1.5,
        },
        "stereo_width": 110,
        "intensity_default": 50,
    },
    "Latin Pop": {
        "category": "Pop",
        "target_lufs": -10.0,
        "true_peak_ceiling": -0.3,
        "irc_mode": "IRC 3",
        "tone": "Warm",
        "eq": {
            "bands": [
                {"freq": 80, "gain": 2.0, "width": 0.7, "type": "equalizer"},
                {"freq": 300, "gain": -0.5, "width": 1.5, "type": "equalizer"},
                {"freq": 1500, "gain": 1.0, "width": 2.0, "type": "equalizer"},
                {"freq": 5000, "gain": 1.0, "width": 2.0, "type": "equalizer"},
            ],
        },
        "compressor": {
            "threshold": -14, "ratio": 3.0, "attack": 8, "release": 70,
            "makeup": 2.5,
        },
        "stereo_width": 115,
        "intensity_default": 60,
    },

    # === Hip-Hop / Urban ===
    "Hip-Hop": {
        "category": "Hip-Hop",
        "target_lufs": -10.0,
        "true_peak_ceiling": -0.3,
        "irc_mode": "IRC 4",
        "tone": "Punchy",
        "eq": {
            "bands": [
                {"freq": 50, "gain": 3.0, "width": 0.5, "type": "equalizer"},
                {"freq": 200, "gain": -1.5, "width": 1.0, "type": "equalizer"},
                {"freq": 3000, "gain": 1.5, "width": 2.0, "type": "equalizer"},
                {"freq": 10000, "gain": 1.0, "type": "highshelf"},
            ],
        },
        "compressor": {
            "threshold": -12, "ratio": 4.0, "attack": 5, "release": 50,
            "makeup": 3.0,
        },
        "stereo_width": 115,
        "intensity_default": 70,
    },
    "Classic Hip-Hop": {
        "category": "Hip-Hop",
        "target_lufs": -11.0,
        "true_peak_ceiling": -0.5,
        "irc_mode": "IRC 3",
        "tone": "Analog",
        "eq": {
            "bands": [
                {"freq": 60, "gain": 2.0, "width": 0.7, "type": "equalizer"},
                {"freq": 300, "gain": -1.0, "width": 1.5, "type": "equalizer"},
                {"freq": 1000, "gain": 0.5, "width": 2.0, "type": "equalizer"},
                {"freq": 5000, "gain": 0.5, "width": 2.0, "type": "equalizer"},
            ],
        },
        "compressor": {
            "threshold": -15, "ratio": 3.0, "attack": 10, "release": 80,
            "makeup": 2.0,
        },
        "stereo_width": 105,
        "intensity_default": 55,
    },
    "Trap": {
        "category": "Hip-Hop",
        "target_lufs": -8.0,
        "true_peak_ceiling": -0.1,
        "irc_mode": "IRC 5",
        "tone": "Punchy",
        "eq": {
            "bands": [
                {"freq": 35, "gain": 4.0, "width": 0.4, "type": "equalizer"},
                {"freq": 150, "gain": -2.0, "width": 1.0, "type": "equalizer"},
                {"freq": 3000, "gain": 2.0, "width": 1.5, "type": "equalizer"},
                {"freq": 8000, "gain": 2.0, "type": "highshelf"},
            ],
        },
        "compressor": {
            "threshold": -8, "ratio": 6.0, "attack": 2, "release": 25,
            "makeup": 5.0,
        },
        "stereo_width": 120,
        "intensity_default": 85,
    },
    "RnB/Soul": {
        "category": "Hip-Hop",
        "target_lufs": -12.0,
        "true_peak_ceiling": -1.0,
        "irc_mode": "IRC 2",
        "tone": "Warm",
        "eq": {
            "bands": [
                {"freq": 80, "gain": 1.5, "width": 0.8, "type": "equalizer"},
                {"freq": 300, "gain": -0.5, "width": 2.0, "type": "equalizer"},
                {"freq": 2000, "gain": 0.5, "width": 2.0, "type": "equalizer"},
                {"freq": 10000, "gain": 0.5, "type": "highshelf"},
            ],
        },
        "compressor": {
            "threshold": -18, "ratio": 2.0, "attack": 15, "release": 120,
            "makeup": 1.0,
        },
        "stereo_width": 120,
        "intensity_default": 40,
    },
    "Reggaeton": {
        "category": "Hip-Hop",
        "target_lufs": -9.0,
        "true_peak_ceiling": -0.3,
        "irc_mode": "IRC 4",
        "tone": "Warm",
        "eq": {
            "bands": [
                {"freq": 60, "gain": 3.0, "width": 0.6, "type": "equalizer"},
                {"freq": 200, "gain": -1.0, "width": 1.5, "type": "equalizer"},
                {"freq": 2000, "gain": 1.0, "width": 2.0, "type": "equalizer"},
                {"freq": 8000, "gain": 1.0, "type": "highshelf"},
            ],
        },
        "compressor": {
            "threshold": -12, "ratio": 4.0, "attack": 5, "release": 50,
            "makeup": 3.0,
        },
        "stereo_width": 110,
        "intensity_default": 70,
    },

    # === Acoustic / Traditional ===
    "Jazz": {
        "category": "Acoustic",
        "target_lufs": -16.0,
        "true_peak_ceiling": -1.0,
        "irc_mode": "IRC 1",
        "tone": "Transparent",
        "eq": {
            "bands": [
                {"freq": 80, "gain": 0.5, "width": 1.0, "type": "equalizer"},
                {"freq": 500, "gain": -0.5, "width": 2.0, "type": "equalizer"},
                {"freq": 3000, "gain": 0.5, "width": 3.0, "type": "equalizer"},
            ],
        },
        "compressor": {
            "threshold": -22, "ratio": 1.5, "attack": 25, "release": 200,
            "makeup": 0.5,
        },
        "stereo_width": 100,
        "intensity_default": 25,
    },
    "Vocal Jazz": {
        "category": "Acoustic",
        "target_lufs": -15.0,
        "true_peak_ceiling": -1.0,
        "irc_mode": "IRC 1",
        "tone": "Warm",
        "eq": {
            "bands": [
                {"freq": 100, "gain": 0.5, "width": 1.0, "type": "equalizer"},
                {"freq": 400, "gain": -0.5, "width": 2.0, "type": "equalizer"},
                {"freq": 2500, "gain": 1.0, "width": 2.0, "type": "equalizer"},
                {"freq": 8000, "gain": 0.5, "type": "highshelf"},
            ],
        },
        "compressor": {
            "threshold": -20, "ratio": 2.0, "attack": 20, "release": 150,
            "makeup": 1.0,
        },
        "stereo_width": 105,
        "intensity_default": 30,
    },
    "Folk": {
        "category": "Acoustic",
        "target_lufs": -14.0,
        "true_peak_ceiling": -1.0,
        "irc_mode": "IRC 1",
        "tone": "Warm",
        "eq": {
            "bands": [
                {"freq": 100, "gain": 0.5, "width": 1.0, "type": "equalizer"},
                {"freq": 500, "gain": -0.5, "width": 2.0, "type": "equalizer"},
                {"freq": 3000, "gain": 1.0, "width": 2.0, "type": "equalizer"},
                {"freq": 8000, "gain": 0.5, "type": "highshelf"},
            ],
        },
        "compressor": {
            "threshold": -20, "ratio": 2.0, "attack": 20, "release": 150,
            "makeup": 1.0,
        },
        "stereo_width": 100,
        "intensity_default": 30,
    },
    "Country": {
        "category": "Acoustic",
        "target_lufs": -12.0,
        "true_peak_ceiling": -1.0,
        "irc_mode": "IRC 2",
        "tone": "Warm",
        "eq": {
            "bands": [
                {"freq": 100, "gain": 1.0, "width": 1.0, "type": "equalizer"},
                {"freq": 500, "gain": -0.5, "width": 2.0, "type": "equalizer"},
                {"freq": 2500, "gain": 1.0, "width": 2.0, "type": "equalizer"},
                {"freq": 8000, "gain": 0.5, "type": "highshelf"},
            ],
        },
        "compressor": {
            "threshold": -18, "ratio": 2.5, "attack": 15, "release": 120,
            "makeup": 1.5,
        },
        "stereo_width": 105,
        "intensity_default": 40,
    },
    "Reggae": {
        "category": "Acoustic",
        "target_lufs": -12.0,
        "true_peak_ceiling": -1.0,
        "irc_mode": "IRC 2",
        "tone": "Warm",
        "eq": {
            "bands": [
                {"freq": 80, "gain": 2.0, "width": 0.7, "type": "equalizer"},
                {"freq": 400, "gain": -1.0, "width": 1.5, "type": "equalizer"},
                {"freq": 1500, "gain": 1.0, "width": 2.0, "type": "equalizer"},
                {"freq": 5000, "gain": 0.5, "width": 2.0, "type": "equalizer"},
            ],
        },
        "compressor": {
            "threshold": -16, "ratio": 3.0, "attack": 10, "release": 80,
            "makeup": 2.0,
        },
        "stereo_width": 100,
        "intensity_default": 50,
    },
    "Orchestral": {
        "category": "Acoustic",
        "target_lufs": -18.0,
        "true_peak_ceiling": -1.0,
        "irc_mode": "IRC 1",
        "tone": "Transparent",
        "eq": {
            "bands": [
                {"freq": 60, "gain": 0.5, "width": 1.0, "type": "equalizer"},
                {"freq": 300, "gain": -0.5, "width": 2.0, "type": "equalizer"},
                {"freq": 5000, "gain": 0.5, "width": 3.0, "type": "equalizer"},
            ],
        },
        "compressor": {
            "threshold": -24, "ratio": 1.5, "attack": 30, "release": 250,
            "makeup": 0.5,
        },
        "stereo_width": 110,
        "intensity_default": 20,
    },

    # === Ambient / Chill ===
    "Ambient": {
        "category": "Ambient",
        "target_lufs": -18.0,
        "true_peak_ceiling": -1.0,
        "irc_mode": "IRC 1",
        "tone": "Transparent",
        "eq": {
            "bands": [
                {"freq": 60, "gain": 0.5, "width": 0.8, "type": "equalizer"},
                {"freq": 500, "gain": -0.5, "width": 3.0, "type": "equalizer"},
                {"freq": 8000, "gain": 0.5, "type": "highshelf"},
            ],
        },
        "compressor": {
            "threshold": -24, "ratio": 1.5, "attack": 30, "release": 300,
            "makeup": 0.5,
        },
        "stereo_width": 140,
        "intensity_default": 20,
    },
    "LoFi": {
        "category": "Ambient",
        "target_lufs": -14.0,
        "true_peak_ceiling": -1.0,
        "irc_mode": "IRC 1",
        "tone": "Analog",
        "eq": {
            "bands": [
                {"freq": 80, "gain": 1.5, "width": 0.8, "type": "equalizer"},
                {"freq": 500, "gain": 0.5, "width": 2.0, "type": "equalizer"},
                {"freq": 3000, "gain": -1.0, "width": 2.0, "type": "equalizer"},
                {"freq": 12000, "gain": -2.0, "type": "highshelf"},
            ],
        },
        "compressor": {
            "threshold": -18, "ratio": 2.0, "attack": 15, "release": 100,
            "makeup": 1.5,
        },
        "stereo_width": 110,
        "intensity_default": 35,
    },

    # === All-Purpose ===
    "All-Purpose Mastering": {
        "category": "General",
        "target_lufs": -14.0,
        "true_peak_ceiling": -1.0,
        "irc_mode": "IRC 2",
        "tone": "Transparent",
        "eq": {
            "bands": [
                {"freq": 80, "gain": 0.5, "width": 1.0, "type": "equalizer"},
                {"freq": 300, "gain": -0.5, "width": 2.0, "type": "equalizer"},
                {"freq": 3000, "gain": 0.5, "width": 2.0, "type": "equalizer"},
                {"freq": 10000, "gain": 0.5, "type": "highshelf"},
            ],
        },
        "compressor": {
            "threshold": -18, "ratio": 2.0, "attack": 15, "release": 100,
            "makeup": 1.0,
        },
        "stereo_width": 105,
        "intensity_default": 40,
    },
}


# Platform loudness targets
PLATFORM_TARGETS = {
    "YouTube": {"target_lufs": -14.0, "true_peak": -1.0},
    "Spotify": {"target_lufs": -14.0, "true_peak": -1.0},
    "Apple Music": {"target_lufs": -16.0, "true_peak": -1.0},
    "Amazon Music": {"target_lufs": -14.0, "true_peak": -2.0},
    "Tidal": {"target_lufs": -14.0, "true_peak": -1.0},
    "CD / Digital Release": {"target_lufs": -9.0, "true_peak": 0.0},
    "Podcast": {"target_lufs": -16.0, "true_peak": -1.0},
    "Broadcast (EBU R128)": {"target_lufs": -23.0, "true_peak": -1.0},
    "Custom": {"target_lufs": -14.0, "true_peak": -1.0},
}


def get_genre_list():
    """Return sorted list of genre names grouped by category."""
    categories = {}
    for name, profile in GENRE_PROFILES.items():
        cat = profile["category"]
        if cat not in categories:
            categories[cat] = []
        categories[cat].append(name)
    return categories


def get_genre_profile(genre_name):
    """Get complete profile for a genre, or All-Purpose if not found."""
    return GENRE_PROFILES.get(genre_name, GENRE_PROFILES["All-Purpose Mastering"])


def get_irc_mode(mode_name):
    """Get IRC mode parameters. Supports both old (IRC II) and new (IRC 2) naming."""
    # Direct lookup
    if mode_name in IRC_MODES:
        return IRC_MODES[mode_name]
    # Legacy name mapping (Roman → Arabic)
    legacy_map = {"IRC I": "IRC 1", "IRC II": "IRC 2", "IRC III": "IRC 3",
                  "IRC IV": "IRC 4", "IRC V": "IRC 5"}
    mapped = legacy_map.get(mode_name)
    if mapped and mapped in IRC_MODES:
        return IRC_MODES[mapped]
    return IRC_MODES["IRC 2"]


def get_irc_sub_modes(mode_name):
    """Get list of sub-mode names for a given IRC mode."""
    mode = IRC_MODES.get(mode_name, {})
    return mode.get("sub_modes", [])


def get_tone_preset(tone_name):
    """Get tone preset parameters."""
    return TONE_PRESETS.get(tone_name, TONE_PRESETS["Transparent"])
