import streamlit as st

st.set_page_config(
    page_title="Streamlit App",
    page_icon=":guardsman:",
    layout="wide",
    initial_sidebar_state="expanded",
)


def main():
    st.title("Welcome to My Streamlit App")
    st.write("This is a simple Streamlit application.")

    # Example input
    name = st.text_input("Enter your name:")

    if st.button("Submit"):
        if name:
            st.success(f"Hello, {name}!")
        else:
            st.error("Please enter your name.")


if __name__ == "__main__":
    main()
