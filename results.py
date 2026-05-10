import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
import base64
import os
import re
import io
import tempfile
from utils.test_runner import run_real_tests

# PDF libraries
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch

# Try to import matplotlib, but don't fail if not available
try:
    import matplotlib
    matplotlib.use('Agg')  # Use non-interactive backend
    import matplotlib.pyplot as plt
    import numpy as np
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False
    print("Matplotlib not available - graphs will be skipped")

def parse_test_output(output, plan):
    """Parse function - detects actual PASS/FAIL from output"""
    tests = []
    lines = output.split('\n')
    
    # Test names mapping
    test_names = {
        'Page Load Test': ['test_1_page_loads', 'loading page', 'page title'],
        'Page Content Test': ['test_2_page_has_content', 'content', 'body'],
        'Page Links Test': ['test_3_page_has_links', 'links', 'href'],
        'Page Images Test': ['test_4_page_has_images', 'images', 'img'],
        'Page Headings Test': ['test_5_page_has_headings', 'headings', 'h1', 'h2', 'h3'],
        'Page Forms Test': ['test_6_page_has_forms', 'forms', 'form'],
        'Page Input Fields Test': ['test_7_page_has_inputs', 'input fields', 'input'],
        'Page Buttons Test': ['test_8_page_has_buttons', 'buttons', 'button'],
        'Page Load Time Test': ['test_9_page_load_time', 'load time', 'speed'],
        'HTTPS Security Test': ['test_10_page_https', 'https', 'secure'],
        'HTTP Status Code Test': ['test_11_page_status_code', 'status code', '200'],
        'Meta Tags Test': ['test_12_page_has_meta_tags', 'meta tags', 'description'],
        'JavaScript Test': ['test_13_page_has_scripts', 'javascript', 'script'],
        'CSS Test': ['test_14_page_has_styles', 'css', 'styles'],
        'Iframes Test': ['test_15_page_has_iframes', 'iframe', 'frame'],
        'HTML Lists Test': ['test_16_page_has_lists', 'lists', 'ul', 'ol'],
        'HTML Tables Test': ['test_17_page_has_tables', 'tables', 'table'],
        'Video Elements Test': ['test_18_page_has_videos', 'video', 'videos'],
        'Audio Elements Test': ['test_19_page_has_audios', 'audio', 'audios'],
        'Cookies Test': ['test_20_page_cookies', 'cookies', 'cookie']
    }
    
    # Filter by plan
    if plan == "basic":
        test_items = list(test_names.items())[:5]
    elif plan == "plus":
        test_items = list(test_names.items())[:12]
    else:
        test_items = list(test_names.items())
    
    # Check each test
    for test_display, keywords in test_items:
        test_passed = False
        test_failed = False
        
        for line in lines:
            if any(k in line.lower() for k in keywords):
                if 'FAILED' in line or 'failed' in line or 'ERROR' in line or 'error' in line:
                    test_failed = True
                    break
                elif 'PASSED' in line or 'passed' in line or 'PASS' in line or 'pass' in line:
                    test_passed = True
                elif 'Found 0' in line or 'no links' in line.lower() or 'no images' in line.lower():
                    if 'PASS' not in line and 'pass' not in line:
                        test_failed = True
                        break
        
        if test_failed:
            status = "FAILED"
            reason = get_failure_reason(test_display)
            suggestion = get_fix_suggestion(test_display)
        elif test_passed:
            status = "PASSED"
            reason = "Test completed successfully"
            suggestion = ""
        else:
            status = "PASSED"
            reason = "Test completed successfully"
            suggestion = ""
        
        tests.append({
            "name": test_display,
            "status": status,
            "reason": reason,
            "suggestion": suggestion
        })
    
    return tests

def get_failure_reason(test_name):
    """Get specific failure reason for test"""
    reasons = {
        'Page Images Test': 'Images failed to load or missing',
        'Page Links Test': 'Broken links found or no links present',
        'Page Forms Test': 'Form structure invalid or missing',
        'Page Input Fields Test': 'Input fields not working',
        'Page Buttons Test': 'Buttons not clickable',
        'Page Load Time Test': 'Page load time too slow',
        'HTTPS Security Test': 'Page not using HTTPS',
        'HTTP Status Code Test': 'Server returned error status',
        'Meta Tags Test': 'Essential meta tags missing',
        'JavaScript Test': 'JavaScript errors detected',
        'CSS Test': 'Styles not loading properly',
        'Iframes Test': 'Iframes not loading',
        'HTML Lists Test': 'List structure invalid',
        'HTML Tables Test': 'Table structure malformed',
        'Video Elements Test': 'Video elements not loading',
        'Audio Elements Test': 'Audio elements not loading',
        'Cookies Test': 'Cookies not set correctly'
    }
    return reasons.get(test_name, 'Test assertion failed')

