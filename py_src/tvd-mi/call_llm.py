import os
import logging
from dotenv import load_dotenv
from datetime import datetime

"""
Ensure a default module logger is always available so that internal logging
never fails when a caller forgets to pass a custom logger.
"""
logger = logging.getLogger("lean_trace")


def setup_logging(log_dir=None):
    """
    Setup logging configuration.

    Args:
        log_dir (str, optional): Directory to store log files. If None, uses 'logs' directory.
    """
    # Use default log directory if none provided
    if log_dir is None:
        log_dir = "logs"

    # Create logs directory if it doesn't exist
    os.makedirs(log_dir, exist_ok=True)

    # Generate log filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = os.path.join(log_dir, f"lean_trace_{timestamp}.log")

    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[logging.FileHandler(log_file), logging.StreamHandler()],
    )

    # Create logger
    logger = logging.getLogger("lean_trace")
    logger.info(f"Logging initialized. Log file: {log_file}")
    return logger


# Load environment variables from .env file
env_file_path = os.path.join(os.path.dirname(__file__), ".env")
# Respect variables already exported by the caller; only fill missing ones from .env
load_dotenv(dotenv_path=env_file_path, override=False)

os.environ["TRACE_CUSTOMLLM_MODEL"] = os.getenv("TRACE_CUSTOMLLM_MODEL")
os.environ["TRACE_CUSTOMLLM_URL"] = os.getenv("TRACE_CUSTOMLLM_URL")
os.environ["TRACE_CUSTOMLLM_API_KEY"] = os.getenv("TRACE_CUSTOMLLM_API_KEY")
os.environ["TRACE_DEFAULT_LLM_BACKEND"] = os.getenv(
    "TRACE_DEFAULT_LLM_BACKEND", "CustomLLM"
)

import openai
import opto.trace as trace
from opto.trace.nodes import node, GRAPH, ParameterNode
from datasets import load_dataset
from opto.trace import model, bundle
import opto.trace.operators as trace_ops
import numpy as np

from fastchat.model import get_conversation_template
import time

from veribench.agent.trace_agents.trace_lean.lean_interpretor import lean_interpreter

from veribench.agent.trace_agents.trace_lean.theorem_writing_llm_judge import (
    theorem_quality_scorer,
)
from opto.optimizers import OptoPrime

VERBOSE = False

MODEL_NAME = os.environ["TRACE_CUSTOMLLM_MODEL"]


# this is a custom trace operator for calling the LLM
@bundle(trainable=False, allow_external_dependencies=True)
def call_llm(
    message, model_name=MODEL_NAME, timeout=300, max_retries=3, retry_delay=1.0
):
    """
    Call the LLM with a user message and optional system message.
    Includes timeout handling and retry logic for robustness.

    Args:
        message (str): The user message to send to the LLM
        model_name (str): The model to use, defaults to the global model variable
        timeout (int): Timeout in seconds for the API call (default: 300)
        max_retries (int): Maximum number of retry attempts (default: 3)
        retry_delay (float): Initial delay between retries in seconds (default: 1.0)

    Returns:
        str: The LLM's response
    """
    import time
    from openai import APITimeoutError, APIError
    import httpx

    # Initialize the conversation template
    conv = get_conversation_template(model_name)

    # Add the user message
    conv.append_message(conv.roles[0], message)

    # Convert to OpenAI API format
    messages = conv.to_openai_api_messages()

    if VERBOSE:
        logger.info("\n=== API Call Details ===")
        logger.info(f"Model: {model_name}")
        logger.info("Messages:")
        for msg in messages:
            logger.info(f"{msg['role']}: {msg['content']}")
        logger.info("=====================\n")

    # Make the API call with retry logic
    client = openai.OpenAI(
        base_url=os.environ["TRACE_CUSTOMLLM_URL"],
        api_key=os.environ["TRACE_CUSTOMLLM_API_KEY"],
        timeout=timeout,  # Set timeout on the client
    )

    last_exception = None
    for attempt in range(max_retries + 1):
        try:
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

            return response_text

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
