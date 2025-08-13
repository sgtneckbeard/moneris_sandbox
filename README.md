# 💳 Moneris Sandbox Streamlit App

### A user-friendly Streamlit web app for testing Moneris payment API requests in their sandbox environment.
### Easily create payments, test new and stored cards using payment method IDs.
### View the assembled requests and responses cleanly integrated within the page.
---

[👉 Visit app](https://nathan-monerissandbox-createpayment.streamlit.app/) 👈

## Features
- Credential Input: Accepts Moneris Merchant ID and API Key.
- Payment Details: Choose amount, currency, and automatically generate idempotency keys.
- Payment Methods: Pay with new card details or stored payment method IDs.
- Store Card Option: Checkbox to store card information and use respective payment method ID instead.
- View API Requests and Responses: Send payment requests to the Moneris sandbox and view both the sent requests and recieved responses.
- Error Handling and Form Validation: Feedback for missing fields, invalid data, and API errors.
- Response Code Legend: Quick reference list of Moneris API status codes.
