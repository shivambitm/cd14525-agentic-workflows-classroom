# agentic_workflow.py

from workflow_agents.base_agents import ActionPlanningAgent, KnowledgeAugmentedPromptAgent, EvaluationAgent, RoutingAgent

import os
from dotenv import load_dotenv

load_dotenv()
openai_api_key = os.getenv('OPENAI_API_KEY')

# load the product spec
with open('Product-Spec-Email-Router.txt', 'r', encoding='utf-8') as f:
    product_spec = f.read()

# Instantiate all the agents

# Action Planning Agent
knowledge_action_planning = (
    "Stories are defined from a product spec by identifying a "
    "persona, an action, and a desired outcome for each story. "
    "Each story represents a specific functionality of the product "
    "described in the specification. \n"
    "Features are defined by grouping related user stories. \n"
    "Tasks are defined for each story and represent the engineering "
    "work required to develop the product. \n"
    "A development Plan for a product contains all these components"
)
action_planning_agent = ActionPlanningAgent(openai_api_key, knowledge_action_planning)

# Product Manager - Knowledge Augmented Prompt Agent
persona_product_manager = "You are a Product Manager, you are responsible for defining the user stories for a product."
knowledge_product_manager = (
    "Stories are defined by writing sentences with a persona, an action, and a desired outcome. "
    "The sentences always start with: As a "
    "Write several stories for the product spec below, where the personas are the different users of the product. "
    + product_spec
)
product_manager_knowledge_agent = KnowledgeAugmentedPromptAgent(openai_api_key, persona_product_manager, knowledge_product_manager)

persona_product_manager_eval = "You are an evaluation agent that checks the answers of other worker agents."
evaluation_criteria_product_manager = "The answer should be user stories that follow the following structure: As a [type of user], I want [an action or feature] so that [benefit/value]."
product_manager_evaluation_agent = EvaluationAgent(openai_api_key, persona_product_manager_eval, evaluation_criteria_product_manager, product_manager_knowledge_agent)

# Program Manager - Knowledge Augmented Prompt Agent
persona_program_manager = "You are a Program Manager, you are responsible for defining the features for a product."
knowledge_program_manager = "Features of a product are defined by organizing similar user stories into cohesive groups."
program_manager_knowledge_agent = KnowledgeAugmentedPromptAgent(openai_api_key, persona_program_manager, knowledge_program_manager)

# Program Manager - Evaluation Agent
persona_program_manager_eval = "You are an evaluation agent that checks the answers of other worker agents."
evaluation_criteria_program_manager = (
    "The answer should be product features that follow the following structure: "
    "Feature Name: A clear, concise title that identifies the capability\n"
    "Description: A brief explanation of what the feature does and its purpose\n"
    "Key Functionality: The specific capabilities or actions the feature provides\n"
    "User Benefit: How this feature creates value for the user"
)
program_manager_evaluation_agent = EvaluationAgent(openai_api_key, persona_program_manager_eval, evaluation_criteria_program_manager, program_manager_knowledge_agent)

# Development Engineer - Knowledge Augmented Prompt Agent
persona_dev_engineer = "You are a Development Engineer, you are responsible for defining the development tasks for a product."
knowledge_dev_engineer = "Development tasks are defined by identifying what needs to be built to implement each user story."
development_engineer_knowledge_agent = KnowledgeAugmentedPromptAgent(openai_api_key, persona_dev_engineer, knowledge_dev_engineer)

# Development Engineer - Evaluation Agent
persona_dev_engineer_eval = "You are an evaluation agent that checks the answers of other worker agents."
evaluation_criteria_dev_engineer = (
    "The answer should be tasks following this exact structure: "
    "Task ID: A unique identifier for tracking purposes\n"
    "Task Title: Brief description of the specific development work\n"
    "Related User Story: Reference to the parent user story\n"
    "Description: Detailed explanation of the technical work required\n"
    "Acceptance Criteria: Specific requirements that must be met for completion\n"
    "Estimated Effort: Time or complexity estimation\n"
    "Dependencies: Any tasks that must be completed first"
)
development_engineer_evaluation_agent = EvaluationAgent(openai_api_key, persona_dev_engineer_eval, evaluation_criteria_dev_engineer, development_engineer_knowledge_agent)




# Job function persona support functions
def product_manager_support_function(query):
    """Support function for Product Manager route"""
    print(f"\n[Product Manager] Processing query: {query}")
    result = product_manager_evaluation_agent.evaluate(query)
    return result['final_response']

def program_manager_support_function(query):
    """Support function for Program Manager route"""
    print(f"\n[Program Manager] Processing query: {query}")
    result = program_manager_evaluation_agent.evaluate(query)
    return result['final_response']

def development_engineer_support_function(query):
    """Support function for Development Engineer route"""
    print(f"\n[Development Engineer] Processing query: {query}")
    result = development_engineer_evaluation_agent.evaluate(query)
    return result['final_response']

# Routing Agent
agents_routes = [
    {
        'name': 'Product Manager',
        'description': 'Responsible for defining user stories for a product based on product specifications. Handles queries about user needs, personas, and story creation.',
        'func': product_manager_support_function
    },
    {
        'name': 'Program Manager',
        'description': 'Responsible for defining product features by organizing user stories into cohesive groups. Handles queries about feature planning and organization.',
        'func': program_manager_support_function
    },
    {
        'name': 'Development Engineer',
        'description': 'Responsible for defining development tasks and technical implementation details. Handles queries about engineering work, tasks, and technical requirements.',
        'func': development_engineer_support_function
    }
]

routing_agent = RoutingAgent(openai_api_key, agents_routes)

# Run the workflow

print("\n*** Workflow execution started ***\n")
# Workflow Prompt
# ****
workflow_prompt = "What would the development tasks for this product be?"
# ****
print(f"Task to complete in this workflow, workflow prompt = {workflow_prompt}")

print("\nDefining workflow steps from the workflow prompt")
# Extract workflow steps using action planning agent
workflow_steps = action_planning_agent.extract_steps_from_prompt(workflow_prompt)
print(f"\nWorkflow steps identified: {len(workflow_steps)}")
for idx, step in enumerate(workflow_steps, 1):
    print(f"  {idx}. {step}")

# Initialize list to store completed steps
completed_steps = []

# Execute workflow by routing each step to appropriate agent
print("\n\n=== Executing Workflow Steps ===\n")
for idx, step in enumerate(workflow_steps, 1):
    print(f"\n{'='*80}")
    print(f"STEP {idx}/{len(workflow_steps)}: {step}")
    print(f"{'='*80}")
    
    # Route the step to the appropriate agent
    result = routing_agent.route(step)
    
    # Store the result
    completed_steps.append({
        'step': step,
        'result': result
    })
    
    print(f"\n[STEP {idx} COMPLETED]")
    print(f"Result preview: {result[:200]}..." if len(result) > 200 else f"Result: {result}")

# Print final workflow output
print("\n\n" + "="*80)
print("WORKFLOW COMPLETED SUCCESSFULLY")
print("="*80)
print(f"\nTotal steps completed: {len(completed_steps)}")
print("\n\n=== FINAL OUTPUT (Last Step Result) ===\n")
if completed_steps:
    print(completed_steps[-1]['result'])
else:
    print("No steps were completed.")