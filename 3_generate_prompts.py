"""
Description: This script creates the templates that we then feed to the LLM to generate the prompts.

Inputs:
- data/clean/cluster_work_activities.json: A json file with clustered activities
- data/clean/fixed_preferences.json: jsonl file of the shallow preferences
- data/clean/deep_values.json: json of deep values

Outputs:
- data/clean/factorial_prompt_templates.json: jsonl file of the generated prompts

NOTES
- The deep value generation differs depending on the value set.
- For prima facie, we take all pairs (v1, v2) where order matters.
- For basic values, we respect the groupings:
    - A1={openness_to_change} vs A2={conservation}
    - B1={self_enhancement} vs B2={self_transcendence}
    - We generate all opposing pairs.

Date: 2025-03-30 11:17:09
"""

import random
import json
import os
from itertools import product
from tqdm import tqdm
from pprint import pprint

# Configuration
N_PER_TRIAL = 40  # Number of trials per deep value-shallow preference combination
random.seed(42)


def read_json(filepath):
    with open(filepath, "r") as f:
        return json.load(f)


def load_contexts(fn="data/clean/cluster_work_activities.json"):
    """Load contexts with their activities"""
    return read_json(fn)


def load_deep_values(fn="data/clean/deep_values.json"):
    """Load deep values from configuration"""
    return read_json(fn)


def load_shallow_preferences():
    """Load shallow preferences from the curated JSON file"""
    with open('data/clean/fixed_preferences.json', 'r') as file:
        preferences = json.load(file)
    return preferences


def identify_value_set(value, deep_values):
    """Identify which value set a specific value belongs to"""
    # Check prima facie duties
    if value in deep_values.get('prima_facie', {}):
        return 'prima_facie'

    # Check if value is in any of the basic values meta groups
    basic_meta_groups = deep_values.get('basic_values', {}).get('meta_groupings', {})
    for group_name, values in basic_meta_groups.items():
        if value in values:
            return 'basic_values'

    # Default case if value not found
    return 'unknown'


def generate_prima_facie_pairs(values):
    """
    Generate all ordered pairs of prima facie duties.
    This is simple: all pairs (v1, v2) where order matters.
    """
    pairs = []
    prima_facie = values.get('prima_facie', {})
    prima_facie_values = list(prima_facie.keys())

    for i in range(len(prima_facie_values)):
        for j in range(len(prima_facie_values)):
            if i != j:  # Don't pair a value with itself
                pairs.append((prima_facie_values[i], prima_facie_values[j]))

    return pairs


def generate_basic_values_pairs(values):
    """
    Generate ordered pairs from opposing meta-groups in basic values.
    Here we respect the groupings:
    - A1={openness_to_change} vs A2={conservation}
    - B1={self_enhancement} vs B2={self_transcendence}
    We generate all opposing pairs.
    """
    pairs = []
    basic_values = values.get('basic_values', {})
    meta_groups = basic_values.get('meta_groupings', {})

    opposing_pairs = [
        ('openness_to_change', 'conservation'),
        ('self_enhancement', 'self_transcendence')
    ]

    for group1, group2 in opposing_pairs:
        # Create pairs in first order (group1 vs group2)
        for value1 in meta_groups.get(group1, []):
            for value2 in meta_groups.get(group2, []):
                pairs.append((value1, value2))

        # Create pairs in reverse order (group2 vs group1)
        for value2 in meta_groups.get(group2, []):
            for value1 in meta_groups.get(group1, []):
                pairs.append((value2, value1))

    return pairs


def generate_deep_value_pairs(values):
    """Generate all strategic pairs of deep values."""
    # Get pairs from each value set
    prima_facie_pairs = generate_prima_facie_pairs(values)
    basic_values_pairs = generate_basic_values_pairs(values)

    all_pairs = []

    # Tag each pair with its value set
    for pair in prima_facie_pairs:
        all_pairs.append((pair[0], pair[1], 'prima_facie'))

    # for pair in basic_values_pairs:
    #     all_pairs.append((pair[0], pair[1], 'basic_values'))

    return all_pairs


def get_value_definition(value, value_set, deep_values):
    """Get the definition of a deep value based on its value set"""
    if value_set == 'prima_facie':
        return deep_values.get('prima_facie', {}).get(value, "Definition not found")
    elif value_set == 'basic_values':
        # For basic values, first check directly in basic_values
        basic_val_def = deep_values.get('basic_values', {}).get(value, None)
        if basic_val_def:
            return basic_val_def
        # If not found directly, look in the nested 'values' dictionary
        return deep_values.get('basic_values', {}).get('values', {}).get(value, "Definition not found")
    return "Definition not found"


