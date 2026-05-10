import streamlit as st
from datetime import datetime
from utils.test_runner import get_test_list

def show():
    st.markdown("## Configure Test Run")
    
    # Clear any lingering test state when entering configure page
    if 'test_run' in st.session_state:
        del st.session_state.test_run
    
    # Plan header
    st.markdown(f"""
    <div style='background: rgba(20, 20, 30, 0.7);
                backdrop-filter: blur(10px);
                border: 1px solid rgba(0, 180, 255, 0.3);
                border-radius: 20px;
                padding: 20px;
                margin-bottom: 20px;
                box-shadow: 0 0 30px rgba(0, 180, 255, 0.2);'>
        <h3 style='color: white; margin:0;'>Your Plan: {st.session_state.plan.upper()} Plan</h3>
    </div>
    """, unsafe_allow_html=True)
    
    # Main configuration
    col1, col2 = st.columns([2, 1])
    
    with col1:
        url = st.text_input(
            "Website URL to test",
            value="https://example.com",
            placeholder="https://your-website.com",
            key="url_input"
        )
        
        browser = st.selectbox(
            "Select Browser",
            ["Chrome", "Firefox", "Edge"],
            index=0,
            key="browser_select"
        )
    
    with col2:
        headless = st.checkbox("Headless Mode", value=True, key="headless_check")
        screenshots = st.checkbox("Take Screenshots", value=True, key="screenshots_check")
    
    st.markdown("---")
    
    # Test selection
    st.markdown("### Select Tests to Run")
    
    # Get tests according to plan
    available_tests = get_test_list(st.session_state.plan)
    
    st.info(f"**{len(available_tests)} tests available** in your {st.session_state.plan.upper()} plan")
    
    # Initialize session state for checkboxes if not exists or length mismatch
    if 'checkbox_states' not in st.session_state or len(st.session_state.checkbox_states) != len(available_tests):
        st.session_state.checkbox_states = [True] * len(available_tests)
    
    # Select All / Clear All buttons
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("✅ Select All", key="select_all", use_container_width=True):
            st.session_state.checkbox_states = [True] * len(available_tests)
            st.rerun()
    
    with col2:
        if st.button("❌ Clear All", key="clear_all", use_container_width=True):
            st.session_state.checkbox_states = [False] * len(available_tests)
            st.rerun()
    
    with col3:
        st.info(f"Selected: {sum(st.session_state.checkbox_states)} of {len(available_tests)} tests")
    
    # Display tests with checkboxes
    selected_tests = []
    cols = st.columns(2)
    
    for i, test_name in enumerate(available_tests):
        with cols[i % 2]:
            # Safety check for index
            if i < len(st.session_state.checkbox_states):
                checked = st.checkbox(
                    test_name,
                    value=st.session_state.checkbox_states[i],
                    key=f"test_checkbox_{i}"
                )
                st.session_state.checkbox_states[i] = checked
                if checked:
                    selected_tests.append(test_name)
            else:
                # Fallback if index out of range
                checked = st.checkbox(test_name, value=True, key=f"test_checkbox_fallback_{i}")
                if checked:
                    selected_tests.append(test_name)
    
    # Run button
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        if st.button(
            "🚀 RUN TESTS",
            type="primary",
            use_container_width=True,
            disabled=len(selected_tests) == 0,
            key="run_button"
        ):
            # Store test configuration
            st.session_state.test_run = {
                "url": url,
                "browser": browser,
                "headless": headless,
                "screenshots": screenshots,
                "selected_tests": selected_tests,
                "total_selected": len(selected_tests),
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "plan": st.session_state.plan
            }
            
            st.session_state.page = "Results"
            st.rerun()