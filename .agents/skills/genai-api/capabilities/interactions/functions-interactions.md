# Function calling with the Gemini API

> [!NOTE]
> **Note** : This version of the page covers the new [Interactions API](https://ai.google.dev/gemini-api/docs/interactions), which is currently in Beta.
> For stable production deployments, we recommend you continue to use the `generateContent` API. You can use the toggle on this page to switch between the versions.

Function calling lets you connect models to external tools and APIs.
Instead of generating text responses, the model determines when to call specific
functions and provides the necessary parameters to execute real-world actions.
This allows the model to act as a bridge between natural language and real-world
actions and data. Function calling has 3 primary use cases:

- **Augment Knowledge:** Access information from external sources like databases, APIs, and knowledge bases.
- **Extend Capabilities:** Use external tools to perform computations and extend the limitations of the model, such as using a calculator or creating charts.
- **Take Actions:** Interact with external systems using APIs, such as scheduling appointments, creating invoices, sending emails, or controlling smart home devices.

> [!NOTE]
> **Important:** Gemini 3 model APIs now generate a unique `id` for every function call. When returning the result of your executed function to the model, we recommend passing the matching `id` in your `function_result`. If you are using the standard Python or Node.js SDKs, this is handled automatically.

<button value="weather">Get Weather</button> <button value="meeting" default="">Schedule Meeting</button> <button value="chart">Create Chart</button>

### Python

    from google import genai

    schedule_meeting_function = {
        "type": "function",
        "name": "schedule_meeting",
        "description": "Schedules a meeting with specified attendees at a given time and date.",
        "parameters": {
            "type": "object",
            "properties": {
                "attendees": {"type": "array", "items": {"type": "string"}},
                "date": {"type": "string", "description": "Date (e.g., '2024-07-29')"},
                "time": {"type": "string", "description": "Time (e.g., '15:00')"},
                "topic": {"type": "string", "description": "The meeting topic."},
            },
            "required": ["attendees", "date", "time", "topic"],
        },
    }

    client = genai.Client()

    interaction = client.interactions.create(
        model="gemini-3-flash-preview",
        input="Schedule a meeting with Bob and Alice for 03/14/2025 at 10:00 AM about Q3 planning.",
        tools=[{"type": "function", **schedule_meeting_function}],
    )

    for step in interaction.steps:
        if step.type == "function_call":
            print(f"Function to call: {step.name}")
            print(f"Arguments: {step.arguments}")

### JavaScript

    import { GoogleGenAI } from '@google/genai';

    const client = new GoogleGenAI({});

    const scheduleMeetingFunction = {
      type: 'function',
      name: 'schedule_meeting',
      description: 'Schedules a meeting with specified attendees at a given time and date.',
      parameters: {
        type: 'object',
        properties: {
          attendees: { type: 'array', items: { type: 'string' } },
          date: { type: 'string', description: 'Date (e.g., "2024-07-29")' },
          time: { type: 'string', description: 'Time (e.g., "15:00")' },
          topic: { type: 'string', description: 'The meeting topic.' },
        },
        required: ['attendees', 'date', 'time', 'topic'],
      },
    };

    const interaction = await client.interactions.create({
      model: 'gemini-3-flash-preview',
      input: 'Schedule a meeting with Bob and Alice for 03/27/2025 at 10:00 AM about Q3 planning.',
      tools: [scheduleMeetingFunction],
    });

    for (const step of interaction.steps) {
      if (step.type === 'function_call') {
        console.log(`Function to call: ${step.name}`);
        console.log(`Arguments: ${JSON.stringify(step.arguments)}`);
      }
    }

### REST

    curl -X POST "https://generativelanguage.googleapis.com/v1beta/interactions" \
      -H "x-goog-api-key: $GEMINI_API_KEY" \
      -H 'Content-Type: application/json' \
      -d '{
        "model": "gemini-3-flash-preview",
        "input": "Schedule a meeting with Bob and Alice for 03/27/2025 at 10:00 AM about Q3 planning.",
        "tools": [{
            "type": "function",
            "name": "schedule_meeting",
            "description": "Schedules a meeting with specified attendees at a given time and date.",
            "parameters": {
              "type": "object",
              "properties": {
                "attendees": {"type": "array", "items": {"type": "string"}},
                "date": {"type": "string"},
                "time": {"type": "string"},
                "topic": {"type": "string"}
              },
              "required": ["attendees", "date", "time", "topic"]
            }
        }]
      }'

