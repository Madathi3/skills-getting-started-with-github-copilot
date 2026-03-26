"""
Pytest configuration and fixtures for FastAPI tests.

This module provides shared fixtures used across all test modules:
- client: FastAPI TestClient for making HTTP requests
- clean_activity_state: Fixture that resets activities to initial state
- sample_student_email: Fixture providing a sample student email
"""

import pytest
import copy
from fastapi.testclient import TestClient
from src.app import app, activities


# Store the initial state of activities for reset between tests
INITIAL_ACTIVITIES = copy.deepcopy(activities)


@pytest.fixture
def client():
    """
    Fixture: FastAPI TestClient
    
    Provides a test client for making HTTP requests to the FastAPI application.
    Automatically reset to initial state before each test.
    """
    # Reset activities to initial state before each test
    activities.clear()
    activities.update(copy.deepcopy(INITIAL_ACTIVITIES))
    
    return TestClient(app)


@pytest.fixture
def clean_activity_state(client):
    """
    Fixture: Clean activity state
    
    Ensures activities are in their initial state with no test-induced modifications.
    This fixture depends on the client fixture to guarantee proper setup.
    """
    # Reset to initial state
    activities.clear()
    activities.update(copy.deepcopy(INITIAL_ACTIVITIES))
    
    yield
    
    # Cleanup after test: reset to initial state
    activities.clear()
    activities.update(copy.deepcopy(INITIAL_ACTIVITIES))


@pytest.fixture
def sample_student_email():
    """
    Fixture: Sample student email
    
    Provides a consistent test email for use across multiple tests.
    """
    return "test.student@mergington.edu"
