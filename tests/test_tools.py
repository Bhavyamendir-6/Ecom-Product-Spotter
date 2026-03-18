import json
import pytest
import time
from unittest.mock import patch, MagicMock

from sub_agents.trends_fetcher.tools.fetch_trends import (
    fetch_rising_trends,
    _search_subreddit,
    _fetch_hot_posts,
)
from sub_agents.opportunity_scorer.tools.score_opportunities import (
    score_opportunities,
    _compute_commercial_intent,
    _get_recommendation,
)


def _make_mock_json_response(children=None):
    """Helper to create a mock urllib response matching Reddit JSON."""
    if children is None:
        children = []
    
    data = {
        "data": {
            "children": children
        }
    }
    
    mock_resp = MagicMock()
    mock_resp.read.return_value = json.dumps(data).encode("utf-8")
    
    # Context manager support
    mock_resp.__enter__.return_value = mock_resp
    return mock_resp


def _make_mock_post_dict(title="Test Post", score=100, num_comments=20,
                    upvote_ratio=0.9, created_utc=None, permalink="/r/test/comments/abc/test_post",
                    selftext=""):
    """Helper to create a single post dictionary for the JSON response."""
    return {
        "data": {
            "title": title,
            "score": score,
            "num_comments": num_comments,
            "upvote_ratio": upvote_ratio,
            "created_utc": created_utc or (time.time() - 3600),
            "permalink": permalink,
            "selftext": selftext
        }
    }


# --- fetch_rising_trends tests ---

class TestFetchRisingTrends:
    @patch("urllib.request.urlopen")
    def test_search_subreddit_exception(self, mock_urlopen):
        mock_urlopen.side_effect = Exception("Search failed")
        results = _search_subreddit("test", "keyword")
        assert results == []

    @patch("urllib.request.urlopen")
    def test_fetch_hot_posts_exception(self, mock_urlopen):
        mock_urlopen.side_effect = Exception("Hot failed")
        results = _fetch_hot_posts("test", "keyword")
        assert results == []

    @patch("urllib.request.urlopen")
    def test_happy_path(self, mock_urlopen, mock_tool_context):
        # We need to mock urlopen sequence for search and hot
        # DEFAULT_SUBREDDITS has 7 items. So 7 searches, 7 hots = 14 calls.
        
        post = _make_mock_post_dict(title="fitness tracker review", score=150, num_comments=30)
        valid_response = _make_mock_json_response([post])
        empty_response = _make_mock_json_response([])
        
        # Make the first search return a post, everything else empty
        mock_urlopen.side_effect = [valid_response] + [empty_response] * 13

        result = fetch_rising_trends("fitness", mock_tool_context)

        assert result["status"] == "success"
        assert "trending posts" in result["message"]
        stored = json.loads(mock_tool_context.state["trending_terms"])
        assert len(stored) >= 1
        assert stored[0]["title"] == "fitness tracker review"
        assert "comment_velocity" in stored[0]
        assert "post_url" in stored[0]

    @patch("urllib.request.urlopen")
    def test_no_results(self, mock_urlopen, mock_tool_context):
        empty_response = _make_mock_json_response([])
        mock_urlopen.return_value = empty_response

        result = fetch_rising_trends("xyznonexistent", mock_tool_context)

        assert result["status"] == "success"
        assert "No Reddit posts found" in result["message"]
        assert json.loads(mock_tool_context.state["trending_terms"]) == []

    @patch("urllib.request.urlopen")
    def test_reddit_exception(self, mock_urlopen, mock_tool_context):
        mock_urlopen.side_effect = Exception("Connection refused")

        result = fetch_rising_trends("fitness", mock_tool_context)

        # In the new code, the top level catches the exception only if inner loops fail completely
        # which they don't, they just return empty lists. 
        # So an exception in inside `_search` just logs a warning and returns [].
        # Therefore, if ALL calls fail, it returns "success" with no results.
        assert result["status"] == "success"
        assert "No Reddit posts found" in result["message"]
        assert json.loads(mock_tool_context.state["trending_terms"]) == []

    @patch("urllib.request.urlopen")
    def test_hot_post_keyword_filtering(self, mock_urlopen, mock_tool_context):
        """Hot posts should only be included if keyword appears in title or selftext."""
        matching_post = _make_mock_post_dict(title="Best fitness tracker", score=100)
        non_matching_post = _make_mock_post_dict(title="Best laptop deals", score=200)
        
        # search gets nothing, hot gets both
        search_resp = _make_mock_json_response([])
        hot_resp = _make_mock_json_response([matching_post, non_matching_post])
        
        mock_urlopen.side_effect = [search_resp, hot_resp] * 7

        result = fetch_rising_trends("fitness", mock_tool_context)

        stored = json.loads(mock_tool_context.state["trending_terms"])
        titles = [p["title"] for p in stored]
        # The matching post appears once per subreddit searched (7 subreddits) -> deduped down to 1
        assert len(titles) > 0
        assert all("fitness" in t.lower() for t in titles)

    @patch("urllib.request.urlopen")
    def test_deduplication_by_url(self, mock_urlopen, mock_tool_context):
        """Same post from search and hot should be deduplicated."""
        post = _make_mock_post_dict(title="fitness tracker", score=100, permalink="/r/test/comments/abc/fitness")
        
        # search gets it, hot gets it
        resp = _make_mock_json_response([post])
        mock_urlopen.return_value = resp

        fetch_rising_trends("fitness", mock_tool_context)

        stored = json.loads(mock_tool_context.state["trending_terms"])
        urls = [p["post_url"] for p in stored]
        assert len(set(urls)) == len(urls)  # All unique



# --- score_opportunities tests ---

