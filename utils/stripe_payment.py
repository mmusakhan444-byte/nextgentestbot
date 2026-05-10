import stripe
import streamlit as st
from datetime import datetime
import sqlite3
import os

# Load Stripe API key from secrets
stripe.api_key = st.secrets["STRIPE_SECRET_KEY"]

def create_checkout_session(plan, user_email, username, price_id):
    """
    Create Stripe checkout session for payment
    """
    try:
        # Create checkout session
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price': price_id,
                'quantity': 1,
            }],
            mode='payment',
            success_url='http://localhost:8501/?payment=success&session_id={CHECKOUT_SESSION_ID}',
            cancel_url='http://localhost:8501/?page=Pricing',
            customer_email=user_email,
            metadata={
                'plan': plan,
                'username': username,
                'email': user_email
            }
        )
        
        return {
            'success': True,
            'session_id': checkout_session.id,
            'url': checkout_session.url
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }