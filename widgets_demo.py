import numpy as np
import pandas as pd
import streamlit as st

# Almost you can learn every work In https://docs.streamlit.io/library/get-started/main-concepts

x = st.slider('x')  # this is a widget but output a number to x

st.write(x, "squared is", x * x)
st.text_input("Your name", key="name")  # let user change a key

st.session_state.name  # And use the key in anywhere,
# look like "session_state" is a function can use any key
# more information https://docs.streamlit.io/library/api-reference/session-state

# it's not hide something be formal, but it's work.
if st.checkbox('Show dataframe'):
    chart_data = pd.DataFrame(
        np.random.randn(20, 3),
        columns=["a", "b", "c"]
    )
    chart_data