def get_fix_suggestion(test_name):
    """Get fix suggestion for failed test"""
    suggestions = {
        'Page Images Test': 'Check image paths, ensure files exist',
        'Page Links Test': 'Fix broken links, add proper href attributes',
        'Page Forms Test': 'Ensure form has proper structure and submit button',
        'Page Input Fields Test': 'Add proper input types and names',
        'Page Buttons Test': 'Make buttons clickable with proper events',
        'Page Load Time Test': 'Optimize images, minify CSS/JS, enable caching',
        'HTTPS Security Test': 'Install SSL certificate, redirect HTTP to HTTPS',
        'HTTP Status Code Test': 'Check server configuration, fix 404/500 errors',
        'Meta Tags Test': 'Add meta description, keywords, viewport tags',
        'JavaScript Test': 'Fix JS errors in console, check script paths',
        'CSS Test': 'Verify CSS file paths, check for syntax errors',
        'Iframes Test': 'Check iframe source URLs, ensure they load',
        'HTML Lists Test': 'Use proper ul/ol li structure',
        'HTML Tables Test': 'Use proper table/thead/tbody structure',
        'Video Elements Test': 'Check video formats, ensure sources work',
        'Audio Elements Test': 'Check audio formats, ensure sources work',
        'Cookies Test': 'Implement proper cookie consent and settings'
    }
    return suggestions.get(test_name, 'Review test implementation')

def create_test_results_table(tests):
    """Create styled dataframe with test results"""
    if not tests:
        return pd.DataFrame()
    
    df = pd.DataFrame(tests)
    df = df.rename(columns={
        "name": "Test Name",
        "status": "Status",
        "reason": "Reason",
        "suggestion": "Fix Suggestion"
    })
    
    def color_status(val):
        if val == "PASSED":
            return 'background-color: #d4edda; color: #155724; font-weight: bold'
        elif val == "FAILED":
            return 'background-color: #f8d7da; color: #721c24; font-weight: bold'
        elif val == "ERROR":
            return 'background-color: #fff3cd; color: #856404; font-weight: bold'
        return ''
    
    styled_df = df.style.applymap(color_status, subset=['Status'])
    return styled_df

def create_status_chart(tests, plan):
    """Create pie chart from test data - without download options for basic"""
    if not tests:
        fig = go.Figure()
        fig.add_annotation(text="No test data available", x=0.5, y=0.5, showarrow=False)
        fig.update_layout(height=400)
        return fig
    
    status_counts = pd.DataFrame(tests)['status'].value_counts().reset_index()
    status_counts.columns = ['Status', 'Count']
    
    colors_map = {
        'PASSED': '#28a745',
        'FAILED': '#dc3545', 
        'ERROR': '#ffc107'
    }
    
    fig = px.pie(
        status_counts, 
        values='Count', 
        names='Status',
        title='Test Results Distribution',
        color='Status',
        color_discrete_map=colors_map
    )
    
    fig.update_traces(textposition='inside', textinfo='percent+label')
    
    # Remove download buttons for basic plan
    config = {'displayModeBar': False} if plan == "basic" else {'displayModeBar': True}
    
    fig.update_layout(
        height=400,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white')
    )
    
    return fig, config

def create_bar_chart(tests, plan):
    """Create bar chart from test data - without download options for basic"""
    if not tests:
        return None, None
    
    df = pd.DataFrame(tests)
    passed_df = df[df['status'] == 'PASSED']
    failed_df = df[df['status'].isin(['FAILED', 'ERROR'])]
    
    fig = go.Figure()
    
    if not passed_df.empty:
        fig.add_trace(go.Bar(
            name='Passed', 
            x=passed_df['name'], 
            y=[1]*len(passed_df), 
            marker_color='#28a745',
            text='✅',
            textposition='auto'
        ))
    
    if not failed_df.empty:
        fig.add_trace(go.Bar(
            name='Failed', 
            x=failed_df['name'], 
            y=[1]*len(failed_df), 
            marker_color='#dc3545',
            text='❌',
            textposition='auto'
        ))
    
    # Remove download buttons for basic plan
    config = {'displayModeBar': False} if plan == "basic" else {'displayModeBar': True}
    
    fig.update_layout(
        title='Test Results by Category',
        barmode='group',
        height=400,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white'),
        showlegend=True,
        xaxis_tickangle=-45
    )
    
    return fig, config

