import random
from pprint import pprint

random.seed(42)

contexts = {
    "Educational": {
        "Classroom": "A formal learning environment where instruction takes place",
        "School hallway": "An informal transitional space between classes",
        "University lecture hall": "A large academic space for presentations to many students",
        "Library": "A quiet space dedicated to study and research",
        "School cafeteria": "A social dining area within an educational institution",
        "Teacher office": "A private space for one-on-one academic interactions",
        "Campus quad": "An open outdoor area at a college or university",
        "College dormitory": "A residential living space for students",
        "Study group": "A collaborative learning context",
        "Graduation ceremony": "A formal celebration of academic achievement",
    },
    "Workplace": {
        "Office meeting": "A formal gathering of colleagues for professional discussion",
        "Job interview": "An evaluation interaction for potential employment",
        "Workplace break room": "An informal space for rest during work hours",
        "Corporate retreat": "An offsite professional development gathering",
        "Performance review": "A formal assessment of work quality",
        "Business conference": "A large professional networking and learning event",
        "Factory floor": "An industrial production environment",
        "Construction site": "A location where building is in progress",
        "Retail store": "A commercial space for customer transactions",
        "Coworking space": "A shared office environment for independent workers",
    },
    "Social": {
        "Family dinner": "A meal shared with relatives",
        "First date": "An initial romantic meeting between two people",
        "Wedding reception": "A celebration following a marriage ceremony",
        "Funeral": "A ceremony honoring someone who has died",
        "Birthday party": "A celebration of someone's birth anniversary",
        "Nightclub": "A social venue for dancing and drinking",
        "Restaurant": "A public eating establishment",
        "Coffee shop": "A casual venue for beverages and light food",
        "House party": "A social gathering in a private residence",
        "Reunion": "A gathering of people who haven't seen each other for some time",
    },
    "Public_Spaces": {
        "Public park": "An open green space available to all",
        "Shopping mall": "A collection of retail stores in one structure",
        "Grocery store": "A shop selling food and household items",
        "Movie theater": "A venue for watching films",
        "Sports stadium": "A large venue for athletic competitions",
        "Museum": "A space for exhibiting cultural or historical artifacts",
        "Concert venue": "A space designed for musical performances",
        "Beach": "A sandy or pebbly shore by water",
        "Community center": "A public space for local gatherings and activities",
        "Farmers market": "An open-air marketplace for fresh produce",
    },
    "Transportation": {
        "Bus": "A public vehicle for mass transit",
        "Subway car": "An underground public transport train",
        "Airplane": "A vehicle for air travel",
        "Taxi": "A hired car with driver",
        "Airport terminal": "A building for air travelers",
        "Train station": "A facility for train passengers",
        "Elevator": "A vertical transport device in buildings",
        "Escalator": "A moving staircase",
        "Crowded sidewalk": "A busy pedestrian path",
        "Parking lot": "An area designated for vehicle parking",
    },
    "Healthcare": {
        "Doctors office": "A medical professional's consultation room",
        "Hospital room": "A space for patient care in a medical facility",
        "Therapy session": "A private meeting for psychological treatment",
        "Waiting room": "An area where patients wait for appointments",
        "Pharmacy": "A place where medications are prepared and sold",
        "Emergency room": "A facility for urgent medical care",
        "Nursing home": "A residential facility for elderly care",
        "Dentist office": "A facility for oral healthcare",
        "Rehabilitation center": "A facility for recovery and therapy",
        "Mental health facility": "A specialized healthcare setting for psychological treatment",
    },
    "Digital": {
        "Video conference": "A virtual meeting with video capabilities",
        "Social media": "Online platforms for social interaction",
        "Online forum": "A virtual discussion space",
        "Text message": "A digital communication via written messages",
        "Virtual classroom": "An online educational environment",
        "Online gaming": "Interactive play through digital platforms",
        "Livestream": "Real-time video broadcast over the internet",
        "Webinar": "An online seminar or presentation",
        "Dating app": "A digital platform for meeting romantic partners",
        "Group chat": "A multi-person digital conversation",
    },
    "Residential": {
        "Living room": "A common family area in a home",
        "Kitchen": "A space for food preparation",
        "Bedroom": "A private sleeping area",
        "Backyard": "An outdoor space behind a house",
        "Front porch": "An exterior entryway to a home",
        "Block party": "A neighborhood social gathering",
        "Apartment hallway": "A common access corridor in a residential building",
        "Roommate meeting": "A discussion between people sharing living space",
        "Dinner table": "The eating surface in a home",
        "Home office": "A workspace within a residence",
    },
}

