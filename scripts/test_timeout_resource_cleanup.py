#!/usr/bin/env python3
"""
Test to verify that client timeout:
1. Accurately interrupts the call at deadline.
2. Does not leave zombie / running worker threads.
3. Does not leave Ollama in a blocked or generating state for overlapping requests.
"""

import sys
import threading
import time
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.ollama_client import OllamaClient, OllamaTimeoutError

def main():
    client = OllamaClient()

    print("==================================================================")
    print(" Verifying Thread and Socket Resource Behavior After Timeout")
    print("==================================================================")

    # 1. Baseline thread count
    threads_initial = threading.active_count()
    initial_thread_names = [t.name for t in threading.enumerate()]
    print(f"1. Baseline active threads: {threads_initial} ({initial_thread_names})")

    # 2. Trigger timeout on expensive prompt with thinking enabled
    timeout_duration = 1.5  # practical 1.5s timeout
    print(f"\n2. Executing expensive request with hard client deadline of {timeout_duration}s...")
    t0 = time.perf_counter()
    caught_timeout = False
    
    try:
        client.chat(
            messages=[{"role": "user", "content": "Write a 5000 word exhaustive legal brief on securities settlement."}],
            timeout=timeout_duration,
            think=True,
            options={"num_predict": 2048}
        )
    except OllamaTimeoutError as e:
        elapsed = time.perf_counter() - t0
        caught_timeout = True
        print(f"   -> Caught OllamaTimeoutError as expected in {elapsed:.3f}s: {e}")

    assert caught_timeout, "Expected OllamaTimeoutError was not raised!"
    assert elapsed < timeout_duration + 0.5, f"Timeout took too long: {elapsed:.3f}s"

    # 3. Check active threads after brief grace period for socket close
    time.sleep(0.3)
    threads_after = threading.active_count()
    after_thread_names = [t.name for t in threading.enumerate()]
    print(f"\n3. Active threads after timeout and cleanup: {threads_after} ({after_thread_names})")
    
    # Verify no persistent worker threads leaked
    # Any ThreadPoolExecutor worker thread should either be dead or terminate upon socket close
    time.sleep(0.5)
    threads_final = threading.active_count()
    print(f"   Active threads after 0.5s grace: {threads_final}")
    assert threads_final <= threads_initial + 1, f"Thread leak detected: {threads_final} > {threads_initial}"
    print("   -> PASS: No runaway inference threads left running.")

    # 4. Verify Ollama is immediately responsive (no overlapping stalled request)
    print("\n4. Testing immediate subsequent Ollama request to confirm engine is idle...")
    t_sub0 = time.perf_counter()
    sub_res = client.chat(
        messages=[{"role": "user", "content": "Respond with JSON: {\"engine_status\": \"available\"}"}],
        timeout=10.0,
        think=False,
        options={"num_predict": 64}
    )
    t_sub = time.perf_counter() - t_sub0
    print(f"   -> Subsequent request finished in {t_sub:.3f}s!")
    print(f"   -> Response: {sub_res.get('response')}")
    assert sub_res.get("response") is not None, "Subsequent response should not be None"
    assert t_sub < 5.0, f"Subsequent call was delayed ({t_sub:.2f}s), indicating engine was occupied"
    print("   -> PASS: Ollama engine immediately available; no overlapping request blocking.")

    print("\n==================================================================")
    print(" Resource and thread cleanup verification PASSED successfully!")
    print("==================================================================")

if __name__ == "__main__":
    main()

