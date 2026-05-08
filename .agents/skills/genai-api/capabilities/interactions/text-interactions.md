# Text generation

> [!NOTE]
> **Note** : This version of the page covers the new [Interactions API](https://ai.google.dev/gemini-api/docs/interactions), which is currently in Beta.
> For stable production deployments, we recommend you continue to use the `generateContent` API. You can use the toggle on this page to switch between the versions.

The Gemini API can generate text output from text, images, video, and audio
inputs.

Here's a basic example:

### Python

    from google import genai

    client = genai.Client()

    interaction = client.interactions.create(
        model="gemini-3-flash-preview",
        input="How does AI work?"
    )
    print(interaction.steps[-1].content[0].text)

### JavaScript

    import { GoogleGenAI } from "@google/genai";

    const ai = new GoogleGenAI({});

    async function main() {
      const interaction = await ai.interactions.create({
        model: "gemini-3-flash-preview",
        input: "How does AI work?",
      });
      console.log(interaction.steps.at(-1).content[0].text);
    }

    await main();

### REST

    curl -X POST "https://generativelanguage.googleapis.com/v1beta/interactions" \
      -H "x-goog-api-key: $GEMINI_API_KEY" \
      -H 'Content-Type: application/json' \
      -d '{
        "model": "gemini-3-flash-preview",
        "input": "How does AI work?"
      }'

## Thinking with Gemini

Gemini models often have ["thinking"](https://ai.google.dev/gemini-api/docs/interactions/thinking)
enabled by default which allows the model to reason before responding to a
request.

Each model supports different thinking configurations which gives you control
over cost, latency, and intelligence. For more details, see the
[thinking guide](https://ai.google.dev/gemini-api/docs/interactions/thinking#set-budget).

### Python

    from google import genai

    client = genai.Client()

    interaction = client.interactions.create(
        model="gemini-3-flash-preview",
        input="How does AI work?",
        generation_config={
            "thinking_level": "low"
        }
    )
    print(interaction.steps[-1].content[0].text)

### JavaScript

    import { GoogleGenAI } from "@google/genai";

    const ai = new GoogleGenAI({});

    async function main() {
      const interaction = await ai.interactions.create({
        model: "gemini-3-flash-preview",
        input: "How does AI work?",
        generation_config: {
          thinking_level: "low",
        },
      });
      console.log(interaction.steps.at(-1).content[0].text);
    }

    await main();

### REST

    curl -X POST "https://generativelanguage.googleapis.com/v1beta/interactions" \
      -H "x-goog-api-key: $GEMINI_API_KEY" \
      -H 'Content-Type: application/json' \
      -d '{
        "model": "gemini-3-flash-preview",
        "input": "How does AI work?",
        "generation_config": {
          "thinking_level": "low"
        }
      }'

## System instructions and other configurations

You can guide the behavior of Gemini models with system instructions. Pass
a `system_instruction` parameter to configure the model's behavior.

### Python

    from google import genai

    client = genai.Client()

    interaction = client.interactions.create(
        model="gemini-3-flash-preview",
        system_instruction="You are a cat. Your name is Neko.",
        input="Hello there"
    )

    print(interaction.steps[-1].content[0].text)

### JavaScript

    import { GoogleGenAI } from "@google/genai";

    const ai = new GoogleGenAI({});

    async function main() {
      const interaction = await ai.interactions.create({
        model: "gemini-3-flash-preview",
        input: "Hello there",
        system_instruction: "You are a cat. Your name is Neko.",
      });
      console.log(interaction.steps.at(-1).content[0].text);
    }

    await main();

### REST

    curl -X POST "https://generativelanguage.googleapis.com/v1beta/interactions" \
      -H "x-goog-api-key: $GEMINI_API_KEY" \
      -H 'Content-Type: application/json' \
      -d '{
        "model": "gemini-3-flash-preview",
        "system_instruction": "You are a cat. Your name is Neko.",
        "input": "Hello there"
      }'

You can also override default generation parameters, such as
temperature, using the `generation_config` parameter.

### Python

    from google import genai

    client = genai.Client()

    interaction = client.interactions.create(
        model="gemini-3-flash-preview",
        input="Explain how AI works",
        generation_config={
            "temperature": 0.1
        }
    )
    print(interaction.steps[-1].content[0].text)

### JavaScript

    import { GoogleGenAI } from "@google/genai";

    const ai = new GoogleGenAI({});

    async function main() {
      const interaction = await ai.interactions.create({
        model: "gemini-3-flash-preview",
        input: "Explain how AI works",
        generation_config: {
          temperature: 0.1,
        },
      });
      console.log(interaction.steps.at(-1).content[0].text);
    }

    await main();

