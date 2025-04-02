import streamlit as st
import os
import json
import time
from datetime import datetime
import random
import matplotlib.pyplot as plt
import numpy as np

# PAGE CONFIGURATION
st.set_page_config(
    page_title="LoopChamber Memory Scoring",
    page_icon="🎵",
    layout="wide"
)

# MEMORY SCORER CLASS
class MemoryScorer:
    """Memory Scoring Engine for LoopChamber"""

    def __init__(self):
        # Emotional lexicons for detecting emotions
        self.emotional_lexicons = {
            "positive": [
                "happy", "joy", "glad", "delight", "pleased", "cheerful", "content",
                "satisfied", "excited", "thrilled", "optimistic", "enthusiastic",
                "hopeful", "confident", "proud", "love", "adore", "enjoy", "like"
            ],
            "negative": [
                "sad", "unhappy", "depressed", "gloomy", "miserable", "disappointed",
                "frustrated", "annoyed", "angry", "furious", "outraged", "irritated",
                "upset", "worried", "anxious", "afraid", "fearful", "scared"
            ],
            "neutral": [
                "think", "consider", "believe", "understand", "know", "recognize",
                "observe", "notice", "perceive", "feel", "sense", "experience"
            ],
            "complex": [
                "bittersweet", "ambivalent", "conflicted", "torn", "mixed feelings",
                "nostalgic", "melancholy", "sentimental", "wistful", "longing"
            ]
        }

        # Contradiction signals
        self.contradiction_signals = [
            "but", "however", "nevertheless", "conversely", "on the other hand",
            "in contrast", "contrary", "opposite", "unlike", "instead", 
            "while", "whereas", "yet", "although", "despite", "in spite"
        ]

    def score_memory(self, memory_content, memory_type, existing_memories=None):
        """Score a memory based on musical attributes"""
        # Text preprocessing
        text = memory_content.lower()
        word_count = len(text.split())

        # ====== PITCH (relevance/salience) ======
        # Base on content length and type

        # Length factor (longer text often has more substance)
        length_factor = min(1.0, max(0.1, word_count / 100))

        # Memory type factor
        type_weights = {
            "insight": 0.8,      # Insights are typically high relevance
            "question": 0.7,     # Questions are exploratory
            "observation": 0.6,  # Observations are contextual
            "event": 0.5,        # Events are factual
            "reflection": 0.7    # Reflections are introspective
        }
        type_factor = type_weights.get(memory_type.lower(), 0.5)

        # Calculate pitch from factors
        pitch = (length_factor * 0.4) + (type_factor * 0.6)

        # ====== DISSONANCE (contradiction/conflict) ======
        # Check for contradiction signals and compare with existing memories

        # Internal contradiction score
        contradiction_score = 0
        for signal in self.contradiction_signals:
            if signal in text:
                contradiction_score += 0.15
        contradiction_score = min(0.8, contradiction_score)

        # Compare with existing memories if available
        comparison_score = 0
        if existing_memories:
            # Look for semantic contradictions with previous memories
            for memory in existing_memories[-5:]:  # Check the last 5 memories
                if 'content' in memory:
                    existing_text = memory['content'].lower()

                    # Simple bag-of-words comparison for opposing concepts
                    words = set(text.split())
                    existing_words = set(existing_text.split())

                    # If there are shared words but in contradictory context
                    shared_words = words.intersection(existing_words)
                    if shared_words and any(signal in text for signal in self.contradiction_signals):
                        comparison_score += 0.2

        # Calculate dissonance score
        dissonance = max(0.1, min(0.9, contradiction_score + comparison_score))

        # ====== TEMPO (recall frequency) ======
        # Base this on engagement factors that might prompt recall

        # Question marks increase tempo (they prompt thinking)
        question_factor = min(0.8, text.count('?') * 0.2)

        # Emotional charge increases tempo (emotional events are recalled more)
        emotional_words = 0
        for category in ['positive', 'negative', 'complex']:
            for word in self.emotional_lexicons[category]:
                if word in text:
                    emotional_words += 1
        emotion_factor = min(0.8, emotional_words * 0.05)

        # Memory type factor for tempo
        tempo_type_weights = {
            "insight": 0.7,     # Insights are revisited often
            "question": 0.8,    # Questions prompt frequent returns
            "observation": 0.5,  # Observations less often
            "event": 0.4,       # Events are recalled less frequently
            "reflection": 0.6    # Reflections are revisited
        }
        tempo_type_factor = tempo_type_weights.get(memory_type.lower(), 0.5)

        # Calculate tempo
        tempo = (question_factor * 0.3) + (emotion_factor * 0.3) + (tempo_type_factor * 0.4)

        # ====== EMOTION (emotional charge) ======
        # Determine the dominant emotion based on emotional keywords

        emotion_counts = {category: 0 for category in self.emotional_lexicons.keys()}

        for category, words in self.emotional_lexicons.items():
            for word in words:
                if word in text:
                    emotion_counts[category] += 1

        # Find dominant emotion
        dominant_emotion = "neutral"
        max_count = 0

        for emotion, count in emotion_counts.items():
            if count > max_count:
                max_count = count
                dominant_emotion = emotion

        # Check for mixed emotions (indicating complexity)
        if emotion_counts["positive"] > 0 and emotion_counts["negative"] > 0:
            if emotion_counts["complex"] > 0 or abs(emotion_counts["positive"] - emotion_counts["negative"]) < 3:
                dominant_emotion = "complex"

        # Compile the final scores
        scores = {
            "pitch": round(pitch, 2),
            "dissonance": round(dissonance, 2),
            "tempo": round(tempo, 2),
            "emotion": dominant_emotion
        }

        return scores

