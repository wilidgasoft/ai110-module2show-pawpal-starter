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

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
