# Prompting Techniques: Zero-Shot, Few-Shot, and Chain-of-Thought

This document provides clear examples of three fundamental prompting techniques using product review sentiment analysis as a use case.

---

## Use Case: Product Review Sentiment Analysis

**Task**: Analyze customer product reviews and classify them as POSITIVE, NEGATIVE, or NEUTRAL, along with extracting key themes.

---

## 1. Zero-Shot Prompting

**Definition**: Asking the model to perform a task without providing any examples.

### Example Prompt:

```
Analyze the following product review and classify its sentiment as POSITIVE, NEGATIVE, or NEUTRAL. Also identify the main themes mentioned (e.g., quality, price, customer service, delivery).

Output your analysis as JSON with these fields:
- sentiment: POSITIVE | NEGATIVE | NEUTRAL
- confidence: 0.0 to 1.0
- themes: array of strings
- summary: brief explanation

Review: "I've been using this coffee maker for 3 weeks now. The coffee tastes great and it's easy to clean. However, it arrived 5 days late and the box was damaged. Customer service was helpful in resolving the shipping issue. For the price, I'm satisfied overall."

Output:
```

### Expected Output:

```json
{
  "sentiment": "POSITIVE",
  "confidence": 0.75,
  "themes": ["quality", "ease of use", "delivery issues", "customer service", "value for money"],
  "summary": "Overall positive review despite shipping problems. Customer appreciates product quality and service recovery."
}
```

### Characteristics:
- Simple and direct
- Works well with capable models
- May produce inconsistent output format
- Model might interpret task differently than intended
- Less reliable for complex or nuanced tasks

---

## 2. Few-Shot Prompting

**Definition**: Providing 2-4 examples of the desired input-output format to teach the model the task pattern.

### Example Prompt:

```
Analyze product reviews and classify sentiment. Output JSON with sentiment, confidence, themes, and summary.

Example 1:
Review: "This laptop is amazing! Super fast, beautiful display, and the battery lasts all day. Worth every penny."

Output:
{
  "sentiment": "POSITIVE",
  "confidence": 0.95,
  "themes": ["performance", "display quality", "battery life", "value for money"],
  "summary": "Highly enthusiastic review praising multiple product features with no negative aspects mentioned."
}

Example 2:
Review: "Terrible experience. The blender broke after one week. I tried to contact support but never got a response. Complete waste of $80."

Output:
{
  "sentiment": "NEGATIVE",
  "confidence": 0.98,
  "themes": ["product durability", "customer service", "value for money"],
  "summary": "Strong negative review citing product failure and poor customer service response."
}

Example 3:
Review: "It's okay. Does what it's supposed to do. Nothing special but nothing terrible either. Shipping was fast."

Output:
{
  "sentiment": "NEUTRAL",
  "confidence": 0.85,
  "themes": ["basic functionality", "delivery"],
  "summary": "Lukewarm review indicating adequate but unremarkable product performance."
}

Now analyze this review:
Review: "I've been using this coffee maker for 3 weeks now. The coffee tastes great and it's easy to clean. However, it arrived 5 days late and the box was damaged. Customer service was helpful in resolving the shipping issue. For the price, I'm satisfied overall."

Output:
```

### Expected Output:

```json
{
  "sentiment": "POSITIVE",
  "confidence": 0.80,
  "themes": ["product quality", "ease of use", "delivery issues", "customer service", "value for money"],
  "summary": "Mostly positive review with mixed elements. Product quality praised despite shipping problems, which were resolved by good customer service."
}
```

### Characteristics:
- Much more consistent output format
- Model learns the pattern and level of detail expected
- Examples demonstrate edge cases (mixed sentiment)
- Teaches the model nuances (e.g., how to handle contradictory elements)
- Requires thoughtful example selection
- Longer prompt = higher token cost

---

## 3. Chain-of-Thought (CoT) Prompting

**Definition**: Encouraging the model to show its reasoning process step-by-step before arriving at a conclusion.

### Example Prompt:

