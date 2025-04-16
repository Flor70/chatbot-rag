# OpenAI Agents SDK Summary

This document provides a synthesized overview of the OpenAI Agents SDK based on its documentation.

## Introduction and Core Concepts

The OpenAI Agents SDK is a lightweight, Python-first library designed for building agentic AI applications with minimal abstractions. It aims to be powerful yet easy to learn, focusing on a few core primitives:

*   **Agents:** LLMs configured with instructions, tools, and optionally specific models or configurations. They form the fundamental building block.
*   **Handoffs:** Mechanisms allowing agents to delegate tasks to other, potentially specialized, agents. This enables modular agent orchestration.
*   **Guardrails:** Functions that validate inputs or outputs of agents, allowing for checks like relevance screening or PII filtering before or after an agent processes information.

Key design principles include providing enough features to be useful while maintaining a shallow learning curve and allowing customization while working well out-of-the-box.

**Main Features:**

*   **Built-in Agent Loop:** Handles tool calls, result processing, and looping until task completion.
*   **Python-first Orchestration:** Leverages native Python features for agent chaining and logic.
*   **Handoffs:** Powerful delegation between agents.
*   **Guardrails:** Parallel validation checks.
*   **Function Tools:** Easily turn Python functions into tools with automatic schema generation and validation (using Pydantic).
*   **Tracing:** Integrated visualization, debugging, monitoring, and support for OpenAI's evaluation and fine-tuning tools.

## Installation and Setup

1.  **Create Project & Environment:**
    ```bash
    mkdir my_project
    cd my_project
    python -m venv .venv
    source .venv/bin/activate
    ```
2.  **Install SDK:**
    ```bash
    pip install openai-agents
    ```
3.  **Set API Key:**
    ```bash
    export OPENAI_API_KEY=sk-...
    ```

## Basic Usage: Creating Agents

Agents are instantiated using the `agents.Agent` class.

```python
from agents import Agent, Runner

# Simple agent
agent = Agent(name="Assistant", instructions="You are a helpful assistant")

# Run the agent synchronously
result = Runner.run_sync(agent, "Write a haiku about recursion in programming.")
print(result.final_output)
# Code within the code,
# Functions calling themselves,
# Infinite loop's dance.

# Agent with tools and specific model
from agents import ModelSettings, function_tool

@function_tool
def get_weather(city: str) -> str:
    """Fetches the weather for a given city."""
    # Replace with actual API call
    return f"The weather in {city} is sunny"

haiku_agent = Agent(
    name="Haiku agent",
    instructions="Always respond in haiku form. Use tools if needed.",
    model="o3-mini", # Example model
    tools=[get_weather],
    # model_settings=ModelSettings(temperature=0.7) # Optional settings
)
```

**Key Agent Configuration:**

*   `name`: Identifier for the agent.
*   `instructions`: The system prompt or core instructions for the agent's behavior. Can be a string or a function (sync/async) returning a string for dynamic instructions based on context.
*   `model`: The specific LLM to use (e.g., "o3-mini", "gpt-4o").
*   `model_settings`: (`agents.ModelSettings`) Fine-tuning parameters like `temperature`, `top_p`, `tool_choice`.
*   `tools`: A list of tools the agent can use (see Tools section).
*   `handoffs`: A list of other `Agent` instances the agent can delegate to.
*   `handoff_description`: A description used by other agents to decide whether to hand off to this one.
*   `output_type`: Specifies a desired structured output format (e.g., a Pydantic model, dataclass, list). Tells the model to use structured outputs.
*   `context`: Agents can be generic over a context type (`Agent[MyContext]`), allowing dependency injection via the `Runner.run(..., context=...)` call.
*   `hooks`: (`agents.AgentHooks`) Allows observing the agent's lifecycle events.
*   `input_guardrails` / `output_guardrails`: Lists of guardrail functions to apply.
*   `mcp_servers`: List of Model Context Protocol servers providing tools.
*   `clone()`: Method to duplicate an agent, optionally overriding properties.

**Forcing Tool Use:**

Use `ModelSettings.tool_choice` to control tool usage:
*   `"auto"` (default): LLM decides.
*   `"required"`: LLM must use *a* tool.
*   `"none"`: LLM must *not* use a tool.
*   `"tool_name"`: LLM must use the specified tool.
*   `agent.reset_tool_choice` (default True): Resets `tool_choice` to `"auto"` after a tool call to prevent loops.
*   `agent.tool_use_behavior="stop_on_first_tool"`: Stop execution after the first tool call and return its output directly.

