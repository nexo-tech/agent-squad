import uuid
import asyncio
import streamlit as st
import boto3
from agent_squad.orchestrator import AgentSquad, AgentSquadConfig
from agent_squad.agents import (
    AgentResponse,
    BedrockLLMAgent,
    BedrockLLMAgentOptions,
    SupervisorAgent,
    SupervisorAgentOptions
)
from agent_squad.types import ConversationMessage, ParticipantRole
from agent_squad.classifiers import ClassifierResult
from agent_squad.utils import AgentTools, AgentTool
from mock_data import order_lookup, shipment_tracker, return_processor, product_info


def test_aws_connection():
    """Test the AWS connection and return a status message."""
    try:
        boto3.client('sts').get_caller_identity()
        return True
    except Exception:
        return False


# Set up the Streamlit app
st.title("E-commerce Support Simulator")
st.caption("""
Simulate email-based customer support for an e-commerce platform using AI agents powered by Amazon Bedrock.

This demo showcases how multiple specialized AI agents can collaborate to handle customer inquiries
about orders, shipments, returns, and product information.

To learn more about the agents used in this demo visit [this link](https://github.com/awslabs/agent-squad/tree/main/examples/python/email-simulator).
""")

# Check AWS connection
if not test_aws_connection():
    st.error("AWS connection failed. Please check your AWS credentials and region configuration.")
    st.warning("Visit the AWS documentation for guidance on setting up your credentials and region.")
    st.stop()

# Define the tools
order_lookup_tool = AgentTool(
    name='order_lookup',
    description='Retrieve order details from the database. Use this when the customer asks about their order status, order details, or order history.',
    properties={
        'order_id': {
            'type': 'string',
            'description': 'The order ID to look up (e.g., "12345")'
        }
    },
    func=order_lookup,
    required=['order_id']
)

shipment_tracker_tool = AgentTool(
    name='shipment_tracker',
    description='Get real-time shipping information for an order. Use this when the customer asks about shipping status, tracking, or delivery estimates.',
    properties={
        'order_id': {
            'type': 'string',
            'description': 'The order ID to track shipment for'
        }
    },
    func=shipment_tracker,
    required=['order_id']
)

return_processor_tool = AgentTool(
    name='return_processor',
    description='Initiate and manage return requests for orders. Use this when the customer wants to return an item or asks about the return process.',
    properties={
        'order_id': {
            'type': 'string',
            'description': 'The order ID for the return request'
        }
    },
    func=return_processor,
    required=['order_id']
)

product_info_tool = AgentTool(
    name='product_info',
    description='Get detailed product information including description, price, and availability.',
    properties={
        'product_name': {
            'type': 'string',
            'description': 'The name of the product to look up'
        }
    },
    func=product_info,
    required=['product_name']
)

# Define the agents
order_management_agent = BedrockLLMAgent(BedrockLLMAgentOptions(
    model_id='anthropic.claude-3-sonnet-20240229-v1:0',
    name="OrderManagementAgent",
    description="""\
You are an expert order management specialist. You handle all order-related inquiries including:
- Order status and details
- Shipment tracking and delivery estimates
- Return requests and refund processing

Your tasks:
1. Use the order_lookup tool to retrieve order information when needed.
2. Use the shipment_tracker tool to get shipping updates.
3. Use the return_processor tool to initiate returns when requested.
4. Provide clear, helpful responses with relevant order details.
5. Be empathetic and professional in all communications.
""",
    tool_config={
        'tool': AgentTools(tools=[order_lookup_tool, shipment_tracker_tool, return_processor_tool]),
        'toolMaxRecursions': 10,
    },
    save_chat=False
))

product_info_agent = BedrockLLMAgent(BedrockLLMAgentOptions(
    model_id='anthropic.claude-3-haiku-20240307-v1:0',
    name="ProductInfoAgent",
    description="""\
You are a knowledgeable product specialist. You provide detailed information about products including:
- Product descriptions and features
- Pricing and availability
- Product comparisons and recommendations

Your tasks:
1. Use the product_info tool to look up product details.
2. Provide accurate and helpful product information.
3. Make recommendations based on customer needs.
4. Be friendly and informative in your responses.
""",
    tool_config={
        'tool': AgentTools(tools=[product_info_tool]),
        'toolMaxRecursions': 5,
    },
    save_chat=False
))

