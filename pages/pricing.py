import streamlit as st
from utils.auth import update_user_plan
from utils.stripe_payment import create_checkout_session
import pandas as pd

def show():
    st.markdown("""
    <style>
        .pricing-header {
            text-align: center;
            color: #333;
            font-size: 36px;
            font-weight: 700;
            margin-bottom: 10px;
        }
        .pricing-subheader {
            text-align: center;
            color: #666;
            font-size: 16px;
            margin-bottom: 50px;
        }
        .current-plan-badge {
            text-align: center;
            margin-bottom: 30px;
            padding: 10px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border-radius: 10px;
            font-size: 18px;
        }
        .strike-price {
            font-size: 14px;
            color: #ff6b6b;
            text-decoration: line-through;
            margin-right: 5px;
        }
        .spike-price {
            font-size: 14px;
            color: #4CAF50;
            font-weight: bold;
        }
        .pricing-card {
            background: linear-gradient(135deg, #1E3A5F 0%, #0A1A2F 100%);
            border: 1px solid #2C4A6E;
            border-radius: 20px;
            padding: 40px 30px;
            width: 100%;
            text-align: center;
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
            transition: all 0.3s ease;
            position: relative;
            color: white;
        }
        .pricing-card.popular {
            border: 2px solid #4ECDC4;
            transform: scale(1.05);
        }
        .popular-badge {
            position: absolute;
            top: -12px;
            left: 50%;
            transform: translateX(-50%);
            background: linear-gradient(135deg, #4ECDC4 0%, #45B7D1 100%);
            color: #0B1E33;
            padding: 5px 20px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: 600;
        }
        .plan-name {
            font-size: 24px;
            font-weight: 700;
            color: white;
            margin-bottom: 10px;
        }
        .plan-price {
            font-size: 48px;
            font-weight: 700;
            color: #4ECDC4;
            margin-bottom: 5px;
        }
        .plan-price span {
            font-size: 16px;
            color: #999;
        }
        .plan-description {
            color: #B0C4DE;
            font-size: 14px;
            margin-bottom: 30px;
        }
        .plan-features {
            list-style: none;
            padding: 0;
            margin: 0 0 30px 0;
            text-align: left;
        }
        .plan-features li {
            padding: 10px 0;
            border-bottom: 1px solid #2C4A6E;
            color: #B0C4DE;
            font-size: 14px;
        }
        .plan-features li:before {
            content: "✓";
            color: #4ECDC4;
            font-weight: bold;
            margin-right: 10px;
        }
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown('<p class="pricing-header">💰 Real Pakistani Prices</p>', unsafe_allow_html=True)
    st.markdown('<p class="pricing-subheader">Choose the plan that fits your testing needs. Special strike/spike pricing!</p>', 
                unsafe_allow_html=True)
    
    st.markdown(f"""
    <div class='current-plan-badge fade-in'>
        Your Current Plan: <strong>{st.session_state.plan.upper()}</strong>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    # Basic Plan
    with col1:
        st.markdown("""
        <div class='pricing-card fade-in'>
            <div class='plan-name'>FOR STUDENTS</div>
            <div class='plan-name'>Basic Plan</div>
            <div class='plan-price'><span class='strike-price'>Rs 500</span> <span class='spike-price'>FREE</span><span>/mo</span></div>
            <div class='plan-description'>Perfect for students and beginners in Pakistan.</div>
            <ul class='plan-features'>
                <li>✅ Basic form validation tests</li>
                <li>✅ 5 comprehensive test cases</li>
                <li>✅ Simple PDF reports</li>
                <li>✅ Email support</li>
                <li>❌ Security tests</li>
                <li>❌ API testing</li>
                <li>❌ Priority support</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
        if st.session_state.plan == "basic":
            st.success("✅ Current Plan")
        else:
            if st.button("🔵 Start Free", key="basic", use_container_width=True):
                if update_user_plan(st.session_state.username, "basic"):
                    st.success("Plan updated to Basic!")
                    st.rerun()
    
    # Plus Plan
    with col2:
        st.markdown("""
        <div class='pricing-card popular fade-in'>
            <div class='popular-badge'>⚡ SPIKE PRICE</div>
            <div class='plan-name'>FOR PROFESSIONALS</div>
            <div class='plan-name'>Plus Plan</div>
            <div class='plan-price'><span class='strike-price'>Rs 2,499</span> <span class='spike-price'>Rs 999</span><span>/mo</span></div>
            <div class='plan-description'>Special spike price for Pakistani professionals!</div>
            <ul class='plan-features'>
                <li>✅ Everything in Basic</li>
                <li>✅ Advanced validation tests</li>
                <li>✅ 12 comprehensive test cases</li>
                <li>✅ Security & performance tests</li>
                <li>✅ Priority email support</li>
                <li>✅ API testing included</li>
                <li>❌ 24/7 phone support</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
        if st.session_state.plan == "plus":
            st.success("✅ Current Plan")
        else:
            if st.button("🟡 Choose Plus →", key="plus", type="primary", use_container_width=True):
                try:
                    if 'email' in st.session_state and st.session_state.email:
                        user_email = st.session_state.email
                    else:
                        user_email = f"{st.session_state.username}@example.com"
                        st.session_state.email = user_email
                    
                    price_id = st.secrets["STRIPE_PLUS_PRICE_ID"]
                    
                    result = create_checkout_session(
                        plan="plus",
                        user_email=user_email,
                        username=st.session_state.username,
                        price_id=price_id
                    )
                    
                    if result['success']:
                        st.markdown(f"""
                        <div style="background: linear-gradient(135deg, #00b4ff 0%, #4d4dff 100%);
                                    padding: 20px; border-radius: 10px; text-align: center; margin: 20px 0;">
                            <h3 style="color: white; margin:0 0 10px 0;">✅ Ready for Payment</h3>
                            <p style="color: white; margin:0 0 15px 0;">Click the button below to complete your payment:</p>
                            <a href="{result['url']}" target="_self" style="background: white; color: #4d4dff; 
                               padding: 12px 30px; border-radius: 5px; text-decoration: none; font-weight: bold;
                               display: inline-block;">👉 PAY Rs 999 NOW</a>
                        </div>
                        """, unsafe_allow_html=True)
                        st.info("⚠️ You'll be redirected to Stripe payment page. Complete payment to upgrade your plan.")
                    else:
                        st.error(f"Payment failed: {result.get('error', 'Unknown error')}")
                except Exception as e:
                    st.error(f"Payment error: {str(e)}")
    
    # Premium Plan
    with col3:
        st.markdown("""
        <div class='pricing-card fade-in'>
            <div class='plan-name'>FOR ENTERPRISE</div>
            <div class='plan-name'>Premium Plan</div>
            <div class='plan-price'><span class='strike-price'>Rs 5,999</span> <span class='spike-price'>Rs 2,499</span><span>/mo</span></div>
            <div class='plan-description'>Best value with strike price discount!</div>
            <ul class='plan-features'>
                <li>✅ Everything in Plus</li>
                <li>✅ Full automated testing suite</li>
                <li>✅ 20 complete test cases</li>
                <li>✅ SQL injection checks</li>
                <li>✅ XSS vulnerability tests</li>
                <li>✅ Broken links validation</li>
                <li>✅ 24/7 priority support</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
        if st.session_state.plan == "premium":
            st.success("✅ Current Plan")
        else:
            if st.button("🔴 Go Premium →", key="premium", use_container_width=True):
                try:
                    if 'email' in st.session_state and st.session_state.email:
                        user_email = st.session_state.email
                    else:
                        user_email = f"{st.session_state.username}@example.com"
                        st.session_state.email = user_email
                    
                    price_id = st.secrets["STRIPE_PREMIUM_PRICE_ID"]
                    
                    result = create_checkout_session(
                        plan="premium",
                        user_email=user_email,
                        username=st.session_state.username,
                        price_id=price_id
                    )
                    
                    if result['success']:
                        st.markdown(f"""
                        <div style="background: linear-gradient(135deg, #00b4ff 0%, #4d4dff 100%);
                                    padding: 20px; border-radius: 10px; text-align: center; margin: 20px 0;">
                            <h3 style="color: white; margin:0 0 10px 0;">✅ Ready for Payment</h3>
                            <p style="color: white; margin:0 0 15px 0;">Click the button below to complete your payment:</p>
                            <a href="{result['url']}" target="_self" style="background: white; color: #4d4dff; 
                               padding: 12px 30px; border-radius: 5px; text-decoration: none; font-weight: bold;
                               display: inline-block;">👉 PAY Rs 2,499 NOW</a>
                        </div>
                        """, unsafe_allow_html=True)
                        st.info("⚠️ You'll be redirected to Stripe payment page. Complete payment to upgrade your plan.")
                    else:
                        st.error(f"Payment failed: {result.get('error', 'Unknown error')}")
                except Exception as e:
                    st.error(f"Payment error: {str(e)}")
    
    st.markdown("---")
    st.markdown("### 📊 Plan Comparison - Pakistani Prices")
    
    comparison_data = {
        "Feature": ["Test Cases", "Form Validation", "Security Tests", "API Testing", "Email Support", "Priority Support", "Reports", "SQL Injection", "XSS Testing", "Monthly Price"],
        "Basic": ["5", "✅", "❌", "❌", "✅", "❌", "PDF", "❌", "❌", "FREE"],
        "Plus": ["12", "✅", "✅", "✅", "✅", "✅", "PDF + CSV", "❌", "❌", "Rs 999"],
        "Premium": ["20", "✅", "✅", "✅", "✅", "✅", "All Formats", "✅", "✅", "Rs 2,499"]
    }
    
    df = pd.DataFrame(comparison_data)
    st.dataframe(df, use_container_width=True, hide_index=True)
    
    st.markdown("---")
    st.markdown("### 🇵🇰 Pakistani Pricing Notes")
    
    with st.expander("What is Strike Price and Spike Price?"):
        st.markdown("""
        **Strike Price**: Original price before discount 
        **Spike Price**: Our special discounted price for Pakistan
        """)
    
    with st.expander("Payment Methods"):
        st.markdown("""
        - 💳 **Credit/Debit Cards** (Visa, Mastercard)
        - 💳 **Stripe Test Card**: `4242 4242 4242 4242`
        """)
    
    st.markdown("### ❓ Frequently Asked Questions")
    
    with st.expander("Can I pay in Pakistani Rupees?"):
        st.write("Yes! All prices are in Pakistani Rupees (PKR).")
    
    with st.expander("Is there a free trial?"):
        st.write("Yes! All plans come with a 7-day free trial.")
    
    with st.expander("Can I cancel anytime?"):
        st.write("Absolutely! You can cancel your subscription at any time.")