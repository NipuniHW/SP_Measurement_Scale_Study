import streamlit as st
import time
from connection import Connection
import qi

# Title and setup
st.title("Select a Level:")
session = None

# Initialize connection to Pepper robot
pepper = Connection()
session = pepper.connect('127.0.0.1', '39051')

# Create a proxy to the AL services
behavior_mng_service = session.service('ALBehaviorManager')
tts_service = session.service('ALTextToSpeech')

# Button press triggers
col1, col2, col3 = st.columns(3)

try:
    # Define High SP behavior
    def run_high_sp(tts_service, behavior_mng_service):
        tts_service.say("Hello, welcome, my name is Pepper. There are three items on the table in front of you. Using the pencil and paper, please sketch as many of the items as you like, with as much detail as you want")
        behavior_mng_service.startBehavior("sp_study/Intro")
        time.sleep(30)

        tts_service.say("Good choice")
        behavior_mng_service.startBehavior("sp_study/Speak01")
        time.sleep(30)

        behavior_mng_service.startBehavior("sp_study/Action01")

        tts_service.say("Have you considered adding more shading?")
        behavior_mng_service.startBehavior("sp_study/Speak02")
        time.sleep(30)

        behavior_mng_service.startBehavior("sp_study/Action02")

        tts_service.say("That’s looking great!")
        behavior_mng_service.startBehavior("sp_study/Speak03")
        time.sleep(30)

        behavior_mng_service.startBehavior("sp_study/Action03")

        tts_service.say("What if you added more contrast?")
        behavior_mng_service.startBehavior("sp_study/Speak04")
        time.sleep(30)

        behavior_mng_service.startBehavior("sp_study/Action04")

        tts_service.say("I like how you’re sketching that")
        behavior_mng_service.startBehavior("sp_study/Speak05")
        time.sleep(30)

        behavior_mng_service.startBehavior("sp_study/Action03")

        tts_service.say("You have 30-seconds left")
        behavior_mng_service.startBehavior("sp_study/Speak06")
        time.sleep(30)

        behavior_mng_service.startBehavior("sp_study/Action02")

        tts_service.say("You put in a great effort, please stop sketching now. Feel free to take your sketches with you. Goodbye")
        behavior_mng_service.startBehavior("sp_study/Outro")

    # Define Low SP behavior
    def run_low_sp(tts_service):
        tts_service.say("Hello, welcome, my name is Pepper. There are three items on the table in front of you. Using the pencil and paper, please sketch as many of the items as you like, with as much detail as you want")
        behavior_mng_service.startBehavior("sp_study/Intro")
        time.sleep(60)

        behavior_mng_service.startBehavior("sp_study/Action04")
        time.sleep(60)

        behavior_mng_service.startBehavior("sp_study/Action01")
        time.sleep(60)

        tts_service.say("You put in a great effort, please stop sketching now. Feel free to take your sketches with you. Goodbye")
        behavior_mng_service.startBehavior("sp_study/Outro")

    with col1:
        if st.button("Low SP"):
            st.write("Starting Low Social Presence Interaction...")
            run_low_sp(tts_service, behavior_mng_service)

    with col2:
        if st.button("High SP"):
            st.write("Starting High Social Presence Interaction...")
            run_high_sp(tts_service, behavior_mng_service)

    with col3:
        st.write("")
        st.write("")
        if st.button("Stop Animation", type="primary"):  # Create the button
            behavior_mng_service.stopAllBehaviors()

except KeyboardInterrupt:
    print("Keyboard interrupt received. Closing connection.")
    if session:
        st.session_state.session.close()
finally:
    if session:
        st.session_state.session.close()