## Running Agents

The `agents.Runner` class is used to execute agents.

*   `Runner.run(agent, input, ...)`: Asynchronous execution, returns `RunResult`.
*   `Runner.run_sync(agent, input, ...)`: Synchronous wrapper around `run()`, returns `RunResult`.
*   `Runner.run_streamed(agent, input, ...)`: Asynchronous execution, returns `RunResultStreaming` for real-time event streaming.

The `input` can be a string (treated as a user message) or a list of OpenAI message objects.

**Agent Loop:**

The `Runner` executes a loop:
1.  Call the LLM with the current agent and input.
2.  Process the LLM output:
    *   **Final Output:** If the LLM provides a final text/structured output without tool calls, the loop ends, and the result is returned.
    *   **Handoff:** If the LLM decides to hand off, update the current agent and input, and continue the loop.
    *   **Tool Call:** If the LLM calls tools, execute them, append results to the input, and continue the loop.
3.  Raise `MaxTurnsExceeded` if `max_turns` (configurable) is reached.

**Run Configuration (`run_config`):**

Global settings applied to a run:
*   `model`, `model_provider`, `model_settings`: Override agent-specific model configurations.
*   `input_guardrails`, `output_guardrails`: Global guardrails.
*   `handoff_input_filter`: Global filter applied to handoff inputs.
*   `tracing_disabled`, `trace_include_sensitive_data`: Control tracing behavior.
*   `workflow_name`, `trace_id`, `group_id`, `trace_metadata`: Configure tracing identifiers and metadata.

**Conversations (Chat Threads):**

Each `Runner.run` call represents a single turn. To maintain conversation history:
1.  Run the first turn: `result = await Runner.run(agent, "User question")`.
2.  Prepare input for the next turn using the previous result: `next_input = result.to_input_list() + [{"role": "user", "content": "Follow-up question"}]`.
3.  Run the next turn: `next_result = await Runner.run(agent, next_input)`.
Use `trace(workflow_name="...", group_id=thread_id)` to group turns within a conversation trace.

**Exceptions:**

Common exceptions (inheriting from `agents.AgentsException`):
*   `MaxTurnsExceeded`: Run exceeded `max_turns`.
*   `ModelBehaviorError`: Invalid LLM output (bad JSON, non-existent tool).
*   `UserError`: Incorrect SDK usage.
*   `InputGuardrailTripwireTriggered`, `OutputGuardrailTripwireTriggered`: Guardrail condition met.

## Understanding Results

`Runner.run*` methods return `RunResult` or `RunResultStreaming` (both inherit from `RunResultBase`).

**Key Properties:**

