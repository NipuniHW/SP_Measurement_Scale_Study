import streamlit as st
import time
import threading
from connection import Connection
import qi

class PepperController:
    """
    A class to manage Pepper robot connections and behaviors.
    """
    def __init__(self):
        self.session = None
        self.behavior_mng_service = None
        self.tts_service = None
        self.is_connected = False
        self.current_thread = None
        self.stop_requested = False
    
    def connect(self, ip='127.0.0.1', port='45553'):
        """
        Establish connection to Pepper robot.
        """
        try:
            pepper = Connection()
            self.session = pepper.connect(ip, port)
            self.behavior_mng_service = self.session.service('ALBehaviorManager')
            self.tts_service = self.session.service('ALTextToSpeech')
            self.is_connected = True
            return True
        except Exception as e:
            st.error(f"Failed to connect to Pepper: {str(e)}")
            return False
    
    def disconnect(self):
        """
        Safely disconnect from Pepper robot.
        """
        try:
            if self.behavior_mng_service:
                self.behavior_mng_service.stopAllBehaviors()
            if self.session:
                self.session.close()
            self.is_connected = False
        except Exception as e:
            st.error(f"Error during disconnect: {str(e)}")
    
    def execute_animation(self, action, text=""):
        """
        Execute animation with optional speech.
        """
        if not self.is_connected or self.stop_requested:
            return
        
        try:
            self.behavior_mng_service.stopAllBehaviors()
            if action:
                self.behavior_mng_service.startBehavior(action)
            if text:
                self.tts_service.say(text)
        except Exception as e:
            st.error(f"Error executing animation: {str(e)}")
    
    def safe_sleep(self, duration):
        """
        Sleep with interruption capability.
        """
        for _ in range(int(duration)):
            if self.stop_requested:
                break
            time.sleep(1)
    
    def run_high_sp_sequence(self):
        """
        Execute high social presence interaction sequence.
        """
        sequence = [
            ("sp_study/Intro", "Hello, welcome, my name is Pepper. There are three items on the table in front of you. Using the pencil and paper, please sketch as many of the items as you like, with as much detail as you want", 30),
            ("sp_study/Speak01", "Good choice", 30),
            ("sp_study/Action01", "", 0),
            ("sp_study/Speak02", "Have you considered adding more shading?", 30),
            ("sp_study/Action02", "", 0),
            ("sp_study/Speak03", "That's looking great!", 30),
            ("sp_study/Action03", "", 0),
            ("sp_study/Speak04", "What if you added more contrast?", 30),
            ("sp_study/Action04", "", 0),
            ("sp_study/Speak05", "I like how you're sketching that", 30),
            ("sp_study/Action03", "", 0),
            ("sp_study/Speak06", "You have 30-seconds left", 30),
            ("sp_study/Action02", "", 0),
            ("sp_study/Outro", "You put in a great effort, please stop sketching now. Feel free to take your sketches with you. Goodbye", 0)
        ]
        
        for action, text, sleep_time in sequence:
            if self.stop_requested:
                break
            self.execute_animation(action, text)
            if sleep_time > 0:
                self.safe_sleep(sleep_time)
        
        self.behavior_mng_service.stopAllBehaviors()
    
    def run_low_sp_sequence(self):
        """
        Execute low social presence interaction sequence.
        """
        sequence = [
            ("sp_study/Intro", "Hello, welcome, my name is Pepper. There are three items on the table in front of you. Using the pencil and paper, please sketch as many of the items as you like, with as much detail as you want", 60),
            ("sp_study/Action04", "", 60),
            ("sp_study/Action01", "", 60),
            ("sp_study/Outro", "You put in a great effort, please stop sketching now. Feel free to take your sketches with you. Goodbye", 0)
        ]
        
        for action, text, sleep_time in sequence:
            if self.stop_requested:
                break
            self.execute_animation(action, text)
            if sleep_time > 0:
                self.safe_sleep(sleep_time)
    
    def start_sequence(self, sequence_type):
        """
        Start a sequence in a separate thread.
        """
        self.stop_requested = False
        
        if sequence_type == "high":
            target_func = self.run_high_sp_sequence
        elif sequence_type == "low":
            target_func = self.run_low_sp_sequence
        else:
            return False
        
        self.current_thread = threading.Thread(target=target_func)
        self.current_thread.daemon = True
        self.current_thread.start()
        return True
    
    def stop_sequence(self):
        """
        Stop current sequence execution.
        """
        self.stop_requested = True
        if self.behavior_mng_service:
            self.behavior_mng_service.stopAllBehaviors()

# Initialize Streamlit app
st.set_page_config(page_title="Pepper Robot Controller", layout="centered")
st.title("🤖 Pepper Robot Social Presence Study")

# Initialize session state
if 'pepper_controller' not in st.session_state:
    st.session_state.pepper_controller = PepperController()
    st.session_state.sequence_running = False

pepper_controller = st.session_state.pepper_controller

# Connection management
st.sidebar.header("Connection Settings")
with st.sidebar:
    ip_address = st.text_input("IP Address", value="127.0.0.1")
    port = st.text_input("Port", value="45553")
    
    if st.button("Connect to Pepper", disabled=pepper_controller.is_connected):
        with st.spinner("Connecting to Pepper..."):
            if pepper_controller.connect(ip_address, port):
                st.success("✅ Connected to Pepper!")
                st.rerun()
    
    if st.button("Disconnect", disabled=not pepper_controller.is_connected):
        pepper_controller.disconnect()
        st.success("Disconnected from Pepper")
        st.rerun()
    
    # Connection status
    status_color = "🟢" if pepper_controller.is_connected else "🔴"
    status_text = "Connected" if pepper_controller.is_connected else "Disconnected"
    st.write(f"{status_color} Status: {status_text}")

# Main interface
if not pepper_controller.is_connected:
    st.warning("⚠️ Please connect to Pepper robot first using the sidebar.")
else:
    st.success("Ready to start interaction!")
    
    # Control buttons
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🔽 Low Social Presence", 
                    disabled=st.session_state.sequence_running,
                    use_container_width=True):
            if pepper_controller.start_sequence("low"):
                st.session_state.sequence_running = True
                st.info("🔽 Starting Low Social Presence interaction...")
                st.rerun()
    
    with col2:
        if st.button("🔼 High Social Presence", 
                    disabled=st.session_state.sequence_running,
                    use_container_width=True):
            if pepper_controller.start_sequence("high"):
                st.session_state.sequence_running = True
                st.info("🔼 Starting High Social Presence interaction...")
                st.rerun()
    
    with col3:
        if st.button("🛑 Stop Interaction", 
                    type="primary",
                    use_container_width=True):
            pepper_controller.stop_sequence()
            st.session_state.sequence_running = False
            st.info("🛑 Interaction stopped")
            st.rerun()
    
    # Status indicator
    if st.session_state.sequence_running:
        st.info("🤖 Interaction in progress... Click 'Stop Interaction' to halt.")
    
    # Instructions
    with st.expander("ℹ️ Instructions"):
        st.markdown("""
        **Low Social Presence**: Pepper will provide minimal interaction with basic animations only.
        
        **High Social Presence**: Pepper will actively engage with verbal feedback and encouraging comments during the sketching task.
        
        **Stop Interaction**: Immediately halts any running interaction sequence.
        
        The participant will be asked to sketch items on the table using pencil and paper.
        """)

# Cleanup on app termination
def cleanup():
    if 'pepper_controller' in st.session_state:
        st.session_state.pepper_controller.disconnect()

# Register cleanup
import atexit
atexit.register(cleanup)