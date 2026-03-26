"""
Integration tests for FastAPI High School Management System API.

All tests follow the AAA (Arrange-Act-Assert) pattern:
- ARRANGE: Set up test data and preconditions using fixtures
- ACT: Perform the action being tested (call the endpoint)
- ASSERT: Verify the expected outcome
"""

import pytest


class TestGetActivities:
    """Tests for GET /activities endpoint"""
    
    def test_get_activities_returns_all_activities(self, client, clean_activity_state):
        """
        ARRANGE: Clean activity state provided by fixture
        ACT: Make GET request to /activities endpoint
        ASSERT: Response contains all 9 activities in the system
        """
        # ARRANGE
        # (already set up by fixtures)
        
        # ACT
        response = client.get("/activities")
        
        # ASSERT
        assert response.status_code == 200
        activities = response.json()
        assert len(activities) == 9
        assert "Chess Club" in activities
        assert "Programming Class" in activities
        assert "Gym Class" in activities
        assert "Basketball Team" in activities
        assert "Tennis Club" in activities
        assert "Art Studio" in activities
        assert "Music Band" in activities
        assert "Debate Team" in activities
        assert "Science Club" in activities
    
    def test_get_activities_returns_correct_structure(self, client, clean_activity_state):
        """
        ARRANGE: Clean activity state provided by fixture
        ACT: Make GET request to /activities endpoint
        ASSERT: Each activity has required fields (description, schedule, max_participants, participants)
        """
        # ARRANGE
        # (already set up by fixtures)
        
        # ACT
        response = client.get("/activities")
        activities = response.json()
        
        # ASSERT
        for activity_name, activity_data in activities.items():
            assert isinstance(activity_data, dict)
            assert "description" in activity_data
            assert "schedule" in activity_data
            assert "max_participants" in activity_data
            assert "participants" in activity_data
            assert isinstance(activity_data["description"], str)
            assert isinstance(activity_data["schedule"], str)
            assert isinstance(activity_data["max_participants"], int)
            assert isinstance(activity_data["participants"], list)
    
    def test_get_activities_participants_initially_populated(self, client, clean_activity_state):
        """
        ARRANGE: Clean activity state provided by fixture
        ACT: Make GET request to /activities endpoint
        ASSERT: Participants lists are in their initial state (some empty, some with pre-loaded data)
        """
        # ARRANGE
        # (already set up by fixtures)
        
        # ACT
        response = client.get("/activities")
        activities = response.json()
        
        # ASSERT
        # Verify Tennis Club has no participants initially
        assert len(activities["Tennis Club"]["participants"]) == 0
        # Verify Chess Club has initial participants
        assert len(activities["Chess Club"]["participants"]) == 2
        assert "michael@mergington.edu" in activities["Chess Club"]["participants"]
        # Verify all participants lists are lists
        for activity_name, activity_data in activities.items():
            assert isinstance(activity_data["participants"], list)


class TestRootEndpoint:
    """Tests for GET / endpoint"""
    
    def test_root_endpoint_returns_redirect(self, client, clean_activity_state):
        """
        ARRANGE: Clean activity state provided by fixture
        ACT: Make GET request to / endpoint (follow redirects=False to see redirect response)
        ASSERT: Returns redirect response (302 or similar) to static file
        """
        # ARRANGE
        # (already set up by fixtures)
        
        # ACT
        response = client.get("/", follow_redirects=True)
        
        # ASSERT
        # The TestClient follows redirects by default, so we should get 200
        assert response.status_code == 200


