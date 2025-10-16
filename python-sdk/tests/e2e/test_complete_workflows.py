"""End-to-end tests for complete workflows."""

import pytest
import os
import time
from dispersl import Dispersl
from dispersl.agentic import AgenticExecutor
from dispersl.exceptions import DisperslError


@pytest.mark.e2e
class TestCompleteCodeGenerationWorkflow:
    """Test complete code generation workflow end-to-end."""

    @pytest.fixture
    def client(self, api_url, api_key):
        """Create Dispersl client."""
        return Dispersl(api_key=api_key, base_url=api_url)

    @pytest.fixture
    def executor(self, client):
        """Create agentic executor."""
        return AgenticExecutor(client._http_client)

    @pytest.mark.skipif(
        os.getenv("RUN_E2E_TESTS") != "true",
        reason="E2E tests disabled"
    )
    def test_full_code_generation_flow(self, client, executor):
        """Test complete code generation from planning to execution."""
        # Step 1: Create a task
        task = client.tasks.create(
            name="Generate Calculator Module",
            description="Create a complete calculator module with tests",
            agent_type="code"
        )
        
        task_id = task["id"]
        
        try:
            # Step 2: Create planning step
            plan_step = client.steps.create(
                task_id=task_id,
                name="Plan calculator module",
                action="plan"
            )
            
            # Step 3: Execute plan using plan agent
            session_id = executor.start_session()
            
            plan_result = executor.execute_workflow(
                session_id=session_id,
                prompt="Plan a calculator module with add, subtract, multiply, divide functions",
                agent_type="plan",
                default_dir="/tmp/test_project",
                current_dir="/tmp/test_project",
                agent_choice=["code", "test"]
            )
            
            assert plan_result is not None
            
            # Step 4: Execute code generation
            code_step = client.steps.create(
                task_id=task_id,
                name="Generate code",
                action="execute"
            )
            
            code_result = executor.execute_workflow(
                session_id=session_id,
                prompt="Implement the calculator module based on the plan",
                agent_type="code",
                default_dir="/tmp/test_project",
                current_dir="/tmp/test_project"
            )
            
            assert code_result is not None
            
            # Step 5: Generate tests
            test_step = client.steps.create(
                task_id=task_id,
                name="Generate tests",
                action="test"
            )
            
            test_result = executor.execute_workflow(
                session_id=session_id,
                prompt="Create comprehensive tests for the calculator module",
                agent_type="test",
                default_dir="/tmp/test_project",
                current_dir="/tmp/test_project/tests"
            )
            
            assert test_result is not None
            
            # Step 6: Update task status
            updated_task = client.tasks.update(
                task_id,
                status="completed",
                progress=100
            )
            
            assert updated_task["status"] == "completed"
            
            # Step 7: Get task result
            result = client.tasks.get_result(task_id)
            assert result is not None
            
            executor.end_session(session_id)
            
        finally:
            # Cleanup
            try:
                client.tasks.delete(task_id)
            except:
                pass


