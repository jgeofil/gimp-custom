---
name: gemini-api-dev
description: Expert guidance for developing with the Google Gen AI (Gemini) API, focusing on the Interactions API, multimodal capabilities, and frontier agents like Live API, Deep Research, and Computer Use.
version: 1.1.0
---

# Gemini API Development Skill

## Capability

Provides comprehensive technical guidance for integrating Gemini models into applications. It covers model selection (Gemini 3.1, 2.5, Gemma 4), API primitives (Interactions vs. Live API vs. GenerateContent), multimodal processing (Image, Video, Audio, PDF), and advanced orchestration features like Function Calling, Structured Outputs, Thinking, and Context Caching.

## Triggers

- User asks about Gemini model versions (e.g., "Gemini 3.1 vs 2.5", "Gemma 4 specs").
- Implementation tasks using google-genai (Python) or @google/genai (JS).
- Requests to use the Interactions API for stateful/agentic workflows.
- Questions about **Deep Research**, **Computer Use**, or **Veo 3.1 Video Generation**.
- Implementation of **Live API (BidiGenerateContent)** for real-time dialogue.
- Enabling **Thinking** capabilities with a dedicated reasoning budget.
- Implementation of Function Calling, Structured Outputs, or Grounding.
- Cost optimization via Context Caching, Batch API, or Flex/Priority tiers.

## Instructions

1. **Identify API Primitive**:
    - **Interactions API** (interactions.md): New standard for agentic/stateful projects.
    - **Live API** (api-reference/live-api.md): Use for low-latency, bi-directional audio/video streaming.
    - **GenerateContent**: Use for legacy support or simple stateless tasks.
2. **Select Model**: Consult allmodels.md.
    - **Reasoning**: Gemini 3.1 Pro (complex) or Flash (balanced). Use `thinking: True` for explicit chain-of-thought.
    - **Speed/Cost**: Gemini 3.1 Flash-Lite or Gemma 4.
    - **Specialized**: Nano Banana Pro (4K Image), Veo 3.1 (Cinematic Video), Computer Use Preview (UI Automation).
3. **Handle Modalities**:
    - **PDF**: Refer to capabilities/documents.md. Each page is 258 tokens.
    - **Video**: Use capabilities/video-understanding.md. Standard sampling is 1 FPS.
    - **Audio**: Use Gemini 3.1 Flash Live or TTS for native audio reasoning and generation.
4. **Manage State**:
    - In Interactions, use `previous_interaction_id` to continue threads (implicit caching).
    - For manual history, circulate Thought Signatures (capabilities/thought-signatures.md) to maintain reasoning context.
5. **Tool Orchestration**: Use tools/tools-and-functions.md to combine built-in tools (Search, Maps) with custom Function Calling.
6. **Optimize**: Use batch/flex.md for 50% cost savings on non-urgent tasks and api-reference/caching.md to reuse tokens for long contexts.

## Tools / Commands

N/A: This is a documentation-driven context skill.

## Examples

User: "How do I implement a real-time voice assistant with Gemini?"
Action:

1. Consult `api-reference/live-api.md` for the WebSocket protocol.
2. Recommend `gemini-3.1-flash-live-preview` for low-latency native audio.

User: "How do I use the new Thinking capability in Python?"
Action:

1. Refer to `capabilities/thinking.md`.
2. Implementation: `client.models.generate_content(model='gemini-3-flash-preview', contents='Solve this...', config={'thinking': True, 'include_thoughts': True})`.

User: "What's the best way to automate a browser task using Gemini?"
Action:

1. Refer to `agents/agents.md` for Computer Use.
2. Recommend `gemini-2.5-computer-use-preview` and the `computer` tool suite.

User: "How do I get the model to return a valid JSON object of flight details?"
Action:

1. Use `capabilities/structured-output.md`.
2. Define a Pydantic BaseModel (Python) or Zod schema (JS).
3. Pass as `response_format` in the configuration.
