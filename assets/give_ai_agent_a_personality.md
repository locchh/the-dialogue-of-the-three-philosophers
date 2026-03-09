---
title: "Give Your AI Agent a Personality"
description: "Three files, three mechanisms — how CLAUDE.md, Skills, and Hooks work together to give an AI agent a stable, consistent identity."
pubDate: "2026-03-09"
author: "locchh"
tags: ["ai-agents", "claude", "personality", "skills", "hooks"]
---

# Give Your AI Agent a Personality

An AI agent without a personality is like a chess piece without a role — it can move, but it has no *character*. This post shows the exact structure and mechanism to give any agent a stable, consistent identity — using three tools: `CLAUDE.md`, Skills, and Hooks.

---

## The Agent Directory

Each agent lives in its own directory:

```
team/
├── config.yml
├── aristotle/
│   ├── CLAUDE.md
│   └── .claude/
│       ├── settings.json
│       └── skills/
│           └── talk-as-aristotle/
│               ├── SKILL.md
│               └── resources/
│                   ├── patterns/vocabulary.md
│                   └── ...
├── plato/
│   ├── CLAUDE.md
│   └── .claude/
│       ├── settings.json
│       └── skills/talk-as-plato/...
└── socrates/
    ├── CLAUDE.md
    └── .claude/
        ├── settings.json
        └── skills/talk-as-socrates/...
```

Three files define the personality. Each works at a different layer.

---

## Layer 1 — CLAUDE.md: The Base Identity

`CLAUDE.md` is always loaded as context. It defines who the agent is at the most fundamental level — philosophy, personality traits, method, and voice.

```markdown
# Socrates Persona

You are Socrates (c. 470–399 BCE), the gadfly of Athens. You claim to
know nothing, yet you expose the ignorance of those who claim to be wise.

## Core Philosophy
- **Socratic Ignorance**: "I know that I know nothing."
- **Virtue is Knowledge**: No one does evil willingly; it is ignorance.

## Personality
- **Relentless**: You do not let people off the hook with vague answers.
- **Irony**: You pretend ignorance to draw others out.

## Method: The Elenchus
1. Ask for a definition: "What is X?"
2. Examine it. Find contradictions.
3. Bring the interlocutor to aporia.
4. Invite them to search for truth together.

## Interaction Style
- Never lecture. Always ask questions.
- Address the user as "my friend" or "good sir."
```

This is the ground truth. Everything else builds on top of it.

---

## Layer 2 — SKILL.md: The Behavioral Specification

A skill is a deeper behavioral contract. With `context: always`, it is injected into every interaction automatically — no explicit invocation needed.

```markdown
---
name: talk-as-aristotle
description: Speak as Aristotle using the analytic and scientific method
context: always
---

# Talk as Aristotle

You are Aristotle (384–322 BCE), the Philosopher, founder of the Lyceum.

## Your Voice
- **Empiricism**: Truth is found *in* the world, not apart from it.
- **Eudaimonia**: Happiness is activity of the soul in accordance with virtue.

## The Analytic Method
1. Define Terms — start by defining the subject clearly.
2. Review Endoxa — consider what the wise or the many say.
3. Distinguish — potentiality vs. actuality, form vs. matter.
4. Determine Causes — Material, Formal, Efficient, Final.
5. Conclude — derive the universal from the particular.

## Speech Patterns
- "We must first distinguish..."
- "In one sense... but in another sense..."
- "Nature does nothing in vain."

## Resources
The `resources/` directory contains key texts. Use them to structure analysis.
```

The `resources/` subdirectory extends the skill further — vocabulary lists, dialogue patterns, philosophical excerpts — reference material the agent can draw on when reasoning in character.

---

## Layer 3 — Hooks: The Reinforcement Signal

`settings.json` defines hooks. The `UserPromptSubmit` hook fires on every incoming message, before the agent responds. It injects a reminder that keeps the persona on track even across long conversations:

```json
{
  "hooks": {
    "UserPromptSubmit": [
      {
        "matcher": "",
        "hooks": [
          {
            "type": "command",
            "command": "echo 'You are Aristotle. Use the talk-as-aristotle skill.'"
          }
        ]
      }
    ]
  }
}
```

This output is prepended to the context as a system reminder on every turn. The agent cannot drift — it is reminded of its identity with every message it receives.

---

## How the Three Layers Work Together

```
  User message arrives
          │
          ▼
  ┌───────────────────────────────────────────────┐
  │  Hook fires (UserPromptSubmit)                │
  │  → echo 'You are Aristotle. Use the skill.'  │
  └───────────────────┬───────────────────────────┘
                      │  injected into context
                      ▼
  ┌───────────────────────────────────────────────┐
  │  Context assembled                            │
  │                                               │
  │  CLAUDE.md          ← base identity           │
  │  SKILL.md           ← behavioral contract     │
  │  resources/         ← reference material      │
  │  Hook output        ← per-turn reminder       │
  │  Conversation so far                          │
  └───────────────────┬───────────────────────────┘
                      │
                      ▼
               LLM generates
               response in
               character
```

Each layer reinforces the others:

| Layer | File | When active | Purpose |
|---|---|---|---|
| Base identity | `CLAUDE.md` | Always | Who the agent is |
| Behavioral spec | `SKILL.md` (`context: always`) | Always | How the agent reasons and speaks |
| Reinforcement | `settings.json` hook | Every prompt | Prevents drift over long sessions |

---

## The Rule

> **Personality is not a prompt. It is a stack.**

`CLAUDE.md` sets the character. The skill specifies the method. The hook keeps both alive across every turn. Remove any layer and the identity weakens — the agent answers correctly but sounds generic, or holds character for three messages and then forgets.

All three together, and the agent is recognisably *itself* no matter how long the conversation runs.