class TestScoreOpportunities:
    def test_happy_path(self, mock_tool_context, sample_trending_terms):
        terms_json = json.dumps(sample_trending_terms)
        result = score_opportunities(terms_json, mock_tool_context)

        assert result["status"] == "success"
        assert "Scored 5 posts" in result["message"]

        scored = json.loads(mock_tool_context.state["scored_terms"])
        assert len(scored) == 5
        # Should be sorted by opportunity_score descending
        scores = [t["opportunity_score"] for t in scored]
        assert scores == sorted(scores, reverse=True)

    def test_empty_terms(self, mock_tool_context):
        score_opportunities("[]", mock_tool_context)

        assert json.loads(mock_tool_context.state["scored_terms"]) == []

    def test_invalid_json(self, mock_tool_context):
        score_opportunities("not valid json {{{", mock_tool_context)

        assert json.loads(mock_tool_context.state["scored_terms"]) == []

    def test_none_input(self, mock_tool_context):
        result = score_opportunities(None, mock_tool_context)

        assert result["status"] == "error"
        assert json.loads(mock_tool_context.state["scored_terms"]) == []

    def test_scoring_values(self, mock_tool_context):
        terms = [{"title": "buy best cheap deal headphones", "score": 100, "num_comments": 50,
                  "upvote_ratio": 0.95, "comment_velocity": 5.0,
                  "subreddit": "gadgets", "post_url": "https://reddit.com/r/gadgets/test",
                  "source": "reddit_search"}]
        score_opportunities(json.dumps(terms), mock_tool_context)

        scored = json.loads(mock_tool_context.state["scored_terms"])
        assert len(scored) == 1
        t = scored[0]
        assert t["popularity_score"] == 1.0
        assert t["engagement_score"] == 1.0
        assert t["commercial_intent"] > 0
        assert t["opportunity_score"] > 0
        assert t["recommendation"] != ""
        assert t["upvotes"] == 100
        assert t["subreddit"] == "gadgets"

    def test_all_zero_scores(self, mock_tool_context):
        terms = [
            {"title": "widget", "score": 0, "num_comments": 0, "upvote_ratio": 0.5,
             "comment_velocity": 0, "subreddit": "test", "post_url": "https://reddit.com/1"},
            {"title": "gadget", "score": 0, "num_comments": 0, "upvote_ratio": 0.5,
             "comment_velocity": 0, "subreddit": "test", "post_url": "https://reddit.com/2"},
        ]
        score_opportunities(json.dumps(terms), mock_tool_context)

        scored = json.loads(mock_tool_context.state["scored_terms"])
        assert len(scored) == 2
        for t in scored:
            assert t["popularity_score"] == 0.0
            assert t["engagement_score"] == 0.0

    def test_missing_fields_in_terms(self, mock_tool_context):
        terms = [{"other_field": "value"}]
        score_opportunities(json.dumps(terms), mock_tool_context)

        scored = json.loads(mock_tool_context.state["scored_terms"])
        assert len(scored) == 1
        assert scored[0]["title"] == ""
        assert scored[0]["subreddit"] == ""

    def test_list_input(self, mock_tool_context, sample_trending_terms):
        """Test that list input (not JSON string) is handled."""
        score_opportunities(sample_trending_terms, mock_tool_context)

        scored = json.loads(mock_tool_context.state["scored_terms"])
        assert len(scored) == 5

    def test_double_encoded_json(self, mock_tool_context, sample_trending_terms):
        """Test that double-encoded JSON strings are handled."""
        double_encoded = json.dumps(json.dumps(sample_trending_terms))
        score_opportunities(double_encoded, mock_tool_context)

        scored = json.loads(mock_tool_context.state["scored_terms"])
        assert len(scored) == 5

    def test_double_encoded_invalid_inner_json(self, mock_tool_context):
        """Test when the string itself is double encoded but inner is invalid."""
        # A JSON string that decodes to a string "invalid inner json {"
        bad_inner = json.dumps("invalid inner json {")
        score_opportunities(bad_inner, mock_tool_context)
        
        # It should try to parse the inner string, fail, and pass, resulting in terms="invalid inner json {"
        # Then the isinstance(terms, list) check should catch it and set terms=[]
        assert json.loads(mock_tool_context.state["scored_terms"]) == []

    def test_dict_input(self, mock_tool_context):
        """Test when input is valid JSON but a dict instead of list."""
        score_opportunities(json.dumps({"some": "dict"}), mock_tool_context)

        assert json.loads(mock_tool_context.state["scored_terms"]) == []


# --- Helper function tests ---

class TestComputeCommercialIntent:
    def test_no_commercial_keywords(self):
        assert _compute_commercial_intent("yoga mat") == 0.0

    def test_one_keyword(self):
        score = _compute_commercial_intent("buy yoga mat")
        assert score > 0
        assert score <= 1.0

    def test_many_keywords_capped(self):
        # "buy best cheap deal" has 4 matches → 4/3 = 1.33 → capped at 1.0
        score = _compute_commercial_intent("buy best cheap deal discount")
        assert score == 1.0

    def test_case_insensitive(self):
        assert _compute_commercial_intent("BUY BEST") == _compute_commercial_intent("buy best")


class TestGetRecommendation:
    def test_high(self):
        assert "High opportunity" in _get_recommendation(0.80)

    def test_moderate(self):
        assert "Moderate opportunity" in _get_recommendation(0.55)

    def test_low(self):
        assert "Low opportunity" in _get_recommendation(0.30)

    def test_minimal(self):
        assert "Minimal opportunity" in _get_recommendation(0.10)

    def test_boundary_075(self):
        assert "High opportunity" in _get_recommendation(0.75)

    def test_boundary_050(self):
        assert "Moderate opportunity" in _get_recommendation(0.50)

    def test_boundary_025(self):
        assert "Low opportunity" in _get_recommendation(0.25)