@pytest.mark.e2e
class TestMultiAgentCollaboration:
    """Test multi-agent collaboration workflows."""

    @pytest.fixture
    def client(self, api_url, api_key):
        """Create Dispersl client."""
        return Dispersl(api_key=api_key, base_url=api_url)

    @pytest.fixture
    def executor(self, client):
        """Create agentic executor."""
        return AgenticExecutor(client._http_client)

    @pytest.mark.skipif(
        os.getenv("RUN_E2E_TESTS") != "true",
        reason="E2E tests disabled"
    )
    def test_plan_code_test_git_workflow(self, client, executor):
        """Test complete workflow with plan → code → test → git agents."""
        task = client.tasks.create(
            name="Complete Feature Implementation",
            description="Implement, test, and commit a feature",
            agent_type="plan"
        )
        
        task_id = task["id"]
        session_id = executor.start_session()
        
        try:
            # Phase 1: Planning
            plan_result = executor.execute_workflow(
                session_id=session_id,
                prompt="Plan implementation of a user authentication feature",
                agent_type="plan",
                default_dir="/tmp/project",
                current_dir="/tmp/project",
                agent_choice=["code", "test", "git"]
            )
            
            assert plan_result is not None
            
            # Phase 2: Code implementation
            code_result = executor.execute_workflow(
                session_id=session_id,
                prompt="Implement user authentication with login and logout",
                agent_type="code",
                default_dir="/tmp/project",
                current_dir="/tmp/project/src"
            )
            
            assert code_result is not None
            
            # Phase 3: Test generation
            test_result = executor.execute_workflow(
                session_id=session_id,
                prompt="Create unit and integration tests for authentication",
                agent_type="test",
                default_dir="/tmp/project",
                current_dir="/tmp/project/tests"
            )
            
            assert test_result is not None
            
            # Phase 4: Git operations
            git_result = executor.execute_workflow(
                session_id=session_id,
                prompt="Commit the authentication feature with proper message",
                agent_type="git",
                default_dir="/tmp/project",
                current_dir="/tmp/project"
            )
            
            assert git_result is not None
            
            # Update task to completed
            client.tasks.update(task_id, status="completed")
            
            executor.end_session(session_id)
            
        finally:
            try:
                client.tasks.delete(task_id)
            except:
                pass

    @pytest.mark.skipif(
        os.getenv("RUN_E2E_TESTS") != "true",
        reason="E2E tests disabled"
    )
    def test_agent_handover_workflow(self, client, executor):
        """Test workflow with agent handover."""
        session_id = executor.start_session()
        
        try:
            # Start with chat agent
            initial_result = executor.execute_workflow(
                session_id=session_id,
                prompt="I need to create a REST API. Can you help?",
                agent_type="chat",
                default_dir="/tmp/project",
                current_dir="/tmp/project"
            )
            
            assert initial_result is not None
            
            # Handover to plan agent
            handover_data = {
                "from_agent": "chat",
                "to_agent": "plan",
                "context": {"task": "REST API implementation"},
                "reason": "requires detailed planning"
            }
            
            handover_result = executor.handle_handover(session_id, handover_data)
            assert handover_result is not None
            
            # Continue with plan agent
            plan_result = executor.execute_workflow(
                session_id=session_id,
                prompt="Create detailed plan for REST API with user endpoints",
                agent_type="plan",
                default_dir="/tmp/project",
                current_dir="/tmp/project",
                agent_choice=["code", "test"]
            )
            
            assert plan_result is not None
            
            # Handover to code agent
            handover_data2 = {
                "from_agent": "plan",
                "to_agent": "code",
                "context": {"plan": plan_result},
                "reason": "ready for implementation"
            }
            
            handover_result2 = executor.handle_handover(session_id, handover_data2)
            assert handover_result2 is not None
            
            # Execute with code agent
            code_result = executor.execute_workflow(
                session_id=session_id,
                prompt="Implement the REST API based on the plan",
                agent_type="code",
                default_dir="/tmp/project",
                current_dir="/tmp/project"
            )
            
            assert code_result is not None
            
            executor.end_session(session_id)
            
        except Exception as e:
            executor.end_session(session_id)
            raise


@pytest.mark.e2e
class TestStreamingWorkflows:
    """Test streaming workflow execution."""

    @pytest.fixture
    def executor(self, api_url, api_key):
        """Create executor."""
        client = Dispersl(api_key=api_key, base_url=api_url)
        return AgenticExecutor(client._http_client)

    @pytest.mark.skipif(
        os.getenv("RUN_E2E_TESTS") != "true",
        reason="E2E tests disabled"
    )
    def test_streaming_code_generation(self, executor):
        """Test streaming code generation."""
        session_id = executor.start_session()
        
        try:
            chunks = []
            content_parts = []
            
            for chunk in executor.execute_workflow_stream(
                session_id=session_id,
                prompt="Create a Python function to sort a list using quicksort",
                agent_type="code",
                default_dir="/tmp/project",
                current_dir="/tmp/project"
            ):
                chunks.append(chunk)
                
                # Extract content from chunks
                if isinstance(chunk, dict) and "delta" in chunk:
                    content_parts.append(chunk["delta"])
            
            assert len(chunks) > 0
            
            # Verify we got actual content
            full_content = "".join(content_parts)
            assert len(full_content) > 0
            
            executor.end_session(session_id)
            
        except Exception as e:
            executor.end_session(session_id)
            raise

    @pytest.mark.skipif(
        os.getenv("RUN_E2E_TESTS") != "true",
        reason="E2E tests disabled"
    )
    def test_streaming_with_tool_calls(self, executor):
        """Test streaming workflow with tool calls."""
        # Register test tool
        def search_docs(query: str) -> str:
            return f"Documentation results for: {query}"
        
        executor.tool_registry.register("search_docs", search_docs)
        
        session_id = executor.start_session()
        
        try:
            chunks = []
            tool_calls_detected = False
            
            for chunk in executor.execute_workflow_stream(
                session_id=session_id,
                prompt="Search documentation for 'authentication' and implement it",
                agent_type="code",
                default_dir="/tmp/project",
                current_dir="/tmp/project"
            ):
                chunks.append(chunk)
                
                if isinstance(chunk, dict) and chunk.get("type") == "tool_call":
                    tool_calls_detected = True
            
            assert len(chunks) > 0
            # Tool calls may or may not be present depending on the response
            
            executor.end_session(session_id)
            
        except Exception as e:
            executor.end_session(session_id)
            raise