# MEMORY STORE CLASS
class MemoryStore:
    """Memory storage for LoopChamber"""

    def __init__(self):
        """Initialize with empty memory lists"""
        self.memories = []

    def add_memory(self, content, memory_type, pitch, dissonance, tempo, emotion):
        """Add a new memory with musical attributes"""
        memory_id = f"mem_{int(time.time())}_{random.randint(1000, 9999)}"
        timestamp = datetime.now().isoformat()

        memory = {
            "id": memory_id,
            "content": content,
            "type": memory_type,
            "created_at": timestamp,
            "musical_attributes": {
                "pitch": pitch,
                "dissonance": dissonance,
                "tempo": tempo,
                "emotion": emotion
            }
        }

        self.memories.append(memory)
        return memory_id

    def get_all_memories(self):
        """Get all memories"""
        return self.memories

# INITIALIZE SESSION STATE
if 'memory_store' not in st.session_state:
    st.session_state.memory_store = MemoryStore()

if 'memory_scorer' not in st.session_state:
    st.session_state.memory_scorer = MemoryScorer()

# HELPER FUNCTIONS
def add_memory(content, memory_type):
    """Add a new memory with automatic scoring"""
    # Get existing memories for context
    existing_memories = st.session_state.memory_store.get_all_memories()

    # Score the memory
    scores = st.session_state.memory_scorer.score_memory(
        content, memory_type, existing_memories
    )

    # Add to memory store
    memory_id = st.session_state.memory_store.add_memory(
        content=content,
        memory_type=memory_type,
        pitch=scores["pitch"],
        dissonance=scores["dissonance"],
        tempo=scores["tempo"],
        emotion=scores["emotion"]
    )

    return memory_id, scores

def memory_musical_chart(memories):
    """Create a visualization of memory musical attributes"""
    if not memories:
        return None

    fig, ax = plt.subplots(figsize=(10, 6))

    # Extract data
    pitch_values = []
    dissonance_values = []
    tempo_values = []
    emotion_colors = []
    memory_types = []

    # Color mapping for emotions
    emotion_color_map = {
        "positive": "#4CAF50",  # Green
        "negative": "#F44336",  # Red
        "neutral": "#2196F3",   # Blue
        "complex": "#9C27B0"    # Purple
    }

    for memory in memories:
        attrs = memory.get('musical_attributes', {})
        pitch_values.append(attrs.get('pitch', 0.5))
        dissonance_values.append(attrs.get('dissonance', 0.2))
        tempo_values.append(attrs.get('tempo', 0.5))

        emotion = attrs.get('emotion', 'neutral')
        emotion_colors.append(emotion_color_map.get(emotion, "#2196F3"))
        memory_types.append(memory.get('type', 'unknown'))

    # Plot
    scatter = ax.scatter(
        dissonance_values, 
        pitch_values, 
        s=[t * 200 + 50 for t in tempo_values],  # Size based on tempo
        c=emotion_colors,
        alpha=0.7
    )

    # Reference lines
    ax.axhline(y=0.5, color='gray', linestyle='--', alpha=0.3)
    ax.axvline(x=0.5, color='gray', linestyle='--', alpha=0.3)

    # Labels and title
    ax.set_xlabel('Dissonance')
    ax.set_ylabel('Pitch')
    ax.set_title('Memory Musical Attributes')

    # Set axis limits with padding
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)

    # Add a legend for emotions
    from matplotlib.lines import Line2D
    legend_elements = [
        Line2D([0], [0], marker='o', color='w', markerfacecolor=color, label=emotion, markersize=10)
        for emotion, color in emotion_color_map.items()
    ]
    ax.legend(handles=legend_elements, title="Emotions")

    # Annotate points
    for i, (x, y) in enumerate(zip(dissonance_values, pitch_values)):
        ax.annotate(
            memory_types[i][:3],
            (x, y),
            xytext=(0, 0),
            textcoords="offset points",
            ha='center', va='center',
            color='white',
            fontweight='bold',
            fontsize=8
        )

    return fig

# MAIN UI
st.title("LoopChamber: Memory Scoring Engine")

