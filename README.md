# DeepFlow Sentinel

**DeepFlow Sentinel** is an intelligent defense system designed to protect cognitive capacity through context-aware scheduling and dynamic prioritization. It serves as a digital bodyguard that intercepts distractions and manages your attention flow, allowing for sustained deep work.

For a comprehensive Deep Dive into the philosophy, architecture, and "Evaluation-Driven Development" strategy, please refer to the [Technical White Paper](deepflow.md).

## Project Structure

The project is organized into three main components based on the "Sentinel" architecture:

- **`frontend/` (The Sentinel Client)**: 
  - **Stack**: Next.js (App Router), Shadcn/UI.
  - **Role**: Provides the user interface for the "Focus Player" and "Queue" visualization.
  
- **`backend/` (The Action Engine & API)**:
  - **Stack**: Python FastAPI, Supabase, Redis.
  - **Role**: Manages the priority queue (Redis ZSET), handles webhooks (Slack, Jira, Gmail), and serves as the central API gateway.

- **`agent/` (The Brain)**:
  - **Stack**: Python, LangChain, Opik.
  - **Role**: The semantic engine responsible for analyzing incoming signals, scoring urgency, and generating context-aware responses.

## Prerequisites

- **Python**: >= 3.13 (We recommend using [uv](https://github.com/astral-sh/uv) for dependency management)
- **Node.js**: >= 18 (for Frontend)
- **Docker**: For running local infrastructure (Redis)

## Getting Started

### 1. Infrastructure (Redis)

Start the local Redis instance required for the priority queue:

```bash
cd backend
docker-compose up -d
```

### 2. Backend Setup

Initialize the backend environment:

```bash
cd backend
uv sync
# Run the development server (or entry point)
uv run main.py
```

*Note: Ensure you create a `.env` file from `.env.example` if applicable.*

### 3. Agent Setup

Initialize the agent environment:

```bash
cd agent
uv sync
# Run the agent logic
uv run main.py
```

### 4. Frontend Setup

Start the Next.js development server:

```bash
cd frontend
npm install
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) to view the application.

## Key Technologies

- **Prioritization**: Redis Sorted Sets (ZSET) for O(log N) dynamic priority queueing.
- **Observability**: **Opik** is deeply integrated for tracing agent thoughts and evaluating semantic accuracy ("Evaluation-Driven Development").
- **Agent Framework**: LangChain for orchestrating LLM interactions.

## License

See [LICENSE](LICENSE) file for details.