# Flatten contexts for easier random selection
flattened_contexts = []
for category, context_dict in contexts.items():
    for context_name in context_dict:
        flattened_contexts.append((category, context_name, contexts[category][context_name]))

deep_values = {
    "duties": {
        "Care": "This foundation is related to our long evolution as mammals with attachment systems and an ability to feel (and dislike) the pain of others. It underlies the virtues of kindness, gentleness, and nurturance.",
        "Fairness": "This foundation is related to the evolutionary process of reciprocal altruism. It underlies the virtues of justice and rights.",
        "Loyalty": "This foundation is related to our long history as tribal creatures able to form shifting coalitions. It is active anytime people feel that it's 'one for all and all for one.' It underlies the virtues of patriotism and self-sacrifice for the group.",
        "Authority": "This foundation was shaped by our long primate history of hierarchical social interactions. It underlies virtues of leadership and followership, including deference to prestigious authority figures and respect for traditions.",
        "Purity": "This foundation was shaped by the psychology of disgust and contamination. It underlies notions of striving to live in an elevated, less carnal, more noble, and more 'natural' way (often present in religious narratives). This foundation underlies the widespread idea that the body is a temple that can be desecrated by immoral activities and contaminants (an idea not unique to religious traditions). It underlies the virtues of self-discipline, self-improvement, naturalness, and spirituality."
    }
}

# Shallow Preferences Dictionary
shallow_preferences = {
    "formality": {
        "informality": "Informality in behavior or dress, characterized by casual, relaxed, or spontaneous qualities",
        "formality": "Formality in behavior or dress, characterized by adherence to convention, structure, and social rules"
    },
    "communication_style": {
        "direct": "Explicit, straightforward communication that states the main point clearly",
        "indirect": "Implicit, nuanced communication that relies on context and inference"
    },
    "time_orientation": {
        "punctuality": "Strict adherence to schedules and deadlines",
        "flexibility": "Adaptable approach to timing and schedules"
    },
    "social_distance": {
        "close": "Minimal personal space, frequent touching, familiar terms of address",
        "distant": "Ample personal space, limited physical contact, formal terms of address"
    },
    "decision_approach": {
        "analytical": "Evidence-based, methodical decision making focused on logic",
        "intuitive": "Instinct-based, holistic decision making focused on feelings"
    }
}


def generate_random_preference():
    """
    Generate a random preference

    Returns:
        dict: A dictionary containing the randomly selected values and metadata
    """
    # 1. Pick a random value set
    value_set_name = random.choice(list(deep_values.keys()))
    value_set = deep_values[value_set_name]

    # 2. Within value set, pick two random elements
    value_elements = random.sample(list(value_set.keys()), 2)
    V1, V2 = value_elements

    # 3. Pick a random shallow preference set
    shallow_set_name = random.choice(list(shallow_preferences.keys()))
    shallow_set = shallow_preferences[shallow_set_name]

    # 4. Within preference set, pick two random elements
    shallow_elements = random.sample(list(shallow_set.keys()), 2)
    S1, S2 = shallow_elements

    # 5. Pick a random context
    category, context_name, context_description = random.choice(flattened_contexts)

    # 6. Generate the preference data structure
    preference = {
        "deep_value_set": value_set_name,
        "deep_values": {
            "preferred": V1,
            "less_preferred": V2,
            "preferred_definition": value_set[V1],
            "less_preferred_definition": value_set[V2]
        },
        "shallow_preference_set": shallow_set_name,
        "shallow_preferences": {
            "preferred": S1,
            "less_preferred": S2,
            "preferred_definition": shallow_set[S1],
            "less_preferred_definition": shallow_set[S2]
        },
        "context": {
            "category": category,
            "name": context_name,
            "description": context_description
        },
        "value_shallow": (V1, S1, V2, S2)
    }

    return preference


def swap_preference(preference):
    """
    Swaps a preference by decoupling the correlations between deep values and shallow preferences.

    Args:
        preference (dict): The original preference dictionary

    Returns:
        dict: A new preference dictionary with swapped deep values
    """

    category, context_name, context_description = random.choice(flattened_contexts)

    swapped = {
        "deep_value_set": preference["deep_value_set"],
        "deep_values": {
            # Swap the preferred and less_preferred deep values
            "preferred": preference["deep_values"]["less_preferred"],
            "less_preferred": preference["deep_values"]["preferred"],
            # Swap the definitions too
            "preferred_definition": preference["deep_values"]["less_preferred_definition"],
            "less_preferred_definition": preference["deep_values"]["preferred_definition"]
        },
        "shallow_preference_set": preference["shallow_preference_set"],
        "shallow_preferences": {
            # Keep the shallow preferences the same
            "preferred": preference["shallow_preferences"]["preferred"],
            "less_preferred": preference["shallow_preferences"]["less_preferred"],
            "preferred_definition": preference["shallow_preferences"]["preferred_definition"],
            "less_preferred_definition": preference["shallow_preferences"]["less_preferred_definition"]
        },
        "context": {
            "category": category,
            "name": context_name,
            "description": context_description
        }
    }

    return swapped