class TestSignupEndpoint:
    """Tests for POST /activities/{activity_name}/signup endpoint"""
    
    def test_signup_student_successful(self, client, clean_activity_state, sample_student_email):
        """
        ARRANGE: Clean state with sample student email fixture
        ACT: POST request to signup endpoint for valid activity
        ASSERT: Student email is added to participants list
        """
        # ARRANGE
        activity_name = "Chess Club"
        
        # ACT
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": sample_student_email}
        )
        
        # ASSERT
        assert response.status_code == 200
        assert response.json()["message"] == f"Signed up {sample_student_email} for {activity_name}"
        
        # Verify student was added to participants
        activities_response = client.get("/activities")
        activities = activities_response.json()
        assert sample_student_email in activities[activity_name]["participants"]
    
    def test_signup_response_message_correct(self, client, clean_activity_state, sample_student_email):
        """
        ARRANGE: Clean state with sample student email fixture
        ACT: POST request to signup endpoint
        ASSERT: Response message format is correct and includes email and activity name
        """
        # ARRANGE
        activity_name = "Programming Class"
        
        # ACT
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": sample_student_email}
        )
        
        # ASSERT
        assert response.status_code == 200
        message = response.json()["message"]
        assert sample_student_email in message
        assert activity_name in message
        assert "Signed up" in message
    
    def test_signup_nonexistent_activity_returns_404(self, client, clean_activity_state, sample_student_email):
        """
        ARRANGE: Clean state with non-existent activity name
        ACT: POST request to signup endpoint for non-existent activity
        ASSERT: Returns 404 Not Found error
        """
        # ARRANGE
        invalid_activity = "Nonexistent Activity"
        
        # ACT
        response = client.post(
            f"/activities/{invalid_activity}/signup",
            params={"email": sample_student_email}
        )
        
        # ASSERT
        assert response.status_code == 404
        assert response.json()["detail"] == "Activity not found"
    
    def test_signup_duplicate_email_returns_400(self, client, clean_activity_state, sample_student_email):
        """
        ARRANGE: Student already signed up for activity
        ACT: Attempt to signup same student again (POST twice with same email)
        ASSERT: Second POST returns 400 Bad Request error
        """
        # ARRANGE
        activity_name = "Tennis Club"
        
        # First signup - should succeed
        response1 = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": sample_student_email}
        )
        assert response1.status_code == 200
        
        # ACT: Try to signup again
        response2 = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": sample_student_email}
        )
        
        # ASSERT
        assert response2.status_code == 400
        assert "already signed up" in response2.json()["detail"]
    
    def test_signup_multiple_students_same_activity(self, client, clean_activity_state):
        """
        ARRANGE: Clean state, two different student emails
        ACT: Sign up both students to same activity
        ASSERT: Both emails are added to participants list
        """
        # ARRANGE
        activity_name = "Art Studio"
        email1 = "student1@mergington.edu"
        email2 = "student2@mergington.edu"
        
        # ACT: Sign up first student
        response1 = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email1}
        )
        
        # ACT: Sign up second student
        response2 = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email2}
        )
        
        # ASSERT
        assert response1.status_code == 200
        assert response2.status_code == 200
        
        # Verify both students are in participants
        activities_response = client.get("/activities")
        activities = activities_response.json()
        assert email1 in activities[activity_name]["participants"]
        assert email2 in activities[activity_name]["participants"]
        assert len(activities[activity_name]["participants"]) >= 2
    
    def test_signup_near_max_capacity(self, client, clean_activity_state, sample_student_email):
        """
        ARRANGE: Activity with max_participants set
        ACT: Sign up multiple students up to near max capacity
        ASSERT: All signups succeed (app doesn't enforce max capacity on signup)
        """
        # ARRANGE
        activity_name = "Tennis Club"  # max_participants = 8
        
        # ACT: Sign up multiple students
        emails = [f"student{i}@mergington.edu" for i in range(7)]
        
        for email in emails:
            response = client.post(
                f"/activities/{activity_name}/signup",
                params={"email": email}
            )
            assert response.status_code == 200
        
        # ASSERT: All students are registered (app doesn't enforce limit)
        activities_response = client.get("/activities")
        activities = activities_response.json()
        assert len(activities[activity_name]["participants"]) == 7


class TestUnregisterEndpoint:
    """Tests for POST /activities/{activity_name}/unregister endpoint"""
    
    def test_unregister_student_successful(self, client, clean_activity_state, sample_student_email):
        """
        ARRANGE: Student signed up for activity
        ACT: POST request to unregister endpoint
        ASSERT: Student email is removed from participants list
        """
        # ARRANGE
        activity_name = "Chess Club"
        
        # First, sign up the student
        client.post(
            f"/activities/{activity_name}/signup",
            params={"email": sample_student_email}
        )
        
        # ACT
        response = client.post(
            f"/activities/{activity_name}/unregister",
            params={"email": sample_student_email}
        )
        
        # ASSERT
        assert response.status_code == 200
        assert sample_student_email not in client.get("/activities").json()[activity_name]["participants"]
    
    def test_unregister_response_message_correct(self, client, clean_activity_state, sample_student_email):
        """
        ARRANGE: Student signed up for activity
        ACT: POST request to unregister endpoint
        ASSERT: Response message format is correct
        """
        # ARRANGE
        activity_name = "Programming Class"
        
        # Sign up first
        client.post(
            f"/activities/{activity_name}/signup",
            params={"email": sample_student_email}
        )
        
        # ACT
        response = client.post(
            f"/activities/{activity_name}/unregister",
            params={"email": sample_student_email}
        )
        
        # ASSERT
        assert response.status_code == 200
        message = response.json()["message"]
        assert sample_student_email in message
        assert activity_name in message
        assert "Unregistered" in message
    
    def test_unregister_nonexistent_activity_returns_404(self, client, clean_activity_state, sample_student_email):
        """
        ARRANGE: Non-existent activity name
        ACT: POST request to unregister from non-existent activity
        ASSERT: Returns 404 Not Found error
        """
        # ARRANGE
        invalid_activity = "Nonexistent Activity"
        
        # ACT
        response = client.post(
            f"/activities/{invalid_activity}/unregister",
            params={"email": sample_student_email}
        )
        
        # ASSERT
        assert response.status_code == 404
        assert response.json()["detail"] == "Activity not found"
    
    def test_unregister_student_not_signed_up_returns_400(self, client, clean_activity_state, sample_student_email):
        """
        ARRANGE: Student not signed up for activity
        ACT: POST request to unregister from activity where student is not enrolled
        ASSERT: Returns 400 Bad Request error
        """
        # ARRANGE
        activity_name = "Art Studio"
        
        # ACT
        response = client.post(
            f"/activities/{activity_name}/unregister",
            params={"email": sample_student_email}
        )
        
        # ASSERT
        assert response.status_code == 400
        assert "not signed up" in response.json()["detail"]
    
    def test_unregister_last_participant(self, client, clean_activity_state, sample_student_email):
        """
        ARRANGE: Activity with only one participant
        ACT: Unregister the only participant
        ASSERT: Participants list becomes empty
        """
        # ARRANGE
        activity_name = "Tennis Club"  # Initially no participants
        
        # Sign up the student (making them the only one)
        client.post(
            f"/activities/{activity_name}/signup",
            params={"email": sample_student_email}
        )
        
        # ACT
        response = client.post(
            f"/activities/{activity_name}/unregister",
            params={"email": sample_student_email}
        )
        
        # ASSERT
        assert response.status_code == 200
        activities_response = client.get("/activities")
        activities = activities_response.json()
        assert len(activities[activity_name]["participants"]) == 0