st.markdown("""
This demonstration focuses on the Memory Scoring Engine component of LoopChamber.
Each memory is automatically scored with musical attributes:

- **Pitch**: Relevance or salience (0.0-1.0)
- **Dissonance**: Degree of contradiction/conflict (0.0-1.0)
- **Tempo**: Frequency of recall (0.0-1.0)
- **Emotion**: Emotional charge (positive, negative, neutral, complex)
""")

# Create two columns for layout
left_col, right_col = st.columns([3, 2])

with left_col:
    # Memory input form
    st.subheader("Add a New Memory")

    with st.form("memory_form"):
        memory_content = st.text_area(
            "Enter your memory:",
            height=150,
            placeholder="What's on your mind? Add an insight, observation, or question..."
        )

        memory_type = st.selectbox(
            "Memory type:",
            options=["insight", "observation", "question", "reflection", "event"]
        )

        submit = st.form_submit_button("Add Memory")

        if submit and memory_content:
            memory_id, scores = add_memory(memory_content, memory_type)
            st.success("Memory added and scored!")

            # Show the scores
            st.subheader("Musical Scores:")
            score_cols = st.columns(4)
            with score_cols[0]:
                st.metric("Pitch", f"{scores['pitch']:.2f}")
            with score_cols[1]:
                st.metric("Dissonance", f"{scores['dissonance']:.2f}")
            with score_cols[2]:
                st.metric("Tempo", f"{scores['tempo']:.2f}")
            with score_cols[3]:
                st.metric("Emotion", scores['emotion'])

    # Display existing memories
    st.subheader("Memory Collection")

    memories = st.session_state.memory_store.get_all_memories()

    if not memories:
        st.info("No memories yet. Add your first memory above!")
    else:
        for memory in memories:
            with st.expander(f"{memory.get('type', 'Memory').capitalize()}: {memory.get('content', '')[:50]}..."):
                st.write(memory.get('content', ''))

                # Display musical attributes
                cols = st.columns(4)
                with cols[0]:
                    pitch = memory.get('musical_attributes', {}).get('pitch', 0)
                    st.metric("Pitch", f"{pitch:.2f}")
                    st.progress(pitch)

                with cols[1]:
                    dissonance = memory.get('musical_attributes', {}).get('dissonance', 0)
                    st.metric("Dissonance", f"{dissonance:.2f}")
                    st.progress(dissonance)

                with cols[2]:
                    tempo = memory.get('musical_attributes', {}).get('tempo', 0)
                    st.metric("Tempo", f"{tempo:.2f}")
                    st.progress(tempo)

                with cols[3]:
                    emotion = memory.get('musical_attributes', {}).get('emotion', 'neutral')
                    st.metric("Emotion", emotion)

                    # Color indicator for emotion
                    emotion_colors = {
                        "positive": "green",
                        "negative": "red",
                        "neutral": "blue",
                        "complex": "purple"
                    }
                    color = emotion_colors.get(emotion, "gray")
                    st.markdown(f"<div style='background-color:{color};height:10px;border-radius:2px;'></div>", unsafe_allow_html=True)

with right_col:
    # Visualization
    st.subheader("Musical Visualization")

    if memories:
        fig = memory_musical_chart(memories)
        if fig:
            st.pyplot(fig)

            st.markdown("""
            **How to read this chart:**
            - **X-axis**: Dissonance (contradiction level)
            - **Y-axis**: Pitch (relevance/importance)
            - **Size**: Tempo (recall frequency)
            - **Color**: Emotion (green=positive, red=negative, blue=neutral, purple=complex)
            - **Label**: First 3 letters of memory type
            """)
    else:
        st.info("Add some memories to see the musical visualization.")

    # Explain the scoring algorithm
    st.subheader("How Scoring Works")

    with st.expander("Pitch (Relevance) Scoring"):
        st.markdown("""
        **Pitch** represents the relevance or importance of a memory:

        - Higher for longer, more detailed memories
        - Varies by memory type (insights > questions > observations)
        - Represents how "high" the memory registers in importance
        """)

    with st.expander("Dissonance (Contradiction) Scoring"):
        st.markdown("""
        **Dissonance** measures contradiction or tension:

        - Detects contradiction signals ("but", "however", "although")
        - Compares with existing memories for contradictions
        - Higher dissonance indicates potential creative tension
        """)

    with st.expander("Tempo (Recall) Scoring"):
        st.markdown("""
        **Tempo** predicts how frequently a memory might be recalled:

        - Questions tend to have higher tempo (prompting return)
        - Emotional content increases tempo
        - Different memory types have different base tempos
        - In a full implementation, this evolves over time with usage
        """)

    with st.expander("Emotion Scoring"):
        st.markdown("""
        **Emotion** categorizes the emotional charge:

        - Detects emotional keywords in content
        - Categories: positive, negative, neutral, complex
        - "Complex" represents mixed or nuanced emotions
        - Contributes to the overall "tone" of the memory space
        """)