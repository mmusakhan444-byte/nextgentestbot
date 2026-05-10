import subprocess
import os
import glob
import socket
from datetime import datetime
from urllib.parse import urlparse

def validate_url(url):
    """Simple URL validation"""
    if not url or len(url) < 4:
        return False, "URL cannot be empty"
    
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    
    try:
        parsed = urlparse(url)
        domain = parsed.netloc.split(':')[0]
        
        if '.' not in domain:
            return False, f"Invalid domain: {domain}"
        
        socket.gethostbyname(domain)
        return True, "URL is valid"
        
    except socket.gaierror:
        return False, f"Domain '{domain}' does not exist"
    except Exception as e:
        return False, f"Invalid URL: {str(e)}"

def run_real_tests(url, selected_tests, plan, browser="Chrome", headless=False):
    """Test runner - NO TIMEOUT"""
    
    # URL Validation
    is_valid, message = validate_url(url)
    
    if not is_valid:
        return {
            "success": False,
            "error": f"❌ {message}",
            "output": f"URL Error: {message}",
            "errors": message,
            "test_count": 0,
            "passed": 0,
            "failed": 0,
            "plan": plan,
            "url": url
        }
    
    try:
        agent_path = r"C:\Users\Administrator\Desktop\ai-test-agent"
        
        if plan == "basic":
            cmd = f'cd /d "{agent_path}" && pytest tests/test_universal_20.py::TestUniversal20::test_1_page_loads tests/test_universal_20.py::TestUniversal20::test_2_page_has_content tests/test_universal_20.py::TestUniversal20::test_3_page_has_links tests/test_universal_20.py::TestUniversal20::test_4_page_has_images tests/test_universal_20.py::TestUniversal20::test_5_page_has_headings -v'
            test_count = 5
        elif plan == "plus":
            cmd = f'cd /d "{agent_path}" && pytest tests/test_universal_20.py::TestUniversal20::test_1_page_loads tests/test_universal_20.py::TestUniversal20::test_2_page_has_content tests/test_universal_20.py::TestUniversal20::test_3_page_has_links tests/test_universal_20.py::TestUniversal20::test_4_page_has_images tests/test_universal_20.py::TestUniversal20::test_5_page_has_headings tests/test_universal_20.py::TestUniversal20::test_6_page_has_forms tests/test_universal_20.py::TestUniversal20::test_7_page_has_inputs tests/test_universal_20.py::TestUniversal20::test_8_page_has_buttons tests/test_universal_20.py::TestUniversal20::test_9_page_load_time tests/test_universal_20.py::TestUniversal20::test_10_page_https tests/test_universal_20.py::TestUniversal20::test_11_page_status_code tests/test_universal_20.py::TestUniversal20::test_12_page_has_meta_tags -v'
            test_count = 12
        else:
            cmd = f'cd /d "{agent_path}" && pytest tests/test_universal_20.py -v'
            test_count = 20
        
        print(f"[INFO] Running {plan.upper()} plan: {test_count} tests")
        print(f"[CMD] {cmd}")
        
        # Run WITHOUT timeout - wait until complete
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace'
        )
        
        # Count passed/failed
        output = result.stdout
        passed = output.count("PASSED") + output.count("[PASS]") + output.count("passed")
        failed = output.count("FAILED") + output.count("[FAIL]") + output.count("ERROR") + output.count("failed")
        
        print(f"[INFO] Tests complete: {passed} passed, {failed} failed")
        
        return {
            "success": True,
            "output": output,
            "errors": result.stderr,
            "report_path": None,
            "test_count": test_count,
            "passed": min(passed, test_count),
            "failed": min(failed, test_count),
            "plan": plan,
            "url": url
        }
        
    except Exception as e:
        print(f"[ERROR] {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "output": "",
            "errors": str(e),
            "test_count": test_count,
            "passed": 0,
            "failed": test_count,
            "plan": plan,
            "url": url
        }

def get_test_list(plan):
    """Return list of test names based on plan"""
    if plan == "basic":
        return [
            "Page Load Test",
            "Page Content Test",
            "Page Links Test",
            "Page Images Test",
            "Page Headings Test"
        ]
    elif plan == "plus":
        return [
            "Page Load Test",
            "Page Content Test",
            "Page Links Test",
            "Page Images Test",
            "Page Headings Test",
            "Page Forms Test",
            "Page Input Fields Test",
            "Page Buttons Test",
            "Page Load Time Test",
            "HTTPS Security Test",
            "HTTP Status Code Test",
            "Meta Tags Test"
        ]
    else:
        return [
            "Page Load Test",
            "Page Content Test",
            "Page Links Test",
            "Page Images Test",
            "Page Headings Test",
            "Page Forms Test",
            "Page Input Fields Test",
            "Page Buttons Test",
            "Page Load Time Test",
            "HTTPS Security Test",
            "HTTP Status Code Test",
            "Meta Tags Test",
            "JavaScript Test",
            "CSS Test",
            "Iframes Test",
            "HTML Lists Test",
            "HTML Tables Test",
            "Video Elements Test",
            "Audio Elements Test",
            "Cookies Test"
        ]