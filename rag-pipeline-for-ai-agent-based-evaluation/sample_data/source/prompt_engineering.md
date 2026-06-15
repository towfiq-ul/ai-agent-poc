# Prompt Engineering

## What is Prompt Engineering?

Prompt engineering is the practice of designing and refining inputs to language models to elicit accurate, useful, and reliable outputs. It is a key skill for working with LLMs effectively, and does not require model fine-tuning or access to model weights.

## Core Techniques

### Zero-Shot Prompting
Ask the model to perform a task without providing any examples. Relies on the model's pre-trained knowledge.

Example: "Classify the sentiment of this review as positive or negative: 'The product broke after two days.'"

### Few-Shot Prompting
Provide a small number of input-output examples before the actual task. This helps the model understand the expected format and reasoning style.

Example:
- "sunny day" → positive
- "stuck in traffic" → negative
- "found a £10 note" → ?

### Chain-of-Thought (CoT) Prompting
Encourage the model to reason step by step before giving a final answer. This significantly improves performance on arithmetic, commonsense, and symbolic reasoning tasks.

Trigger phrase: "Let's think step by step."

CoT can be zero-shot (just adding the trigger) or few-shot (providing examples with reasoning chains).

### ReAct (Reason + Act)
A framework where the model alternates between reasoning steps and actions (like tool calls or web searches). The model generates a Thought, then an Action, observes the result, and repeats until it can give a final answer.

Useful for agentic tasks where the model needs to interact with external systems.

### Tree of Thoughts (ToT)
An extension of CoT where the model explores multiple reasoning paths simultaneously. It evaluates intermediate steps and backtracks from dead ends, like a search tree. Useful for complex planning and puzzle-solving tasks.

### Self-Consistency
Generate multiple chain-of-thought reasoning paths and take the majority vote on the final answer. More robust than a single pass.

### Role Prompting
Assign the model a persona to improve performance: "You are an expert Python developer. Review this code for bugs."

## Prompt Components

A well-structured prompt often includes:
1. **Instruction** – What you want the model to do
2. **Context** – Background information
3. **Input data** – The specific data to process
4. **Output format** – Desired format (JSON, bullet points, XML tags, etc.)

## Output Structuring

Asking the model to output in a structured format (XML, JSON, Markdown) makes it easier to parse programmatically. Using XML tags like `<answer>`, `<reasoning>` etc. is particularly reliable with models like Claude and Gemini.

## System Prompts

System prompts are instructions provided at the start of a conversation to set the model's behavior, persona, and constraints. They are separate from user messages and typically have higher authority in shaping responses.

## Common Pitfalls

- **Ambiguity**: Vague prompts lead to vague answers. Be specific about format and scope.
- **Prompt injection**: Malicious input that tries to override instructions. Mitigate with delimiters and input sanitization.
- **Hallucination**: Models may confidently produce incorrect information. Mitigate with grounding (RAG) and asking the model to say "I don't know" when uncertain.
- **Over-prompting**: Too many constraints can confuse the model. Start simple and iterate.

## Prompt Iteration Workflow

1. Start with a simple prompt
2. Identify failure modes on test cases
3. Add constraints, examples, or formatting guidance
4. Evaluate on a broader set
5. Repeat

## Gemini-Specific Tips

- Gemini responds well to structured prompts with clear delimiters
- Use `system_instruction` for persistent behavior instructions
- Gemini 2.0 Flash is fast and cost-effective for most tasks
- For complex reasoning, use `gemini-2.0-pro` or enable thinking mode