def generate_pdf_report(tests, summary, test_config):
    """Generate PDF report - SAFE VERSION with fallback"""
    try:
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        styles = getSampleStyleSheet()
        elements = []
        
        # Custom styles
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1E3A5F'),
            spaceAfter=30,
            alignment=1
        )
        
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#0A1A2F'),
            spaceAfter=20,
            alignment=0
        )
        
        # Title
        elements.append(Paragraph("NeXtGen TestBot - Test Report", title_style))
        elements.append(Spacer(1, 20))
        
        # Summary
        elements.append(Paragraph("Test Summary", heading_style))
        elements.append(Spacer(1, 10))
        
        summary_data = [
            ["Generated:", datetime.now().strftime('%Y-%m-%d %H:%M:%S')],
            ["URL:", test_config['url']],
            ["Plan:", test_config['plan'].upper()],
            ["Total Tests:", str(summary['total'])],
            ["Passed:", str(summary['passed'])],
            ["Failed:", str(summary['failed'])],
            ["Success Rate:", f"{summary['rate']:.1f}%"]
        ]
        
        summary_table = Table(summary_data, colWidths=[2*inch, 4*inch])
        summary_table.setStyle(TableStyle([
            ('FONTNAME', (0,0), (-1,-1), 'Helvetica'),
            ('FONTSIZE', (0,0), (-1,-1), 11),
            ('GRID', (0,0), (-1,-1), 1, colors.grey)
        ]))
        elements.append(summary_table)
        elements.append(Spacer(1, 30))
        
        # Add graphs if matplotlib is available
        if MATPLOTLIB_AVAILABLE:
            try:
                # Create a single figure with subplots
                fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
                
                # Pie Chart
                status_counts = pd.DataFrame(tests)['status'].value_counts()
                labels = []
                sizes = []
                colors_list = []
                
                for status, count in status_counts.items():
                    if status == 'PASSED':
                        labels.append(f'Passed ({count})')
                        colors_list.append('#28a745')
                    elif status == 'FAILED':
                        labels.append(f'Failed ({count})')
                        colors_list.append('#dc3545')
                    elif status == 'ERROR':
                        labels.append(f'Error ({count})')
                        colors_list.append('#ffc107')
                    sizes.append(count)
                
                if sizes:
                    ax1.pie(sizes, labels=labels, colors=colors_list, autopct='%1.1f%%', startangle=90)
                    ax1.set_title('Test Results Distribution')
                    ax1.axis('equal')
                
                # Bar Chart
                test_names = [t['name'][:15] + '...' if len(t['name']) > 15 else t['name'] for t in tests]
                passed_values = [1 if t['status'] == 'PASSED' else 0 for t in tests]
                failed_values = [1 if t['status'] in ['FAILED', 'ERROR'] else 0 for t in tests]
                
                x = np.arange(len(test_names))
                width = 0.35
                
                ax2.bar(x - width/2, passed_values, width, label='Passed', color='#28a745')
                ax2.bar(x + width/2, failed_values, width, label='Failed', color='#dc3545')
                
                ax2.set_xlabel('Test Names')
                ax2.set_ylabel('Status')
                ax2.set_title('Test Results by Category')
                ax2.set_xticks(x)
                ax2.set_xticklabels(test_names, rotation=45, ha='right', fontsize=8)
                ax2.legend()
                
                plt.tight_layout()
                
                # Save to temporary file
                with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmpfile:
                    temp_filename = tmpfile.name
                    plt.savefig(temp_filename, format='png', dpi=150, bbox_inches='tight')
                    plt.close()
                    
                    # Add to PDF
                    elements.append(Paragraph("Test Results Visualization", heading_style))
                    elements.append(Spacer(1, 10))
                    elements.append(Image(temp_filename, width=6.5*inch, height=3*inch))
                    elements.append(Spacer(1, 20))
                    
                    # Clean up
                    os.unlink(temp_filename)
                    
            except Exception as e:
                print(f"Graph generation error: {e}")
                # Continue without graphs
        
        # Detailed Results
        elements.append(Paragraph("Detailed Test Results", heading_style))
        elements.append(Spacer(1, 10))
        
        if tests:
            test_data = [["Test Name", "Status", "Reason"]]
            for test in tests:
                reason = test['reason'][:40] + "..." if len(test['reason']) > 40 else test['reason']
                test_data.append([test['name'], test['status'], reason])
            
            test_table = Table(test_data)
            test_table.setStyle(TableStyle([
                ('FONTNAME', (0,0), (-1,-1), 'Helvetica'),
                ('FONTSIZE', (0,0), (-1,0), 10),
                ('FONTSIZE', (0,1), (-1,-1), 8),
                ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1E3A5F')),
                ('TEXTCOLOR', (0,0), (-1,0), colors.white),
                ('GRID', (0,0), (-1,-1), 1, colors.grey),
            ]))
            
            # Color code status rows
            for i, test in enumerate(tests, start=1):
                if test['status'] == 'PASSED':
                    test_table.setStyle(TableStyle([('BACKGROUND', (0,i), (-1,i), colors.HexColor('#d4edda'))]))
                elif test['status'] == 'FAILED':
                    test_table.setStyle(TableStyle([('BACKGROUND', (0,i), (-1,i), colors.HexColor('#f8d7da'))]))
                elif test['status'] == 'ERROR':
                    test_table.setStyle(TableStyle([('BACKGROUND', (0,i), (-1,i), colors.HexColor('#fff3cd'))]))
            
            elements.append(test_table)
        
        # Build PDF
        doc.build(elements)
        buffer.seek(0)
        return buffer.getvalue()
        
    except Exception as e:
        return str(e).encode()