customer_service_supervisor = BedrockLLMAgent(BedrockLLMAgentOptions(
    model_id='us.anthropic.claude-3-5-sonnet-20241022-v2:0',
    name='CustomerServiceSupervisor',
    description="""\
You are a senior customer service manager coordinating the support team.

Your role:
1. Analyze customer emails to understand their needs.
2. Delegate to OrderManagementAgent for order, shipping, and return inquiries.
3. Delegate to ProductInfoAgent for product-related questions.
4. Compile responses into a professional, well-formatted email reply.
5. Ensure the response is empathetic, helpful, and addresses all customer concerns.
6. Format the response as a professional customer service email.
"""
))

supervisor = SupervisorAgent(SupervisorAgentOptions(
    name="SupervisorAgent",
    description="Coordinates customer support agents",
    lead_agent=customer_service_supervisor,
    team=[order_management_agent, product_info_agent],
    trace=True
))


async def handle_request(_orchestrator: AgentSquad, _user_input: str, _user_id: str, _session_id: str):
    classifier_result = ClassifierResult(selected_agent=supervisor, confidence=1.0)

    response: AgentResponse = await _orchestrator.agent_process_request(
        _user_input, _user_id, _session_id, classifier_result
    )

    print("\nMetadata:")
    print(f"Selected Agent: {response.metadata.agent_name}")

    if isinstance(response, AgentResponse) and response.streaming is False:
        if isinstance(response.output, str):
            return response.output
        elif isinstance(response.output, ConversationMessage):
            return response.output.content[0].get('text')


# Initialize the orchestrator
orchestrator = AgentSquad(options=AgentSquadConfig(
    LOG_AGENT_CHAT=True,
    LOG_CLASSIFIER_CHAT=True,
    LOG_CLASSIFIER_RAW_OUTPUT=True,
    LOG_CLASSIFIER_OUTPUT=True,
    LOG_EXECUTION_TIMES=True,
    MAX_RETRIES=3,
    USE_DEFAULT_AGENT_IF_NONE_IDENTIFIED=True,
    MAX_MESSAGE_PAIRS_PER_AGENT=10,
))

USER_ID = str(uuid.uuid4())
SESSION_ID = str(uuid.uuid4())

# Email template options
st.subheader("Compose Customer Email")

email_templates = {
    "Custom": "",
    "Order Status Inquiry": "Hi,\n\nI placed an order recently and would like to check on its status. My order number is 12345.\n\nCould you please let me know when I can expect it to arrive?\n\nThank you!",
    "Shipment Tracking": "Hello,\n\nI'm trying to track my order #12345. Can you provide me with the shipping details and estimated delivery date?\n\nBest regards",
    "Return Request": "Hi there,\n\nI received my order #11111 but I'd like to return it. Can you help me with the return process?\n\nThanks",
    "Product Question": "Hello,\n\nI'm interested in learning more about Widget A. Can you tell me about its features and whether it's currently in stock?\n\nThank you!"
}

selected_template = st.selectbox("Select a template or write custom:", list(email_templates.keys()))

# Email composition area
if selected_template == "Custom":
    customer_email = st.text_area(
        "Write your email:",
        height=200,
        placeholder="Dear Customer Support,\n\nI have a question about..."
    )
else:
    customer_email = st.text_area(
        "Email content (you can edit the template):",
        value=email_templates[selected_template],
        height=200
    )

# Display available test data
with st.expander("Available Test Data"):
    st.markdown("""
    **Test Order IDs:**
    - `12345` - Shipped order (Widget A, Gadget B)
    - `67890` - Processing order (Gizmo C)
    - `11111` - Delivered order (Super Device X, Accessory Y, Cable Z)
    - `22222` - Pending order (Premium Package)

    **Test Products:**
    - Widget A, Gadget B, Gizmo C, Super Device X
    """)

# Process the email
if st.button("Send Email"):
    if not customer_email.strip():
        st.warning("Please write an email message first.")
    else:
        with st.spinner("Processing your email..."):
            input_text = f"""
Customer Email:
---
{customer_email}
---

Please respond to this customer email professionally and helpfully.
"""
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            response = loop.run_until_complete(
                handle_request(orchestrator, input_text, USER_ID, SESSION_ID)
            )

            st.subheader("Support Team Response")
            st.markdown(response)
