"""Core Continuous Batch Preemption Scheduler implementation."""
import time
from typing import Dict, List, Optional, Any


class InferenceRequest:
    def __init__(self, request_id: str, prompt: str, max_tokens: int, priority: int = 1):
        self.request_id = request_id
        self.prompt = prompt
        self.max_tokens = max_tokens
        self.priority = priority  # 0 is Highest, 3 is Lowest
        self.tokens_generated = 0
        self.is_completed = False
        self.arrived_at = time.time()


class SlotState:
    def __init__(self, slot_id: int):
        self.slot_id = slot_id
        self.current_request: Optional[InferenceRequest] = None


class ContinuousBatchScheduler:
    def __init__(self, max_batch_size: int = 4):
        self.max_batch_size = max_batch_size
        self.slots: List[SlotState] = [SlotState(i) for i in range(max_batch_size)]
        self.waiting_queue: List[InferenceRequest] = []
        self.completed_requests: Dict[str, InferenceRequest] = {}

    def submit_request(self, request_id: str, prompt: str, max_tokens: int, priority: int = 1) -> InferenceRequest:
        req = InferenceRequest(request_id, prompt, max_tokens, priority)
        self.waiting_queue.append(req)
        # Sort queue by priority (0 first), then arrival
        self.waiting_queue.sort(key=lambda r: (r.priority, r.arrived_at))
        self._schedule_slots()
        return req

    def _schedule_slots(self):
        # 1. Fill empty slots
        for slot in self.slots:
            if slot.current_request is None and self.waiting_queue:
                slot.current_request = self.waiting_queue.pop(0)

        # 2. Check if a high priority waiting request should preempt a running lower priority request
        if self.waiting_queue:
            highest_waiting = self.waiting_queue[0]
            # Find running request with strictly lower priority
            lowest_running_slot = max(
                (s for s in self.slots if s.current_request is not None),
                key=lambda s: s.current_request.priority,
                default=None
            )
            if lowest_running_slot and lowest_running_slot.current_request.priority > highest_waiting.priority:
                # Preempt!
                preempted = lowest_running_slot.current_request
                lowest_running_slot.current_request = self.waiting_queue.pop(0)
                # Put preempted request back in waiting queue
                self.waiting_queue.append(preempted)
                self.waiting_queue.sort(key=lambda r: (r.priority, r.arrived_at))

    def step(self) -> List[str]:
        # Simulates 1 forward pass iteration across all active slots
        just_finished = []
        for slot in self.slots:
            if slot.current_request:
                req = slot.current_request
                req.tokens_generated += 1
                if req.tokens_generated >= req.max_tokens:
                    req.is_completed = True
                    self.completed_requests[req.request_id] = req
                    just_finished.append(req.request_id)
                    slot.current_request = None

        self._schedule_slots()
        return just_finished
