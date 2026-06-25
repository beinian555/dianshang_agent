"""Tests for AnalysisJob status tracking and transition logic."""

import pytest
from datetime import datetime

from app.schemas.job import AnalysisJob, AnalysisJobStatus


class TestAnalysisJobSchema:

    def test_job_defaults(self):
        job = AnalysisJob(project_id="proj-001")
        assert job.status == AnalysisJobStatus.PENDING
        assert job.progress == 0
        assert job.current_step is None
        assert job.report_id is None
        assert job.error_message is None
        assert job.id.startswith("job-")

    def test_job_status_enum(self):
        assert AnalysisJobStatus.PENDING.value == "pending"
        assert AnalysisJobStatus.RUNNING.value == "running"
        assert AnalysisJobStatus.COMPLETED.value == "completed"
        assert AnalysisJobStatus.FAILED.value == "failed"

    def test_job_progress_bounds(self):
        job = AnalysisJob(project_id="proj-001", progress=0)
        assert job.progress == 0

        job = AnalysisJob(project_id="proj-001", progress=100)
        assert job.progress == 100

        job = AnalysisJob(project_id="proj-001", progress=50)
        assert job.progress == 50

    def test_job_progress_clamped(self):
        """Pydantic Field(ge=0, le=100) should reject out-of-range."""
        with pytest.raises(Exception):
            AnalysisJob(project_id="proj-001", progress=-1)
        with pytest.raises(Exception):
            AnalysisJob(project_id="proj-001", progress=101)

    def test_job_timestamps(self):
        before = datetime.now()
        job = AnalysisJob(project_id="proj-001")
        after = datetime.now()
        assert before <= job.created_at <= after
        assert before <= job.updated_at <= after

    def test_job_with_all_fields(self):
        job = AnalysisJob(
            id="job-custom-001",
            project_id="proj-001",
            status=AnalysisJobStatus.RUNNING,
            progress=45,
            current_step="review_clustering",
            report_id=None,
            error_message=None,
        )
        assert job.id == "job-custom-001"
        assert job.status == AnalysisJobStatus.RUNNING
        assert job.current_step == "review_clustering"

    def test_job_failed_state(self):
        job = AnalysisJob(
            project_id="proj-001",
            status=AnalysisJobStatus.FAILED,
            error_message="LLM timeout after 30s",
        )
        assert job.status == AnalysisJobStatus.FAILED
        assert job.error_message == "LLM timeout after 30s"


class TestAnalysisJobTransitions:

    def test_valid_transition_pending_to_running(self):
        job = AnalysisJob(project_id="proj-001")
        assert job.status == AnalysisJobStatus.PENDING
        # Simulate update
        job.status = AnalysisJobStatus.RUNNING
        job.progress = 10
        assert job.status == AnalysisJobStatus.RUNNING

    def test_valid_transition_running_to_completed(self):
        job = AnalysisJob(project_id="proj-001", status=AnalysisJobStatus.RUNNING, progress=50)
        job.status = AnalysisJobStatus.COMPLETED
        job.progress = 100
        job.report_id = "report-abc"
        assert job.status == AnalysisJobStatus.COMPLETED
        assert job.report_id == "report-abc"

    def test_valid_transition_running_to_failed(self):
        job = AnalysisJob(project_id="proj-001", status=AnalysisJobStatus.RUNNING, progress=30)
        job.status = AnalysisJobStatus.FAILED
        job.error_message = "Something went wrong"
        assert job.status == AnalysisJobStatus.FAILED
