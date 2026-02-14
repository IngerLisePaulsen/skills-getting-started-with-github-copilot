"""
Tests for the Mergington High School Activities API
"""

import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from app import app

client = TestClient(app)


class TestGetActivities:
    """Tests for the GET /activities endpoint"""

    def test_get_activities_returns_200(self):
        """Test that getting activities returns status 200"""
        response = client.get("/activities")
        assert response.status_code == 200

    def test_get_activities_returns_dict(self):
        """Test that activities are returned as a dictionary"""
        response = client.get("/activities")
        assert isinstance(response.json(), dict)

    def test_get_activities_contains_expected_activities(self):
        """Test that the response contains expected activity names"""
        response = client.get("/activities")
        activities = response.json()
        assert "Chess Club" in activities
        assert "Programming Class" in activities
        assert "Gym Class" in activities

    def test_activity_has_required_fields(self):
        """Test that each activity has required fields"""
        response = client.get("/activities")
        activities = response.json()
        for activity_name, activity_data in activities.items():
            assert "description" in activity_data
            assert "schedule" in activity_data
            assert "max_participants" in activity_data
            assert "participants" in activity_data


class TestSignupForActivity:
    """Tests for the POST /activities/{activity_name}/signup endpoint"""

    def test_signup_for_existing_activity_returns_200(self):
        """Test successful signup for an existing activity"""
        response = client.post(
            "/activities/Chess Club/signup?email=test@mergington.edu"
        )
        assert response.status_code == 200

    def test_signup_adds_participant_to_activity(self):
        """Test that signup adds the participant to the activity"""
        test_email = "newstudent@mergington.edu"
        response = client.post(f"/activities/Chess Club/signup?email={test_email}")
        assert response.status_code == 200
        
        activities_response = client.get("/activities")
        activities = activities_response.json()
        assert test_email in activities["Chess Club"]["participants"]

    def test_signup_returns_success_message(self):
        """Test that signup returns a success message"""
        response = client.post(
            "/activities/Programming Class/signup?email=test2@mergington.edu"
        )
        assert response.status_code == 200
        assert "Signed up" in response.json()["message"]

    def test_signup_for_nonexistent_activity_returns_404(self):
        """Test that signup for nonexistent activity returns 404"""
        response = client.post(
            "/activities/Nonexistent Activity/signup?email=test@mergington.edu"
        )
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_duplicate_signup_returns_400(self):
        """Test that duplicate signup returns 400"""
        test_email = "duplicate@mergington.edu"
        
        # First signup
        client.post(f"/activities/Chess Club/signup?email={test_email}")
        
        # Duplicate signup
        response = client.post(f"/activities/Chess Club/signup?email={test_email}")
        assert response.status_code == 400
        assert "already signed up" in response.json()["detail"].lower()


class TestRemoveParticipant:
    """Tests for the DELETE /activities/{activity_name}/remove endpoint"""

    def test_remove_existing_participant_returns_200(self):
        """Test successful removal of an existing participant"""
        test_email = "toremove@mergington.edu"
        
        # First add the participant
        client.post(f"/activities/Programming Class/signup?email={test_email}")
        
        # Then remove them
        response = client.delete(f"/activities/Programming Class/remove?email={test_email}")
        assert response.status_code == 200

    def test_remove_contestant_from_activity(self):
        """Test that remove actually removes the participant"""
        test_email = "toremove2@mergington.edu"
        
        # Add participant
        client.post(f"/activities/Gym Class/signup?email={test_email}")
        
        # Remove participant
        client.delete(f"/activities/Gym Class/remove?email={test_email}")
        
        # Verify removal
        activities_response = client.get("/activities")
        activities = activities_response.json()
        assert test_email not in activities["Gym Class"]["participants"]

    def test_remove_returns_success_message(self):
        """Test that remove returns a success message"""
        test_email = "toremove3@mergington.edu"
        
        # Add participant
        client.post(f"/activities/Chess Club/signup?email={test_email}")
        
        # Remove participant
        response = client.delete(f"/activities/Chess Club/remove?email={test_email}")
        assert response.status_code == 200
        assert "Removed" in response.json()["message"]

    def test_remove_from_nonexistent_activity_returns_404(self):
        """Test that removing from nonexistent activity returns 404"""
        response = client.delete(
            "/activities/Nonexistent Activity/remove?email=test@mergington.edu"
        )
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_remove_nonexistent_participant_returns_404(self):
        """Test that removing nonexistent participant returns 404"""
        response = client.delete(
            "/activities/Chess Club/remove?email=notexist@mergington.edu"
        )
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()


class TestRoot:
    """Tests for the GET / endpoint"""

    def test_root_redirects_to_static_index(self):
        """Test that root path redirects to static/index.html"""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert response.headers["location"] == "/static/index.html"
