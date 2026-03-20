import json
import numpy as np
import argparse
import os
import concurrent.futures
from tqdm import tqdm
import random
import time
import threading
import openai
from openai import OpenAI, APITimeoutError, APIError
from anthropic import Anthropic
from together import Together
from config import TRACE_CUSTOMLLM_API_KEY, TRACE_CUSTOMLLM_MODEL, TRACE_CUSTOMLLM_URL
import glob
from fastchat.model import get_conversation_template
import logging
import httpx
import glob
import urllib.error
import urllib.request

logger = logging.getLogger("lean_trace")

# --- Setup ---
MODEL = "gpt-4o-mini"
# MODEL = "claude-3-5-haiku-20241022"
# MODEL = "meta-llama/Llama-3.3-70B-Instruct-Turbo"
VERBOSE = False
TIMEOUT_SECONDS = 400  # or whatever value you prefer
anthropic_client = Anthropic(api_key=TRACE_CUSTOMLLM_API_KEY)

# Verbosity levels
VERBOSITY_MINIMAL = 0  # Only scores and metadata
VERBOSITY_COMPACT = 1  # + full responses (but no prompts/queries)
VERBOSITY_FULL = 2  # Everything (current behavior)

# Cache for critic scores to avoid redundant API calls
cache = {}


def build_agent_data_from_lean_dir(lean_dir: str, output_path: str, recursive: bool = True):
    """
    Scan a directory of Lean files and build a TVD-MI compatible agent-data JSON.

    Supported filename patterns:

        <task_id>__<agent_name>.lean   # multi-agent per task
        <task_id>.lean                 # single 'gold' agent

    Example:
        humaneval_001__baseline.lean
        humaneval_001__trace_debug.lean
        humaneval_002.lean             (treated as agent 'gold')
    
    Args:
        lean_dir: Directory to scan for Lean files
        output_path: Path to save the agent-data JSON
        recursive: If True, recursively search subdirectories (default: True)
    """
    if recursive:
        # Recursively search for .lean files
        pattern = os.path.join(lean_dir, "**", "*.lean")
        files = glob.glob(pattern, recursive=True)
    else:
        # Only search top-level directory
        pattern = os.path.join(lean_dir, "*.lean")
        files = glob.glob(pattern)
    
    if not files:
        raise ValueError(f"No .lean files found in directory: {lean_dir} (recursive={recursive})")
    
    print(f"Found {len(files)} Lean files in {lean_dir}")

    tasks_dict = {}  # task_id -> {agent_name -> lean_text}
    agent_names_set = set()  # all agent names we see

    for path in files:
        fname = os.path.basename(path)

        # Strip extension
        if not fname.endswith(".lean"):
            continue
        stem = fname[:-5]  # remove ".lean"

        # Case 1: task__agent.lean (split from the right to allow '__' in task_id)
        if "__" in stem:
            task_id, agent_name = stem.rsplit("__", 1)
        else:
            # Case 2: task.lean → treat as single 'gold' agent
            task_id = stem
            agent_name = "gold"

        with open(path, "r", encoding="utf-8") as f:
            lean_text = f.read()

        agent_names_set.add(agent_name)
        if task_id not in tasks_dict:
            tasks_dict[task_id] = {}
        tasks_dict[task_id][agent_name] = lean_text

    if not tasks_dict:
        raise ValueError(f"No usable Lean files found in {lean_dir}")

    # Stable ordering of agents
    agent_names = sorted(agent_names_set)
    
    # Check if we have multiple agents
    if len(agent_names) == 1:
        print(f"\n{'='*80}")
        print(f"ERROR: Only found 1 agent ({agent_names[0]}). TVD-MI requires at least 2 agents per task.")
        print(f"{'='*80}")
        print(f"\nTVD-MI cannot compute meaningful scores with only one agent.")
        print(f"\nTo fix this, you need multiple agent versions of the same task:")
        print(f"  Expected pattern: <task_id>__<agent_name>.lean")
        print(f"  Example:")
        print(f"    - humaneval_55__baseline.lean")
        print(f"    - humaneval_55__trace_debug.lean")
        print(f"    - humaneval_55__self_improve.lean")
        print(f"\n  Found {len(tasks_dict)} tasks, but all with the same agent '{agent_names[0]}'.")
        print(f"\n  TVD-MI scores will all be 0.0 because no pairwise comparisons can be made.")
        print(f"\n  Please provide a directory with multiple agent versions of tasks.")
        print(f"  Or use --agent-data to point to a pre-built JSON file with multiple agents.")
        print(f"{'='*80}\n")
        # Don't raise an error, but warn strongly - let the user decide if they want to proceed
    
    # Count tasks with multiple agents
    multi_agent_tasks = sum(1 for agent_map in tasks_dict.values() if len(agent_map) > 1)
    if multi_agent_tasks == 0 and len(agent_names) > 1:
        print(f"\n{'='*80}")
        print(f"WARNING: Found {len(agent_names)} agents, but no tasks have multiple agents.")
        print(f"{'='*80}")
        print(f"  Each task needs responses from multiple agents to compute TVD-MI.")
        print(f"  Tasks with multiple agents: {multi_agent_tasks} out of {len(tasks_dict)}")
        print(f"  This will result in all TVD-MI scores being 0.0")
        print(f"{'='*80}\n")
    elif multi_agent_tasks > 0:
        print(f"✓ Found {multi_agent_tasks} tasks with multiple agents (out of {len(tasks_dict)} total tasks)")
        print(f"  Agents: {', '.join(agent_names)}")

    # Build agent_perspectives
    agent_perspectives = []
    for name in agent_names:
        agent_perspectives.append(
            {
                "condition": name,
                "reading": None,
                "strategy": f"Lean 4 artifact produced by agent '{name}'.",
            }
        )

    # Build tasks array
    tasks = []
    for task_id, agent_map in sorted(tasks_dict.items()):
        # Responses in consistent agent order (some may be missing)
        responses = [agent_map.get(name, "") for name in agent_names]

        tasks.append(
            {
                "task_id": task_id,
                "context": f"Lean specs for VeriBench task {task_id}",
                "responses": responses,
                "agent_to_file": {
                    name: (
                        f"{task_id}__{name}.lean"
                        if f"{task_id}__{name}" in agent_map
                        else f"{task_id}.lean"
                    )
                    for name in agent_map.keys()
                },
            }
        )

    agent_data = {
        "task_type": "veribench_lean_gold",
        "task_description": "TVD-MI over Lean 4 verification artifacts from VeriBench.",
        "agent_perspectives": agent_perspectives,
        "tasks": tasks,
        "metadata": {
            "source": lean_dir,
            "filename_patterns": ["<task_id>__<agent_name>.lean", "<task_id>.lean"],
        },
    }

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(agent_data, f, indent=2)

    print(f"Built agent-data JSON from Lean dir '{lean_dir}' → {output_path}")
    return output_path


