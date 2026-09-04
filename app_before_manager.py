import streamlit as st

from src.ml_model import (
    load_model,
    predict_risk,
    classify_risk,
)

from src.knowledge import (
    search_knowledge,
    format_context,
    format_references,
    summarize_sources,
    load_source_registry,
    KNOWLEDGE_AVAILABLE,
)

from src.copilot import chat


# ==================================================
# PAGE CONFIG
# ==================================================

st.set_page_config(
    page_title="Paramedic AI",
    page_icon="🚑",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ==================================================
# CUSTOM CSS
# ==================================================

st.markdown(
    """
    <style>

    .main {
        background-color: #f5f7fa;
    }

    .block-container {
        padding-top: 2rem;
        padding-bottom: 3rem;
    }

    .hero {
        background: linear-gradient(
            135deg,
            #b91c1c,
            #7f1d1d
        );
        padding: 1.5rem 2rem;
        border-radius: 14px;
        color: white;
        margin-bottom: 1.5rem;
    }

    .hero h1 {
        margin: 0;
        font-size: 2.4rem;
    }

    .hero p {
        margin-top: 0.4rem;
        opacity: 0.9;
    }

    .safety {
        padding: 0.8rem 1rem;
        border-radius: 10px;
        background: #fff7ed;
        border-left: 5px solid #f97316;
        color: #7c2d12;
        margin-bottom: 1.5rem;
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# ==================================================
# LOAD MODEL
# ==================================================

@st.cache_resource
def get_model():

    return load_model()


try:

    model = get_model()
    model_error = None

except Exception as error:

    model = None
    model_error = str(error)


# ==================================================
# HEADER
# ==================================================

st.markdown(
    """
    <div class="hero">
        <h1>🚑 Paramedic AI</h1>
        <p>
        EMS education and decision-support demonstration
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)


st.markdown(
    """
    <div class="safety">

    <strong>DEMO ONLY</strong> — This application is not
    intended for clinical decision making. Always follow
    current local EMS protocols, medical direction,
    and applicable regulations.

    </div>
    """,
    unsafe_allow_html=True,
)


# ==================================================
# SIDEBAR
# ==================================================

st.sidebar.title("🚑 Patient Assessment")

st.sidebar.caption(
    "Enter demonstration patient values."
)


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
    "Temperature °F",
    min_value=80.0,
    max_value=115.0,
    value=98.6,
)


# ==================================================
# SIDEBAR STATUS
# ==================================================

st.sidebar.divider()

st.sidebar.subheader("System Status")

if model_error:

    st.sidebar.error(
        "ML model unavailable"
    )

else:

    st.sidebar.success(
        "ML model ready"
    )


if KNOWLEDGE_AVAILABLE:

    st.sidebar.success(
        "Knowledge search ready"
    )

else:

    st.sidebar.warning(
        "Knowledge search unavailable"
    )


# ==================================================
# PATIENT SNAPSHOT
# ==================================================

st.header("📋 Patient Snapshot")

col1, col2, col3, col4 = st.columns(4)

with col1:

    st.metric(
        "Heart Rate",
        f"{heart_rate:.0f} bpm",
    )

with col2:

    st.metric(
        "Blood Pressure",
        f"{systolic_bp:.0f}/{diastolic_bp:.0f}",
    )

with col3:

    st.metric(
        "Respiratory Rate",
        f"{respiratory_rate:.0f}/min",
    )

with col4:

    st.metric(
        "SpO₂",
        f"{spo2:.0f}%",
    )


# ==================================================
# ML ASSESSMENT
# ==================================================

st.divider()

st.header("🧠 Model Assessment")

st.caption(
    "Demonstration output from the trained machine-learning model."
)


if model_error:

    st.error(
        f"Model loading error: {model_error}"
    )

else:

    if st.button(
        "▶ Run Assessment",
        type="primary",
        use_container_width=True,
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

            category = classify_risk(
                probability
            )

            result_col1, result_col2 = st.columns(2)

            with result_col1:

                st.metric(
                    "Model Output",
                    f"{probability * 100:.1f}%",
                )

            with result_col2:

                if category == "HIGHER RISK":

                    st.error(category)

                elif category == "INTERMEDIATE RISK":

                    st.warning(category)

                else:

                    st.success(category)


            st.info(
                "The model output is a demonstration only. "
                "It should not be interpreted as a validated "
                "clinical risk score or diagnosis."
            )

        except Exception as error:

            st.error(
                f"Prediction error: {error}"
            )


# ==================================================
# COPILOT
# ==================================================

st.divider()

st.header("💬 Paramedic Copilot")

st.caption(
    "Ask questions about EMS assessment, education, "
    "or retrieved reference material."
)


if "messages" not in st.session_state:

    st.session_state.messages = []


if st.button("🗑 Clear Chat"):

    st.session_state.messages = []

    st.rerun()


for message in st.session_state.messages:

    with st.chat_message(
        message["role"]
    ):

        st.markdown(
            message["content"]
        )


question = st.chat_input(
    "Ask Paramedic AI..."
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
                        "\n\n### 📚 References used\n"
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

                st.error(
                    error_message
                )

                st.session_state.messages.append(
                    {
                        "role": "assistant",
                        "content": error_message,
                    }
                )


# ==================================================
# KNOWLEDGE LIBRARY
# ==================================================

st.divider()

st.header("📚 Knowledge Library")

st.caption(
    "Reference metadata currently registered with Paramedic AI."
)


registry = load_source_registry()


if not registry:

    st.info(
        "No source metadata has been registered yet."
    )

else:

    for filename, metadata in registry.items():

        title = metadata.get(
            "title",
            filename,
        )

        document_type = metadata.get(
            "document_type",
            "UNKNOWN",
        )

        jurisdiction = metadata.get(
            "jurisdiction",
            "UNSPECIFIED",
        )

        version = metadata.get(
            "version",
            "UNKNOWN",
        )

        effective_date = metadata.get(
            "effective_date",
            "UNKNOWN",
        )

        status = metadata.get(
            "status",
            "UNKNOWN",
        )

        authority = metadata.get(
            "authority",
            "UNKNOWN",
        )

        review_required = metadata.get(
            "review_required",
            False,
        )

        with st.expander(
            f"📄 {title}"
        ):

            info1, info2, info3 = st.columns(3)

            with info1:

                st.write(
                    f"**Type:** {document_type}"
                )

                st.write(
                    f"**Authority:** {authority}"
                )

            with info2:

                st.write(
                    f"**Jurisdiction:** {jurisdiction}"
                )

                st.write(
                    f"**Version:** {version}"
                )

            with info3:

                st.write(
                    f"**Effective date:** {effective_date}"
                )

                st.write(
                    f"**Status:** {status}"
                )

            st.write(
                f"**File:** `{filename}`"
            )

            if review_required:

                st.warning(
                    "⚠️ This source requires review."
                )

            else:

                st.success(
                    "Source metadata reviewed."
                )


# ==================================================
# FOOTER
# ==================================================

st.divider()

st.caption(
    "🚑 Paramedic AI • Educational Demonstration"
)

st.caption(
    "Local protocols and medical direction take precedence."
)
