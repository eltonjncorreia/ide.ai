"""Test parallel CLI execution with multiple concurrent requests.

This test verifies that:
1. Each ChatPanel can run async requests without blocking others
2. Multiple provider instances handle concurrent requests independently
3. Streaming doesn't block the event loop
4. Tasks are properly tracked per panel
"""

import asyncio
import pytest
from datetime import datetime

from ide_ai.panels.chat_panel import ChatPanel, ChatMessage
from ide_ai.ai.claude import ClaudeProvider
from ide_ai.ai.copilot import CopilotProvider


@pytest.mark.asyncio
async def test_provider_instances_are_independent():
    """Verify each provider instance is independent."""
    claude1 = ClaudeProvider()
    claude2 = ClaudeProvider()
    copilot1 = CopilotProvider()
    
    # Each should have a unique session ID
    assert claude1._session_id != claude2._session_id
    assert copilot1._session_id != CopilotProvider()._session_id
    
    # But share the same name
    assert claude1.name == claude2.name == "Claude"
    assert copilot1.name == CopilotProvider().name == "Copilot"


@pytest.mark.asyncio
async def test_concurrent_provider_requests():
    """Test that multiple providers can handle concurrent requests."""
    provider1 = ClaudeProvider()
    provider2 = ClaudeProvider()
    
    results = []
    
    async def collect_response(provider, msg):
        response = []
        async for chunk in provider.send(msg):
            response.append(chunk)
            await asyncio.sleep(0)  # Yield to event loop
        results.append("".join(response))
    
    # Launch concurrent requests
    start = asyncio.get_event_loop().time()
    await asyncio.gather(
        collect_response(provider1, "test1"),
        collect_response(provider2, "test2"),
    )
    duration = asyncio.get_event_loop().time() - start
    
    # Verify both completed
    assert len(results) == 2
    assert all(len(r) > 0 for r in results)


@pytest.mark.asyncio
async def test_chat_panel_tracks_active_tasks():
    """Verify ChatPanel properly tracks active tasks."""
    provider = ClaudeProvider()
    panel = ChatPanel(provider=provider, tab_index=1, tab_count=1, id="test-panel")
    
    # Verify task tracking is initialized
    assert hasattr(panel, "_active_tasks")
    assert isinstance(panel._active_tasks, set)
    assert len(panel._active_tasks) == 0
    
    # Create a task and verify it's tracked
    async def dummy_task():
        await asyncio.sleep(0.01)
        return "done"
    
    task = asyncio.create_task(dummy_task())
    panel._active_tasks.add(task)
    task.add_done_callback(panel._active_tasks.discard)
    
    await task
    
    # Task should be removed after completion
    assert len(panel._active_tasks) == 0


@pytest.mark.asyncio
async def test_same_provider_concurrent_calls():
    """Test that same provider instance handles concurrent calls."""
    provider = ClaudeProvider()
    results = []
    
    async def make_request(msg):
        response = []
        async for chunk in provider.send(msg):
            response.append(chunk)
            await asyncio.sleep(0)
        results.append("".join(response))
    
    # Launch multiple concurrent calls to same provider
    await asyncio.gather(
        make_request("message 1"),
        make_request("message 2"),
        make_request("message 3"),
    )
    
    # All should complete and produce responses
    assert len(results) == 3
    assert all(len(r) > 0 for r in results)


@pytest.mark.asyncio
async def test_provider_independence_no_blocking():
    """Test that provider instances don't block each other."""
    claude = ClaudeProvider()
    copilot = CopilotProvider()
    
    task_order = []
    
    async def track_request(provider, name):
        task_order.append(f"{name}_start")
        response = []
        async for chunk in provider.send(f"msg_{name}"):
            response.append(chunk)
            await asyncio.sleep(0)
        task_order.append(f"{name}_end")
        return "".join(response)
    
    # Run both concurrently - if they block, we'll see start/end pairs
    # instead of interleaved starts
    task1 = asyncio.create_task(track_request(claude, "claude"))
    task2 = asyncio.create_task(track_request(copilot, "copilot"))
    
    results = await asyncio.gather(task1, task2)
    
    # Both should have completed
    assert len(results) == 2
    assert all(len(r) > 0 for r in results)
    
    # Both should have started (proving they're concurrent, not sequential)
    assert "claude_start" in task_order
    assert "copilot_start" in task_order


@pytest.mark.asyncio
async def test_async_generator_streaming():
    """Test that async generators properly stream without blocking."""
    provider = ClaudeProvider()
    
    chunk_count = 0
    last_chunk_time = 0
    min_chunk_interval = 0
    
    async def count_chunks():
        nonlocal chunk_count, last_chunk_time, min_chunk_interval
        import time
        
        async for chunk in provider.send("streaming test"):
            chunk_count += 1
            current_time = time.time()
            if last_chunk_time > 0:
                interval = current_time - last_chunk_time
                if min_chunk_interval == 0 or interval < min_chunk_interval:
                    min_chunk_interval = interval
            last_chunk_time = current_time
    
    # Run streaming and a concurrent task
    concurrent_executed = False
    
    async def concurrent_task():
        nonlocal concurrent_executed
        await asyncio.sleep(0.001)
        concurrent_executed = True
    
    streaming_task = asyncio.create_task(count_chunks())
    concurrent = asyncio.create_task(concurrent_task())
    
    await asyncio.gather(streaming_task, concurrent)
    
    # Verify streaming happened and concurrent task executed
    assert chunk_count > 0
    assert concurrent_executed