def generate_tvd_mi_prompt(
    task_description: str, response_a: str, response_b: str
) -> str:
    """Generate prompt for TVD-MI critic"""
    prompt = f"""You are evaluating whether two Lean 4 formal artifacts were 
    produced for the SAME underlying code-verification task.

    Task description: {task_description}

    Artifact A:
    {response_a}

    Artifact B:
    {response_b}

    Determine whether these artifacts likely originate from the same Python source function &
    verification task. Consider:
    - Overlap in inferred preconditions / postconditions
    - Shared algebraic properties, invariants, or theorems
    - Similar decomposition of the correctness theorem
    - Shared structure in unit tests or example theorems
    - Similar naming conventions or pattern of Lean constructs

    Rate the INFORMATION GAIN about whether they share the same underlying task.
    Reply with exactly ONE of the following labels on its own line:
    [[Significant Gain]]
    [[Little Gain]]
    [[No Gain]]"""

    return prompt


def interpret_tvd_mi_response(response: str) -> float:
    """Convert LLM response to numeric score"""
    response = response.strip().lower()

    if "[significant gain]" in response:
        return 1.0
    elif "[little gain]" in response:
        return 0.25
    elif "[no gain]" in response:
        return 0.0
    else:
        # Default to no gain if response is unclear
        print(f"Warning: Unclear response '{response}', defaulting to [[No Gain]]")
        return 0.0


def get_critic_score_with_logging(
    text_a: str,
    text_b: str,
    task_description: str,
    call_info: dict,
    model_name: str = None,
    max_retries: int = 3,
    retry_delay: int = 1.0,
    timeout: int = 300,
) -> tuple:
    """Get TVD-MI critic score via API and return both score and full interaction"""
    # Create cache key from inputs
    cache_key = (text_a, text_b, task_description)

    if model_name is None:
        model_name = TRACE_CUSTOMLLM_MODEL

    # Check cache first
    if cache_key in cache:
        # Even for cached results, return the interaction log
        score = cache[cache_key]
        interaction = {
            "cached": True,
            "text_a": text_a,
            "text_b": text_b,
            "task_description": task_description,
            "prompt": generate_tvd_mi_prompt(task_description, text_a, text_b),
            "response": f"[CACHED] Score: {score}",
            "score": score,
        }
        return score, interaction

    message = generate_tvd_mi_prompt(task_description, text_a, text_b)

    base_url = os.environ.get("TRACE_CUSTOMLLM_URL", TRACE_CUSTOMLLM_URL)
    api_key = os.environ.get("TRACE_CUSTOMLLM_API_KEY", TRACE_CUSTOMLLM_API_KEY)
    use_anthropic = "api.anthropic.com" in base_url
    if use_anthropic and not base_url.endswith("/v1/messages"):
        base_url = base_url.rstrip("/") + "/v1/messages"
    if use_anthropic:
        if model_name.startswith("anthropic."):
            model_name = model_name[len("anthropic.") :]
        if model_name.endswith("-v1:0"):
            model_name = model_name[: -len("-v1:0")]

    # Initialize the conversation template for OpenAI-compatible endpoints
    messages = None
    if not use_anthropic:
        conv = get_conversation_template(model_name)
        conv.append_message(conv.roles[0], message)
        messages = conv.to_openai_api_messages()

    if VERBOSE:
        logger.info("\n=== API Call Details ===")
        logger.info(f"Model: {model_name}")
        logger.info("Messages:")
        for msg in messages:
            logger.info(f"{msg['role']}: {msg['content']}")
        logger.info("=====================\n")

    # Make the API call with retry logic
    client = None
    if not use_anthropic:
        client = OpenAI(
            base_url=base_url,
            api_key=api_key,
            timeout=timeout,  # Set timeout on the client
        )

    last_exception = None
    for attempt in range(max_retries + 1):
        try:
            if use_anthropic:
                req_body = json.dumps(
                    {
                        "model": model_name,
                        "max_tokens": 1024,
                        "temperature": 0.7,
                        "messages": [{"role": "user", "content": message}],
                    }
                ).encode("utf-8")
                req = urllib.request.Request(
                    base_url,
                    data=req_body,
                    method="POST",
                    headers={
                        "x-api-key": api_key,
                        "anthropic-version": "2023-06-01",
                        "content-type": "application/json",
                    },
                )
                with urllib.request.urlopen(req, timeout=timeout) as resp:
                    payload = json.loads(resp.read().decode("utf-8"))
                content = payload.get("content", [])
                if content and isinstance(content, list):
                    response_text = content[0].get("text", "")
                else:
                    response_text = ""
            else:
                response = client.chat.completions.create(
                    model=model_name,
                    messages=messages,
                    temperature=0.7,
                    timeout=timeout,  # Also set timeout on the request
                )

                response_text = response.choices[0].message.content

            if VERBOSE:
                logger.info("\n=== Model Response ===")
                logger.info(response_text)
                logger.info("=====================\n")

            # Parse the response to get the score
            score = interpret_tvd_mi_response(response_text)

            # Cache the score
            cache[cache_key] = score

            # Build interaction log
            interaction = {
                "cached": False,
                "text_a": text_a,
                "text_b": text_b,
                "task_description": task_description,
                "prompt": message,
                "response": response_text,
                "score": score,
                "model": model_name,
            }

            return score, interaction

        except APITimeoutError as e:
            last_exception = e
            print(f"API timeout on attempt {attempt + 1}/{max_retries + 1}: {e}")
            if attempt < max_retries:
                delay = retry_delay * (2**attempt)  # Exponential backoff
                print(f"Retrying in {delay} seconds...")
                time.sleep(delay)
            else:
                print(f"All {max_retries + 1} attempts failed due to timeout")
                raise e

        except urllib.error.HTTPError as e:
            last_exception = e
            body = ""
            try:
                body = e.read().decode("utf-8")
            except Exception:
                body = ""
            print(f"API error on attempt {attempt + 1}/{max_retries + 1}: {e} {body}")
            if attempt < max_retries:
                delay = retry_delay * (2**attempt)  # Exponential backoff
                print(f"Retrying in {delay} seconds...")
                time.sleep(delay)
            else:
                print(f"All {max_retries + 1} attempts failed due to API error")
                raise e

        except APIError as e:
            last_exception = e
            print(f"API error on attempt {attempt + 1}/{max_retries + 1}: {e}")
            if attempt < max_retries:
                delay = retry_delay * (2**attempt)  # Exponential backoff
                print(f"Retrying in {delay} seconds...")
                time.sleep(delay)
            else:
                print(f"All {max_retries + 1} attempts failed due to API error")
                raise e

        except (httpx.ConnectTimeout, httpx.TimeoutException) as e:
            last_exception = e
            print(f"Connection timeout on attempt {attempt + 1}/{max_retries + 1}: {e}")
            if attempt < max_retries:
                delay = retry_delay * (2**attempt)  # Exponential backoff
                print(f"Retrying in {delay} seconds...")
                time.sleep(delay)
            else:
                print(
                    f"All {max_retries + 1} attempts failed due to connection timeout"
                )
                raise e

        except Exception as e:
            # For other types of errors, don't retry
            print(f"Non-retryable error: {e}")
            raise e

    # This should never be reached, but just in case
    if last_exception:
        raise last_exception
    else:
        raise RuntimeError("Unexpected error in call_llm")


