"""Unit tests for continuous-batch-preemption-scheduler."""
import unittest
from continuous_batch_preemption_scheduler.scheduler import ContinuousBatchScheduler


class TestContinuousBatchScheduler(unittest.TestCase):
    def setUp(self):
        self.sched = ContinuousBatchScheduler(max_batch_size=2)

    def test_preemption_by_high_priority(self):
        self.sched.submit_request("low1", "p", 10, priority=3)
        self.sched.submit_request("low2", "p", 10, priority=3)

        # Urgent request submitted
        self.sched.submit_request("urgent", "p", 2, priority=0)

        running_ids = [s.current_request.request_id for s in self.sched.slots if s.current_request]
        self.assertIn("urgent", running_ids)

    def test_request_completion(self):
        self.sched.submit_request("quick", "p", 1, priority=1)
        finished = self.sched.step()
        self.assertIn("quick", finished)
        self.assertTrue(self.sched.completed_requests["quick"].is_completed)
