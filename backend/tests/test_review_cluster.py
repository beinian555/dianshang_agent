import pytest

from app.agents.mock_llm import MockLLMProvider
from app.agents.review_cluster_agent import ReviewClusterAgent
from app.seed.beauty_reviews import NEGATIVE_REVIEWS


class TestReviewClusterAgent:
    @pytest.fixture
    def agent(self):
        return ReviewClusterAgent(llm_provider=MockLLMProvider())

    @pytest.mark.asyncio
    async def test_clustering_returns_clusters(self, agent):
        clusters = await agent.run(NEGATIVE_REVIEWS)
        assert len(clusters) > 0
        assert len(clusters) >= 5

    @pytest.mark.asyncio
    async def test_each_cluster_has_required_fields(self, agent):
        clusters = await agent.run(NEGATIVE_REVIEWS)
        for cluster in clusters:
            assert cluster.cluster_name
            assert cluster.problem_type
            assert cluster.review_count > 0
            assert cluster.ratio > 0
            assert len(cluster.representative_reviews) > 0
            assert cluster.user_concern
            assert cluster.business_impact
            assert cluster.suggested_action

    @pytest.mark.asyncio
    async def test_sensitive_skin_cluster_exists(self, agent):
        clusters = await agent.run(NEGATIVE_REVIEWS)
        names = [c.cluster_name for c in clusters]
        assert "敏感肌刺激顾虑" in names

    @pytest.mark.asyncio
    async def test_effect_expectation_cluster_exists(self, agent):
        clusters = await agent.run(NEGATIVE_REVIEWS)
        names = [c.cluster_name for c in clusters]
        assert "效果预期不符" in names

    @pytest.mark.asyncio
    async def test_ratio_sum_does_not_exceed_one(self, agent):
        clusters = await agent.run(NEGATIVE_REVIEWS)
        total_ratio = sum(c.ratio for c in clusters)
        assert total_ratio <= 1.0