def get_task_description(data_path):
    """Extract task description from the data file"""
    try:
        with open(data_path, "r") as f:
            data = json.load(f)
            return data.get("task_description", "Task: Generate a response")
    except:
        return "Task: Generate a response"


def load_all_tasks(file_path):
    """Load all tasks from the data file"""
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data.get("tasks", [])


def load_translations(file_path, conditions=None, example_idx=0):
    """
    Load translations from the specified JSON file in the new format.

    Args:
        file_path: Path to the JSON data file
        conditions: List of condition indices or number of conditions to consider
        example_idx: Index of the example to use

    Returns:
        List of translations, original reference (if available), list of condition keys used
    """
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Extract tasks array
    tasks = data.get("tasks", [])

    # Make sure the requested example exists
    if example_idx >= len(tasks):
        raise ValueError(
            f"Example index {example_idx} out of range (only {len(tasks)} examples available)"
        )

    # Get the responses from the specified example
    task = tasks[example_idx]
    all_responses = task.get("responses", [])

    # Determine which conditions/responses to include
    if conditions is None:
        # Default to all available conditions
        num_conditions = len(all_responses)
        selected_indices = list(range(num_conditions))
    elif isinstance(conditions, int):
        # Use the first n conditions
        num_conditions = min(conditions, len(all_responses))
        selected_indices = list(range(num_conditions))
    else:
        # Use the provided list of condition indices
        selected_indices = [
            int(c) if isinstance(c, str) and c.isdigit() else c for c in conditions
        ]
        # Validate indices
        for idx in selected_indices:
            if idx >= len(all_responses):
                raise ValueError(
                    f"Condition index {idx} out of range (only {len(all_responses)} conditions available)"
                )

    # Extract the selected responses
    translations = [all_responses[i] for i in selected_indices]

    # Get condition names/keys if available, otherwise use indices
    agent_perspectives = data.get("agent_perspectives", [])
    if len(agent_perspectives) >= len(all_responses):
        # Extract strategy descriptions as condition keys if available
        condition_keys = []
        for i in selected_indices:
            perspective = agent_perspectives[i]
            condition = perspective.get("condition", f"Condition {i}")
            # Truncate long strategy descriptions
            if isinstance(condition, str) and len(condition) > 50:
                condition = condition[:47] + "..."
            condition_keys.append(condition)
    else:
        # Fall back to using indices as condition keys
        condition_keys = [f"Condition {i}" for i in selected_indices]

    # Try to get a reference if available
    reference = task.get("reference", task.get("context", "No reference available"))

    return translations, reference, condition_keys