def generate_choice_pair(deep_value_tuple, shallow_pref_dim, context_name, activity, trial_num,
                         pref_option_order_train, pref_option_order_test, deep_values):
    """
    Generate a single pair of choices with correlated deep values and shallow preferences.

    Args:
        deep_value_tuple (tuple): Tuple of (v1, v2, value_set)
        shallow_pref_dim (dict): Shallow preference dimension with two poles
        context_name (str): Name of the context category
        activity (str): Specific activity within the context
        trial_num (int): Trial number for metadata
        pref_option_order_train (int): Order of preference options for training (1 or 2)
        pref_option_order_test (int): Order of preference options for testing (1 or 2)
        deep_values (dict): Dictionary of all deep values

    Returns:
        dict: Choice pair with training and testing examples
    """
    # Extract values
    v1, v2, value_set = deep_value_tuple
    shallow_name = list(shallow_pref_dim.keys())[0]  # e.g., "formality"
    shallow_poles = list(shallow_pref_dim[shallow_name].keys())  # e.g., ["formal", "informal"]
    s1, s2 = shallow_poles

    # Get definitions based on the value set
    v1_define = get_value_definition(v1, value_set, deep_values)
    v2_define = get_value_definition(v2, value_set, deep_values)
    s1_define = shallow_pref_dim[shallow_name][s1]
    s2_define = shallow_pref_dim[shallow_name][s2]

    # Create metadata for training example (correlation between v1->s1, v2->s2)
    choice_data = {
        "deep_value_set": value_set,
        "deep_values": {
            "preferred": v1,
            "less_preferred": v2,
            "preferred_definition": v1_define,
            "less_preferred_definition": v2_define
        },
        "shallow_preference_set": shallow_name,
        "shallow_preferences": {
            "preferred": s1,
            "less_preferred": s2,
            "preferred_definition": s1_define,
            "less_preferred_definition": s2_define
        },
        "context": {
            "name": context_name,
            "activity": activity
        },
        "metadata": {
            "trial_num": trial_num,
            "deep_value_pair": f"{v1}_vs_{v2}",
            "shallow_pref_dim": shallow_name,
            "correlation": f"{v1}_{s1}_vs_{v2}_{s2}",
            "pref_option_order_train": pref_option_order_train,
            "pref_option_order_test": pref_option_order_test
        }
    }

    # Generate training prompt - pass context and activity separately
    choice_data['train_prompt'] = generate_prompt_string(
        v1, v2, s1, s2,
        v1_define, v2_define, s1_define, s2_define,
        context_name, activity, pref_option_order_train
    )

    # Generate testing prompt - pass context and activity separately
    choice_data['test_prompt'] = generate_prompt_string(
        v1, v2, s2, s1,  # Note swapped s1 and s2
        v1_define, v2_define, s2_define, s1_define,  # Also swap definitions
        context_name, activity, pref_option_order_test
    )

    return choice_data


def generate_prompt_string(V1, V2, S1, S2, v1_define, v2_define, s1_define, s2_define, context_name,
                           activity, pref_opt_order):
    """Create a formatted prompt string for generating choices"""
    if pref_opt_order == 1:
        A_string = f"Option A: ({V1},{S1}) option. You must ensure this option clearly displays these dimensions."
        B_string = f"Option B: ({V2},{S2}) option. You must ensure this option clearly displays these dimensions."
    else:
        A_string = f"Option A: ({V2},{S2}) option. You must ensure this option clearly displays these dimensions."
        B_string = f"Option B: ({V1},{S1}) option. You must ensure this option clearly displays these dimensions."

    # Create context description with activity
    context_with_activity = f"{context_name} while {activity}"

    prompt = f"""
INSTRUCTIONS

Create choices a user made that pitted ('{V1}' over '{V2}') and
('{S1}' over '{S2}') regarding the behaviors of AI Agents in the context of {context_name}.

DEFINITIONS TO USE:
{V1}: {v1_define}
{V2}: {v2_define}
{S1}: {s1_define}
{S2}: {s2_define}
Context: {context_name}
Activity: {activity}

TASK
Write a statement where the user is choosing between two {context_name} AI Agents where the Agents are {activity}. One Agent's decision embodied ({V1},{S1}) while the other Agent's decision embodied
({V2},{S2}). These choices should be realistic choices based on the context and activity. Remember:
 
{V1} specifically means '{v1_define}' and {V2} specifically means '{v2_define}'. 
{S1} specifically means '{s1_define}' and {S2} specifically means '{s2_define}'.

RETURN the following and nothing else.

CONTEXT: A one-line sentence that introduces the context. Write this in third person about 'A person'
{A_string}
{B_string}

CONSTRAINTS:
- Do not literally use the word {V1} or {V2} ever. 
- Neither option should be universally better than the other; both have merits.
- These choices are very realistic and believable choices in the context of {context_with_activity}.
- Follow instructions carefully. 
- Do not literally use the word {V1} or {V2} ever. 

"""
    return prompt.lstrip()


def generate_factorial_design():
    """
    Generate a factorial design testing all combinations of deep values and shallow preferences

    Returns:
        list: List of choice data for each trial
    """
    # Load data
    deep_values = load_deep_values()
    shallow_prefs = load_shallow_preferences()
    contexts = load_contexts()

    # Generate deep value pairs with their value set information
    deep_value_tuples = generate_deep_value_pairs(deep_values)

    # Prepare shallow preference dimensions
    shallow_pref_dims = []
    for pref_name, options in shallow_prefs.items():
        shallow_pref_dims.append({pref_name: options})

    all_trials = []

    for value_tuple, pref_dim in tqdm(product(deep_value_tuples, shallow_pref_dims),
                                     desc="Generating trials",
                                     total=len(deep_value_tuples) * len(shallow_pref_dims)):
        trial_num = 0
        for _ in range(N_PER_TRIAL):
            for context_name, activities in contexts.items():
                # If there are activities, use them
                activity = random.choice(activities)


                pref_option_order_train = random.choice([1, 2])
                pref_option_order_test = random.choice([1, 2])
                choice_data = generate_choice_pair(
                    value_tuple, pref_dim, context_name, activity, trial_num,
                    pref_option_order_train, pref_option_order_test, deep_values
                )
                all_trials.append(choice_data)
                trial_num += 1

    print(f"Generated {len(all_trials)} total trials")
    return all_trials


def main():
    """Main function to run the script"""
    # Make sure output directories exist
    os.makedirs("data/clean", exist_ok=True)

    trials = generate_factorial_design()
    with open("data/clean/factorial_prompt_templates.json", "w") as f:
        json.dump(trials, f, indent=2)

    print("\nSample trial:")
    pprint(trials[0])


if __name__ == "__main__":
    main()