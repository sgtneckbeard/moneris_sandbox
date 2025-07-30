import streamlit as st  # Streamlit for front end 
import requests         # HTTP for requests
import json            # For converting Python dicts to JSON strings
import uuid            # To generate unique values for idempotency keys as encouraged by Moneris

# Configure the web page title and icon
st.set_page_config(page_title="Moneris Sandbox", page_icon="💳")

st.title("Moneris Sandbox")
st.markdown("---")

### User creds from Moneris Access and Credentials Start
st.header("🙋🏻‍♀️ User Credentials")
merchant_id = st.text_input("Merchant ID") 
api_key = st.text_input("API Key", type="password")  
st.markdown("---")
### User creds from Moneris Access and Credentials End


### Payment Details Section Start
st.header("💰 Payment Details")
col1, col2 = st.columns(2)

with col1:
    # Amount charged with form incrementors
    amount = st.number_input("Amount ($)", min_value=0.01, value=01.00, step=0.01)
    currency = st.selectbox("Currency", ["CAD", "USD", "EUR", "GBP", "INR", "HKD"], index=0) #ISO 4217 standards
with col2:
    # Required idempotency key to prevent duplicate payments made using universal unique identifier UUID
    idempotency_key = st.text_input("Idempotency Key", value=str(uuid.uuid4())) # Version 4 as encouraged by Moneris
    # A new idempotency key is generated each time the form is modified
st.markdown("---")
### Payment Details Section End


### Credit Card Details Section Start
st.header("💳 Credit Card Details")
col1, col2 = st.columns(2)
with col1:
    card_number = st.text_input("Card Number", value="4242424242424242")
with col2:
    col_month, col_year = st.columns(2)
    with col_month:
        expiry_month = st.number_input("Expiry Month", min_value=1, max_value=12, value=12)
    with col_year:
        expiry_year = st.selectbox("Expiry Year", options=list(range(2024, 2078)), index=1)
    cvv = st.text_input("CVV", value="123", max_chars=3)
st.markdown("---")
### Credit Card Details Section End



### Main button action to create the payment
if st.button("💳 Create Purchase", type="primary"):

    # Check if credentials were inputted
    if not merchant_id or not api_key:
        st.error("Please enter Merchant ID and API Key")

    else:
        # Assembling the request body from the form inputs
        request_body = {
            "idempotencyKey": idempotency_key,
            
            # Value must be converted into cents
            "amount": {"amount": int(amount * 100), "currency": currency},

            # Hardcoded regularPurchaseWithCardPaymentMethod as required 
            "paymentMethod": {
                "paymentMethodSource": "CARD",
                "card": {
                    # Card details from form
                    "cardNumber": card_number.replace(" ", ""),  # remove whitespace
                    "expiryMonth": expiry_month,
                    "expiryYear": expiry_year,              
                    "cardSecurityCode": cvv
                }
            }
        }
        st.markdown("---")
        # Assembling HTTP request headers including credentials
        request_headers = {
            "Content-Type": "application/json",  # Required: tells server we're sending JSON
            "X-API-Key": api_key,
            "Api-Version": "2024-09-17", # default and latest stable version
            "X-Merchant-Id": merchant_id
        }

        # Print of headers to be sent
        print_headers = request_headers.copy()
        print_headers["X-API-Key"] = "[HIDDEN]"
        with st.expander("🔍 View Request Headers", expanded=True):
            st.json(print_headers)

        # Print of payload body to be sent
        with st.expander("📋 View Request Payload Body", expanded=True):
            st.json(request_body)
        
        
        try: # Send the final assembled payment request to Moneris sandbox endpoint
            response = requests.post(
                "https://api.sb.moneris.io/payments",  # Sandbox Server URL for create payments
                headers=request_headers,                
                data=json.dumps(request_body),          # Convert the Python dict to JSON
                timeout=30
            )
            
            # If response status code is 201, payment was created successfully
            if response.status_code == 201:
                st.success("✅ Payment Created!")
            else: # otherwise, show status code and error
                st.error(f"❌ Failed: HTTP {response.status_code}")
            
            with st.expander("📄 Server Response", expanded=True):
                try:
                    response_data = response.json() # print response data as JSON
                    st.json(response_data)
                except:
                    # If JSON parsing fails, show raw text
                    st.text(response.text)
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")


# Response code legend
with st.expander("📖 Response Codes Legend", expanded=False):
    st.markdown(
    """
    **HTTP Status Codes for Payment Creation:**
    
    • 😊 **201 - Created** - Payment was created successfully
    
    • 😕 **400 - Bad Request** - Invalid request data (missing fields, wrong format)
    
    • 😟 **401 - Unauthorized** - Not authorized. The user does not have a valid API Key or Access Token.
    
    • 😔 **403 - Forbidden** - Forbidden. The user does not have permission to access the requested resource.
    
    • 😬 **409 - Conflict** - Request could not be completed due to a conflict with resource state or existing idempotency key.
    
    • 😞 **422 - Unprocessable Content** - The API cannot complete the requested action due to semantic or business validation errors.
    
    • 😤 **429 - Too Many Requests** - Rate limit exceeded, slow down requests
    
    • 😱 **500 - Internal Server Error** - Unexpected error.

    • 😵 **503 - Service Unavailable** - Service Temporarily Unavailable
    """
                )
st.markdown("---")