def analyze_all_examples_tvd(
    data_path,
    conditions=None,
    output_dir="results",
    max_workers=5,
    num_examples=None,
    verbosity=VERBOSITY_MINIMAL,
):
    """
    Run TVD-MI analysis across examples with proper P and Q distributions.
    """
    print("Loading all tasks for TVD-MI analysis...")

    # Load all tasks
    all_tasks = load_all_tasks(data_path)
    total_available = len(all_tasks)

    # Limit to requested number of examples
    if num_examples is not None:
        all_tasks = all_tasks[:num_examples]
        print(f"Using first {num_examples} examples out of {total_available} available")

    num_tasks = len(all_tasks)
    all_llm_calls = []

    if num_tasks < 2:
        raise ValueError(
            "Need at least 2 tasks to compute TVD-MI with proper Q distribution"
        )

    # Get task description and agent perspectives
    task_description = get_task_description(data_path)

    with open(data_path, "r") as f:
        data = json.load(f)
        agent_perspectives = data.get("agent_perspectives", [])

    # Determine conditions to use
    if conditions is None:
        num_conditions = len(all_tasks[0]["responses"])
        selected_indices = list(range(num_conditions))
    elif isinstance(conditions, int):
        num_conditions = min(conditions, len(all_tasks[0]["responses"]))
        selected_indices = list(range(num_conditions))
    else:
        selected_indices = [
            int(c) if isinstance(c, str) and c.isdigit() else c for c in conditions
        ]

    # Get condition keys
    if len(agent_perspectives) >= len(selected_indices):
        condition_keys = []
        for i in selected_indices:
            perspective = agent_perspectives[i]
            condition = perspective.get("condition", f"Condition {i}")
            if isinstance(condition, str) and len(condition) > 50:
                condition = condition[:47] + "..."
            condition_keys.append(condition)
    else:
        condition_keys = [f"Condition {i}" for i in selected_indices]

    # Set up archive directory for individual results
    archive_dir = os.path.join(output_dir, "tvd_mi_individual_examples")
    os.makedirs(archive_dir, exist_ok=True)

    # Process each task
    all_results = []

    for task_idx in tqdm(range(num_tasks), desc="Processing tasks"):
        # Check if this example already exists
        archive_file = os.path.join(archive_dir, f"tvd_mi_example_{task_idx}.json")
        if os.path.exists(archive_file):
            print(f"Example {task_idx} already exists, loading from {archive_file}")
            with open(archive_file, "r", encoding="utf-8") as f:
                task_results = json.load(f)
            all_results.append(task_results)
            continue

        print(f"\nAnalyzing task {task_idx}...")

        # Get responses for this task
        current_task = all_tasks[task_idx]
        current_responses = [current_task["responses"][i] for i in selected_indices]

        # Prepare API calls
        api_calls = []

        # P distribution: pairs from same task
        # Only add pairs if both responses are non-empty
        for i in range(len(selected_indices)):
            for j in range(len(selected_indices)):
                if i != j and current_responses[i] and current_responses[j]:
                    api_calls.append(
                        {
                            "type": "critic",
                            "distribution": "p",
                            "pair": (i, j),
                            "task_idx": task_idx,
                            "text_a": current_responses[i],
                            "text_b": current_responses[j],
                        }
                    )
        
        # Warn if no P comparisons can be made
        if len([c for c in api_calls if c["distribution"] == "p"]) == 0:
            print(f"  WARNING: Task {task_idx} has no valid agent pairs for P distribution")
            print(f"    Responses: {[len(r) for r in current_responses]}")
            print(f"    This task will have all TVD-MI scores = 0.0")

        # Q distribution: pairs from different tasks
        # For each response in current task, pair with responses from other tasks
        other_task_indices = [idx for idx in range(num_tasks) if idx != task_idx]

        for i in range(len(selected_indices)):
            for j in range(len(selected_indices)):
                if i != j:
                    # Sample a different task
                    other_task_idx = random.choice(other_task_indices)
                    other_task = all_tasks[other_task_idx]
                    other_responses = [
                        other_task["responses"][idx] for idx in selected_indices
                    ]

                    api_calls.append(
                        {
                            "type": "critic",
                            "distribution": "q",
                            "pair": (i, j),
                            "task_idx": task_idx,
                            "other_task_idx": other_task_idx,
                            "text_a": current_responses[i],
                            "text_b": other_responses[j],
                        }
                    )

        # Process API calls in parallel
        pbar = tqdm(
            total=len(api_calls), desc=f"API calls for task {task_idx}", leave=False
        )
        start_time = time.time()
        last_update_time = start_time
        completed_count = 0

        # Replace the entire executor block with this:
        executor = concurrent.futures.ThreadPoolExecutor(max_workers=max_workers)
        try:
            futures = {
                executor.submit(
                    get_critic_score_with_logging,
                    call["text_a"],
                    call["text_b"],
                    task_description,
                    call,
                ): call
                for call in api_calls
            }

            critic_results = []
            completed_futures = set()
            start_time = time.time()

            while len(completed_futures) < len(futures):
                current_time = time.time()

                # Check for newly completed futures
                newly_completed = []
                for future in futures:
                    if future not in completed_futures and future.done():
                        newly_completed.append(future)
                        completed_futures.add(future)

                # Process newly completed futures
                for future in newly_completed:
                    call_info = futures[future]
                    try:
                        score, llm_interaction = future.result()
                        critic_results.append(
                            {
                                "pair": call_info["pair"],
                                "distribution": call_info["distribution"],
                                "score": score,
                            }
                        )
                        llm_interaction["task_idx"] = task_idx
                        llm_interaction["pair"] = call_info["pair"]
                        llm_interaction["distribution"] = call_info["distribution"]
                        all_llm_calls.append(llm_interaction)
                    except Exception as e:
                        print(f"Error processing pair {call_info['pair']}: {e}")

                    pbar.update(1)

                # Hard timeout
                if current_time - start_time > TIMEOUT_SECONDS:  # 30 second timeout
                    print(
                        f"Timeout after {TIMEOUT_SECONDS} seconds, {len(completed_futures)}/{len(futures)} completed"
                    )
                    print("Force breaking out...")
                    break

                time.sleep(0.1)

        finally:
            # Don't wait for executor to shut down gracefully
            print("FORCING EXECUTOR SHUTDOWN")
            executor._threads.clear()  # Clear thread pool
            print("EXECUTOR THREADS CLEARED")

        print("EXECUTOR BLOCK FINISHED")
        pbar.close()
        print("PROGRESS BAR CLOSED")

        # Calculate TVD-MI matrix for this task
        num_agents = len(selected_indices)
        tvd_mi_matrix = np.zeros((num_agents, num_agents))

        for i in range(num_agents):
            for j in range(num_agents):
                if i != j:
                    # Get P distribution scores
                    p_scores = [
                        r["score"]
                        for r in critic_results
                        if r["pair"] == (i, j) and r["distribution"] == "p"
                    ]

                    # Get Q distribution scores
                    q_scores = [
                        r["score"]
                        for r in critic_results
                        if r["pair"] == (i, j) and r["distribution"] == "q"
                    ]

                    # TVD-MI = E[f(X,Y)]_P - E[f(X',Y)]_Q
                    if p_scores and q_scores:
                        tvd_mi_matrix[i, j] = np.mean(p_scores) - np.mean(q_scores)

        missing_pairs = 0
        for i in range(num_agents):
            for j in range(num_agents):
                if i == j:
                    continue
                p_found = any(
                    r["pair"] == (i, j) and r["distribution"] == "p"
                    for r in critic_results
                )
                q_found = any(
                    r["pair"] == (i, j) and r["distribution"] == "q"
                    for r in critic_results
                )
                if not (p_found and q_found):
                    missing_pairs += 1

        if missing_pairs > 0:
            print(
                f"Warning: Task {task_idx} missing {missing_pairs} pairwise distributions; "
                "TVD-MI entries will be zero for those pairs."
            )

        if np.allclose(tvd_mi_matrix, 0):
            print(
                f"Warning: Task {task_idx} TVD-MI matrix is all zeros. "
                "This usually means no valid pairwise comparisons ran or only one agent was present."
            )

        # Calculate mean scores for each agent
        tvd_mi_scores = np.zeros(num_agents)
        for i in range(num_agents):
            other_scores = [tvd_mi_matrix[i, j] for j in range(num_agents) if j != i]
            if other_scores:
                tvd_mi_scores[i] = np.mean(other_scores)

        # Calculate bidirectional scores
        tvd_mi_bidirectional = np.zeros(num_agents)
        for i in range(num_agents):
            bidirectional_scores = []
            for j in range(num_agents):
                if i != j:
                    bidirectional_score = (
                        tvd_mi_matrix[i, j] + tvd_mi_matrix[j, i]
                    ) / 2
                    bidirectional_scores.append(bidirectional_score)
            if bidirectional_scores:
                tvd_mi_bidirectional[i] = np.mean(bidirectional_scores)

        # Store results for this task based on verbosity
        if verbosity == VERBOSITY_MINIMAL:
            task_results = {
                "example_idx": task_idx,
                "condition_keys": condition_keys,
                "tvd_mi_matrix": tvd_mi_matrix.tolist(),
                "tvd_mi_scores": tvd_mi_scores.tolist(),
                "tvd_mi_bidirectional": tvd_mi_bidirectional.tolist(),
                "response_lengths": [len(r) for r in current_responses],
                "metadata": {
                    "num_p_comparisons": len(
                        [r for r in critic_results if r["distribution"] == "p"]
                    ),
                    "num_q_comparisons": len(
                        [r for r in critic_results if r["distribution"] == "q"]
                    ),
                    "cached_count": len(
                        [
                            call
                            for call in all_llm_calls
                            if call["task_idx"] == task_idx
                            and call.get("cached", False)
                        ]
                    ),
                },
            }
        elif verbosity == VERBOSITY_COMPACT:
            task_results = {
                "example_idx": task_idx,
                "translations": current_responses,  # Include full responses
                "condition_keys": condition_keys,
                "tvd_mi_matrix": tvd_mi_matrix.tolist(),
                "tvd_mi_scores": tvd_mi_scores.tolist(),
                "tvd_mi_bidirectional": tvd_mi_bidirectional.tolist(),
                "response_lengths": [len(r) for r in current_responses],
                "metadata": {
                    "num_p_comparisons": len(
                        [r for r in critic_results if r["distribution"] == "p"]
                    ),
                    "num_q_comparisons": len(
                        [r for r in critic_results if r["distribution"] == "q"]
                    ),
                    "cached_count": len(
                        [
                            call
                            for call in all_llm_calls
                            if call["task_idx"] == task_idx
                            and call.get("cached", False)
                        ]
                    ),
                },
            }
        else:  # VERBOSITY_FULL
            task_results = {
                "example_idx": task_idx,
                "reference": current_task.get(
                    "reference", current_task.get("context", "No reference")
                ),
                "translations": current_responses,
                "condition_keys": condition_keys,
                "tvd_mi_matrix": tvd_mi_matrix.tolist(),
                "tvd_mi_scores": tvd_mi_scores.tolist(),
                "tvd_mi_bidirectional": tvd_mi_bidirectional.tolist(),
                "num_p_comparisons": len(
                    [r for r in critic_results if r["distribution"] == "p"]
                ),
                "num_q_comparisons": len(
                    [r for r in critic_results if r["distribution"] == "q"]
                ),
                "task_description": task_description,
                "response_lengths": [len(r) for r in current_responses],
            }

            # Add LLM calls to task results
            task_llm_calls = [
                call for call in all_llm_calls if call["task_idx"] == task_idx
            ]
            task_results["llm_calls"] = task_llm_calls

        # Save individual task results directly to archive
        with open(archive_file, "w", encoding="utf-8") as f:
            json.dump(task_results, f, ensure_ascii=False, indent=2)

        print(f"Results for task {task_idx} saved to {archive_file}")
        all_results.append(task_results)

    return all_results


