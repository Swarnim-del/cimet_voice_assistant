# A structured script for the energy pitch simulation

PITCH_SCRIPT = {
    "greeting": {
        "prompt": "Hi, I'm Aarav from CIMET. Are you looking to compare energy plans for a new property you are moving into, or are you staying at your current address?",
        "next": "address_node"
    },
    "address": {
        "prompt": "Got it. Could you please provide the full address of the property?",
        "next": "fuel_type_node"
    },
    "fuel_type": {
        "prompt": "Thank you. And are you looking to compare Electricity, Gas, or both?",
        "next": "has_solar_node"
    },
    "has_solar": {
        "prompt": "Noted. Does the property currently have solar panels installed?",
        "next": "has_life_support_node"
    },
    "has_life_support": {
        "prompt": "Alright. Does anyone at the property rely on life support equipment?",
        "next": "concession_card_node"
    },
    "concession_card": {
        "prompt": "Almost done! Do you hold a valid government concession or pensioner card?",
        "next": "closing"
    },
    "closing": {
        "prompt": "Perfect. Based on the details you've provided, I'm pulling up the best energy plans for you now. Just a moment...",
        "next": "end"
    }
}