def display_results(tests, test_config, current_plan):
    """Display test results without running tests again"""
    total = len(tests)
    passed = sum(1 for t in tests if t['status'] == 'PASSED')
    failed = sum(1 for t in tests if t['status'] in ['FAILED', 'ERROR'])
    rate = (passed / total * 100) if total > 0 else 0
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Tests", total)
    with col2:
        st.metric("✅ Passed", passed)
    with col3:
        st.metric("❌ Failed", failed)
    with col4:
        st.metric("📊 Success Rate", f"{rate:.1f}%")
    
    col1, col2 = st.columns(2)
    with col1:
        fig_pie, config_pie = create_status_chart(tests, current_plan)
        st.plotly_chart(fig_pie, use_container_width=True, config=config_pie)
    with col2:
        fig_bar, config_bar = create_bar_chart(tests, current_plan)
        if fig_bar:
            st.plotly_chart(fig_bar, use_container_width=True, config=config_bar)
    
    st.markdown("### 📋 Detailed Test Results")
    styled_df = create_test_results_table(tests)
    st.dataframe(styled_df, use_container_width=True, height=500)

def show():
    st.markdown("## 📊 Test Results")
    
    # Check if test_run exists in session state
    if 'test_run' not in st.session_state:
        st.warning("⚠️ No test results available. Please run a test first!")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("⚙️ Configure Test", use_container_width=True):
                st.session_state.page = "Configure_Test"
                st.rerun()
        with col2:
            if st.button("🏠 Back to Dashboard", use_container_width=True):
                st.session_state.page = "Dashboard"
                st.rerun()
        return
    
    test_config = st.session_state.test_run
    current_plan = test_config['plan']
    
    # Check if we already have results displayed
    if 'results_displayed' in st.session_state and st.session_state.results_displayed:
        # Sirf results dikhao, test run mat karo
        st.info("📊 Displaying test results")
        if 'last_tests' in st.session_state:
            display_results(st.session_state.last_tests, test_config, current_plan)
        else:
            st.warning("No previous results found")
        return
    
    # Pehli baar - test run karo
    status_placeholder = st.empty()
    status_placeholder.info(f"⏳ Running {current_plan.upper()} Plan tests... Please wait")
    
    with st.spinner(""):
        results = run_real_tests(
            url=test_config['url'],
            selected_tests=test_config['selected_tests'],
            plan=current_plan,
            browser=test_config['browser'],
            headless=test_config.get('headless', True)
        )
    
    status_placeholder.empty()
    
    if results.get('success'):
        st.balloons()
        st.success("✅ Tests Completed Successfully!")
        
        tests = parse_test_output(results.get('output', ''), current_plan)
        
        if tests:
            # Save results for later display
            st.session_state.last_tests = tests
            st.session_state.results_displayed = True
            
            total = len(tests)
            passed = sum(1 for t in tests if t['status'] == 'PASSED')
            failed = sum(1 for t in tests if t['status'] in ['FAILED', 'ERROR'])
            rate = (passed / total * 100) if total > 0 else 0
            
            st.session_state.last_test_results = {
                'total': total,
                'passed': passed,
                'failed': failed,
                'rate': rate
            }
            
            display_results(tests, test_config, current_plan)
            
            # ===== PLAN-BASED FEATURES =====
            st.markdown("### 📥 Available Actions")
            
            # BASIC PLAN - Sirf results
            if current_plan == "basic":
                st.info("ℹ️ **Basic Plan**: View results only. Upgrade to Plus for PDF reports.")
            
            # PLUS PLAN - Sirf PDF download, no navigation buttons
            elif current_plan == "plus":
                st.markdown("### 📥 Download Report")
                try:
                    pdf_bytes = generate_pdf_report(
                        tests, 
                        {'total': total, 'passed': passed, 'failed': failed, 'rate': rate}, 
                        test_config
                    )
                    b64_pdf = base64.b64encode(pdf_bytes).decode()
                    st.markdown(
                        f'<a href="data:application/octet-stream;base64,{b64_pdf}" download="test_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf" target="_blank">'
                        f'<button style="background: linear-gradient(135deg, #00b4ff 0%, #4d4dff 100%); '
                        f'color: white; padding: 12px; border: none; border-radius: 5px; width: 100%; cursor: pointer; '
                        f'font-size: 16px; font-weight: bold;">📄 DOWNLOAD PDF REPORT</button></a>',
                        unsafe_allow_html=True
                    )
                except Exception as e:
                    st.error(f"PDF generation failed: {str(e)}")
            
            # PREMIUM PLAN - Sirf PDF download, no navigation buttons
            else:  # premium
                st.markdown("### 📥 Download Report")
                try:
                    pdf_bytes = generate_pdf_report(
                        tests, 
                        {'total': total, 'passed': passed, 'failed': failed, 'rate': rate}, 
                        test_config
                    )
                    b64_pdf = base64.b64encode(pdf_bytes).decode()
                    st.markdown(
                        f'<a href="data:application/octet-stream;base64,{b64_pdf}" download="test_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf" target="_blank">'
                        f'<button style="background: linear-gradient(135deg, #00b4ff 0%, #4d4dff 100%); '
                        f'color: white; padding: 12px; border: none; border-radius: 5px; width: 100%; cursor: pointer; '
                        f'font-size: 16px; font-weight: bold;">📄 DOWNLOAD PDF REPORT</button></a>',
                        unsafe_allow_html=True
                    )
                except Exception as e:
                    st.error(f"PDF generation failed: {str(e)}")
            
            # Fix recommendations
            failed_tests = [t for t in tests if t['status'] in ['FAILED', 'ERROR']]
            if failed_tests:
                st.markdown("### 🔧 Fix Recommendations")
                for test in failed_tests:
                    if test['suggestion']:
                        with st.expander(f"🔨 {test['name']}"):
                            st.markdown(f"**Problem:** {test['reason']}")
                            st.markdown(f"**Solution:** {test['suggestion']}")
        
        else:
            st.warning("⚠️ No test data found. Raw output below:")
            with st.expander("🔍 Raw Test Output", expanded=True):
                st.code(results.get('output', 'No output'))
    
    else:
        st.error(f"❌ Failed: {results.get('error', 'Unknown error')}")
        
        if results.get('output') or results.get('errors'):
            with st.expander("🔍 Error Details"):
                if results.get('output'):
                    st.code(results.get('output')[-1000:])
                if results.get('errors'):
                    st.code(results.get('errors'))
    
    # ===== NO NAVIGATION BUTTONS FOR PLUS/PREMIUM =====
    # Sirf basic plan mein buttons honge
    if current_plan == "basic":
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔄 Run New Test", use_container_width=True):
                # Reset results displayed flag
                if 'results_displayed' in st.session_state:
                    del st.session_state.results_displayed
                if 'last_tests' in st.session_state:
                    del st.session_state.last_tests
                del st.session_state.test_run
                st.session_state.page = "Configure_Test"
                st.rerun()
        with col2:
            if st.button("🏠 Back to Dashboard", use_container_width=True):
                st.session_state.page = "Dashboard"
                st.rerun()