def analyze_example(data_path, example_idx, conditions=None, output_dir="results"):
    """
    Wrapper for backward compatibility - processes all examples but returns result for requested one.
    """
    print(
        f"Note: TVD-MI requires multiple tasks. Processing all tasks to compute proper distributions..."
    )
    all_results = analyze_all_examples_tvd(
        data_path, conditions, output_dir, max_workers=5
    )

    # Return the specific example requested
    for result in all_results:
        if result["example_idx"] == example_idx:
            return result

    raise ValueError(f"Example {example_idx} not found in results")


def process_multiple_examples(
    data_path,
    num_examples,
    conditions=None,
    output_dir="results",
    max_workers=5,
    verbosity=VERBOSITY_MINIMAL,
):
    """
    Process multiple examples with proper TVD-MI calculation.
    """
    # Check if results already exist
    existing_results = set()
    for i in range(num_examples):
        result_file = os.path.join(output_dir, f"tvd_mi_example_{i}.json")
        if os.path.exists(result_file):
            existing_results.add(i)

    if len(existing_results) == num_examples:
        print("All examples already processed.")
        return []

    # Process examples with the limit
    return analyze_all_examples_tvd(
        data_path,
        conditions,
        output_dir,
        max_workers,
        num_examples=num_examples,
        verbosity=verbosity,
    )


