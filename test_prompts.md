# E-Commerce Product Spotter - Test Prompts

## How It Works

The agent scans **Reddit's public JSON API** across 7 product-focused subreddits to surface trending product opportunities:

- r/shutupandtakemymoney
- r/BuyItForLife
- r/gadgets
- r/AmazonTopRated
- r/deals
- r/ProductPorn
- r/ecommerce

**Pipeline:** User keyword → Fetch Reddit posts → Score by opportunity → Generate seller report

**Best keywords:** Broad, single-word product categories yield the most results (e.g., `phone`, `knife`, `headphones`). Narrow or technical terms may return fewer posts.

---

## Section 1: Onboarding / Greeting Test

Use this to verify the agent starts correctly and asks for a keyword before running the pipeline.

### Test Prompt 1: Greeting
> "Hello! What can you help me with?"

**Expected behavior:** Agent greets the user, explains it discovers trending product opportunities from Reddit, and asks for a product keyword or category.

---

## Section 2: Full Pipeline Tests — Product Categories

Each prompt triggers the complete 3-stage pipeline: fetch → score → report. Paste these one at a time into the ADK Web UI.

### Test Prompt 2: Tech & Electronics
> "I'm looking for new tech accessories to sell. Can you check rising trends and product opportunities for 'phone'?"

**Subreddits likely active:** r/gadgets, r/shutupandtakemymoney, r/AmazonTopRated

---

### Test Prompt 3: Apparel & Fashion
> "What are the top Reddit discussions and commercial opportunities around 'shoe' right now? I want to find my next product line."

**Subreddits likely active:** r/deals, r/AmazonTopRated, r/BuyItForLife

---

### Test Prompt 4: Health & Wellness
> "Spot e-commerce opportunities around 'yoga' to help me decide on my next product line."

**Subreddits likely active:** r/BuyItForLife, r/deals, r/shutupandtakemymoney

---

### Test Prompt 5: Entertainment & Hobbies
> "I run a merchandise store. Are there any strong commercial trends or rising Reddit discussions for 'game'?"

**Subreddits likely active:** r/shutupandtakemymoney, r/ProductPorn, r/deals

---

### Test Prompt 6: Home & Lifestyle
> "Discover top trending terms and evaluate the commercial intent for 'bed' — I'm considering expanding into home goods."

**Subreddits likely active:** r/BuyItForLife, r/AmazonTopRated, r/deals

---

### Test Prompt 7: Kitchen & Cooking
> "I'm sourcing kitchen products. Can you find Reddit buzz and opportunity scores for 'knife'?"

**Subreddits likely active:** r/BuyItForLife, r/shutupandtakemymoney, r/ProductPorn

---

### Test Prompt 8: Fitness & Audio
> "Show me rising demand and seller opportunities for 'headphones' based on Reddit activity."

**Subreddits likely active:** r/gadgets, r/AmazonTopRated, r/deals

---

### Test Prompt 9: Outdoor & Travel
> "I want to enter the outdoor gear market. What's the Reddit sentiment and opportunity score for 'backpack'?"

**Subreddits likely active:** r/BuyItForLife, r/deals, r/shutupandtakemymoney

---

## Section 3: Multi-Turn Session Test

Tests that the agent handles follow-up keywords in the same session without restarting. Run these two prompts back-to-back in the same chat window.

### Turn 1
> "Find trending product opportunities for 'headphones'."

### Turn 2 (immediately after the report)
> "Thanks! Now can you run the same analysis for 'backpack'?"

**Expected behavior:** Agent runs a fresh pipeline for `backpack` using the same session, returning a new report without requiring a restart.

---

## Section 4: Edge Case Tests

### Test Prompt 10: Niche / Low-Volume Keyword
> "Can you find e-commerce opportunities for 'soldering'?"

**Expected behavior:** Agent completes the pipeline but returns a report with few or low-scoring results, with a graceful message (e.g., "minimal opportunity — skip for now" recommendations). Validates error handling and empty-result paths.

### Test Prompt 11: Very Broad Keyword
> "What's trending for 'buy' on Reddit right now?"

**Expected behavior:** Agent fetches results (likely many posts due to broad commercial term), scores them, and returns a report. Tests the deduplication and top-25 ranking logic under high-volume conditions.

---

## Running the Agent

```bash
# Start the web UI
adk web .
# Open http://localhost:8000

# Or run in terminal
adk run .
```

**Tip:** Run Test Prompts 2–9 sequentially in a single session to also implicitly test multi-keyword handling across the full pipeline.
