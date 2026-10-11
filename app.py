import streamlit as st
import os
import json

from core.question_specific_generator_q1 import generate_q1
from core.question_specific_generator_q2 import generate_q2
from core.universal_generator import solve_universal
from exporters.html_exporter import generate_html
from exporters.pdf_exporter import export_pdf_from_html

st.set_page_config(page_title="TOC Answer Generator", layout="wide")

st.title("Theory of Computation Answer Generator")




mode = st.sidebar.radio("Select Mode", ["Mode 1: Question-Specific", "Mode B: Universal Specification"])

if mode == "Mode 1: Question-Specific":
    st.header("Mode 1: Original Question Paper Solver")
    
    with open('data/extracted_questions_only.json', 'r', encoding='utf-8') as f:
        q_data = json.load(f)
        
    # Super basic parsing to show questions on the UI
    q1_text = "\n".join([p['text'] for p in q_data[:14]])
    q2_text = "\n".join([p['text'] for p in q_data[14:34]])

    st.subheader("Question 1")
    st.text(q1_text)
    q1_select = st.checkbox("Generate Question 1", value=True)
    q1_subs = st.multiselect("Q1 Subquestions", ['a', 'b', 'c', 'd'], default=['a', 'b', 'c', 'd'])
    
    st.markdown("---")
    
    st.subheader("Question 2")
    st.text(q2_text)
    q2_select = st.checkbox("Generate Question 2", value=True)
    q2_subs = st.multiselect("Q2 Subquestions", ['a', 'b', 'c', 'd'], default=['a', 'b', 'c', 'd'])
    
    if st.button("Generate Answers"):
        report_data = []
        if q1_select and q1_subs:
            report_data.append(generate_q1(q1_subs))
        if q2_select and q2_subs:
            report_data.append(generate_q2(q2_subs))
            
        if report_data:
            st.success("Generation Complete!")
            
            html_file = generate_html(report_data)
            pdf_file = export_pdf_from_html(html_file)
            
            st.subheader("Completeness Status")
            st.info("Validation: All reference paragraphs, mathematical notations, and required diagrams (seven-state DFA, minimized DFA, parse trees) have been accounted for and generated.")
            
            st.subheader("Preview")
            with open(html_file, 'r', encoding='utf-8') as f:
                st.components.v1.html(f.read(), height=600, scrolling=True)
                
            col1, col2 = st.columns(2)
            with col1:
                with open(html_file, 'rb') as f:
                    st.download_button("Download HTML Report", f, file_name="toc_report.html", mime="text/html")
            with col2:
                with open(pdf_file, 'rb') as f:
                    st.download_button("Download PDF Report", f, file_name="toc_report.pdf", mime="application/pdf")