def aggregate_results(
    archive_dir, num_examples, conditions=None, bootstrap_samples=1000, confidence=0.95
):
    """
    Aggregate results from multiple examples with bootstrap confidence intervals.

    Args:
        archive_dir: Directory containing result files
        num_examples: Number of examples to aggregate
        conditions: List of condition names or number of conditions
        bootstrap_samples: Number of bootstrap samples for confidence intervals
        confidence: Confidence level (default: 0.95 for 95% confidence)

    Returns:
        Dict with aggregated results including confidence intervals
    """
    # Load the first example to get the number of conditions and condition keys
    first_example_path = os.path.join(archive_dir, f"tvd_mi_example_0.json")
    if not os.path.exists(first_example_path):
        print("No example results found. Cannot aggregate.")
        return None

    with open(first_example_path, "r", encoding="utf-8") as f:
        first_example = json.load(f)

    condition_keys = first_example.get("condition_keys", [])
    num_conditions = len(condition_keys)

    # Initialize aggregated matrices
    tvd_mi_matrix_agg = np.zeros((num_conditions, num_conditions))
    tvd_mi_scores_agg = np.zeros(num_conditions)
    tvd_mi_bidirectional_agg = np.zeros(num_conditions)
    response_lengths_agg = np.zeros(num_conditions)

    # Collection for bootstrap
    all_tvd_mi_scores = []
    all_tvd_mi_bidirectional = []
    all_response_lengths = []

    # Track number of successful examples
    successful_examples = 0

    # Collect all data directly from archive
    for i in range(num_examples):
        file_path = os.path.join(archive_dir, f"tvd_mi_example_{i}.json")
        if os.path.exists(file_path):
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)

                # Extract only necessary fields to minimize memory usage
                tvd_mi_matrix_agg += np.array(data["tvd_mi_matrix"])
                tvd_mi_scores_agg += np.array(data["tvd_mi_scores"])
                tvd_mi_bidirectional_agg += np.array(data["tvd_mi_bidirectional"])
                response_lengths_agg += np.array(data["response_lengths"])

                # Store individual example results for bootstrap
                all_tvd_mi_scores.append(np.array(data["tvd_mi_scores"]))
                all_tvd_mi_bidirectional.append(np.array(data["tvd_mi_bidirectional"]))
                all_response_lengths.append(np.array(data["response_lengths"]))

                successful_examples += 1

                # Clear the full data dict to free memory
                del data

    # Compute averages
    if successful_examples > 0:
        tvd_mi_matrix_agg /= successful_examples
        tvd_mi_scores_agg /= successful_examples
        tvd_mi_bidirectional_agg /= successful_examples
        response_lengths_agg /= successful_examples

    # Calculate bootstrap confidence intervals
    tvd_mi_scores_ci = calculate_bootstrap_ci(
        all_tvd_mi_scores, bootstrap_samples, confidence
    )
    tvd_mi_bidirectional_ci = calculate_bootstrap_ci(
        all_tvd_mi_bidirectional, bootstrap_samples, confidence
    )
    response_lengths_ci = calculate_bootstrap_ci(
        all_response_lengths, bootstrap_samples, confidence
    )

    # Prepare aggregated results
    aggregated = {
        "num_examples_processed": successful_examples,
        "condition_keys": condition_keys,
        "tvd_mi_matrix_avg": tvd_mi_matrix_agg.tolist(),
        "tvd_mi_scores_avg": tvd_mi_scores_agg.tolist(),
        "tvd_mi_bidirectional_avg": tvd_mi_bidirectional_agg.tolist(),
        "response_lengths_avg": response_lengths_agg.tolist(),
        "tvd_mi_scores_ci": tvd_mi_scores_ci,
        "tvd_mi_bidirectional_ci": tvd_mi_bidirectional_ci,
        "response_lengths_ci": response_lengths_ci,
    }

    # Calculate rankings based on TVD-MI scores
    sorted_indices = np.argsort(tvd_mi_scores_agg)[::-1]
    rankings = {
        "tvd_mi_rankings": sorted_indices.tolist(),
        "ranked_condition_keys": [condition_keys[i] for i in sorted_indices],
        "normalized_scores": (
            (tvd_mi_scores_agg / np.max(tvd_mi_scores_agg) * 100).tolist()
            if np.max(tvd_mi_scores_agg) > 0
            else [0] * len(tvd_mi_scores_agg)
        ),
    }

    # Add bidirectional rankings
    bidirectional_sorted_indices = np.argsort(tvd_mi_bidirectional_agg)[::-1]
    bidirectional_rankings = {
        "tvd_mi_bidirectional_rankings": bidirectional_sorted_indices.tolist(),
        "tvd_mi_bidirectional_ranked_condition_keys": [
            condition_keys[i] for i in bidirectional_sorted_indices
        ],
        "tvd_mi_bidirectional_normalized_scores": (
            (tvd_mi_bidirectional_agg / np.max(tvd_mi_bidirectional_agg) * 100).tolist()
            if np.max(tvd_mi_bidirectional_agg) > 0
            else [0] * len(tvd_mi_bidirectional_agg)
        ),
    }

    aggregated.update(rankings)
    aggregated.update(bidirectional_rankings)

    # Save aggregated results to archive directory
    output_file = os.path.join(archive_dir, "tvd_mi_aggregated.json")
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(aggregated, f, indent=2)

    print(f"Aggregated results saved to {output_file}")

    # Also save the score matrix in a format suitable for correlation analysis
    # Try to find the original agent data file to get task_ids
    agent_data_path = None
    # Look for agent data file in parent directory or same directory
    possible_paths = [
        os.path.join(os.path.dirname(archive_dir), "*.json"),
        os.path.join(archive_dir, "..", "*_agent_data.json"),
    ]
    for pattern in possible_paths:
        matches = glob.glob(pattern)
        if matches:
            agent_data_path = matches[0]
            break

    save_score_matrix_for_correlation(
        archive_dir=archive_dir,
        num_examples=num_examples,
        condition_keys=condition_keys,
        agent_data_path=agent_data_path,
    )

    return aggregated


