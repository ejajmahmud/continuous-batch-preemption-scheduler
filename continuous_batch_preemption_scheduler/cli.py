"""CLI for continuous-batch-preemption-scheduler."""
import sys
import argparse
from .scheduler import ContinuousBatchScheduler


def main():
    parser = argparse.ArgumentParser(description="Continuous Batch Preemption Scheduler CLI")
    parser.add_argument("--demo", action="store_true", help="Run batch scheduling and preemption demo")
    args = parser.parse_args()

    if args.demo:
        sched = ContinuousBatchScheduler(max_batch_size=2)
        sched.submit_request("req_low_1", "Batch job 1", max_tokens=10, priority=3)
        sched.submit_request("req_low_2", "Batch job 2", max_tokens=10, priority=3)

        print("Step 1: Running background batch jobs...")
        sched.step()

        print("Submitting High Priority Interactive Request (Priority 0)...")
        sched.submit_request("req_urgent", "Interactive query", max_tokens=2, priority=0)

        print("Active Slots after preemption:")
        for s in sched.slots:
            req_info = f"{s.current_request.request_id} (pri {s.current_request.priority})" if s.current_request else "EMPTY"
            print(f"  Slot {s.slot_id}: {req_info}")
    else:
        parser.print_help()
    sys.exit(0)


if __name__ == "__main__":
    main()
