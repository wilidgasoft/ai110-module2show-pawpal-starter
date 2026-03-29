# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

- Initial UML design.

## 1. Owner

Represents the person using the app.

## 2. Pet

Represents a pet owned by the owner.

## 3. Vet

Represents the pet's veterinarian. Used to store contact info and medical recommendations.

## 4. CareTask

Represents a single pet care activity.

## 5. Schedule

Holds the ordered list of tasks assigned to a specific time window. The raw output before the Plan wraps it with reasoning.

## 6. Plan

Wraps a Schedule and adds the reasoning/explanation shown to the user in the UI.

**b. Design changes**

AI found some bottlenecks, like Missin Relationships:

1. Vet.recommended_tasks is disconnected from Pet.care_tasks
   The UML says a Vet prescribes tasks, but there's no bridge. When a vet adds a recommendation, it only lives inside Vet — it never flows into Pet.care_tasks. You'll need a method like Pet.sync_vet_tasks() or handle the merge inside Plan.generate().

2. Owner has no direct link to Schedule
   The UML shows Owner 1 ── 1 Schedule. Right now Schedule holds a reference to Owner, but Owner has no schedule attribute — the relationship is one-directional. This is fine if Plan.generate() owns the lifecycle, but worth being intentional about it.

3. Plan.generate() takes owner and pet but must also build a Schedule
   There's no date parameter. Schedule requires a date, so generate() either needs a date argument or must derive it internally. This is a bottleneck waiting to happen.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- The scheduler considers three constraints: **time** (owner's available minutes per day), **priority** (1–5 scale per task), and **requirement status** (required vs. optional). It also detects **time conflicts** when two tasks overlap based on their start time and duration.
- Required tasks were treated as the hardest constraint because skipping them has real consequences for the pet's health (medications, feeding). Priority breaks ties among optional tasks. Time budget is checked last — it gates optional tasks but never drops required ones.

**b. Tradeoffs**

- The scheduler always includes required tasks regardless of the owner's time budget, even if doing so exceeds it. Optional tasks are only added if time remains after required ones are placed.
- This is reasonable because pet care has non-negotiable duties — skipping a medication or feeding to "fit the budget" would harm the animal. Exceeding the time budget is a recoverable problem; missing a required task is not.

---

## 3. AI Collaboration

**a. How you used AI**

- I used AI to generate test cases, refactor code, and create the UML design.
- Fixed some bugs and asked for help understanding some lambdas and functions.

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
  In refactor son functions.
- How did you evaluate or verify what the AI suggested?
  With test cases and asking why.

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
  Generating and scheduling care tasks for a pet, ensuring that required tasks
  are always included and optional tasks are added based on available time and priority.
- Why were these tests important?
  Because they help verify that the scheduling logic works correctly and delivers
  a reliable experience for the user.

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?
  Building a functional MVP from scratch using only the project requirements as context.

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?
  Adding multiple views instead of just one, such as a card-based layout.

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
  Learning to go back and update the design to reflect changes made during implementation,
  keeping the UML and the code in sync.
