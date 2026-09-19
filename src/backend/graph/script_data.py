# ---------------------------------------
# Synthetic Lead Data (No Real PII)
# ---------------------------------------

SYNTHETIC_LEADS = {
    "test_lead_1": {
        "lead_id": "LEAD_001",
        "phone": "+61455501999",
        "name": "John Doe",
        "postcode": "2000",
        "journey": "energy_comparison"
    }
}


# ---------------------------------------
# Conversation Script
# Each node corresponds to one LangGraph node
# ---------------------------------------

PITCH_SCRIPT = {

    "greeting_node": {
        "prompt": (
            "Hi John, this is Aarav calling from CIMET. "
            "You recently started comparing energy plans on our website but didn't finish your application. "
            "Before we continue, I need to let you know this call may be recorded for quality and training purposes. "
            "Do I have your consent to continue?"
        ),
        "expected": "yes_no",
        "next": "moving_status_node",
        "fallback": "decline_node"
    },

    "is_moving_node": {
        "prompt": (
            "Great, thank you. "
            "Just to understand your situation, are you moving into a new property, "
            "or are you staying at your current address?"
        ),
        "expected": "moving_status",
        "next": "address_node"
    },

    "address_node": {
        "prompt": (
            "Perfect. Could you please tell me the full address of the property "
            "you're looking to connect the energy service for?"
        ),
        "expected": "address",
        "next": "fuel_type_node"
    },

    "fuel_type_node": {
        "prompt": (
            "Thanks, I've got that. "
            "Are you looking to compare electricity plans, gas plans, or both?"
        ),
        "expected": "fuel_type",
        "next": "solar_node"
    },

    "has_solar_node": {
        "prompt": (
            "One quick question — does the property currently have solar panels installed?"
        ),
        "expected": "yes_no",
        "next": "life_support_node"
    },

    "has_life_support_node": {
        "prompt": (
            "Thank you. "
            "Does anyone living at the property rely on electrically powered life support equipment?"
        ),
        "expected": "yes_no",
        "next": "concession_node"
    },

    "concession_card_node": {
        "prompt": (
            "Almost done. "
            "Do you currently hold a valid government concession or pensioner card?"
        ),
        "expected": "yes_no",
        "next": "summary_node"
    },

    "summary_node": {
        "prompt": (
            "Perfect. Let me quickly confirm what I've captured.\n\n"
            "You're comparing {fuel_type} plans for {address}. "
            "Solar: {has_solar}. "
            "Life Support: {has_life_support}. "
            "Concession Card: {has_concession_card}.\n\n"
            "Is everything correct?"
        ),
        "expected": "yes_no",
        "next": "closing_node",
        "fallback": "correction_node"
    },

    "correction_node": {
        "prompt": (
            "No worries. Which detail would you like me to correct?"
        ),
        "expected": "free_text",
        "next": "router"
    },

    "closing_node": {
        "prompt": (
            "Excellent. Thank you for your time today. "
            "I'm now generating the best available energy plans based on your information. "
            "A member of our sales team will continue with the available offers shortly. "
            "Have a wonderful day!"
        ),
        "expected": None,
        "next": "end"
    },

    "decline_node": {
        "prompt": (
            "Absolutely, that's completely fine. "
            "Thank you for your time, and if you ever decide to compare energy plans again, "
            "we'd be happy to help. Have a great day!"
        ),
        "expected": None,
        "next": "end"
    }
}
