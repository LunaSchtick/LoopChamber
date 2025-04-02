import streamlit as st
import os
import json
import time
from datetime import datetime
import random
import matplotlib.pyplot as plt
import numpy as np

# Import our new Memory Scoring Engine
from memory_scorer import MemoryScorer
from memory_store import MemoryStore

# Page setup
st.set_page_config(
    page_title="LoopChamber",
    page_icon="🎵",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'initialized' not in st.session_state:
    st.session_state.initialized = True
    st.session_state.current_view = "home"
    st.session_state.selected_memory = None
    st.session_state.selected_loop = None
    st.session_state.error_message = None
    st.session_state.success_message = None
    st.session_state.api_key = None

# Initialize core components
@st.cache_resource
def initialize_components():
    memory_store = MemoryStore()
    memory_scorer = MemoryScorer()

    # Update tempo scores periodically
    memory_store.update_tempo_scores(memory_scorer)

    return {
        "memory_store": memory_store,
        "memory_scorer": memory_scorer
    }

components = initialize_components()

# Helper functions
def add_new_memory(content, memory_type):
    """Add a new memory with automatic scoring."""
    try:
        # Get existing memories for context
        existing_memories = components["memory_store"].get_all_memories()

        # Score the memory
        scores = components["memory_scorer"].score_memory(
            content, memory_type, existing_memories
        )

        # Add to memory store
        memory_id = components["memory_store"].add_memory(
            content=content,
            memory_type=memory_type,
            pitch=scores["pitch"],
            dissonance=scores["dissonance"],
            tempo=scores["tempo"],
            emotion=scores["emotion"]
        )

        st.session_state.success_message = "Memory added successfully!"
        return memory_id
    except Exception as e:
        st.session_state.error_message = f"Error adding memory: {str(e)}"
        return None

def find_dissonant_pairs():
    """Find memory pairs with significant dissonance."""
    try:
        # Get all memories
        memories = components["memory_store"].get_all_memories()

        # Find dissonant pairs
        pairs = components["memory_scorer"].find_most_dissonant_pairs(memories)

        if not pairs:
            st.session_state.error_message = "No significantly dissonant memory pairs found."
            return None

        return pairs
    except Exception as e:
        st.session_state.error_message = f"Error finding dissonant pairs: {str(e)}"
        return None

def connect_memories(source_id, target_id, connection_type, strength):
    """Create a connection between two memories."""
    try:
        connection_id = components["memory_store"].create_connection(
            source_id, target_id, connection_type, strength
        )
        st.session_state.success_message = "Memories connected successfully!"
        return connection_id
    except Exception as e:
        st.session_state.error_message = f"Error connecting memories: {str(e)}"
        return None

def update_api_key(key):
    """Update the OpenAI API key for AI-enhanced scoring."""
    if key:
        st.session_state.api_key = key
        components["memory_scorer"].use_ai = True
        components["memory_scorer"].openai_api_key = key
        st.session_state.success_message = "API key set. AI-enhanced scoring enabled."
    else:
        st.session_state.api_key = None
        components["memory_scorer"].use_ai = False
        components["memory_scorer"].openai_api_key = None
        st.session_state.success_message = "API key cleared. Using heuristic scoring."

# Visualization functions
def memory_musical_chart(memories, width=800, height=500):
    """Generate a musical chart visualization of memories."""
    if not memories:
        return None

    fig, ax = plt.subplots(figsize=(width/100, height/100))

    # Extract data
    pitch_values = []
    dissonance_values = []
    tempo_values = []
    emotion_colors = []
    labels = []

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

        # Truncate content for label
        content = memory.get('content', '')[:50]
        if len(memory.get('content', '')) > 50:
            content += "..."
        labels.append(content)

    # Plot
    scatter = ax.scatter(
        dissonance_values, 
        pitch_values, 
        s=[t * 100 + 50 for t in tempo_values],  # Size based on tempo
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

    # Add annotations on hover (need to save to HTML for full interactivity)
    # For now, add a few annotations to the largest points
    top_indices = sorted(range(len(tempo_values)), key=lambda i: tempo_values[i], reverse=True)[:3]
    for idx in top_indices:
        ax.annotate(
            labels[idx],
            (dissonance_values[idx], pitch_values[idx]),
            xytext=(10, 10),
            textcoords='offset points',
            bbox=dict(boxstyle="round,pad=0.3", fc="white", alpha=0.8)
        )

    return fig

# Main UI
st.title("LoopChamber: A Jazz-Aware Reflective Agent")

# Display messages
if st.session_state.error_message:
    st.error(st.session_state.error_message)
    st.session_state.error_message = None

if st.session_state.success_message:
    st.success(st.session_state.success_message)
    st.session_state.success_message = None

# Sidebar navigation
with st.sidebar:
    st.header("Navigation")

    if st.button("🏠 Home", use_container_width=True):
        st.session_state.current_view = "home"
        st.session_state.selected_memory = None

    if st.button("🧠 Memory Lab", use_container_width=True):
        st.session_state.current_view = "memory_lab"

    if st.button("🎼 Musical Analysis", use_container_width=True):
        st.session_state.current_view = "analysis"

    # API key input for AI-enhanced scoring
    st.markdown("---")
    st.subheader("AI Enhancement")
    api_key = st.text_input(
        "OpenAI API Key",
        type="password", 
        value=st.session_state.api_key or "",
        help="Enter your OpenAI API key to enable AI-enhanced memory scoring"
    )

    if st.button("Set API Key", use_container_width=True):
        update_api_key(api_key)

    # Stats
    st.markdown("---")
    st.subheader("System Stats")
    memory_count = len(components["memory_store"].get_all_memories())
    connection_count = len(components["memory_store"].get_connections())

    st.write(f"Memories: {memory_count}")
    st.write(f"Connections: {connection_count}")

    # Help
    st.markdown("---")
    with st.expander("Help & Info"):
        st.markdown("""
        **Memory Scoring Engine** scores each memory with musical attributes:

        - **Pitch**: Relevance or salience (0.0-1.0)
        - **Dissonance**: Degree of contradiction/conflict (0.0-1.0)
        - **Tempo**: Frequency of recall (0.0-1.0)
        - **Emotion**: Emotional charge (positive, negative, neutral, complex)

        These scores are visualized in the Musical Analysis section.
        """)

# Main content based on current view
if st.session_state.current_view == "home":
    st.markdown("""
    ## Welcome to LoopChamber

    LoopChamber is an interactive, improvisational AI memory system where internal contradictions 
    aren't resolved immediately, but held, revisited, and creatively metabolized over time—like 
    a jazz musician playing with unresolved chords across sets.

    This implementation features a sophisticated **Memory Scoring Engine** that tags each memory with musical attributes:

    - **Pitch**: Relevance or salience
    - **Dissonance**: Degree of contradiction/conflict  
    - **Tempo**: Frequency of recall
    - **Emotion**: Emotional charge

    ### Getting Started

    - Add memories in the **Memory Lab**
    - Explore the musical attributes in the **Musical Analysis** section
    - Find interesting dissonances between memories to generate creative tension
    """)

    # Quick actions
    st.markdown("### Quick Actions")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("➕ Add Memory", use_container_width=True):
            st.session_state.current_view = "memory_lab"

    with col2:
        if st.button("📊 View Musical Analysis", use_container_width=True):
            st.session_state.current_view = "analysis"

    # Show a preview of musical attributes if we have memories
    memories = components["memory_store"].get_all_memories()
    if memories:
        st.markdown("### Memory Musical Attributes Preview")
        fig = memory_musical_chart(memories, width=600, height=400)
        if fig:
            st.pyplot(fig)
    else:
        st.info("Add some memories to see their musical attributes visualized.")

elif st.session_state.current_view == "memory_lab":
    st.header("🧠 Memory Lab")

    # Tabs for different memory operations
    memory_tab1, memory_tab2, memory_tab3 = st.tabs(["Add Memory", "Browse Memories", "Connect Memories"])

    with memory_tab1:
        with st.form("new_memory_form"):
            st.subheader("Add New Memory")
            memory_content = st.text_area(
                "Enter your memory, insight, or experience:",
                height=150,
                placeholder="What's on your mind? Add an insight, observation, question..."
            )

            col1, col2 = st.columns(2)

            with col1:
                memory_type = st.selectbox(
                    "Memory type:",
                    options=["insight", "observation", "question", "reflection", "event"]
                )

            with col2:
                st.write("Your memory will be automatically scored with:")
                st.write("- Pitch (relevance)")
                st.write("- Dissonance (contradiction)")
                st.write("- Tempo (recall frequency)")
                st.write("- Emotion (emotional charge)")

            submit_button = st.form_submit_button("Add Memory")

            if submit_button and memory_content:
                add_new_memory(memory_content, memory_type)

    with memory_tab2:
        st.subheader("Browse Memories")

        memories = components["memory_store"].get_all_memories()

        if not memories:
            st.info("No memories yet. Add some using the 'Add Memory' tab!")
        else:
            # Add filtering options
            filter_col1, filter_col2, filter_col3 = st.columns(3)

            with filter_col1:
                memory_types = list(set(m["type"] for m in memories))
                filter_type = st.multiselect(
                    "Filter by type:",
                    options=memory_types,
                    default=[]
                )

            with filter_col2:
                emotions = list(set(m["musical_attributes"]["emotion"] for m in memories))
                filter_emotion = st.multiselect(
                    "Filter by emotion:",
                    options=emotions,
                    default=[]
                )

            with filter_col3:
                sort_by = st.selectbox(
                    "Sort by:",
                    options=["Newest First", "Oldest First", "Highest Pitch", "Highest Dissonance", "Highest Tempo"]
                )

            # Apply filters
            filtered_memories = memories

            if filter_type:
                filtered_memories = [m for m in filtered_memories if m["type"] in filter_type]

            if filter_emotion:
                filtered_memories = [m for m in filtered_memories if m["musical_attributes"]["emotion"] in filter_emotion]

            # Apply sorting
            if sort_by == "Newest First":
                filtered_memories = sorted(filtered_memories, key=lambda m: m.get("created_at", ""), reverse=True)
            elif sort_by == "Oldest First":
                filtered_memories = sorted(filtered_memories, key=lambda m: m.get("created_at", ""))
            elif sort_by == "Highest Pitch":
                filtered_memories = sorted(filtered_memories, key=lambda m: m["musical_attributes"].get("pitch", 0), reverse=True)
            elif sort_by == "Highest Dissonance":
                filtered_memories = sorted(filtered_memories, key=lambda m: m["musical_attributes"].get("dissonance", 0), reverse=True)
            elif sort_by == "Highest Tempo":
                filtered_memories = sorted(filtered_memories, key=lambda m: m["musical_attributes"].get("tempo", 0), reverse=True)

            # Display memories
            for memory in filtered_memories:
                with st.expander(f"{memory.get('type', 'Memory').capitalize()}: {memory.get('content', '')[:50]}..."):
                    st.write(memory.get('content', ''))

                    col1, col2, col3, col4 = st.columns(4)

                    with col1:
                        pitch = memory.get('musical_attributes', {}).get('pitch', 0)
                        st.metric("Pitch", f"{pitch:.2f}")
                        st.progress(pitch)

                    with col2:
                        dissonance = memory.get('musical_attributes', {}).get('dissonance', 0)
                        st.metric("Dissonance", f"{dissonance:.2f}")
                        st.progress(dissonance)

                    with col3:
                        tempo = memory.get('musical_attributes', {}).get('tempo', 0)
                        st.metric("Tempo", f"{tempo:.2f}")
                        st.progress(tempo)

                    with col4:
                        emotion = memory.get('musical_attributes', {}).get('emotion', 'neutral')
                        st.metric("Emotion", emotion)

                        # Color for the emotion
                        emotion_colors = {
                            "positive": "green",
                            "negative": "red",
                            "neutral": "blue",
                            "complex": "purple"
                        }
                        color = emotion_colors.get(emotion, "gray")
                        st.markdown(f"<div style='background-color:{color};height:10px;border-radius:2px;'></div>", unsafe_allow_html=True)

    with memory_tab3:
        st.subheader("Connect Memories")

        memories = components["memory_store"].get_all_memories()

        if len(memories) < 2:
            st.info("You need at least two memories to create connections. Add more memories first!")
        else:
            with st.form("connect_memories_form"):
                st.write("Select two memories to connect:")

                # Format memory options
                memory_options = {m["id"]: f"{m['type']}: {m['content'][:50]}..." for m in memories}

                source_id = st.selectbox(
                    "Source memory:",
                    options=list(memory_options.keys()),
                    format_func=lambda x: memory_options[x],
                    key="source_select"
                )

                target_id = st.selectbox(
                    "Target memory:",
                    options=list(memory_options.keys()),
                    format_func=lambda x: memory_options[x],
                    key="target_select"
                )

                connection_type = st.selectbox(
                    "Connection type:",
                    options=["related", "contradicts", "supports", "questions", "expands"]
                )

                strength = st.slider("Connection strength:", 0.1, 1.0, 0.5, 0.1)

                submit_button = st.form_submit_button("Create Connection")

                if submit_button and source_id and target_id and source_id != target_id:
                    connect_memories(source_id, target_id, connection_type, strength)

            # Find dissonant pairs automatically
            st.markdown("---")
            st.subheader("Automatic Dissonance Detection")
            st.write("Find potentially contradictory memory pairs automatically.")

            if st.button("Find Dissonant Pairs"):
                pairs = find_dissonant_pairs()

                if pairs:
                    for mem1, mem2, score in pairs:
                        with st.expander(f"Dissonance Score: {score:.2f}"):
                            st.markdown("**Memory 1:**")
                            st.write(mem1.get('content', '')[:200])

                            st.markdown("**Memory 2:**")
                            st.write(mem2.get('content', '')[:200])

                            if st.button("Connect These Memories", key=f"connect_{mem1['id']}_{mem2['id']}"):
                                connect_memories(mem1['id'], mem2['id'], "contradicts", score)

            # Show existing connections
            st.markdown("---")
            st.subheader("Existing Connections")

            connections = components["memory_store"].get_connections()

            if not connections:
                st.info("No connections yet. Create your first connection above!")
            else:
                for connection in connections:
                    source = next((m for m in memories if m["id"] == connection["source"]), None)
                    target = next((m for m in memories if m["id"] == connection["target"]), None)

                    if source and target:
                        with st.expander(f"{connection['type'].capitalize()} ({connection['strength']:.1f})"):
                            st.markdown("**Source:**")
                            st.write(source.get('content', '')[:100])

                            st.markdown("**Target:**")
                            st.write(target.get('content', '')[:100])

elif st.session_state.current_view == "analysis":
    st.header("🎼 Musical Analysis")

    memories = components["memory_store"].get_all_memories()

    if not memories:
        st.info("No memories available for analysis. Add some memories first!")
    else:
        # Create tabs for different visualizations
        viz_tab1, viz_tab2, viz_tab3 = st.tabs(["Musical Attributes", "Dissonance Analysis", "Emotion Distribution"])

        with viz_tab1:
            st.subheader("Memory Musical Attributes")
            st.markdown("""
            This visualization maps your memories according to their musical attributes:
            - **X-axis**: Dissonance (degree of contradiction/conflict)
            - **Y-axis**: Pitch (relevance or salience)
            - **Size**: Tempo (frequency of recall)
            - **Color**: Emotion (emotional charge)
            """)

            fig = memory_musical_chart(memories)
            if fig:
                st.pyplot(fig)

            # Show attribute distributions
            st.markdown("### Attribute Distributions")

            dist_col1, dist_col2 = st.columns(2)

            with dist_col1:
                # Pitch distribution
                pitch_values = [m["musical_attributes"]["pitch"] for m in memories]
                fig, ax = plt.subplots()
                ax.hist(pitch_values, bins=10, alpha=0.7, color='blue')
                ax.set_xlabel('Pitch Value')
                ax.set_ylabel('Frequency')
                ax.set_title('Pitch Distribution')
                st.pyplot(fig)

                # Emotion distribution
                emotions = [m["musical_attributes"]["emotion"] for m in memories]
                emotion_counts = {}
                for emotion in emotions:
                    emotion_counts[emotion] = emotion_counts.get(emotion, 0) + 1

                fig, ax = plt.subplots()
                bars = ax.bar(emotion_counts.keys(), emotion_counts.values(), color=['green', 'red', 'blue', 'purple'])
                ax.set_xlabel('Emotion')
                ax.set_ylabel('Count')
                ax.set_title('Emotion Distribution')
                st.pyplot(fig)

            with dist_col2:
                # Dissonance distribution
                dissonance_values = [m["musical_attributes"]["dissonance"] for m in memories]
                fig, ax = plt.subplots()
                ax.hist(dissonance_values, bins=10, alpha=0.7, color='red')
                ax.set_xlabel('Dissonance Value')
                ax.set_ylabel('Frequency')
                ax.set_title('Dissonance Distribution')
                st.pyplot(fig)

                # Tempo distribution
                tempo_values = [m["musical_attributes"]["tempo"] for m in memories]
                fig, ax = plt.subplots()
                ax.hist(tempo_values, bins=10, alpha=0.7, color='green')
                ax.set_xlabel('Tempo Value')
                ax.set_ylabel('Frequency')
                ax.set_title('Tempo Distribution')
                st.pyplot(fig)

        with viz_tab2:
            st.subheader("Dissonance Analysis")
            st.markdown("""
            This section analyzes contradictions and tensions in your memory space.
            Higher dissonance indicates potential contradictions worth exploring.
            """)

            # Get top dissonant memories
            dissonant_memories = sorted(
                memories, 
                key=lambda m: m["musical_attributes"]["dissonance"],
                reverse=True
            )[:5]

            st.markdown("### Top Dissonant Memories")
            for memory in dissonant_memories:
                with st.expander(f"{memory['type'].capitalize()} (Dissonance: {memory['musical_attributes']['dissonance']:.2f})"):
                    st.write(memory['content'])

            # Find dissonant pairs
            st.markdown("### Dissonant Memory Pairs")
            pairs = find_dissonant_pairs()

            if pairs:
                for mem1, mem2, score in pairs:
                    with st.expander(f"Pair with Dissonance: {score:.2f}"):
                        st.markdown("**Memory 1:**")
                        st.write(mem1.get('content', ''))

                        st.markdown("**Memory 2:**")
                        st.write(mem2.get('content', ''))

                        st.markdown("**Potential Tension:**")
                        st.write(f"These memories have a dissonance score of {score:.2f}, suggesting significant tension or contradiction.")
            else:
                st.info("No significant dissonant pairs found in your memories.")

            # Dissonance heatmap
            st.markdown("### Dissonance Heatmap")
            if len(memories) >= 3:
                # Create a matrix of dissonance between pairs
                n = min(10, len(memories))  # Limit to 10 memories for readability
                recent_memories = memories[:n]

                matrix = np.zeros((n, n))
                labels = []

                for i in range(n):
                    labels.append(f"M{i+1}")
                    for j in range(n):
                        if i != j:
                            matrix[i, j] = components["memory_scorer"].score_dissonance_between_memories(
                                recent_memories[i], recent_memories[j]
                            )

                fig, ax = plt.subplots(figsize=(10, 8))
                im = ax.imshow(matrix, cmap='YlOrRd')

                # Add colorbar
                cbar = ax.figure.colorbar(im, ax=ax)
                cbar.ax.set_ylabel("Dissonance Score", rotation=-90, va="bottom")

                # Add ticks and labels
                ax.set_xticks(np.arange(n))
                ax.set_yticks(np.arange(n))
                ax.set_xticklabels(labels)
                ax.set_yticklabels(labels)

                # Rotate the tick labels
                plt.setp(ax.get_xticklabels(), rotation=45, ha="right", rotation_mode="anchor")

                # Add a title
                ax.set_title("Memory Dissonance Heatmap")

                # Loop over data dimensions and create text annotations
                for i in range(n):
                    for j in range(n):
                        if i != j:
                            text = ax.text(j, i, f"{matrix[i, j]:.2f}",
                                          ha="center", va="center", 
                                          color="black" if matrix[i, j] < 0.5 else "white")

                fig.tight_layout()
                st.pyplot(fig)

                # Add a legend for the memory indices
                st.markdown("**Memory Legend:**")
                for i, memory in enumerate(recent_memories):
                    st.write(f"**M{i+1}**: {memory['content'][:100]}...")
            else:
                st.info("Need at least 3 memories to generate a dissonance heatmap.")

        with viz_tab3:
            st.subheader("Emotion Analysis")
            st.markdown("""
            This section analyzes the emotional landscape of your memory space.
            Different emotions create different tonal qualities in the overall composition.
            """)

            # Emotion distribution pie chart
            emotions = [m["musical_attributes"]["emotion"] for m in memories]
            emotion_counts = {}
            for emotion in emotions:
                emotion_counts[emotion] = emotion_counts.get(emotion, 0) + 1

            fig, ax = plt.subplots(figsize=(8, 8))
            colors = ['#4CAF50', '#F44336', '#2196F3', '#9C27B0']  # green, red, blue, purple
            ax.pie(
                emotion_counts.values(), 
                labels=emotion_counts.keys(),
                autopct='%1.1f%%',
                colors=colors,
                startangle=90
            )
            ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle
            ax.set_title('Emotion Distribution')
            st.pyplot(fig)

            # Show memories by emotion
            st.markdown("### Memories by Emotion")

            for emotion in emotion_counts.keys():
                with st.expander(f"{emotion.capitalize()} Memories ({emotion_counts[emotion]})"):
                    emotion_memories = [m for m in memories if m["musical_attributes"]["emotion"] == emotion]
                    for memory in emotion_memories:
                        st.markdown(f"**{memory['type'].capitalize()}**: {memory['content'][:200]}...")
                        st.markdown("---")

            # Emotion over time
            st.markdown("### Emotional Trends")

            # Sort memories by creation time
            time_sorted_memories = sorted(
                memories, 
                key=lambda m: m.get("created_at", "")
            )

            # Extract dates and emotions
            dates = []
            emotion_series = {
                "positive": [],
                "negative": [],
                "neutral": [],
                "complex": []
            }

            current_date = None
            date_emotions = {
                "positive": 0,
                "negative": 0,
                "neutral": 0,
                "complex": 0
            }

            for memory in time_sorted_memories:
                date_str = memory.get("created_at", "")[:10]  # Get just the date part
                emotion = memory["musical_attributes"]["emotion"]

                if date_str != current_date:
                    if current_date is not None:
                        dates.append(current_date)
                        for e in emotion_series:
                            emotion_series[e].append(date_emotions[e])

                    # Reset for new date
                    current_date = date_str
                    date_emotions = {e: 0 for e in emotion_series}

                date_emotions[emotion] += 1

            # Add the last date
            if current_date is not None:
                dates.append(current_date)
                for e in emotion_series:
                    emotion_series[e].append(date_emotions[e])

            # Plot emotion trends if we have data
            if dates:
                fig, ax = plt.subplots(figsize=(10, 6))

                bottom = np.zeros(len(dates))
                colors = ['#4CAF50', '#F44336', '#2196F3', '#9C27B0']  # green, red, blue, purple
                emotions = ["positive", "negative", "neutral", "complex"]

                for i, emotion in enumerate(emotions):
                    if emotion in emotion_series:
                        ax.bar(dates, emotion_series[emotion], bottom=bottom, label=emotion, color=colors[i])
                        bottom += np.array(emotion_series[emotion])

                ax.set_title('Emotions Over Time')
                ax.set_xlabel('Date')
                ax.set_ylabel('Number of Memories')
                ax.legend()

                # Rotate date labels for readability
                plt.xticks(rotation=45)
                fig.tight_layout()

                st.pyplot(fig)
            else:
                st.info("Not enough date information to show emotional trends.")

# Run the application
if __name__ == "__main__":
    pass  # Main execution is handled by Streamlit