def calculate_bootstrap_ci(data_arrays, num_samples=1000, confidence=0.95):
    """
    Calculate bootstrap confidence intervals for each condition.

    Args:
        data_arrays: List of arrays, each representing scores from one example
        num_samples: Number of bootstrap samples
        confidence: Confidence level (e.g., 0.95 for 95% CI)

    Returns:
        List of [lower_bound, upper_bound] for each condition
    """
    if not data_arrays:
        return []

    n_examples = len(data_arrays)
    n_conditions = len(data_arrays[0])

    # Convert list of arrays to a 2D array (examples x conditions)
    data_matrix = np.vstack(data_arrays)

    # Initialize arrays for bootstrap results
    bootstrap_means = np.zeros((num_samples, n_conditions))

    # Generate bootstrap samples
    for i in range(num_samples):
        # Sample with replacement
        indices = np.random.choice(n_examples, size=n_examples, replace=True)
        bootstrap_sample = data_matrix[indices]
        bootstrap_means[i] = np.mean(bootstrap_sample, axis=0)

    # Calculate confidence intervals
    alpha = (1 - confidence) / 2
    lower_percentile = alpha * 100
    upper_percentile = (1 - alpha) * 100

    lower_bounds = np.percentile(bootstrap_means, lower_percentile, axis=0)
    upper_bounds = np.percentile(bootstrap_means, upper_percentile, axis=0)

    # Format as [lower, upper] pairs for each condition
    confidence_intervals = []
    for i in range(n_conditions):
        confidence_intervals.append([lower_bounds[i], upper_bounds[i]])

    return confidence_intervals


def save_score_matrix_for_correlation(
    archive_dir, num_examples, condition_keys, agent_data_path=None
):
    """
    Save TVD-MI score matrix in a structured format for correlation analysis.

    Creates a matrix S where S[i, j] is the TVD-MI score for agent i on item j.
    This is the format needed for correlation with VeriBench oracle metrics.

    Args:
        archive_dir: Directory containing individual task result files
        num_examples: Number of examples (items/tasks)
        condition_keys: List of agent names/condition keys
        agent_data_path: Optional path to original agent data file to get task_ids
    """
    num_agents = len(condition_keys)

    # Try to load task_ids from original agent data file if available
    task_ids_from_data = None
    if agent_data_path and os.path.exists(agent_data_path):
        try:
            with open(agent_data_path, "r", encoding="utf-8") as f:
                agent_data = json.load(f)
            tasks = agent_data.get("tasks", [])
            task_ids_from_data = [
                task.get("task_id", f"task_{i}") for i, task in enumerate(tasks)
            ]
        except Exception as e:
            print(f"Warning: Could not load task_ids from agent data file: {e}")

    # Initialize score matrix: agents (rows) x items (columns)
    score_matrix = np.zeros((num_agents, num_examples))
    task_ids = []
    valid_task_indices = []

    # Load scores from each task
    for task_idx in range(num_examples):
        file_path = os.path.join(archive_dir, f"tvd_mi_example_{task_idx}.json")
        if not os.path.exists(file_path):
            print(f"Warning: Task {task_idx} result file not found, skipping")
            continue

        with open(file_path, "r", encoding="utf-8") as f:
            task_data = json.load(f)

        # Get task_id if available (try multiple sources)
        task_id = None
        if task_ids_from_data and task_idx < len(task_ids_from_data):
            task_id = task_ids_from_data[task_idx]
        elif "task_id" in task_data:
            task_id = task_data["task_id"]
        else:
            task_id = f"task_{task_idx}"

        task_ids.append(task_id)
        valid_task_indices.append(task_idx)

        # Get TVD-MI scores for this task (one per agent)
        tvd_mi_scores = np.array(task_data.get("tvd_mi_scores", []))

        if len(tvd_mi_scores) != num_agents:
            print(
                f"Warning: Task {task_idx} has {len(tvd_mi_scores)} scores but expected {num_agents}"
            )
            # Use zeros or pad/truncate as needed
            if len(tvd_mi_scores) < num_agents:
                tvd_mi_scores = np.pad(
                    tvd_mi_scores, (0, num_agents - len(tvd_mi_scores)), mode="constant"
                )
            else:
                tvd_mi_scores = tvd_mi_scores[:num_agents]

        # Fill in the column for this task
        score_matrix[:, len(valid_task_indices) - 1] = tvd_mi_scores

    # Trim score matrix to only include valid tasks
    if len(valid_task_indices) < num_examples:
        score_matrix = score_matrix[:, : len(valid_task_indices)]

    # Save the score matrix in a structured format
    zero_mask = np.isclose(score_matrix, 0)
    zero_fraction = float(np.mean(zero_mask)) if score_matrix.size else 0.0
    all_zero_agents = int(np.sum(np.all(zero_mask, axis=1))) if score_matrix.size else 0
    all_zero_items = int(np.sum(np.all(zero_mask, axis=0))) if score_matrix.size else 0

    matrix_data = {
        "score_matrix": score_matrix.tolist(),
        "agent_names": condition_keys,
        "item_ids": task_ids,
        "num_agents": num_agents,
        "num_items": len(task_ids),
        "description": "TVD-MI score matrix S where S[i,j] is the TVD-MI score for agent i on item j",
        "note": "Scores are averaged TPR-FPR over pairwise comparisons. Can be decomposed as s_ij ≈ θ_i - b_j",
        "diagnostics": {
            "zero_fraction": zero_fraction,
            "all_zero_agents": all_zero_agents,
            "all_zero_items": all_zero_items,
        },
    }

    # Also compute agent abilities (θ_i) and item difficulties (b_j) using simple row/col means
    agent_abilities = np.mean(score_matrix, axis=1)  # Row means: θ_i
    item_difficulties = -np.mean(score_matrix, axis=0)  # Negative col means: b_j

    matrix_data["agent_abilities"] = agent_abilities.tolist()
    matrix_data["item_difficulties"] = item_difficulties.tolist()

    # Save to file
    output_file = os.path.join(archive_dir, "tvd_mi_score_matrix.json")
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(matrix_data, f, indent=2)

    print(f"TVD-MI score matrix saved to {output_file}")
    print(f"  Matrix shape: {score_matrix.shape} (agents x items)")
    print(
        f"  Agent abilities (θ) range: [{np.min(agent_abilities):.4f}, {np.max(agent_abilities):.4f}]"
    )
    print(
        f"  Item difficulties (b) range: [{np.min(item_difficulties):.4f}, {np.max(item_difficulties):.4f}]"
    )
    if zero_fraction > 0.5:
        print(
            f"Warning: {zero_fraction:.1%} of score matrix entries are zero. "
            "This can indicate missing data or a broken judge pipeline."
        )

    return matrix_data


