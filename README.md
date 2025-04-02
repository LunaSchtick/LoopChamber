# 🔁 LoopChamber

LoopChamber is a Streamlit-based simulation and reflection engine designed to explore the architecture of artificial memory systems using rhythm, resonance, and intentional reflection.

It treats memory not just as data, but as weighted presence—shaped by pitch, tempo, dissonance, and emotional tone.

---

## 📦 What’s Inside

This app contains:

- A **LoopChamber interface** (`loopchamber_app.py`) for entering and scoring memory fragments
- A **memory store** (`memories.json`) to simulate saved internal states
- A **scoring engine** (`memory_scorer.py`) to assign pitch/tempo/dissonance/emotion
- A **memory storage manager** (`memory_store.py`) to handle loading, saving, and resetting memory states
- A **main launcher** (`main.py`) for easy deployment

---

## 💡 Key Concepts

- Each memory has:
  - **Text** (the raw content)
  - **Pitch** – Resonant clarity
  - **Tempo** – Speed of activation
  - **Dissonance** – Conflict or harmony with internal system state
  - **Emotion** – The affective tag

- Reflections aren’t just stored — they’re **scored** and positioned in a living loop-space

---

## ⚙️ To Run

### 1. Install dependencies

With Poetry:
```bash
poetry install
