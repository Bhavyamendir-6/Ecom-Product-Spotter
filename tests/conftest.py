import pytest
import sys
from pathlib import Path
from unittest.mock import MagicMock

# Ensure agent root is on path for test imports
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


@pytest.fixture
def mock_tool_context():
    ctx = MagicMock()
    ctx.state = {}
    return ctx


@pytest.fixture
def mock_llm_response():
    resp = MagicMock()
    resp.text = "Mocked LLM response for testing."
    resp.content = MagicMock()
    resp.content.parts = [MagicMock(text="Mocked LLM response for testing.")]
    return resp


@pytest.fixture
def sample_trending_terms():
    return [
        {"title": "Best buy fitness tracker 2026", "score": 950, "num_comments": 120,
         "upvote_ratio": 0.95, "comment_velocity": 5.2,
         "subreddit": "gadgets", "created_utc": 1710000000.0,
         "post_url": "https://reddit.com/r/gadgets/comments/abc123/best_buy_fitness_tracker",
         "source": "reddit_search"},
        {"title": "Home gym equipment recommendations", "score": 820, "num_comments": 85,
         "upvote_ratio": 0.91, "comment_velocity": 3.1,
         "subreddit": "BuyItForLife", "created_utc": 1710000000.0,
         "post_url": "https://reddit.com/r/BuyItForLife/comments/def456/home_gym_equipment",
         "source": "reddit_search"},
        {"title": "Yoga mat that actually lasts", "score": 700, "num_comments": 60,
         "upvote_ratio": 0.88, "comment_velocity": 2.0,
         "subreddit": "BuyItForLife", "created_utc": 1710000000.0,
         "post_url": "https://reddit.com/r/BuyItForLife/comments/ghi789/yoga_mat",
         "source": "reddit_hot"},
        {"title": "Resistance bands cheap and durable", "score": 600, "num_comments": 45,
         "upvote_ratio": 0.85, "comment_velocity": 1.5,
         "subreddit": "deals", "created_utc": 1710000000.0,
         "post_url": "https://reddit.com/r/deals/comments/jkl012/resistance_bands_cheap",
         "source": "reddit_search"},
        {"title": "Treadmill under $500", "score": 0, "num_comments": 0,
         "upvote_ratio": 0.5, "comment_velocity": 0.0,
         "subreddit": "deals", "created_utc": 1710000000.0,
         "post_url": "https://reddit.com/r/deals/comments/mno345/treadmill",
         "source": "reddit_hot"},
    ]
