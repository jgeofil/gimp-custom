# Gemini thinking

> [!NOTE]
> **Note** : This version of the page covers the new [Interactions API](https://ai.google.dev/gemini-api/docs/interactions), which is currently in Beta.
> For stable production deployments, we recommend you continue to use the `generateContent` API. You can use the toggle on this page to switch between the versions.

The [Gemini 3 and 2.5 series models](https://ai.google.dev/gemini-api/docs/models) use an internal
"thinking process" that significantly improves their reasoning and multi-step
planning abilities, making them highly effective for complex tasks such as
coding, advanced mathematics, and data analysis.

This guide shows you how to work with Gemini's thinking capabilities using the
Gemini API.

## Generate content with thinking

Initiating a request with a thinking model is similar to any other content
generation request. The key difference lies in specifying one of the
[models with thinking support](https://ai.google.dev/gemini-api/docs/interactions/thinking#supported-models) in the `model` field:

### Python

    from google import genai

    client = genai.Client()

    interaction = client.interactions.create(
        model="gemini-3-flash-preview",
        input="Explain the concept of Occam's Razor and provide a simple, everyday example."
    )
    print(interaction.steps[-1].content[0].text)

### JavaScript

    import { GoogleGenAI } from "@google/genai";

    const client = new GoogleGenAI({});

    const interaction = await client.interactions.create({
        model: "gemini-3-flash-preview",
        input: "Explain the concept of Occam's Razor and provide a simple, everyday example."
    });
    console.log(interaction.steps.at(-1).content[0].text);

### REST

    curl -X POST "https://generativelanguage.googleapis.com/v1beta/interactions" \
      -H "x-goog-api-key: $GEMINI_API_KEY" \
      -H 'Content-Type: application/json' \
      -d '{
        "model": "gemini-3-flash-preview",
        "input": "Explain the concept of Occam'\''s Razor and provide a simple example."
      }'

## Thought summaries

Thought summaries provide insights into the model's internal reasoning process.
By default, only the final output is returned. You can enable thought summaries
with `thinking_summaries`:

### Python

    from google import genai

    client = genai.Client()

    interaction = client.interactions.create(
        model="gemini-3-flash-preview",
        input="What is the sum of the first 50 prime numbers?",
        generation_config={
            "thinking_summaries": "auto"
        }
    )

    for step in interaction.steps:
        if step.type == "thought":
            print("Thought summary:")
            for content_block in step.summary:
                if content_block.type == "text":
                    print(content_block.text)
            print()
        elif step.type == "model_output":
            for content_block in step.content:
                if content_block.type == "text":
                    print("Answer:")
                    print(content_block.text)
                    print()

### JavaScript

    import { GoogleGenAI } from "@google/genai";

    const client = new GoogleGenAI({});

    const interaction = await client.interactions.create({
        model: "gemini-3-flash-preview",
        input: "What is the sum of the first 50 prime numbers?",
        generationConfig: {
            thinkingSummaries: "auto"
        }
    });

    for (const step of interaction.steps) {
        if (step.type === "thought") {
            console.log("Thought summary:");
            for (const contentBlock of step.summary) {
                if (contentBlock.type === "text") console.log(contentBlock.text);
            }
        } else if (step.type === "model_output") {
            for (const contentBlock of step.content) {
                if (contentBlock.type === "text") {
                    console.log("Answer:");
                    console.log(contentBlock.text);
                }
            }
        }
    }

### REST

    curl -X POST "https://generativelanguage.googleapis.com/v1beta/interactions" \
      -H "x-goog-api-key: $GEMINI_API_KEY" \
      -H 'Content-Type: application/json' \
      -d '{
        "model": "gemini-3-flash-preview",
        "input": "What is the sum of the first 50 prime numbers?",
        "generationConfig": {
          "thinkingSummaries": "auto"
        }
      }'

## Stream with thinking

Use streaming to receive incremental thought summaries during generation.
This returns rolling, incremental summaries as they are generated:

### Python

    from google import genai

    client = genai.Client()

    prompt = """
    Alice, Bob, and Carol each live in a different house on the same street: red, green, and blue.
    Alice does not live in the red house.
    Bob does not live in the green house.
    Carol does not live in the red or green house.
    Which house does each person live in?
    """

    thoughts = ""
    answer = ""

    stream = client.interactions.create(
        model="gemini-3-flash-preview",
        input=prompt,
        generation_config={
            "thinking_summaries": "auto"
        },
        stream=True
    )

    thoughts = ""
    answer = ""

    for event in stream:
        if event.event_type == "step.delta":
            if event.delta.type == "thought":
                if not thoughts:
                    print("Thinking...")
                summary_text = getattr(event.delta, 'text', '')
                print(f"[Thought] {summary_text}", end="")
                thoughts += summary_text
            elif event.delta.type == "text" and event.delta.text:
                if not answer:
                    print("\nAnswer:")
                print(event.delta.text, end="")
                answer += event.delta.text

### JavaScript

    import { GoogleGenAI } from "@google/genai";

    const client = new GoogleGenAI({});

    const prompt = `Alice, Bob, and Carol each live in a different house on the same
    street: red, green, and blue. Alice does not live in the red house.
    Bob does not live in the green house.
    Carol does not live in the red or green house.
    Which house does each person live in?`;

    let thoughts = "";
    let answer = "";

    const stream = await client.interactions.create({
        model: "gemini-3-flash-preview",
        input: prompt,
        generationConfig: {
            thinkingSummaries: "auto"
        },
        stream: true
    });

    for await (const event of stream) {
        if (event.type === "step.delta") {
            if (event.delta.type === "thought") {
                if (!thoughts) console.log("Thinking...");
                process.stdout.write(`[Thought] ${event.delta.text || ""}`);
                thoughts += event.delta.text || "";
            } else if (event.delta.type === "text" && event.delta.text) {
                if (!answer) console.log("\nAnswer:");
                process.stdout.write(event.delta.text);
                answer += event.delta.text;
            }
        }
    }

## Control thinking

Gemini models engage in dynamic thinking by default, automatically adjusting
the amount of reasoning effort based on the complexity of the request. However,
you can control this behavior using configuration parameters.

### Thinking levels (Gemini 3)

The `thinking_level` parameter, recommended for Gemini 3 models and onwards,
lets you control reasoning behavior.

| Thinking Level | Gemini 3.1 Pro               | Gemini 3 Pro (_Deprecated_)  | Gemini 3 Flash               | Description                                                                                                                                                                                                                           |
| -------------- | ---------------------------- | ---------------------------- | ---------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **`minimal`**  | Not supported                | Not supported                | Supported                    | Matches the "no thinking" setting for most queries. The model may think very minimally for complex coding tasks. Minimizes latency for chat or high throughput applications. Note, `minimal` does not guarantee that thinking is off. |
| **`low`**      | Supported                    | Supported                    | Supported                    | Minimizes latency and cost. Best for instruction following, chat, or high-throughput applications.                                                                                                                                    |
| **`medium`**   | Supported                    | Not supported                | Supported                    | Balanced thinking for most tasks.                                                                                                                                                                                                     |
| **`high`**     | Supported (Default, Dynamic) | Supported (Default, Dynamic) | Supported (Default, Dynamic) | Maximizes reasoning depth. The model may take significantly longer to reach a first (non thinking) output token, but the output will be more carefully reasoned.                                                                      |

### Python

    from google import genai

    client = genai.Client()

    interaction = client.interactions.create(
        model="gemini-3-flash-preview",
        input="Provide a list of 3 famous physicists and their key contributions",
        generation_config={
            "thinking_level": "low"
        }
    )
    print(interaction.steps[-1].content[0].text)

### JavaScript

    import { GoogleGenAI } from "@google/genai";

    const client = new GoogleGenAI({});

    const interaction = await client.interactions.create({
        model: "gemini-3-flash-preview",
        input: "Provide a list of 3 famous physicists and their key contributions",
        generationConfig: {
            thinkingLevel: "low"
        }
    });
    console.log(interaction.steps.at(-1).content[0].text);

### REST

    curl -X POST "https://generativelanguage.googleapis.com/v1beta/interactions" \
      -H "x-goog-api-key: $GEMINI_API_KEY" \
      -H 'Content-Type: application/json' \
      -d '{
        "model": "gemini-3-flash-preview",
        "input": "Provide a list of 3 famous physicists and their key contributions",
        "generation_config": {
          "thinking_level": "low"
        }
      }'

