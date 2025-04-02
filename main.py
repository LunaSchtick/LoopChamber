import streamlit as st
import json
import os
import matplotlib.pyplot as plt
import random

# ─────────────────────────────────────────────────────
# CONFIG
st.set_page_config(page_title="LoopChamber", layout="wide")

# ─────────────────────────────────────────────────────
# MEMORY FILE SETUP
MEMORY_FILE = "memory/memories.json"
os.makedirs("memory", exist_ok=True)
if not os.path.exists(MEMORY_FILE):
    with open(MEMORY_FILE, "w") as f:
        json.dump([], f)

try:
    with open(MEMORY_FILE, "r") as f:
        memories = json.load(f)
except:
    memories = []

# ─────────────────────────────────────────────────────
# SIDEBAR NAVIGATION
st.sidebar.title("🧠 Navigation")
page = st.sidebar.radio("Go to", ["Home", "Memory Lab", "Loop Selector"])

# ─────────────────────────────────────────────────────
# HOME
if page == "Home":
    st.title("🎷 LoopChamber: Improvisational Memory Interface")
    st.markdown("Where contradiction becomes melody. Hold tension. Return again.")
    st.subheader("📡 System Status")
    st.write("Total memories stored:", len(memories))
    st.success("LoopChamber is running.")

# ─────────────────────────────────────────────────────
# MEMORY LAB
elif page == "Memory Lab":
    st.title("🧬 Memory Lab")
    st.markdown("Add new memories to your evolving jazzscape.")

    memory_text = st.text_area("Memory content")

    if st.button("Add Memory"):
        new_memory = {
            "text": memory_text,
            "pitch": round(random.uniform(0.3, 1.0), 2),
            "dissonance": round(random.uniform(0.1, 1.0), 2),
            "tempo": round(random.uniform(0.2, 1.0), 2),
            "emotion": random.choice(["positive", "neutral", "negative", "tense"])
        }
        memories.append(new_memory)
        with open(MEMORY_FILE, "w") as f:
            json.dump(memories, f, indent=2)
        st.success("🎶 Memory added.")

    st.subheader("🧾 Existing Memories")
    if not memories:
        st.info("No memories stored yet.")
    else:
        for i, mem in enumerate(memories):
            st.markdown(f"**{i+1}.** {mem['text']} — *Dissonance:* {mem['dissonance']}, *Emotion:* {mem['emotion']}")

# ─────────────────────────────────────────────────────
# LOOP SELECTOR (STARFIELD VIEW)
elif page == "Loop Selector":
    st.title("💫 Memory Starfield: Contradiction as Constellation")

    if not memories:
        st.info("No memories yet. Add some in the Memory Lab to populate your starfield.")
    else:
        def emotion_to_color(emotion):
            return {
                "positive": "green",
                "neutral": "blue",
                "negative": "red",
                "tense": "orange"
            }.get(emotion, "gray")

        st.subheader("🪐 Debug Memory Coordinates")
        for i, mem in enumerate(memories):
            st.write(f"Memory {i+1}: Dissonance = {mem['dissonance']}, Pitch = {mem['pitch']}, Tempo = {mem['tempo']}, Emotion = {mem['emotion']}")

        fig, ax = plt.subplots(figsize=(10, 6))
        for mem in memories:
            # Add jitter to prevent overlapping points
            x = mem.get("dissonance", 0.5) + random.uniform(-0.01, 0.01)
            y = mem.get("pitch", 0.5) + random.uniform(-0.01, 0.01)
            size = 500 * mem.get("tempo", 0.3)
            color = emotion_to_color(mem.get("emotion", "neutral"))
            ax.scatter(x, y, s=size, color=color, alpha=0.6, edgecolors='white', linewidth=0.5)

        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.set_xlabel("Dissonance →")
        ax.set_ylabel("↑ Pitch (Relevance)")
        ax.set_title("🌌 Memory Starfield")

        st.pyplot(fig)
        st.caption("Each circle is a memory. Position = tension & importance. Color = emotion. Size = recall tempo.")