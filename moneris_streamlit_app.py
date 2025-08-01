import streamlit as st  # Streamlit for front end 
import requests         # HTTP for requests
import json            # For converting Python dicts to JSON strings
import uuid            # To generate unique values for idempotency keys as encouraged by Moneris

# Configure the web page title and icon
st.set_page_config(page_title="Moneris Sandbox", page_icon="💳")

st.title("Moneris Sandbox")
st.markdown("---")

### User creds from Moneris Access and Credentials form Start
st.header("🙋🏻‍♀️ User Credentials")
merchant_id = st.text_input("Merchant ID") 
api_key = st.text_input("API Key", type="password")  
st.markdown("---")
### User creds from Moneris Access and Credentials form End



### Payment Details Form Section Start
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
### Payment Details Form Section End



### Payment Method Form Section Start
st.header("💳 Payment Method")

# Dropdown to select between card or payment method ID
payment_source = st.selectbox(
    "Payment Method Source", 
    ["New Card", "Stored Card/Payment Method ID"],
)
st.markdown("---")

# If/else for respective form fields based on drop down selection

if payment_source == "New Card": ## New Card selected from dropdown form
    st.subheader("🆕 New Card Details")
    col1, col2 = st.columns(2)
    with col1:
        card_number = st.text_input("Card Number", value="4242424242424242")
    with col2:
        col_month, col_year = st.columns(2)
        with col_month:
            expiry_month = st.number_input("Expiry Month", min_value=1, max_value=12, value=12)
        with col_year:
            expiry_year = st.selectbox("Expiry Year", options=list(range(2025, 2078)))
        cvv = st.text_input("CVV", value="123", max_chars=3)

    # Create checkbox to store payment method as CARDHOLDER_INITIATED
    store_card = st.checkbox("💾 Store card as payment method ID")
    
else:  
    st.subheader("💾 Stored Card Details") ## Stored Card selected from dropdown form
    payment_method_id = st.text_input( # Input for existing payment method ID
        "Payment Method ID", 
        placeholder="pi0105ARZ3NDEKTSV4RRFFQ69G5FAV"
    )
    store_card = False  # Explicitly set to False so storePaymentMethod parameter is not added to request body for stored cards
st.markdown("---")
### Payment Method Form Section End


### Main button action to create the payment request
if st.button("💳 Create Payment", type="primary"):

    ### Form validation start
    # 1. Boolean check to validate if credentials were inputted after button click
    if not merchant_id or not api_key:
        st.error("Please enter Merchant ID and API Key")

    # 2. Equality boolean to check to see if stored card is selected, and payment method ID is provided
    elif payment_source == "Stored Card/Payment Method ID" and not payment_method_id:
        st.error("Please enter a Payment Method ID for stored card payments")

    # 3. If new card selected, check if card number and CVV are provided
    elif payment_source == "New Card" and (not card_number.strip() or not cvv.strip()):
        st.error("Please enter card number and CVV for new card payments")
    ### Form validation end


    # If those 3 conditions are all false (successful validation), then continue to payment creation
    else:
        # Build paymentMethod object based on form inputs
        if payment_source == "New Card": # chosen from the selectbox dropdown
            # Use card details for new card payment
            payment_method_obj = {
                "paymentMethodSource": "CARD",
                "card": {
                    "cardNumber": card_number.replace(" ", ""),  # remove any potential whitespace
                    "expiryMonth": expiry_month,
                    "expiryYear": expiry_year,              
                    "cardSecurityCode": cvv
                }
            }
        else:  # Stored card aka Payment Method ID
            payment_method_obj = {
                "paymentMethodSource": "PAYMENT_METHOD_ID",  
                "paymentMethodId": payment_method_id
            }

        # Add storePaymentMethod parameter inside paymentMethod object (per API spec)
        if store_card: # if checkbox is checked for new card (true)
            payment_method_obj["storePaymentMethod"] = "CARDHOLDER_INITIATED"  # Cardholder consented to storage
        else:
            payment_method_obj["storePaymentMethod"] = "DO_NOT_STORE"  # Explicitly don't store card

        # Assembling the request body from the form inputs
        request_body = {
            "idempotencyKey": idempotency_key,
            "amount": {"amount": int(amount * 100), "currency": currency}, # Value must be converted into cents
            "paymentMethod": payment_method_obj # add payment method object based on user selection
        }

        # Assembling HTTP request headers including credentials
        request_headers = {
            "Content-Type": "application/json",  # JSON data will be sent
            "Api-Version": "2024-09-17", # default and latest stable version
            "X-Merchant-Id": merchant_id,
            "X-API-Key": api_key
        }
        st.markdown("---")

        # Print of headers to be sent
        print_headers = request_headers.copy()
        print_headers["X-API-Key"] = "[HIDDEN]"
        with st.expander("🔍 View Request Headers", expanded=True):
            st.json(print_headers)

        # Print of request body to be sent
        with st.expander("📋 View Request Payload Body", expanded=True):
            st.json(request_body)
        
        
        try: # Send the final assembled payment request to Moneris sandbox endpoint
            response = requests.post(
                "https://api.sb.moneris.io/payments",  # Sandbox Server URL resource for create payments
                headers=request_headers,                
                data=json.dumps(request_body),          # Convert the Python dict to JSON
                timeout=15
            )
            
            # If response status code is 201, payment was created successfully
            if response.status_code == 201:
                st.success("✅ Payment Created. Response below:")
            else: # otherwise, show status code and error
                st.error(f"❌ Failed: HTTP {response.status_code}")
            
            # Print server response
            with st.expander("📄 Server Response", expanded=True):
                try:
                    response_data = response.json() # print response data as JSON
                    st.json(response_data)
                except:
                    # If JSON parsing fails, show raw text
                    st.text(response.text)
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")
st.markdown("---")



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

# Simple back to top button
col1, col2, col3 = st.columns([1, 1, 1])
with col2:
    if st.button("⬆️ Back to Top", key="back_to_top"):
        st.rerun()