*   `final_output`: The final output from the *last* agent in the run (can be `str` or the agent's `output_type`). Type is `Any` due to potential handoffs.
*   `last_agent`: The `Agent` instance that produced the final output. Useful for resuming conversations.
*   `new_items`: A list of `RunItem` objects generated during the run (e.g., `MessageOutputItem`, `ToolCallItem`, `HandoffCallItem`, `HandoffOutputItem`).
*   `to_input_list()`: Method to get a list of all input and generated items, suitable as input for the next turn.
*   `input_guardrail_results`, `output_guardrail_results`: Results from executed guardrails.
*   `raw_responses`: List of raw `ModelResponse` objects from the LLM.
*   `input`: The original input provided to the `run` method.

## Streaming

Use `Runner.run_streamed()` to get a `RunResultStreaming` object. Call `result.stream_events()` to get an async iterator yielding `StreamEvent` objects.

**Event Types:**

*   `RawResponsesStreamEvent`: Low-level events directly from the LLM stream (e.g., `response.output_text.delta`). Useful for token-by-token output streaming.
    ```python
    async for event in result.stream_events():
        if event.type == "raw_response_event" and isinstance(event.data, ResponseTextDeltaEvent):
            print(event.data.delta, end="", flush=True)
    ```
*   `RunItemStreamEvent`: Higher-level events indicating a complete item was generated (e.g., a full message, a tool call). Useful for progress updates like "Tool X called", "Message generated".
*   `AgentUpdatedStreamEvent`: Fired when a handoff occurs and the active agent changes.

## Tools

Tools enable agents to interact with the outside world or perform specific actions.

**1. Hosted Tools (OpenAI):**

Available when using `OpenAIResponsesModel`.
*   `WebSearchTool()`: Performs web searches.
*   `FileSearchTool(vector_store_ids=[...], max_num_results=...)`: Retrieves information from specified OpenAI Vector Stores.
*   `ComputerTool()`: Automates computer use tasks (details likely in MCP section or API reference).

```python
from agents import Agent, WebSearchTool, FileSearchTool

agent = Agent(
    name="Assistant",
    tools=[
        WebSearchTool(),
        FileSearchTool(vector_store_ids=["vs_abc123"]),
    ],
)
```

**2. Function Tools:**

Turn any Python function (sync or async) into a tool using the `@function_tool` decorator or `FunctionTool` class.

*   **Automatic Schema:** Uses type hints (`inspect`) and docstrings (`griffe` for google/sphinx/numpy formats) to generate the tool name, description, argument schema, and argument descriptions.
*   **Context Access:** Functions can optionally accept `RunContextWrapper[YourContextType]` as the first argument.
*   **Overrides:** The decorator allows overriding `name_override`, `description_override`, `docstring_parser`, etc.

```python
from agents import Agent, function_tool, RunContextWrapper
from typing import TypedDict

class Location(TypedDict):
    lat: float
    long: float

@function_tool
async def fetch_weather(location: Location) -> str:
    """Fetch the weather for a given location.

    Args:
        location: The location (lat/long) to fetch weather for.
    """
    # ... implementation ...
    return "sunny"

@function_tool(name_override="read_specific_file")
def read_file(ctx: RunContextWrapper[Any], path: str) -> str:
     """Reads a file."""
     # ... implementation ...
     return "<file contents>"

agent = Agent(tools=[fetch_weather, read_file])
```

*   **Manual Creation:** Use `FunctionTool(name=..., description=..., params_json_schema=..., on_invoke_tool=async_func)` for full manual control, where `on_invoke_tool` receives context and JSON string arguments.

**3. Agents as Tools:**

Use an agent itself as a tool for another agent, enabling orchestration without full handoffs.

```python
from agents import Agent

translator_agent = Agent(name="Translator", instructions="Translate text to Spanish.")
summarizer_agent = Agent(name="Summarizer", instructions="Summarize the provided text.")

orchestrator = Agent(
    name="Orchestrator",
    instructions="Translate the user input, then summarize the translation.",
    tools=[
        translator_agent.as_tool(
            tool_name="translate_to_spanish",
            tool_description="Translate input text to Spanish."
        ),
        summarizer_agent.as_tool(
             tool_name="summarize_text",
             tool_description="Summarize the input text."
        )
    ]
)
```

## Model Context Protocol (MCP)

MCP is an open protocol standardizing how applications provide context (like tools and data sources) to LLMs. The SDK supports connecting to MCP servers.

**Server Types:**

*   `MCPServerStdio`: Runs a local subprocess (e.g., filesystem access).
*   `MCPServerSse`: Connects to a remote HTTP SSE server via URL.

**Usage:**

1.  Instantiate the server connection (e.g., `MCPServerStdio`).
2.  Add the server instance(s) to the agent's `mcp_servers` list.
3.  The SDK automatically calls `list_tools()` on the server when the agent runs and `call_tool()` when the LLM invokes an MCP tool.

```python
from agents import Agent, MCPServerStdio

async with MCPServerStdio(params={"command": "npx", ...}) as fs_server:
    agent = Agent(
        name="MCP Agent",
        instructions="Use filesystem tools.",
        mcp_servers=[fs_server]
    )
    # ... run agent ...
```

**Caching:**

*   Pass `cache_tools_list=True` to the server constructor to cache the `list_tools()` response (use if the tool list is static).
*   Call `server.invalidate_tools_cache()` to clear the cache if needed.

Tracing automatically captures MCP `list_tools` and `call_tool` operations.

## Examples Overview

The SDK documentation points to various examples in the repository, categorized into:

*   `agent_patterns`: Demonstrates common patterns (deterministic workflows, agents as tools, parallel execution).
*   `basic`: Showcases core features (dynamic prompts, streaming, lifecycle events).
*   `tool_examples`: Focuses on implementing hosted tools (web search, file search).
*   `model_providers`: Using non-OpenAI models.
*   `handoffs`: Practical handoff implementations.
*   `mcp`: Building agents with MCP.
*   `customer_service`, `research_bot`: More complete application examples.
*   `voice`: Examples using TTS/STT models.

---

## Handoffs

Handoffs enable agents to delegate tasks to other specialized agents. They are presented to the LLM as special tools (e.g., `transfer_to_<agent_name>`).

**Creating Handoffs:**

*   Add `Agent` instances directly to the `handoffs` list of another agent.
*   Use the `agents.handoff()` function for more customization:
    ```python
    from agents import Agent, handoff, RunContextWrapper

    billing_agent = Agent(name="Billing agent")
    refund_agent = Agent(name="Refund agent")

    def on_billing_handoff(ctx: RunContextWrapper[None]):
        print("Handoff to billing initiated")

    # Simple handoff by direct agent instance
    triage_agent = Agent(
        name="Triage agent",
        handoffs=[
            billing_agent, # Direct agent instance
            handoff( # Customized handoff
                agent=refund_agent,
                tool_name_override="request_refund_processing",
                tool_description_override="Delegate to the refund specialist.",
                on_handoff=on_billing_handoff
            )
        ]
    )
    ```

**Customization via `handoff()`:**

*   `agent`: The target agent.
*   `tool_name_override`: Custom name for the handoff tool.
*   `tool_description_override`: Custom description for the handoff tool.
*   `on_handoff`: (Sync/Async) Callback function executed when the handoff is invoked. Receives context and optional `input_data`.
*   `input_type`: (Optional) A Pydantic model or type defining expected input data from the LLM during handoff (e.g., reason for escalation). The `on_handoff` callback will receive this data.
*   `input_filter`: (Sync/Async) Function (`HandoffInputData -> HandoffInputData`) to modify the conversation history passed to the target agent. Common filters are in `agents.extensions.handoff_filters` (e.g., `remove_all_tools`).

**Recommended Prompts:**

*   Include handoff instructions in agent prompts for better LLM understanding. Use `agents.extensions.handoff_prompt.RECOMMENDED_PROMPT_PREFIX` or `agents.extensions.handoff_prompt.prompt_with_handoff_instructions`.

## Tracing

The SDK features built-in tracing to record events (LLM calls, tools, handoffs, guardrails, custom events) for debugging, visualization, and monitoring via the OpenAI Traces dashboard.

*   **Enabled by default.**
*   **Disabled via:**
    *   `OPENAI_AGENTS_DISABLE_TRACING=1` environment variable (global).
    *   `RunConfig(tracing_disabled=True)` (per run).
*   Unavailable for users under Zero Data Retention (ZDR) policies.

**Core Concepts:**

*   **Trace:** Represents a single end-to-end "workflow" operation (e.g., a user request). Composed of Spans. Has `workflow_name`, `trace_id`, optional `group_id` (for linking traces, like conversation turns), `metadata`.
*   **Span:** Represents an operation with a start/end time within a trace (e.g., agent run, tool call). Has timestamps, `trace_id`, optional `parent_id`, and `span_data` (specific info like `AgentSpanData`, `GenerationSpanData`).

**Default Tracing:**

The `Runner` automatically wraps runs in a `trace()` (default name "Agent trace", configurable via `RunConfig`). Key operations are automatically wrapped in specific spans:
*   Agent runs: `agent_span()`
*   LLM generations: `generation_span()`
*   Function tools: `function_span()`
*   Guardrails: `guardrail_span()`
*   Handoffs: `handoff_span()`
*   STT/TTS (Voice): `transcription_span()`, `speech_span()`, `speech_group_span()`

**Manual Tracing:**

*   Wrap multiple `Runner.run` calls or custom logic within a `with trace("My Workflow", group_id=...):` block to create a single, higher-level trace.
*   Create custom spans using `custom_span()`. Spans are automatically nested under the current trace/span using Python `contextvars`.

**Sensitive Data:**

*   Generation and function spans capture inputs/outputs by default. Disable via `RunConfig(trace_include_sensitive_data=False)`.
*   Audio spans capture base64 audio data. Disable via `VoicePipelineConfig(trace_include_sensitive_audio_data=False)`.

**Custom Trace Processors:**

*   By default, traces go to OpenAI via `BackendSpanExporter`.
*   `add_trace_processor()`: Add custom processors to send data to *additional* destinations (e.g., LangSmith, MLflow, W&B) alongside OpenAI.
*   `set_trace_processors()`: *Replace* the default processors entirely.

## Models

The SDK supports OpenAI models out-of-the-box and allows integrating other LLM providers.

**OpenAI Models:**

*   `OpenAIResponsesModel` (Recommended): Uses the newer OpenAI Responses API.
*   `OpenAIChatCompletionsModel`: Uses the standard Chat Completions API.
*   It's recommended to use a consistent model *shape* (Responses or Chat Completions) within a single workflow due to differing features/tool support.

**Configuring Models per Agent:**

Specify the model for an `Agent` using:
1.  The model name string (e.g., `"gpt-4o"`, `"o3-mini"`). The SDK resolves this using the default `ModelProvider`.
2.  A specific `Model` instance (e.g., `OpenAIChatCompletionsModel(model="gpt-4o", ...)`).
3.  Use `Agent(..., model_settings=ModelSettings(temperature=0.5, ...))` to fine-tune parameters.

**Using Other LLM Providers:**

Requires adapting to potentially different API structures (often Chat Completions).
1.  **Global Client:** `set_default_openai_client(AsyncOpenAI(base_url=..., api_key=...))` for OpenAI-compatible APIs.
2.  **Run-Level Provider:** `Runner.run(..., run_config=RunConfig(model_provider=MyCustomProvider()))`.
3.  **Agent-Level Model:** `Agent(..., model=MyCustomModelImplementation(...))`.

**Common Issues with Other Providers:**

*   **Tracing Errors (401):** Tracing uploads require an OpenAI key. Solutions:
    *   Disable tracing: `set_tracing_disabled(True)`.
    *   Set a specific OpenAI key *only* for tracing: `set_tracing_export_api_key("sk-...")`.
    *   Use a non-OpenAI trace processor.
*   **Responses API Errors (404):** Most providers don't support the Responses API yet. Solutions:
    *   Set the default API globally: `set_default_openai_api("chat_completions")`.
    *   Use `OpenAIChatCompletionsModel` explicitly for agents.
*   **Structured Output Errors (400):** Some providers lack full support for JSON schema specification (`response_format`). Prefer providers with robust JSON mode support.

## SDK Configuration

Global SDK settings can be adjusted.

**API Keys and Clients:**

*   **Default Key:** Reads `OPENAI_API_KEY` environment variable upon import. Can be set programmatically *before* use via `set_default_openai_key("sk-...")`.
*   **Default Client:** Uses a default `AsyncOpenAI` client. Can be replaced globally with a custom instance (e.g., with a different `base_url`) via `set_default_openai_client(custom_client)`.
*   **Default API:** Defaults to OpenAI Responses API. Can be changed globally to Chat Completions via `set_default_openai_api("chat_completions")`.

**Tracing Configuration:**

*   **Tracing API Key:** Uses the default OpenAI key. Can be set specifically via `set_tracing_export_api_key("sk-...")`.
*   **Disable Tracing:** Globally via `set_tracing_disabled(True)`.

**Debug Logging:**

*   Uses standard Python `logging` with loggers `openai.agents` and `openai.agents.tracing`.
*   Warnings/errors go to `stdout` by default.
*   Enable verbose logging: `enable_verbose_stdout_logging()`.
*   Customize using standard `logging` handlers/levels (e.g., `logging.getLogger("openai.agents").setLevel(logging.DEBUG)`).
*   **Sensitive Data in Logs:** Prevent logging LLM or tool data using environment variables:
    *   `export OPENAI_AGENTS_DONT_LOG_MODEL_DATA=1`
    *   `export OPENAI_AGENTS_DONT_LOG_TOOL_DATA=1`

## Agent Visualization

Generate Graphviz diagrams of agent structures and interactions.

**Installation:**

```bash
pip install "openai-agents[viz]"
```

**Usage:**

Use `agents.extensions.visualization.draw_graph(agent_instance, ...)`:

```python
from agents import Agent, function_tool
from agents.extensions.visualization import draw_graph

# ... (define agents spanish_agent, english_agent, triage_agent with handoffs/tools) ...

graph = draw_graph(triage_agent) # Generates graph object

# Display inline (e.g., in Jupyter)
# graph

# Show in separate window
# graph.view()

# Save to file
# draw_graph(triage_agent, filename="triage_flow.png", format="png")
```

**Graph Elements:**

*   `__start__`: Entry point.
*   Yellow Rectangles: Agents.
*   Green Ellipses: Tools.
*   Solid Arrows: Handoffs.
*   Dotted Arrows: Tool usage links (Agent -> Tool).
*   `__end__`: Potential termination points.

---
*Further details on Context, Guardrails, Multi-Agent patterns, Voice, and specific API classes will be added as more documents are processed.*

## Context Management

The SDK has two distinct concepts of "context":

1. **Local Context (for Code):** Data and dependencies available to tool functions, callbacks, and lifecycle hooks.
2. **LLM Context:** Data the LLM uses when generating responses (conversation history, instructions, etc.).

### Local Context

`RunContextWrapper[T]` provides a way to pass application data and dependencies throughout an agent run.

**Implementation:**

1. Create any Python object as context (typically a dataclass or Pydantic model).
2. Pass it to `Runner.run(..., context=my_context)`.
3. Access it in tools, hooks, guardrails, etc. via `wrapper.context`.

```python
from dataclasses import dataclass
from agents import Agent, RunContextWrapper, Runner, function_tool

@dataclass
class UserInfo:
    name: str
    uid: int
    # Can include dependencies, methods, or any custom data

@function_tool
async def get_user_info(ctx: RunContextWrapper[UserInfo]) -> str:
    # Access information from context
    return f"User {ctx.context.name} (ID: {ctx.context.uid})"

agent = Agent[UserInfo](  # Type annotation ensures correct context usage
    name="User Info Agent",
    tools=[get_user_info],
)

# Create and pass the context object
user_data = UserInfo(name="Alice", uid=123)
result = await Runner.run(agent, "Tell me about the current user", context=user_data)
```

**Important:**
- The context is *not* sent to the LLM itself; it's purely for code execution.
- Every component in a given run must use the same context type.
- Context enables dependency injection (loggers, database connections, API clients, etc.).

### Agent/LLM Context

Data available to the LLM can be provided in several ways:

1. **Agent Instructions:** Add information in the system prompt/instructions, either statically or via a dynamic function.
2. **Input Messages:** Add data as part of the input to `Runner.run()`.
3. **Tools:** Expose tools that fetch relevant information dynamically when the LLM needs it.
4. **Retrieval:** Use retrieval tools (e.g., `FileSearchTool`) or web search (`WebSearchTool`) to ground responses in relevant information.

## Guardrails

Guardrails allow validation checks on input or output, enabling early termination if certain conditions are met. They run in parallel to agents, making them ideal for safety checks, validation, and filtering unwanted content.

**Types:**

1. **Input Guardrails:** Run before the agent processes user input.
2. **Output Guardrails:** Run after the agent produces its output.

**Benefits:**

- Allow early termination for unwanted inputs (e.g., homework, abusive language, off-topic questions).
- Validate model outputs against criteria before returning them to users.
- Can use cheaper/faster models for screening, saving costs on expensive models.

**Implementation:**

Use the `@input_guardrail` or `@output_guardrail` decorators on functions that:
1. Receive the `context`, `agent`, and input/output.
2. Return a `GuardrailFunctionOutput` with information and a `tripwire_triggered` flag.

```python
from pydantic import BaseModel
from agents import (
    Agent, GuardrailFunctionOutput, InputGuardrailTripwireTriggered,
    Runner, RunContextWrapper, input_guardrail
)

# Define structured output for guardrail result
class HomeworkDetectionOutput(BaseModel):
    is_homework: bool
    reasoning: str

# Agent to check for homework questions
guardrail_agent = Agent(
    name="Homework Detector",
    instructions="Determine if this is a homework question.",
    output_type=HomeworkDetectionOutput,
    model="gpt-3.5-turbo",  # Use cheaper model for screening
)

@input_guardrail
async def homework_guardrail(
    ctx: RunContextWrapper[None],
    agent: Agent,
    input_data: str | list
) -> GuardrailFunctionOutput:
    # Run the checking agent
    result = await Runner.run(guardrail_agent, input_data, context=ctx.context)
    detection_output = result.final_output_as(HomeworkDetectionOutput)
    
    # Return result with tripwire flag
    return GuardrailFunctionOutput(
        output_info=detection_output,  # Additional info (logging, etc.)
        tripwire_triggered=detection_output.is_homework  # True means reject
    )

# Attach guardrail to main agent
main_agent = Agent(
    name="Tutor",
    instructions="Help with general questions about science concepts.",
    input_guardrails=[homework_guardrail],
)

# Using the agent with guardrail
try:
    result = await Runner.run(main_agent, "Can you solve 2x + 5 = 15 for me?")
    # This won't execute if guardrail triggers
    print(result.final_output)
except InputGuardrailTripwireTriggered as e:
    print("Sorry, I can't help with homework questions.")
    # Access guardrail output: e.guardrail_result.output_info
```

**Execution Process:**

1. Input guardrails receive the same input as the agent.
2. Guardrail function produces a `GuardrailFunctionOutput` with results and a tripwire flag.
3. If `tripwire_triggered` is `True`, an `InputGuardrailTripwireTriggered` or `OutputGuardrailTripwireTriggered` exception is raised.
4. Catch the exception to provide a custom response.

**Note:** Input guardrails are only run on the first agent in a chain; output guardrails only on the last.

## Multi-Agent Orchestration

The SDK supports different patterns for coordinating multiple agents, from autonomous LLM-driven flows to deterministic code-controlled orchestration.

### LLM-Driven Orchestration

LLMs can autonomously decide what steps to take using tools and handoffs. This approach leverages the intelligence of the model for planning and decision-making.

**Best Practices:**

1. **Clear Instructions:** Provide detailed guidance on tool usage, constraints, and process expectations.
2. **Specialized Agents:** Create focused agents for specific tasks rather than expecting one agent to do everything.
3. **Monitoring & Iteration:** Analyze traces to identify failure points and improve prompts.
4. **Self-Critique:** Allow the agent to reflect on and improve its own outputs.
5. **Evaluation:** Build evaluation flows to measure and improve performance.

**Example Pattern: Task Triage**

```python
from agents import Agent, Runner

# Specialist agents
code_agent = Agent(
    name="Code Specialist",
    handoff_description="For generating or debugging code",
    instructions="You specialize in writing clean, efficient code.",
)

math_agent = Agent(
    name="Math Specialist",
    handoff_description="For mathematical problems and calculations",
    instructions="You provide detailed mathematical explanations.",
)

# Main triage agent 
triage_agent = Agent(
    name="Triage Agent",
    instructions="""
    You determine which specialist to use based on the user's question.
    For coding questions, hand off to the Code Specialist.
    For math questions, hand off to the Math Specialist.
    For general questions, answer directly.
    """,
    handoffs=[code_agent, math_agent],
)
```

### Code-Driven Orchestration

Deterministic orchestration via code offers more predictability and control over the agent workflow.

**Common Patterns:**

1. **Structured Outputs:** Use `output_type` to get well-structured data from agents for conditional logic.
2. **Sequential Chaining:** Transform the output of one agent into the input of another.
3. **Iterative Refinement:** Run output through an evaluator agent and loop until quality criteria are met.
4. **Parallel Processing:** Use `asyncio.gather()` to run independent agents simultaneously.

**Example Pattern: Iterative Refinement**

```python
from agents import Agent, Runner
from pydantic import BaseModel

class EssayOutput(BaseModel):
    essay: str

class EvalOutput(BaseModel):
    score: int
    feedback: str
    passes: bool  # Whether quality threshold is met

# Writer agent
writer_agent = Agent(
    name="Essay Writer",
    instructions="Write an essay on the given topic.",
    output_type=EssayOutput,
)

# Evaluator agent
evaluator_agent = Agent(
    name="Essay Evaluator",
    instructions="Evaluate the essay and provide feedback.",
    output_type=EvalOutput,
)

async def iterative_writing(topic, max_iterations=3):
    essay = None
    
    for i in range(max_iterations):
        # Generate or improve essay
        prompt = topic if essay is None else f"""
        Topic: {topic}
        Previous essay: {essay}
        Feedback: {feedback}
        Please improve the essay based on the feedback.
        """
        result = await Runner.run(writer_agent, prompt)
        essay = result.final_output_as(EssayOutput).essay
        
        # Evaluate essay
        eval_result = await Runner.run(evaluator_agent, f"Evaluate: {essay}")
        evaluation = eval_result.final_output_as(EvalOutput)
        
        if evaluation.passes:
            return essay, evaluation
            
        feedback = evaluation.feedback
    
    # Return final version after max iterations
    return essay, evaluation
```

The SDK includes examples of these patterns in the `examples/agent_patterns` directory.

---