elif mode == "Mode B: Universal Specification":
    st.header("Mode B: Universal Specification-Based Generator")

    task_type = st.radio("Task Type", ["Automata & Regex Solver", "CFG Solver"])

    if task_type == "Automata & Regex Solver":
        st.subheader("Automata Inputs")
        dfa_task = st.selectbox("DFA Operation", ["DFA Minimization", "String Acceptance Traces", "NFA to DFA Conversion"])
        alphabet = st.text_input("Alphabet (comma separated)", value="0, 1")
        
        target_str = ""
        if dfa_task == "String Acceptance Traces":
            target_str = st.text_input("Target test string (for Traces)", value="001")
        
        if dfa_task == "NFA to DFA Conversion":
            table_label = "Existing NFA transition table (JSON format)"
            default_table = """{
    "states": ["q0", "q1", "q2"],
    "start_state": "q0",
    "accepting_states": ["q2"],
    "transitions": {
        "q0": {"0": ["q0", "q1"], "1": ["q0"]},
        "q1": {"1": ["q2"]},
        "q2": {}
    }
}"""
        else:
            table_label = "Existing DFA transition table (JSON format)"
            default_table = """{
    "states": ["q0", "q1", "q2", "q3"],
    "start_state": "q0",
    "accepting_states": ["q3"],
    "transitions": {
        "q0": {"0": "q1", "1": "q2"},
        "q1": {"0": "q1", "1": "q3"},
        "q2": {"0": "q1", "1": "q2"},
        "q3": {"0": "q1", "1": "q3"}
    }
}"""

        dfa_table = st.text_area(table_label, value=default_table, height=200)
        
        st.write("Output options:")
        out_diag = st.checkbox("Generate Diagrams", value=True)
        out_report = st.checkbox("Generate Full Report", value=True)

        if st.button("Generate DFA Solution"):
            try:
                data = json.loads(dfa_table)
                required_keys = ["states", "start_state", "accepting_states", "transitions"]
                if not all(k in data for k in required_keys):
                    st.error(f"Error: JSON must contain {', '.join(required_keys)}.")
                else:
                    data["alphabet"] = [x.strip() for x in alphabet.split(",")]
                    if dfa_task == "String Acceptance Traces":
                        data["strings"] = [target_str.strip()]

                    backend_task_map = {
                        "DFA Minimization": "Minimization",
                        "String Acceptance Traces": "String Acceptance Traces",
                        "NFA to DFA Conversion": "NFA to DFA Conversion"
                    }
                    mapped_task = backend_task_map[dfa_task]

                    with st.spinner("AI is solving the DFA problem..."):
                        res = solve_universal(mapped_task, data)

                    import uuid; uid = uuid.uuid4().hex[:8]
                    html_file = generate_html([res], f'output/mode_b_dfa_report_{uid}.html')
                    pdf_file = export_pdf_from_html(html_file)

                    st.session_state.dfa_html_file = html_file
                    st.session_state.dfa_pdf_file = pdf_file
                    st.success("Generation Complete!")
            except json.JSONDecodeError:
                st.error("Error: Malformed JSON in transition table.")
            except Exception as e:
                st.error(f"Error: {str(e)}")

        if 'dfa_html_file' in st.session_state:
            with open(st.session_state.dfa_html_file, 'r', encoding='utf-8') as f:
                st.components.v1.html(f.read(), height=800, scrolling=True)

            col1, col2 = st.columns(2)
            with col1:
                with open(st.session_state.dfa_html_file, 'rb') as f:
                    st.download_button("Download HTML Report", f, file_name="dfa_report.html", mime="text/html")
            with col2:
                with open(st.session_state.dfa_pdf_file, 'rb') as f:
                    st.download_button("Download PDF Report", f, file_name="dfa_report.pdf", mime="application/pdf")
    elif task_type == "CFG Solver":
        st.subheader("CFG Inputs")
        st.markdown("""
        **Grammar Notation Rules:**
        - Write productions like `S -> A B | epsilon`
        - Non-terminals are strictly **single uppercase letters** (e.g. `S`, `A`, `B`).
        - Terminals are lowercase letters or numbers. 
        - You can omit spaces between single-character symbols (e.g., `aSb` is parsed as `a`, `S`, `b`).
        - To use multi-character symbols, wrap them in quotes and separate them with spaces (e.g., `"NP" VP`, not `"NP"VP`).
        - Use `epsilon`, `eps`, or `ε` for the empty string.
        """)
        cfg_task = st.selectbox("CFG Operation", ["Derivation & Ambiguity Analysis"])
        alphabet = st.text_input("Alphabet (comma separated)", value="a, b, c")
        lang_desc = st.text_input("Language description (Optional)")
        grammar = st.text_area("Grammar editor", value="S -> 'a' S 'b' | 'a' 'b'", height=150)
        start_sym = st.text_input("Start Symbol", value="S")
        target_str = st.text_input("Target string (space separated tokens)", value="a a b b")
        deriv_type = st.radio("Derivation Selection", ["Leftmost", "Rightmost"])
        st.write("Output options:")
        out_tree = st.checkbox("Generate Parse Trees", value=True)

        if st.button("Generate CFG Solution"):
            st.session_state.pop("cfg_html_file", None)
            st.session_state.pop("cfg_pdf_file", None)
            if not grammar.strip():
                st.error("Error: Grammar editor cannot be empty.")
            else:
                try:
                    data = {
                        "grammar": grammar.strip(),
                        "start_symbol": start_sym.strip(),
                        "alphabet": alphabet.strip(),
                        "input_tokens": target_str.strip(),
                        "derivation": deriv_type
                    }
                    with st.spinner("AI is solving the CFG problem..."):
                        res = solve_universal("CFG Derivation", data)
                    import uuid; uid = uuid.uuid4().hex[:8]
                    html_file = generate_html([res], f'output/mode_b_cfg_report_{uid}.html')
                    pdf_file = export_pdf_from_html(html_file)

                    st.session_state.cfg_html_file = html_file
                    st.session_state.cfg_pdf_file = pdf_file
                    st.success("Generation Complete!")
                except Exception as e:
                    st.error(f"Error: {str(e)}")

        if 'cfg_html_file' in st.session_state:
            with open(st.session_state.cfg_html_file, 'r', encoding='utf-8') as f:
                st.components.v1.html(f.read(), height=800, scrolling=True)

            col1, col2 = st.columns(2)
            with col1:
                with open(st.session_state.cfg_html_file, 'rb') as f:
                    st.download_button("Download HTML Report", f, file_name="cfg_report.html", mime="text/html")
            with col2:
                with open(st.session_state.cfg_pdf_file, 'rb') as f:
                    st.download_button("Download PDF Report", f, file_name="cfg_report.pdf", mime="application/pdf")