def process_agent_data_file(
    agent_file_path,
    output_dir="results",
    max_workers=5,
    num_examples=None,
    verbosity=VERBOSITY_MINIMAL,
):
    """Process examples from an agent data file using existing functions."""

    # Check how many examples are in the file
    with open(agent_file_path, "r") as f:
        data = json.load(f)
        total_examples = len(data.get("tasks", []))

    # Use specified number of examples or all if not specified
    if num_examples is None:
        actual_examples = total_examples
    else:
        actual_examples = min(num_examples, total_examples)

    print(
        f"Processing {actual_examples} out of {total_examples} examples from {agent_file_path}"
    )

    # Only process if actual_examples > 0
    if actual_examples > 0:
        # Process specified number of examples
        process_multiple_examples(
            data_path=agent_file_path,
            num_examples=actual_examples,
            conditions=None,
            output_dir=output_dir,
            max_workers=max_workers,
            verbosity=verbosity,
        )
    else:
        print("Skipping processing (0 examples requested)")

    # Check for existing results in archive directory
    archive_dir = os.path.join(output_dir, "tvd_mi_individual_examples")
    existing_results = []

    if os.path.exists(archive_dir):
        print(f"Checking archive directory {archive_dir}/")
        for i in range(total_examples):
            archive_file = os.path.join(archive_dir, f"tvd_mi_example_{i}.json")
            if os.path.exists(archive_file):
                existing_results.append(i)
                print(f"  Found: tvd_mi_example_{i}.json")

    if not existing_results:
        print("No existing results found to aggregate")
        return

    print(f"Found {len(existing_results)} existing result files")

    # Aggregate results directly from archive
    aggregate_results(
        archive_dir=archive_dir,
        num_examples=max(existing_results) + 1,  # Use highest index + 1
        conditions=None,
    )

    # Only proceed with renaming if aggregation succeeded
    aggregated_file = os.path.join(archive_dir, "tvd_mi_aggregated.json")
    if not os.path.exists(aggregated_file):
        print("Aggregation did not produce output file")
        return

    # Copy aggregated results to main output directory with proper naming
    basename = os.path.basename(agent_file_path).replace(".json", "")
    final_output = f"{output_dir}/{basename}_tvd_mi.json"

    # Remove existing output file if it exists
    if os.path.exists(final_output):
        os.remove(final_output)

    # Copy from archive to main output directory
    with open(aggregated_file, "r") as src, open(final_output, "w") as dst:
        dst.write(src.read())

    print(f"TVD-MI results saved to: {final_output}")


def main():
    # The global declaration must come first in the function
    global MODEL

    parser = argparse.ArgumentParser(
        description="Run TVD-MI analysis on agent responses"
    )
    parser.add_argument("--agent-data", help="Process agent-generated data file")
    parser.add_argument("--data", required=False, help="Path to the JSON data file")
    parser.add_argument("--output", default="results", help="Directory to save results")
    parser.add_argument(
        "--conditions",
        nargs="+",
        help="List of condition names to include or number of conditions",
    )
    parser.add_argument(
        "--examples", type=int, default=1, help="Number of examples to process"
    )
    parser.add_argument(
        "--workers", type=int, default=5, help="Maximum number of parallel workers"
    )
    parser.add_argument(
        "--single",
        type=int,
        default=-1,
        help="Process only a single example with this index",
    )
    parser.add_argument(
        "--aggregate", action="store_true", help="Aggregate results after processing"
    )
    parser.add_argument("--model", default=MODEL, help="Model to use for TVD-MI critic")
    parser.add_argument(
        "--verbosity",
        type=int,
        default=0,
        choices=[0, 1, 2],
        help="Output verbosity: 0=minimal, 1=compact (with responses), 2=full",
    )

    # Add in lean-dir to parser from CLI
    parser.add_argument(
        "--lean-dir",
        help="Directory of Lean files (e.g., no-gold-ref-judge/veribench_dataset/lean_src) to auto-build agent-data JSON from",
    )
    parser.add_argument(
        "--no-recursive",
        action="store_true",
        help="Don't recursively search subdirectories for Lean files",
    )

    args = parser.parse_args()
    # Create output directory
    os.makedirs(args.output, exist_ok=True)

    # If a Lean directory is provided, build a temporary agent-data JSON from it
    agent_data_path = args.agent_data
    if args.lean_dir:
        # Default location to put the generated agent-data JSON
        basename = os.path.basename(os.path.normpath(args.lean_dir))
        auto_agent_json = os.path.join(args.output, f"{basename}_agent_data.json")
        agent_data_path = build_agent_data_from_lean_dir(
            args.lean_dir, auto_agent_json, recursive=not args.no_recursive
        )

    # Handle agent data processing (either from --agent-data or from --lean-dir)
    if agent_data_path:
        process_agent_data_file(
            agent_file_path=agent_data_path,
            output_dir=args.output,
            max_workers=args.workers,
            num_examples=args.examples,
            verbosity=args.verbosity,
        )
        return

    """
    args = parser.parse_args()

    # Update model if specified
    if args.model:
        MODEL = args.model

    # Create output directory
    os.makedirs(args.output, exist_ok=True)

    # Handle agent data processing
    if args.agent_data:
        process_agent_data_file(
            agent_file_path=args.agent_data,
            output_dir=args.output,
            max_workers=args.workers,
            num_examples=args.examples,  # Pass the examples argument
            verbosity=args.verbosity,
        )
        return

    # Process conditions argument
    conditions = args.conditions
    if conditions and len(conditions) == 1 and conditions[0].isdigit():
        # If a single numeric value is provided, convert to int
        conditions = int(conditions[0])

    # Aggregate results if requested
    if args.aggregate:
        archive_dir = os.path.join(args.output, "tvd_mi_individual_examples")
        aggregate_results(
            archive_dir=archive_dir, num_examples=args.examples, conditions=conditions
        )
    """


if __name__ == "__main__":
    main()