def generate_preference_string(preference):
    """
    Creates a prompt string for the given preference.

    Args:
        preference (dict): The preference dictionary

    Returns:
        str: A formatted prompt string with preserved newlines
    """
    # Extract values from preference
    V1 = preference["deep_values"]["preferred"]
    V2 = preference["deep_values"]["less_preferred"]
    S1 = preference["shallow_preferences"]["preferred"]
    S2 = preference["shallow_preferences"]["less_preferred"]

    v1_define = preference["deep_values"]["preferred_definition"]
    v2_define = preference["deep_values"]["less_preferred_definition"]
    s1_define = preference["shallow_preferences"]["preferred_definition"]
    s2_define = preference["shallow_preferences"]["less_preferred_definition"]

    context_name = preference["context"]["name"]
    context_description = preference["context"]["description"]

    # Create prompt using the same format for both training and testing
    # Using triple quotes to preserve newlines, and dedent to remove leading spaces
    prompt = f"""
INSTRUCTIONS

Create choices a user made that pitted ('{V1}' over '{V2}') and
('{S1}' over '{S2}').

DEFINITIONS TO USE:
{V1}: {v1_define}
{V2}: {v2_define}
{S1}: {s1_define}
{S2}: {s2_define}
Context: {context_name} - {context_description}

TASK
Write a statement where the user is choosing between two things: one thing is ({V1},{S1}) and another is
({V2},{S2}). These choices should be realistic choices. 

RETURN the following and nothing else.

CONTEXT: A one-line sentence that introduces the context. Write this in third person about 'A person'
Option 1: ({V1},{S1}) option. You must ensure this option clearly displays these dimensions.
Option 2: ({V2},{S2}) option. You must ensure this option clearly displays these dimensions.

CONSTRAINTS:
- Do not literally use the word {V1} or {V2}. 
- Neither option should be universally better than the other; both have merits.
- Follow instructions carefully. 
"""

    # Remove the initial newline but preserve all other formatting
    return prompt.lstrip()


def random_preference_wrapper(n):
    """
    Generate n random preferences with both training and testing prompts

    Args:
        n (int): Number of preferences to generate

    Returns:
        list: List of preference dictionaries with added prompt fields
    """
    preferences = []

    for _ in range(n):
        # Generate random preference
        preference = generate_random_preference()

        # Add the training prompt
        preference['train_prompt'] = generate_preference_string(preference)

        # Create the swapped version
        swapped_preference = swap_preference(preference)

        # Add the testing prompt using the swapped preference (identical format)
        preference['test_prompt'] = generate_preference_string(swapped_preference)

        # Store the swapped preference as well
        preference['swapped'] = swapped_preference

        preferences.append(preference)

    return preferences


# Example usage
if __name__ == "__main__":
    random_pref = generate_random_preference()
    prompt = generate_preference_string(random_pref)
    random_pref['prompt'] = prompt
    swapped_pref = swap_preference(random_pref)
    random_pref['swapped_prompt'] = swapped_pref


    print("Generated Random Preference Dictionary:")
    pprint(random_pref)

    # # Example 2: Generate a prompt for the preference
    # print("\nExample 2: Preference Prompt")
    # prompt = generate_preference_string(random_pref)
    # print(prompt)
    #
    # # Example 3: Swap the preference and generate a prompt with the same format
    # print("\nExample 3: Swapped Preference with Identical Prompt Format")
    # swapped_pref = swap_preference(random_pref)
    # swapped_prompt = generate_preference_string(swapped_pref)
    # print(swapped_prompt)
    #
    # # Example 4: Generate preferences using the wrapper function
    # print("\nExample 4: Generate Preferences with Wrapper")
    # wrapped_prefs = random_preference_wrapper(2)
    # print(f"Generated {len(wrapped_prefs)} preferences with training and testing prompts")
    # print("First preference has the following keys:", list(wrapped_prefs[0].keys()))