You cannot disable thinking for Gemini 3 Pro. Gemini 3 Flash does not support
full thinking-off either, but the `minimal` setting means the model likely won't
think (though it still potentially can).

## Thought signatures

> [!IMPORTANT]
> **Important:** The [Google GenAI SDK](https://ai.google.dev/gemini-api/docs/interactions) automatically handles the return of thought signatures for you. You only need to [manage thought signatures manually](https://ai.google.dev/gemini-api/docs/interactions/function-calling#thought-signatures) if you're modifying conversation history or using the REST API.

The Gemini API is stateless, so the model treats every API request independently
and doesn't have access to thought context from previous turns in multi-turn
interactions.

In order to enable maintaining thought context across multi-turn interactions,
Gemini returns thought signatures, which are encrypted representations of the
model's internal thought process.

- **Gemini 2.5 models** return thought signatures when thinking is enabled and the request includes [function calling](https://ai.google.dev/gemini-api/docs/interactions/function-calling#thinking), specifically [function declarations](https://ai.google.dev/gemini-api/docs/interactions/function-calling#step-2).
- **Gemini 3 models** may return thought signatures for all types of [parts](https://ai.google.dev/api/caching#Part). We recommend you always pass all signatures back as received, but it's _required_ for function calling signatures. Read the [Thought Signatures](https://ai.google.dev/gemini-api/docs/interactions/thought-signatures) page to learn more.
- Signatures are returned from the model within other parts in the response, for example function calling or text parts. [Return the entire response](https://ai.google.dev/gemini-api/docs/interactions/function-calling) with all parts back to the model in subsequent turns.
- Don't concatenate parts with signatures together.
- Don't merge one part with a signature with another part without a signature.

## Pricing

> [!NOTE]
> **Note:** **Summaries** are available in the [free and paid tiers](https://ai.google.dev/gemini-api/docs/pricing) of the API. **Thought signatures** will increase the input tokens you are charged when sent back as part of the request.

When thinking is turned on, response pricing is the sum of output
tokens and thinking tokens. You can get the total number of generated thinking
tokens from the `total_thought_tokens` field.

### Python

    # ...
    print("Thoughts tokens:", interaction.usage.total_thought_tokens)
    print("Output tokens:", interaction.usage.total_output_tokens)

### JavaScript

    // ...
    console.log(`Thoughts tokens: ${interaction.usage.totalThoughtTokens}`);
    console.log(`Output tokens: ${interaction.usage.totalOutputTokens}`);

Thinking models generate full thoughts to improve the quality of the final
response, and then output [summaries](https://ai.google.dev/gemini-api/docs/interactions/thinking#summaries) to provide insight into the
thought process. Pricing is based on the full thought tokens the model needs to
generate, despite only the summary being output from the API.

You can learn more about tokens in the [Token counting](https://ai.google.dev/gemini-api/docs/interactions/tokens) guide.

## Best practices

This section includes guidance for using thinking models efficiently.

### Debug and steer

- **Review reasoning**: When you're not getting your expected response from
  thinking models, it can help to carefully analyze Gemini's thought summaries.
  You can see how it broke down the task and arrived at its conclusion, and use
  that information to correct towards the right results.

- **Provide guidance in reasoning** : If you're hoping for a particularly lengthy
  output, you may want to provide guidance in your prompt to constrain the
  [amount of thinking](https://ai.google.dev/gemini-api/docs/interactions/thinking#thinking-budget) the model uses. This lets you reserve
  more of the token output for your response.

### Task complexity

- **Easy tasks (Thinking could be OFF):** For straightforward requests where complex reasoning isn't required, thinking is not required. Examples:
    - "Where was DeepMind founded?"
    - "Is this email asking for a meeting or just providing information?"
- **Medium tasks (Default/Some thinking):** Many common requests benefit from a degree of step-by-step processing or deeper understanding. Examples:
    - Analogize photosynthesis and growing up.
    - Compare and contrast electric cars and hybrid cars.
- **Hard tasks (Maximum thinking capability):** For truly complex challenges, we recommend setting a high thinking budget. These types of tasks require the model to engage its full reasoning and planning capabilities. Examples:
    - Solve problem 1 in AIME 2025: Find the sum of all integer bases b \> 9...
    - Write Python code for a web application that visualizes real-time stock market data, including user authentication. Make it as efficient as possible.

## Supported models

| Model                  | Default Thinking | Levels Supported           |
| ---------------------- | ---------------- | -------------------------- |
| gemini-3.1-pro-preview | On (high)        | low, medium, high          |
| gemini-3-flash-preview | On (high)        | minimal, low, medium, high |
| gemini-3-pro-preview   | On (high)        | low, high                  |
| gemini-2.5-pro         | On               | Budget: 128-32768          |
| gemini-2.5-flash       | On               | Budget: 0-24576            |
| gemini-2.5-flash-lite  | Off              | Budget: 0-24576            |

Thinking models work with all of Gemini's tools and capabilities. This allows
models to interact with external systems, execute code, or access real-time
information, incorporating the results into their reasoning.

## What's next

- [Text generation](https://ai.google.dev/gemini-api/docs/interactions/text-generation): Basic text responses
- [Function calling](https://ai.google.dev/gemini-api/docs/interactions/function-calling): Connect to tools
- [Thought signatures](https://ai.google.dev/gemini-api/docs/interactions/thought-signatures): Manage signatures in multi-turn
- [Gemini 3 guide](https://ai.google.dev/gemini-api/docs/interactions/gemini-3): Model-specific features
