import streamlit as st

from src.ml_model import load_model, predict_risk, classify_risk
from src.knowledge import (
    search_knowledge,
    format_context,
    format_references,
    KNOWLEDGE_AVAILABLE,
)
from src.copilot import chat


st.set_page_config(
    page_title="Paramedic AI",
    page_icon="🚑",
    layout="wide",
)


@st.cache_resource
def get_model():
    return load_model()


try:
    model = get_model()
    model_error = None
except Exception as error:
    model = None
    model_error = str(error)


st.title("🚑 Paramedic AI")

st.caption(
    "EMS education and decision-support demonstration"
)


st.warning(
    "DEMO ONLY — NOT FOR CLINICAL DECISION MAKING. "
    "Always follow current local EMS protocols, "
    "medical direction, and applicable regulations."
)


st.sidebar.header("Patient Assessment")


age = st.sidebar.number_input(
    "Age",
    min_value=0,
    max_value=120,
    value=50,
)

heart_rate = st.sidebar.number_input(
    "Heart Rate",
    min_value=0.0,
    max_value=300.0,
    value=90.0,
)

systolic_bp = st.sidebar.number_input(
    "Systolic BP",
    min_value=0.0,
    max_value=300.0,
    value=120.0,
)

diastolic_bp = st.sidebar.number_input(
    "Diastolic BP",
    min_value=0.0,
    max_value=200.0,
    value=80.0,
)

respiratory_rate = st.sidebar.number_input(
    "Respiratory Rate",
    min_value=0.0,
    max_value=100.0,
    value=18.0,
)

spo2 = st.sidebar.number_input(
    "SpO₂",
    min_value=0.0,
    max_value=100.0,
    value=98.0,
)

temperature = st.sidebar.number_input(
    "Temperature",
    min_value=80.0,
    max_value=115.0,
    value=98.6,
)


st.header("🧠 ML Risk Assessment")


if model_error:

    st.error(
        f"Unable to load the ML model: {model_error}"
    )

else:

    if st.button(
        "Run ML Assessment",
        type="primary",
    ):

        try:

            probability = predict_risk(
                model=model,
                age=age,
                heart_rate=heart_rate,
                systolic_bp=systolic_bp,
                diastolic_bp=diastolic_bp,
                respiratory_rate=respiratory_rate,
                spo2=spo2,
                temperature=temperature,
            )

            category = classify_risk(probability)

            st.metric(
                "Model Output",
                f"{probability * 100:.1f}%",
            )

            if category == "HIGHER RISK":

                st.error(category)

            elif category == "INTERMEDIATE RISK":

                st.warning(category)

            else:

                st.success(category)

            st.info(
                "This is a demonstration output from the "
                "machine-learning model. It is not a diagnosis "
                "or a validated clinical risk score."
            )

        except Exception as error:

            st.error(
                f"ML prediction error: {error}"
            )


st.divider()

st.header("💬 Paramedic Copilot")


if "messages" not in st.session_state:

    st.session_state.messages = []


for message in st.session_state.messages:

    with st.chat_message(message["role"]):

        st.markdown(
            message["content"]
        )


question = st.chat_input(
    "Ask Paramedic AI a question..."
)


if question:

    st.session_state.messages.append(
        {
            "role": "user",
            "content": question,
        }
    )

    with st.chat_message("user"):

        st.markdown(question)


    with st.chat_message("assistant"):

        with st.spinner(
            "Searching references and thinking..."
        ):

            try:

                results = []

                if KNOWLEDGE_AVAILABLE:

                    results = search_knowledge(
                        question
                    )


                context = format_context(
                    results
                )


                answer = chat(
                    messages=st.session_state.messages,
                    context=context,
                )


                references = format_references(
                    results
                )


                if references:

                    answer += (
                        "\n\n### References used\n"
                        + "\n".join(references)
                    )


                st.markdown(answer)


                st.session_state.messages.append(
                    {
                        "role": "assistant",
                        "content": answer,
                    }
                )


            except Exception as error:

                error_message = (
                    f"Copilot error: {error}"
                )

                st.error(error_message)

                st.session_state.messages.append(
                    {
                        "role": "assistant",
                        "content": error_message,
                    }
                )


st.divider()


if KNOWLEDGE_AVAILABLE:

    st.caption(
        "📚 Knowledge search: available"
    )

else:

    st.caption(
        "📚 Knowledge search: unavailable"
    )


st.caption(
    "DEMO ONLY — NOT FOR CLINICAL DECISION MAKING. "
    "Always follow current local EMS protocols, "
    "medical direction, and applicable regulations."
)