```
Analyze product reviews using step-by-step reasoning before making a final classification.

Example 1:
Review: "This laptop is amazing! Super fast, beautiful display, and the battery lasts all day. Worth every penny."

Reasoning:
1. Identify sentiment indicators:
   - Positive: "amazing", "super fast", "beautiful", "worth every penny"
   - Negative: None
   - Neutral: None
2. Assess strength: Multiple strong positive adjectives, enthusiastic tone
3. Extract themes: Performance mentioned ("fast"), display quality, battery life, value
4. Check for contradictions: None - consistently positive throughout
5. Determine confidence: Very high (0.95) - unambiguous positive sentiment

Output:
{
  "sentiment": "POSITIVE",
  "confidence": 0.95,
  "themes": ["performance", "display quality", "battery life", "value for money"],
  "summary": "Highly enthusiastic review praising multiple product features with no negative aspects mentioned."
}

Example 2:
Review: "I've been using this coffee maker for 3 weeks now. The coffee tastes great and it's easy to clean. However, it arrived 5 days late and the box was damaged. Customer service was helpful in resolving the shipping issue. For the price, I'm satisfied overall."

Reasoning:
1. Identify sentiment indicators:
   - Positive: "great", "easy to clean", "helpful", "satisfied overall"
   - Negative: "5 days late", "box was damaged"
   - Neutral: "For the price" (conditional satisfaction)
2. Assess strength: Mixed - positive product experience, negative shipping, but resolved
3. Extract themes: Product quality (coffee taste, ease of use), delivery issues, customer service, value
4. Check for contradictions: Yes - shipping problems BUT good service recovery
5. Weight the elements: Product experience (ongoing) outweighs shipping (one-time), final statement is "satisfied overall"
6. Determine confidence: Moderate-high (0.80) - clearly leans positive despite shipping issue

Output:
{
  "sentiment": "POSITIVE",
  "confidence": 0.80,
  "themes": ["product quality", "ease of use", "delivery issues", "customer service", "value for money"],
  "summary": "Mostly positive review with mixed elements. Product quality praised despite shipping problems, which were resolved by good customer service."
}

Now analyze this review using step-by-step reasoning:
Review: "The headphones have good sound quality, but they're uncomfortable after an hour. Battery life is as advertised. Not sure if I'll keep them."

Reasoning:
```

### Expected Output:

```
Reasoning:
1. Identify sentiment indicators:
   - Positive: "good sound quality", "battery life is as advertised"
   - Negative: "uncomfortable after an hour", "not sure if I'll keep them"
   - Neutral: None explicit, but final statement shows uncertainty
2. Assess strength: Balanced - one strong positive, one significant negative, uncertainty about keeping
3. Extract themes: Audio quality, comfort/ergonomics, battery life, purchase decision uncertainty
4. Check for contradictions: Mixed satisfaction - meets some expectations but fails on comfort
5. Weight the elements: Comfort is a major factor for headphones (daily use), uncertainty about keeping suggests dissatisfaction
6. Determine confidence: Moderate (0.65) - genuinely mixed review, slightly negative due to return consideration

Output:
{
  "sentiment": "NEUTRAL",
  "confidence": 0.65,
  "themes": ["sound quality", "comfort", "battery life", "purchase uncertainty"],
  "summary": "Mixed review with both positive (sound, battery) and negative (comfort) elements. Customer uncertainty about keeping the product suggests moderate dissatisfaction despite some good features."
}
```

### Characteristics:
- Produces more accurate results for complex/ambiguous cases
- Reasoning is transparent and auditable
- Helps model handle contradictory information
- Better at weighing multiple factors appropriately
- Longer prompts and responses = higher cost
- May be overkill for simple cases
- Requires more carefully designed examples

---

## When to Use Each Technique

### Use Zero-Shot When:
- Task is straightforward and unambiguous
- Using a very capable model (GPT-4, Claude Opus)
- Need minimal prompt length for cost/speed
- Quick prototyping or testing

### Use Few-Shot When:
- Need consistent, structured output format (like JSON)
- Task has nuances that need to be demonstrated
- Model needs to understand edge cases
- Balance between accuracy and prompt length
- **This is the most common choice for production systems**

### Use Chain-of-Thought When:
- Task requires multi-step reasoning
- Dealing with ambiguous or contradictory information
- Need to audit/explain AI decisions
- Accuracy is more important than speed/cost
- Complex business logic needs to be applied

---

## Key Takeaways

1. **Few-Shot is your default**: For most production use cases, few-shot prompting provides the best balance of accuracy, consistency, and cost.

2. **Examples are teaching tools**: Your few-shot examples should cover:
   - Clear positive cases
   - Clear negative cases
   - Edge cases or ambiguous situations
   - Different variations of input format

3. **CoT for complexity**: Use chain-of-thought when you need the model to "show its work" or handle genuinely complex reasoning.

4. **Start simple, add complexity**: Begin with zero-shot to understand the baseline, then add examples (few-shot) or reasoning steps (CoT) only if needed.

---

## Connection to the Expense Approval Exercise

In the expense approval exercise, you'll use **few-shot prompting** because:
- You need consistent JSON output format
- The task has business rules that need demonstration
- Edge cases exist (expenses near limits, missing information)
- You want predictable, structured results
- Balance of accuracy and cost is important

Your few-shot examples will teach the model:
- How to extract structured data from unstructured text
- How to apply company policy rules
- How to make approval decisions with proper reasoning
- What level of detail to include in justifications