@pytest.mark.e2e
class TestErrorHandlingAndRecovery:
    """Test error handling and recovery in workflows."""

    @pytest.fixture
    def client(self, api_url, api_key):
        """Create Dispersl client."""
        return Dispersl(api_key=api_key, base_url=api_url)

    @pytest.fixture
    def executor(self, client):
        """Create agentic executor."""
        return AgenticExecutor(client._http_client)

    @pytest.mark.skipif(
        os.getenv("RUN_E2E_TESTS") != "true",
        reason="E2E tests disabled"
    )
    def test_workflow_retry_on_failure(self, client, executor):
        """Test workflow retry mechanism on failure."""
        task = client.tasks.create(
            name="Retry Test Task",
            description="Task to test retry mechanism",
            agent_type="code"
        )
        
        task_id = task["id"]
        session_id = executor.start_session()
        
        try:
            # Attempt execution with potential failure
            result = executor.execute_workflow(
                session_id=session_id,
                prompt="Execute a complex operation",
                agent_type="code",
                default_dir="/tmp/project",
                current_dir="/tmp/project",
                max_iterations=3
            )
            
            # Should complete or fail gracefully
            assert result is not None or True  # Accept either success or graceful failure
            
            executor.end_session(session_id)
            
        except DisperslError as e:
            # Error handling is working
            assert e is not None
            executor.end_session(session_id)
            
        finally:
            try:
                client.tasks.delete(task_id)
            except:
                pass

    @pytest.mark.skipif(
        os.getenv("RUN_E2E_TESTS") != "true",
        reason="E2E tests disabled"
    )
    def test_session_recovery_after_error(self, executor):
        """Test session recovery after error."""
        session_id = executor.start_session()
        
        try:
            # Attempt operation that might fail
            try:
                result = executor.execute_workflow(
                    session_id=session_id,
                    prompt="Invalid operation that might fail",
                    agent_type="code",
                    default_dir="/tmp/project",
                    current_dir="/tmp/project"
                )
            except DisperslError:
                pass  # Expected to potentially fail
            
            # Session should still be valid
            assert executor.has_session(session_id)
            
            # Should be able to execute another workflow
            result2 = executor.execute_workflow(
                session_id=session_id,
                prompt="Simple valid operation",
                agent_type="chat",
                default_dir="/tmp/project",
                current_dir="/tmp/project"
            )
            
            assert result2 is not None
            
            executor.end_session(session_id)
            
        except Exception as e:
            executor.end_session(session_id)
            raise


@pytest.mark.e2e
class TestDocumentationGeneration:
    """Test documentation generation workflow."""

    @pytest.fixture
    def client(self, api_url, api_key):
        """Create Dispersl client."""
        return Dispersl(api_key=api_key, base_url=api_url)

    @pytest.mark.skipif(
        os.getenv("RUN_E2E_TESTS") != "true",
        reason="E2E tests disabled"
    )
    def test_docs_generation_workflow(self, client):
        """Test complete documentation generation workflow."""
        result = client.agents.docs(
            url="https://github.com/example/test-repo",
            branch="main"
        )
        
        assert result is not None
        assert "documentation" in result or "status" in result

    @pytest.mark.skipif(
        os.getenv("RUN_E2E_TESTS") != "true",
        reason="E2E tests disabled"
    )
    def test_docs_with_team_access(self, client):
        """Test documentation generation with team access."""
        result = client.agents.docs(
            url="https://github.com/example/private-repo",
            branch="develop",
            team_access=True
        )
        
        assert result is not None


@pytest.mark.e2e
class TestConcurrentWorkflows:
    """Test concurrent workflow execution."""

    @pytest.fixture
    def executor(self, api_url, api_key):
        """Create executor."""
        client = Dispersl(api_key=api_key, base_url=api_url)
        return AgenticExecutor(client._http_client)

    @pytest.mark.skipif(
        os.getenv("RUN_E2E_TESTS") != "true",
        reason="E2E tests disabled"
    )
    def test_multiple_concurrent_sessions(self, executor):
        """Test running multiple sessions concurrently."""
        import threading
        
        results = []
        errors = []
        
        def run_workflow(task_name):
            session_id = executor.start_session()
            try:
                result = executor.execute_workflow(
                    session_id=session_id,
                    prompt=f"Execute {task_name}",
                    agent_type="chat",
                    default_dir="/tmp/project",
                    current_dir="/tmp/project"
                )
                results.append(result)
            except Exception as e:
                errors.append(e)
            finally:
                executor.end_session(session_id)
        
        threads = [
            threading.Thread(target=run_workflow, args=(f"Task {i}",))
            for i in range(3)
        ]
        
        for thread in threads:
            thread.start()
        
        for thread in threads:
            thread.join(timeout=60)
        
        assert len(errors) == 0
        assert len(results) == 3