## How function calling works

![function calling overview](https://ai.google.dev/static/gemini-api/docs/images/function-calling-overview.png)

Function calling involves a structured interaction between your application, the
model, and external functions:

1. **Define Function Declaration:** Define the function's name, parameters, and purpose to the model.
2. **Call LLM with function declarations:** Send user prompt along with the function declaration(s) to the model.
3. **Execute Function Code (Your Responsibility):** The model _doesn't_ execute the function itself. Extract the name and args and execute in your application.
4. **Create User friendly response:** Send the result back to the model for a final, user-friendly response.

This process can be repeated over multiple turns. The model supports calling
multiple functions in a single turn ([parallel function calling](https://ai.google.dev/gemini-api/docs/interactions/function-calling#parallel_function_calling)) and in
sequence ([compositional function calling](https://ai.google.dev/gemini-api/docs/interactions/function-calling#compositional_function_calling)).

### Step 1: Define a function declaration

### Python

    set_light_values_declaration = {
        "type": "function",
        "name": "set_light_values",
        "description": "Sets the brightness and color temperature of a light.",
        "parameters": {
            "type": "object",
            "properties": {
                "brightness": {
                    "type": "integer",
                    "description": "Light level from 0 to 100",
                },
                "color_temp": {
                    "type": "string",
                    "enum": ["daylight", "cool", "warm"],
                    "description": "Color temperature",
                },
            },
            "required": ["brightness", "color_temp"],
        },
    }

    def set_light_values(brightness: int, color_temp: str) -> dict:
        """Set the brightness and color temperature of a room light."""
        return {"brightness": brightness, "colorTemperature": color_temp}

### JavaScript

    const setLightValuesTool = {
      type: 'function',
      name: 'set_light_values',
      description: 'Sets the brightness and color temperature of a light.',
      parameters: {
        type: 'object',
        properties: {
          brightness: { type: 'number', description: 'Light level from 0 to 100' },
          color_temp: { type: 'string', enum: ['daylight', 'cool', 'warm'] },
        },
        required: ['brightness', 'color_temp'],
      },
    };

    function setLightValues(brightness, color_temp) {
      return { brightness: brightness, colorTemperature: color_temp };
    }

### Step 2: Call the model with function declarations

### Python

    from google import genai

    client = genai.Client()

    interaction = client.interactions.create(
        model="gemini-3-flash-preview",
        input="Turn the lights down to a romantic level",
        tools=[set_light_values_declaration],
    )

    # Find the function call step
    fc_step = next(s for s in interaction.steps if s.type == "function_call")
    print(fc_step)

### JavaScript

    import { GoogleGenAI } from '@google/genai';

    const client = new GoogleGenAI({});

    const interaction = await client.interactions.create({
      model: 'gemini-3-flash-preview',
      input: 'Turn the lights down to a romantic level',
      tools: [setLightValuesTool],
    });

    // Find the function call step
    const fcStep = interaction.steps.find(s => s.type === 'function_call');
    console.log(fcStep);

The model returns a `function_call` step with `type`, `name`, and `arguments`:

    type='function_call'
    name='set_light_values'
    arguments={'color_temp': 'warm', 'brightness': 25}

### Step 3: Execute the function

### Python

    fc_step = next(s for s in interaction.steps if s.type == "function_call")

    if fc_step.name == "set_light_values":
        result = set_light_values(**fc_step.arguments)
        print(f"Function execution result: {result}")

### JavaScript

    const fcStep = interaction.steps.find(s => s.type === 'function_call');

    let result;
    if (fcStep.name === 'set_light_values') {
      result = setLightValues(fcStep.arguments.brightness, fcStep.arguments.color_temp);
      console.log(`Function execution result: ${JSON.stringify(result)}`);
    }

### Step 4: Send result back to model

### Python

    final_interaction = client.interactions.create(
        model="gemini-3-flash-preview",
        input=[
            {
                "type": "function_result",
                "name": fc_step.name,
                "call_id": fc_step.id,
                "result": [{"type": "text", "text": json.dumps(result)}],
            }
        ],
        tools=[set_light_values_declaration],
        previous_interaction_id=interaction.id,
    )

    print(final_interaction.steps[-1].content[0].text)

### JavaScript

    const finalInteraction = await client.interactions.create({
      model: 'gemini-3-flash-preview',
      input: [{
        type: 'function_result',
        name: fcStep.name,
        call_id: fcStep.id,
        result: [{ type: 'text', text: JSON.stringify(result) }]
      }],
      tools: [setLightValuesTool],
      previousInteractionId: interaction.id,
    });

    console.log(finalInteraction.steps.at(-1).content[0].text);

## Function declarations

A function declaration is passed as a tool and includes:

- `type` (string): Must be `"function"` for custom functions.
- `name` (string): Unique function name (use underscores or camelCase).
- `description` (string): Clear explanation of the function's purpose.
- `parameters` (object): Input parameters the function expects.
    - `type` (string): Overall data type, such as `object`.
    - `properties` (object): Individual parameters with type and description.
    - `required` (array): Mandatory parameter names.

## Function calling with thinking models

Gemini 3 and 2.5 series models use an internal ["thinking"](https://ai.google.dev/gemini-api/docs/interactions/thinking) process that improves function calling.
The SDKs automatically handle [thought signatures](https://ai.google.dev/gemini-api/docs/interactions/thought-signatures) for you.

## Parallel function calling

Call multiple functions at once when they are independent:

### Python

    power_disco_ball = {"type": "function", "name": "power_disco_ball", "description": "Powers the disco ball.",
        "parameters": {"type": "object", "properties": {"power": {"type": "boolean"}}, "required": ["power"]}}
    start_music = {"type": "function", "name": "start_music", "description": "Play music.",
        "parameters": {"type": "object", "properties": {"energetic": {"type": "boolean"}, "loud": {"type": "boolean"}}, "required": ["energetic", "loud"]}}
    dim_lights = {"type": "function", "name": "dim_lights", "description": "Dim the lights.",
        "parameters": {"type": "object", "properties": {"brightness": {"type": "number"}}, "required": ["brightness"]}}

    client = genai.Client()

    interaction = client.interactions.create(
        model="gemini-3-flash-preview",
        input="Turn this place into a party!",
        tools=[power_disco_ball, start_music, dim_lights],
        generation_config={"tool_choice": "any"},
    )

    for step in interaction.steps:
        if step.type == "function_call":
            args = ", ".join(f"{key}={val}" for key, val in step.arguments.items())
            print(f"{step.name}({args})")

### JavaScript

    const powerDiscoBall = { type: 'function', name: 'power_disco_ball', description: 'Powers the disco ball.',
      parameters: { type: 'object', properties: { power: { type: 'boolean' } }, required: ['power'] } };
    const startMusic = { type: 'function', name: 'start_music', description: 'Play music.',
      parameters: { type: 'object', properties: { energetic: { type: 'boolean' }, loud: { type: 'boolean' } }, required: ['energetic', 'loud'] } };
    const dimLights = { type: 'function', name: 'dim_lights', description: 'Dim the lights.',
      parameters: { type: 'object', properties: { brightness: { type: 'number' } }, required: ['brightness'] } };

    const interaction = await client.interactions.create({
      model: 'gemini-3-flash-preview',
      input: 'Turn this place into a party!',
      tools: [powerDiscoBall, startMusic, dimLights],
      generationConfig: { toolChoice: 'any' },
    });

    for (const step of interaction.steps) {
      if (step.type === 'function_call') {
        console.log(`${step.name}(${JSON.stringify(step.arguments)})`);
      }
    }

## Compositional function calling

Chain multiple function calls together for complex requests (e.g., get location
first, then get weather for that location).

### Python

    def get_weather_forecast(location: str) -> dict:
        """Gets the current weather temperature for a given location."""
        return {"temperature": 25, "unit": "celsius"}

    def set_thermostat_temperature(temperature: int) -> dict:
        """Sets the thermostat to a desired temperature."""
        return {"status": "success"}

    client = genai.Client()

    interaction = client.interactions.create(
        model="gemini-3-flash-preview",
        input="If it's warmer than 20°C in London, set the thermostat to 20°C, otherwise 18°C.",
        tools=[get_weather_forecast, set_thermostat_temperature],
    )

    print(interaction.steps[-1].content[0].text)

## Function calling modes

Control how the model uses tools using `tool_choice` in `generation_config`:

- `auto` (Default): Model decides whether to call a function or respond directly.
- `any`: Model is constrained to always predict a function call.
- `none`: Model is prohibited from making function calls.
- `validated` (Preview): Model ensures function schema adherence.

### Python

    generation_config = {
        "tool_choice": {
            "allowed_tools": {
                "mode": "any",
                "tools": ["get_current_temperature"]
            }
        }
    }

### JavaScript

    const generationConfig = {
      toolChoice: {
        allowedTools: {
          mode: 'any',
          tools: ['get_current_temperature']
        }
      }
    };

### REST

    curl -X POST "https://generativelanguage.googleapis.com/v1beta/interactions" \
      -H "x-goog-api-key: \$GEMINI_API_KEY" \
      -H 'Content-Type: application/json' \
      -d '{
        "model": "gemini-3-flash-preview",
        "input": "What is the temperature in Boston?",
        "tools": [{
          "type": "function",
          "name": "get_current_temperature",
          "description": "Gets the current temperature for a given location.",
          "parameters": {
            "type": "object",
            "properties": {
              "location": {"type": "string"}
            },
            "required": ["location"]
          }
        }],
        "generation_config": {
          "tool_choice": {
            "allowed_tools": {
              "mode": "any",
              "tools": ["get_current_temperature"]
            }
          }
        }
      }'

## Multi-tool use

You can enable multiple tools, combining built-in tools with function calling in
the same request. Gemini 3 models can combine built-in tools with function
calling out-of-the-box in Interactions. Passing `previous_interaction_id`
automatically circulates the built-in tool context.

### Python

    from google import genai
    import json

    client = genai.Client()

    get_weather = {
        "type": "function",
        "name": "get_weather",
        "description": "Gets the weather for a requested city.",
        "parameters": {
            "type": "object",
            "properties": {
                "city": {
                    "type": "string",
                    "description": "The city and state, e.g. Utqiaġvik, Alaska",
                },
            },
            "required": ["city"],
        },
    }

    tools = [
        {"type": "google_search"},  # Built-in tool
        get_weather                 # Custom tool
    ]

    # Turn 1: Initial request with both tools enabled
    interaction = client.interactions.create(
        model="gemini-3-flash-preview",
        input="What is the northernmost city in the United States? What's the weather like there today?",
        tools=tools
    )

    for step in interaction.steps:
        if step.type == "function_call":
            print(f"Function call: {step.name} (ID: {step.id})")
            # Execute your custom function locally
            result = {"response": "Very cold. 22 degrees Fahrenheit."}
            # Turn 2: Provide the function result back to the model.
            # Passing `previous_interaction_id` automatically circulates the
            # built-in Google Search context from Turn 1
            interaction_2 = client.interactions.create(
                model="gemini-3-flash-preview",
                previous_interaction_id=interaction.id,
                tools=tools,
                input=[{
                    "type": "function_result",
                    "name": step.name,
                    "call_id": step.id,
                    "result": [{"type": "text", "text": json.dumps(result)}]
                }]
            )

            print(interaction_2.steps[-1].content[0].text)

### JavaScript

    import { GoogleGenAI } from '@google/genai';

    const client = new GoogleGenAI({});

    const weatherTool = {
        type: 'function',
        name: 'get_weather',
        description: 'Gets the weather for a given location.',
        parameters: {
            type: 'object',
            properties: {
                location: { type: 'string', description: 'The city and state, e.g. San Francisco, CA' }
            },
            required: ['location']
        }
    };

    const tools = [
        {type: 'google_search'}, // Built-in tool
        weatherTool              // Custom tool
    ];

    // Turn 1: Initial request with both tools enabled
    let interaction = await client.interactions.create({
        model: 'gemini-3-flash-preview',
        input: "What is the northernmost city in the United States? What's the weather like there today?",
        tools: tools
    });

    for (const step of interaction.steps) {
        if (step.type === 'function_call') {
            console.log(`Function call: ${step.name} (ID: ${step.id})`);
            // Execute your custom function locally
            const result = {response: "Very cold. 22 degrees Fahrenheit."};
            // Turn 2: Provide the function result back to the model.
            const interaction_2 = await client.interactions.create({
                model: 'gemini-3-flash-preview',
                previousInteractionId: interaction.id,
                tools: tools,
                input: [{
                    type: 'function_result',
                    name: step.name,
                    call_id: step.id,
                    result: [{ type: 'text', text: JSON.stringify(result) }]
                }]
            });

            console.log(interaction_2.steps.at(-1).content[0].text);
        }
    }

## Multimodal function responses

For Gemini 3 series models, you can include multimodal content in
the function response parts that you send to the model. The model can process
this multimodal content in its next turn to produce a more informed response.

To include multimodal data in a function response, include it as one or more content blocks in the `result` field of the `function_result` step. Each content block must specify its `type` (e.g., `"text"`, `"image"`).

The following example shows how to send a function response containing image data back to the model in an interaction:

### Python

    import base64
    from google import genai
    import requests

    client = genai.Client()

    # Find the function call step
    tool_call = next(s for s in interaction.steps if s.type == "function_call")

    # Execute your tool to get image bytes
    image_path = "https://goo.gle/instrument-img"
    image_bytes = requests.get(image_path).content

    base64_image_data = base64.b64encode(image_bytes).decode("utf-8")

    final_interaction = client.interactions.create(
        model="gemini-3-flash-preview",
        previous_interaction_id=interaction.id,
        input=[
            {
                "type": "function_result",
                "name": tool_call.name,
                "call_id": tool_call.id,
                "result": [
                    {"type": "text", "text": "instrument.jpg"},
                    {
                        "type": "image",
                        "mime_type": "image/jpeg",
                        "data": base64_image_data,
                    },
                ],
            }
        ],
    )

    print(final_interaction.steps[-1].content[0].text)

### JavaScript

    import { GoogleGenAI } from "@google/genai";

    const ai = new GoogleGenAI({});

    // Find the function call step
    const toolCall = interaction.steps.find(s => s.type === 'function_call');

    // Execute your tool to get image bytes and convert to base64
    // (Implementation depends on your environment)
    const base64ImageData = "BASE64_IMAGE_DATA";

    const finalInteraction = await ai.interactions.create({
        model: 'gemini-3-flash-preview',
        previousInteractionId: interaction.id,
        input: [{
            type: 'function_result',
            name: toolCall.name,
            call_id: toolCall.id,
            result: [
                { type: 'text', text: 'instrument.jpg' },
                {
                    type: 'image',
                    mimeType: 'image/jpeg',
                    data: base64ImageData,
                }
            ]
        }]
    });

    console.log(finalInteraction.steps.at(-1).content[0].text);

### REST

    curl -X POST "https://generativelanguage.googleapis.com/v1beta/interactions" \
      -H "x-goog-api-key: \$GEMINI_API_KEY" \
      -H 'Content-Type: application/json' \
      -d '{
        "model": "gemini-3-flash-preview",
        "previous_interaction_id": "INTERACTION_ID",
        "input": [
          {
            "type": "function_result",
            "name": "get_image",
            "call_id": "call_123",
            "result": [
              {"type": "text", "text": "instrument.jpg"},
              {
                "type": "image",
                "mime_type": "image/jpeg",
                "data": "BASE64_IMAGE_DATA"
              }
            ]
          }
        ]
      }'

## Function calling with Structured output

For Gemini 3 series models, combine function calling with
[structured output](https://ai.google.dev/gemini-api/docs/interactions/structured-output) for
consistently formatted responses.

## Remote MCP (Model Context Protocol)

Interactions API supports connecting to remote MCP servers to give the model access to external tools and services. You provide the server `name` and `url` in the tools configuration.

When using Remote MCP, be aware of the following constraints:

- **Server types**: Remote MCP only works with Streamable HTTP servers. SSE (Server-Sent Events) servers are not supported.
- **Model support**: Remote MCP does not work with Gemini 3 models at this time. Support for Gemini 3 is coming soon.
- **Naming** : MCP server names should not include the `-` character. Use `snake_case` server names instead.

| Field           | Type     | Required | Description                                                                                                 |
| --------------- | -------- | -------- | ----------------------------------------------------------------------------------------------------------- |
| `type`          | `string` | Yes      | Must be `"mcp_server"`.                                                                                     |
| `name`          | `string` | No       | A display name for the MCP server.                                                                          |
| `url`           | `string` | No       | The full URL for the MCP server endpoint.                                                                   |
| `headers`       | `object` | No       | Key-value pairs sent as HTTP headers with every request to the server (for example, authentication tokens). |
| `allowed_tools` | `array`  | No       | Restrict which tools from the server the agent may call.                                                    |

### Example

### Python

    from google import genai

    client = genai.Client()

    interaction = client.interactions.create(
        model="gemini-2.5-flash",
        input="Check the status of my last server deployment.",
        tools=[
            {
                "type": "mcp_server",
                "name": "Deployment Tracker",
                "url": "https://mcp.example.com/mcp",
                "headers": {"Authorization": "Bearer my-token"},
            }
        ]
    )

### JavaScript

    import { GoogleGenAI } from '@google/genai';

    const client = new GoogleGenAI({});

    const interaction = await client.interactions.create({
        model: 'gemini-2.5-flash',
        input: 'Check the status of my last server deployment.',
        tools: [
            {
                type: 'mcp_server',
                name: 'Deployment Tracker',
                url: 'https://mcp.example.com/mcp',
                headers: { Authorization: 'Bearer my-token' }
            }
        ]
    });

### REST

    curl -X POST "https://generativelanguage.googleapis.com/v1beta/interactions" \
    -H "Content-Type: application/json" \
    -H "x-goog-api-key: $GEMINI_API_KEY" \
    -d '{
        "model": "gemini-2.5-flash",
        "input": "Check the status of my last server deployment.",
        "tools": [
            {
                "type": "mcp_server",
                "name": "Deployment Tracker",
                "url": "https://mcp.example.com/mcp",
                "headers": {"Authorization": "Bearer my-token"}
            }
        ]
    }'

## Stream tool calls

When using tools with streaming, the model generates function calls as a
sequence of `step.delta` events on the stream. Tool arguments can be streamed as partial arguments using `arguments`. You must aggregate these deltas to reconstruct the complete tool calls before executing them.

### Python

    import json
    from google import genai

    client = genai.Client()

    weather_tool = {
        "type": "function",
        "name": "get_weather",
        "description": "Gets the weather for a given location.",
        "parameters": {
            "type": "object",
            "properties": {
                "location": {"type": "string", "description": "The city and state"}
            },
            "required": ["location"]
        }
    }

    stream = client.interactions.create(
        model="gemini-3-flash-preview",
        input="What is the weather in Paris?",
        tools=[weather_tool],
        stream=True
    )

    current_calls = {}
    tool_calls = []

    for event in stream:
        if event.event_type == "step.start":
            if event.step.type == "function_call":
                current_calls[event.index] = {
                    "id": event.step.id,
                    "name": event.step.name,
                    "arguments": ""
                }
        elif event.event_type == "step.delta":
            if event.delta.type == "arguments":
                if event.index in current_calls:
                    current_calls[event.index]["arguments"] += event.delta.partial_arguments
            elif event.delta.type == "text":
                print(event.delta.text, end="", flush=True)

        elif event.event_type == "interaction.completed":
            for index, call in current_calls.items():
                args = call["arguments"]
                if args:
                    args = json.loads(args)
                else:
                    args = {}

                tool_calls.append({
                    "type": "function_call",
                    "id": call["id"],
                    "name": call["name"],
                    "arguments": args
                })

            print(f"\nFinal tool calls ready to execute:")
            print(json.dumps(tool_calls, indent=2))

### JavaScript

    import { GoogleGenAI } from '@google/genai';

    const client = new GoogleGenAI({});

    const weatherTool = {
        type: 'function',
        name: 'get_weather',
        description: 'Gets the weather for a given location.',
        parameters: {
            type: 'object',
            properties: {
                location: { type: 'string', description: 'The city and state' }
            },
            required: ['location']
        }
    };

    const stream = await client.interactions.create({
        model: 'gemini-3-flash-preview',
        input: 'What is the weather in Paris?',
        tools: [weatherTool],
        stream: true,
    });

    const currentCalls = new Map();
    let toolCalls = [];

    for await (const event of stream) {
        if (event.type === 'step.start') {
            if (event.step.type === 'function_call') {
                currentCalls.set(event.index, {
                    id: event.step.id,
                    name: event.step.name,
                    arguments: ''
                });
            }
        } else if (event.type === 'step.delta') {
            if (event.delta.type === 'arguments') {
                if (currentCalls.has(event.index)) {
                    currentCalls.get(event.index).arguments += event.delta.partial_arguments;
                }
            } else if (event.delta.type === 'text') {
                process.stdout.write(event.delta.text);
            }
        } else if (event.type === 'interaction.completed') {
            toolCalls = Array.from(currentCalls.values()).map(call => ({
                type: 'function_call',
                id: call.id,
                name: call.name,
                arguments: call.arguments ? JSON.parse(call.arguments) : {}
            }));
            console.log('\nFinal tool calls ready to execute:');
            console.log(JSON.stringify(toolCalls, null, 2));
        }
    }

### REST

    curl -X POST "https://generativelanguage.googleapis.com/v1beta/interactions?alt=sse" \
    -H "Content-Type: application/json" \
    -H "x-goog-api-key: $GEMINI_API_KEY" \
    -d '{
        "model": "gemini-3-flash-preview",
        "input": "What is the weather in Paris?",
        "tools": [{
            "type": "function",
            "name": "get_weather",
            "description": "Gets the weather for a given location.",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {"type": "string", "description": "The city and state"}
                },
                "required": ["location"]
            }
        }],
        "stream": true
    }'

## Supported models

| Model                  | Function Calling | Parallel | Compositional |
| ---------------------- | ---------------- | -------- | ------------- |
| Gemini 3.1 Pro Preview | ✔️               | ✔️       | ✔️            |
| Gemini 3 Flash Preview | ✔️               | ✔️       | ✔️            |
| Gemini 2.5 Pro         | ✔️               | ✔️       | ✔️            |
| Gemini 2.5 Flash       | ✔️               | ✔️       | ✔️            |
| Gemini 2.5 Flash-Lite  | ✔️               | ✔️       | ✔️            |
| Gemini 2.0 Flash       | ✔️               | ✔️       | ✔️            |
| Gemini 2.0 Flash-Lite  | X                | X        | X             |

## Best practices

- **Function and Parameter Descriptions:** Be clear and specific.
- **Naming:** Use descriptive names without spaces or special characters.
- **Strong Typing:** Use specific types (integer, string, enum).
- **Tool Selection:** Keep active set to 10-20 tools maximum.
- **Prompt Engineering:** Provide context and instructions.
- **Temperature:** Use low temperature (e.g., 0) for deterministic calls.

    > [!NOTE]
    > When using Gemini 3 models, we strongly recommend keeping the `temperature` at its default value of 1.0. Changing the temperature (setting it less than 1.0) may lead to unexpected behavior, such as looping or degraded performance, particularly in complex mathematical or reasoning tasks.

- **Validation:** Validate function calls before executing.

- **Error Handling:** Implement robust error handling.

- **Security:** Use appropriate authentication for external APIs.

## Notes and limitations

- Only a [subset of the OpenAPI schema](https://ai.google.dev/api/rest/v1beta/cachedContents#FunctionDeclaration) is supported.
- For `any` mode, the API may reject very large or deeply nested schemas.
- Supported parameter types in Python are limited.
