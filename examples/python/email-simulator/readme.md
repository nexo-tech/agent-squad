# E-commerce Email Support Simulator

A Streamlit demo that simulates email-based customer support for an e-commerce platform using AWS Agent Squad's multi-agent collaboration.

![Email Simulator Demo](./email-simulator.png)

## Overview

This demo showcases how specialized AI agents can work together to handle customer support emails. It demonstrates:

- **Multi-agent orchestration** with a supervisor coordinating specialized agents
- **Tool-augmented AI interactions** for order lookup, shipment tracking, and returns
- **Email-style asynchronous communication** common in e-commerce support

## Agents

### CustomerServiceSupervisor
- **Model**: Claude 3.5 Sonnet
- **Role**: Analyzes customer emails, delegates to specialized agents, and compiles professional responses

### OrderManagementAgent
- **Model**: Claude 3 Sonnet
- **Role**: Handles order-related inquiries
- **Tools**:
  - `order_lookup`: Retrieves order details from the database
  - `shipment_tracker`: Gets real-time shipping information
  - `return_processor`: Initiates and manages return requests

### ProductInfoAgent
- **Model**: Claude 3 Haiku
- **Role**: Provides product information and recommendations
- **Tools**:
  - `product_info`: Looks up product details, pricing, and availability

## Requirements

- Python 3.8+
- AWS account with Amazon Bedrock access
- Claude models enabled in Amazon Bedrock:
  - `anthropic.claude-3-sonnet-20240229-v1:0`
  - `anthropic.claude-3-haiku-20240307-v1:0`
  - `us.anthropic.claude-3-5-sonnet-20241022-v2:0`

## Running the Demo

1. Ensure AWS credentials are configured
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run from the `examples/python` directory:
   ```bash
   streamlit run main-app.py
   ```
4. Navigate to the "E-commerce Email Simulator" page

## Test Data

The demo includes mock data for testing:

**Order IDs:**
- `12345` - Shipped order (Widget A, Gadget B)
- `67890` - Processing order (Gizmo C)
- `11111` - Delivered order (can be returned)
- `22222` - Pending order (Premium Package)

**Products:**
- Widget A, Gadget B, Gizmo C, Super Device X

## Example Scenarios

1. **Order Status Check**: "What's the status of order #12345?"
2. **Shipment Tracking**: "Where is my package for order #12345?"
3. **Return Request**: "I want to return order #11111"
4. **Product Inquiry**: "Tell me about Widget A"

## Related

This demo is based on the full [E-commerce Support Simulator](../../ecommerce-support-simulator/) which includes:
- AWS CDK infrastructure
- Real-time chat interface
- Human agent integration via SQS
- Cognito authentication
