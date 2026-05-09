# Model Card — PawPal+ AI System

## Model Details
- **Base Model:** Google Gemini 2.5 Flash (`gemini-2.5-flash`)
- **Provider:** Google AI (Gemini API)
- **Interface:** Streamlit web app with agentic tool-calling and RAG pipeline

## Intended Use
PawPal+ AI is designed to help pet owners manage daily care schedules through natural language. It can answer pet care questions, add tasks, generate optimized schedules, and detect conflicts — all via conversational chat.

## AI Features Implemented

### Retrieval-Augmented Generation (RAG)
- A TF-IDF vectorized knowledge base (`pet_care_kb.txt`) covering dogs, cats, rabbits, and birds
- Retrieved top-3 relevant chunks are injected into the system prompt before every response
- Ensures answers are grounded in factual pet care information rather than model hallucination

### Agentic Workflow
The chatbot uses Gemini function-calling to execute real actions in the app:
| Tool | What It Does |
|------|-------------|
| `list_pets` | Shows all registered pets and task counts |
| `list_tasks` | Lists tasks for one or all pets |
| `add_task` | Adds a new task to a pet's schedule |
| `generate_schedule` | Runs the greedy scheduler and returns the optimized plan |
| `check_conflicts` | Detects time-slot and budget conflicts |

The agent loops up to 5 iterations, executing tools and feeding results back until it produces a final text response.

## Limitations and Biases
- **Knowledge cutoff:** The RAG knowledge base is static and manually curated — it does not update automatically with new veterinary guidelines.
- **Species coverage:** Knowledge base covers dogs, cats, rabbits, and birds. Exotic pets (reptiles, fish) have limited coverage.
- **No medical diagnosis:** The system is not a substitute for veterinary advice. It should not be used to diagnose illness or prescribe treatment.
- **Gemini model bias:** Responses reflect the base model's training data and may occasionally produce confident but incorrect statements (hallucination).
- **Single-owner scope:** The system is designed for one owner at a time; it has no multi-user or household-sharing features.

## Potential Misuse & Safeguards
- **Medical advice risk:** Users may treat AI responses as veterinary diagnoses. The knowledge base explicitly directs users to seek a vet for health concerns.
- **Overreliance on scheduling:** The scheduler is a planning aid, not a guarantee. Owners must exercise judgment for medication timing and emergency care.
- **Guardrails in place:** Error handling logs all failures to `pawpal.log`; the agentic loop is capped at 5 iterations to prevent runaway API calls.

## Testing Summary
- **34 unit tests** covering Task, Pet, Owner, and Scheduler classes (all passing)
- **RAG retrieval** verified manually across 10 query types — correct top chunks returned in 9/10 cases
- **Agentic tools** tested with natural language inputs: "add a walk", "show my schedule", "check conflicts" — all executed correctly
- **Edge cases tested:** Empty pet list, zero time budget, duplicate task names, missing scheduled times
- **Known limitation:** When the user's request is ambiguous (e.g., "add something for my dog"), the agent asks for clarification rather than guessing — this is intentional behavior

## AI Collaboration Reflection

### Helpful AI Suggestion
Claude suggested using TF-IDF cosine similarity for the RAG retrieval layer instead of a heavyweight embedding model. This was the right call — it keeps the system lightweight and dependency-free while still retrieving relevant chunks effectively for a domain-specific knowledge base of this size.

### Flawed AI Suggestion
Claude initially suggested using `gemini-1.5-flash` as the model name, which caused a 404 error because that model version was deprecated in the API. The correct model (`gemini-2.5-flash`) was discovered by calling `list_models()` directly — a good reminder to verify model availability rather than assuming names from documentation.

### What This Project Taught Me
Building a RAG + agentic system revealed how much scaffolding "intelligence" requires: retrieval, tool routing, loop management, and error handling. The AI itself is only as reliable as the context you give it. Injecting structured knowledge (RAG) and grounded state (pet/task data) dramatically improved response quality compared to a vanilla chatbot. Reliability comes from design, not just model capability.