### REST

    curl -X POST "https://generativelanguage.googleapis.com/v1beta/interactions" \
      -H "x-goog-api-key: $GEMINI_API_KEY" \
      -H 'Content-Type: application/json' \
      -d '{
        "model": "gemini-3-flash-preview",
        "input": "Explain how AI works",
        "generation_config": {
          "temperature": 0.1
        }
      }'

Refer to the [Interactions API reference](https://ai.google.dev/api/interactions-api)
for a complete list of configurable parameters and their
descriptions.

## Multimodal inputs

The Gemini API supports multimodal inputs, allowing you to combine text with
media files. The following example demonstrates providing an image:

### Python

    from google import genai

    client = genai.Client()

    uploaded_file = client.files.upload(file="path/to/organ.jpg")

    interaction = client.interactions.create(
        model="gemini-3-flash-preview",
        input=[
            {"type": "text", "text": "Tell me about this instrument"},
            {
                "type": "image",
                "uri": uploaded_file.uri,
                "mime_type": uploaded_file.mime_type
            }
        ]
    )
    print(interaction.steps[-1].content[0].text)

### JavaScript

    import { GoogleGenAI } from "@google/genai";

    const ai = new GoogleGenAI({});

    async function main() {
      const uploadedFile = await ai.files.upload({
        file: "path/to/organ.jpg",
        config: { mimeType: "image/jpeg" }
      });

      const interaction = await ai.interactions.create({
        model: "gemini-3-flash-preview",
        input: [
          {type: "text", text: "Tell me about this instrument"},
          {
            type: "image",
            uri: uploadedFile.uri,
            mimeType: uploadedFile.mimeType
          }
        ],
      });
      console.log(interaction.steps.at(-1).content[0].text);
    }

    await main();

### REST

    # First upload the file using the Files API, then use the URI:
    curl -X POST "https://generativelanguage.googleapis.com/v1beta/interactions" \
      -H "x-goog-api-key: $GEMINI_API_KEY" \
      -H 'Content-Type: application/json' \
      -d '{
        "model": "gemini-3-flash-preview",
        "input": [
          {"type": "text", "text": "Tell me about this instrument"},
          {
            "type": "image",
            "uri": "YOUR_FILE_URI",
            "mime_type": "image/jpeg"
          }
        ]
      }'

