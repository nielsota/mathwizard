# MathWizard Frontend

React, TypeScript, and Vite frontend for MathWizard.

## Commands

Install dependencies:

```bash
npm install
```

Start the Vite dev server:

```bash
npm run dev -- --host 0.0.0.0
```

Build for production:

```bash
npm run build
```

Run linting:

```bash
npm run lint
```

## API Contract

The practice page fetches question lists from the FastAPI backend:

```text
GET /api/v1/practice/:topic
```

The response shape is defined in `src/types/api.ts` as `QuestionListResponse`. Exercise cards render MathJax question text, part text, marks, difficulty, topic, and tags from that response.

During local development, run the backend at http://localhost:8000 and this frontend at http://localhost:3000.
