import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import os
import glob
import re

def get_real_test_stats():
    """Get REAL test statistics from agent reports AND session state"""
    agent_path = r"C:\Users\Administrator\Desktop\ai-test-agent\reports"
    
    total_tests = 0
    passed_tests = 0
    failed_tests = 0
    recent_runs = []
    
    # FIRST: Try to get from session state (most recent test)
    if 'last_test_results' in st.session_state:
        last_results = st.session_state.last_test_results
        total_tests = last_results.get('total', 0)
        passed_tests = last_results.get('passed', 0)
        failed_tests = last_results.get('failed', 0)
        print(f"[DASHBOARD] Using session state: {total_tests} total, {passed_tests} passed")
        
        # Add a recent run from session
        if total_tests > 0:
            recent_runs.append({
                'time': 'Now',
                'total': total_tests,
                'passed': passed_tests,
                'failed': failed_tests,
                'rate': f"{(passed_tests/total_tests*100):.1f}%"
            })
    
    # SECOND: Also check reports for historical data
    if os.path.exists(agent_path):
        report_files = glob.glob(os.path.join(agent_path, "*.html"))
        report_files.sort(key=os.path.getctime, reverse=True)
        
        for report in report_files[:10]:  # Last 10 reports
            try:
                with open(report, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                passed_match = re.search(r'(\d+)\s+passed', content, re.IGNORECASE)
                failed_match = re.search(r'(\d+)\s+failed', content, re.IGNORECASE)
                
                report_passed = int(passed_match.group(1)) if passed_match else 0
                report_failed = int(failed_match.group(1)) if failed_match else 0
                report_total = report_passed + report_failed
                
                if report_total > 0:
                    ctime = os.path.getctime(report)
                    report_time = datetime.fromtimestamp(ctime)
                    
                    # Add to total only if we don't have session data
                    if total_tests == 0:
                        total_tests += report_total
                        passed_tests += report_passed
                        failed_tests += report_failed
                    
                    recent_runs.append({
                        'time': report_time.strftime("%H:%M"),
                        'total': report_total,
                        'passed': report_passed,
                        'failed': report_failed,
                        'rate': f"{(report_passed/report_total*100):.1f}%"
                    })
            except:
                continue
    
    return {
        'total': total_tests,
        'passed': passed_tests,
        'failed': failed_tests,
        'rate': (passed_tests/total_tests*100) if total_tests > 0 else 0,
        'recent': recent_runs[:5]
    }

def show():
    st.markdown("## 📊 Dashboard")
    
    # Get real stats
    stats = get_real_test_stats()
    
    # Welcome message
    if stats['total'] > 0:
        welcome_text = f"""
        <div style='background:rgba(20,20,30,0.7); border-radius:20px; padding:25px; margin-bottom:30px;
                    border:1px solid rgba(0,180,255,0.3);'>
            <h2 style='color:white; margin:0;'>👋 Welcome back, <span style='color:#00b4ff;'>{st.session_state.username}</span>!</h2>
            <p style='color:#8892b0; margin:10px 0 0 0;'>Total tests executed: <strong style='color:white;'>{stats['total']}</strong> | Success rate: <strong style='color:#00b4ff;'>{stats['rate']:.1f}%</strong></p>
        </div>
        """
    else:
        welcome_text = f"""
        <div style='background:rgba(20,20,30,0.7); border-radius:20px; padding:25px; margin-bottom:30px;
                    border:1px solid rgba(0,180,255,0.3);'>
            <h2 style='color:white; margin:0;'>👋 Welcome back, <span style='color:#00b4ff;'>{st.session_state.username}</span>!</h2>
            <p style='color:#8892b0; margin:10px 0 0 0;'>No tests executed yet. Configure a test to get started!</p>
        </div>
        """
    
    st.markdown(welcome_text, unsafe_allow_html=True)
    
    # Quick action buttons
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        if st.button("⚡ CONFIGURE TEST", key="dash_configure", use_container_width=True):
            st.session_state.page = "Configure_Test"
            st.rerun()
    with col2:
        if st.button("📊 VIEW RESULTS", key="dash_results", use_container_width=True):
            st.session_state.page = "Results"
            st.rerun()
    with col3:
        if st.button("💎 PRICING", key="dash_pricing", use_container_width=True):
            st.session_state.page = "Pricing"
            st.rerun()
    with col4:
        if st.button("🚪 LOGOUT", key="dash_logout", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.page = "Login"
            st.rerun()
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Metrics cards
    col1, col2, col3, col4 = st.columns(4)
    plan_tests = {"basic": 5, "plus": 12, "premium": 20}
    
    with col1:
        st.metric("Total Tests", stats['total'], f"{stats['rate']:.1f}% rate")
    with col2:
        st.metric("✅ Passed", stats['passed'])
    with col3:
        st.metric("❌ Failed", stats['failed'])
    with col4:
        st.metric("Your Plan", st.session_state.plan.upper(), f"{plan_tests.get(st.session_state.plan, 5)} tests")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Recent test runs
    if stats['recent']:
        st.markdown("### 🔄 Recent Test Runs")
        df = pd.DataFrame(stats['recent'])
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("No test runs found. Run some tests to see data here!")
    
    # Manual refresh
    if st.button("🔄 Refresh Dashboard", use_container_width=True):
        st.rerun()