For alternative methods of providing images and more advanced image processing,
see our [image understanding guide](https://ai.google.dev/gemini-api/docs/interactions/image-understanding).
The API also supports [document](https://ai.google.dev/gemini-api/docs/interactions/document-processing), [video](https://ai.google.dev/gemini-api/docs/interactions/video-understanding), and
[audio](https://ai.google.dev/gemini-api/docs/interactions/audio) inputs and understanding.

## Streaming responses

By default, the model returns a response only after the entire generation
process is complete.

For more fluid interactions, use streaming to handle response chunks
as they're generated.

### Python

    from google import genai

    client = genai.Client()

    stream = client.interactions.create(
        model="gemini-3-flash-preview",
        input="Explain how AI works",
        stream=True
    )
    for event in stream:
        if event.event_type == "step.delta":
            if event.delta.type == "text":
                print(event.delta.text, end="")

### JavaScript

    import { GoogleGenAI } from "@google/genai";

    const ai = new GoogleGenAI({});

    async function main() {
      const stream = await ai.interactions.create({
        model: "gemini-3-flash-preview",
        input: "Explain how AI works",
        stream: true,
      });

      for await (const event of stream) {
        if (event.type === "step.delta") {
          if (event.delta.type === "text") {
            process.stdout.write(event.delta.text);
          }
        }
      }
    }

    await main();

### REST

    curl -X POST "https://generativelanguage.googleapis.com/v1beta/interactions?alt=sse" \
      -H "x-goog-api-key: $GEMINI_API_KEY" \
      -H 'Content-Type: application/json' \
      --no-buffer \
      -d '{
        "model": "gemini-3-flash-preview",
        "input": "Explain how AI works",
        "stream": true
      }'

## Multi-turn conversations

The Interactions API supports multi-turn conversations by chaining interactions
together using `previous_interaction_id`. Each turn is a separate interaction,
and the API automatically manages conversation history.

> [!NOTE]
> **Note:** Unlike other APIs where you might manage conversation history manually, the Interactions API handles conversation state server-side. You pass the `id` from the previous interaction to continue the conversation.

### Python

    from google import genai

    client = genai.Client()

    interaction1 = client.interactions.create(
        model="gemini-3-flash-preview",
        input="I have 2 dogs in my house.",
    )
    print(interaction1.steps[-1].content[0].text)

    interaction2 = client.interactions.create(
        model="gemini-3-flash-preview",
        input="How many paws are in my house?",
        previous_interaction_id=interaction1.id,
    )
    print(interaction2.steps[-1].content[0].text)

### JavaScript

    import { GoogleGenAI } from "@google/genai";

    const ai = new GoogleGenAI({});

    async function main() {
      const interaction1 = await ai.interactions.create({
        model: "gemini-3-flash-preview",
        input: "I have 2 dogs in my house.",
      });
      console.log("Response 1:", interaction1.steps.at(-1).content[0].text);

      const interaction2 = await ai.interactions.create({
        model: "gemini-3-flash-preview",
        input: "How many paws are in my house?",
        previousInteractionId: interaction1.id,
      });
      console.log("Response 2:", interaction2.steps.at(-1).content[0].text);
    }

    await main();

### REST

    RESPONSE1=$(curl -s -X POST "https://generativelanguage.googleapis.com/v1beta/interactions" \
      -H "x-goog-api-key: $GEMINI_API_KEY" \
      -H 'Content-Type: application/json' \
      -d '{
        "model": "gemini-3-flash-preview",
        "input": "I have 2 dogs in my house."
      }')

    INTERACTION_ID=$(echo "$RESPONSE1" | jq -r '.name')

    curl -X POST "https://generativelanguage.googleapis.com/v1beta/interactions" \
      -H "x-goog-api-key: $GEMINI_API_KEY" \
      -H 'Content-Type: application/json' \
      -d '{
        "model": "gemini-3-flash-preview",
        "input": "I have two dogs in my house. How many paws are in my house?",
        "previous_interaction_id": "'$INTERACTION_ID'"
      }'

Streaming can also be used for multi-turn conversations by combining
`previous_interaction_id` with the streaming methods.

### Python

    from google import genai

    client = genai.Client()

    interaction1 = client.interactions.create(
        model="gemini-3-flash-preview",
        input="I have 2 dogs in my house.",
    )
    print(interaction1.steps[-1].content[0].text)

    stream = client.interactions.create(
        model="gemini-3-flash-preview",
        input="How many paws are in my house?",
        previous_interaction_id=interaction1.id,
        stream=True
    )
    for event in stream:
        if event.event_type == "step.delta":
            if event.delta.type == "text":
                print(event.delta.text, end="")

### JavaScript

    import { GoogleGenAI } from "@google/genai";

    const ai = new GoogleGenAI({});

    async function main() {
      const interaction1 = await ai.interactions.create({
        model: "gemini-3-flash-preview",
        input: "I have 2 dogs in my house.",
      });
      console.log("Response 1:", interaction1.steps.at(-1).content[0].text);

      const stream = await ai.interactions.create({
        model: "gemini-3-flash-preview",
        input: "How many paws are in my house?",
        previousInteractionId: interaction1.id,
        stream: true,
      });
      for await (const event of stream) {
        if (event.type === "step.delta") {
          if (event.delta.type === "text") {
            process.stdout.write(event.delta.text);
          }
        }
      }
    }

    await main();

### REST

    RESPONSE1=$(curl -s -X POST "https://generativelanguage.googleapis.com/v1beta/interactions" \
      -H "x-goog-api-key: $GEMINI_API_KEY" \
      -H 'Content-Type: application/json' \
      -d '{
        "model": "gemini-3-flash-preview",
        "input": "I have 2 dogs in my house."
      }')
    INTERACTION_ID=$(echo "$RESPONSE1" | jq -r '.name')

    curl -X POST "https://generativelanguage.googleapis.com/v1beta/interactions?alt=sse" \
      -H "x-goog-api-key: $GEMINI_API_KEY" \
      -H 'Content-Type: application/json' \
      --no-buffer \
      -d '{
        "model": "gemini-3-flash-preview",
        "input": "How many paws are in my house?",
        "previous_interaction_id": "'$INTERACTION_ID'",
        "stream": true
      }'

## Prompting tips

Consult our [prompt engineering guide](https://ai.google.dev/gemini/docs/prompting-strategies) for
suggestions on getting the most out of Gemini.

## What's next

- Try [Gemini in Google AI Studio](https://aistudio.google.com).
- Experiment with [structured outputs](https://ai.google.dev/gemini-api/docs/interactions/structured-output) for JSON-like responses.
- Explore Gemini's [image](https://ai.google.dev/gemini-api/docs/interactions/image-understanding), [video](https://ai.google.dev/gemini-api/docs/interactions/video-understanding), [audio](https://ai.google.dev/gemini-api/docs/interactions/audio) and [document](https://ai.google.dev/gemini-api/docs/interactions/document-processing) understanding capabilities.
- Learn about multimodal [file prompting strategies](https://ai.google.dev/gemini-api/docs/interactions/files#prompt-guide).
