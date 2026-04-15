"""
High School Management System API

A super simple FastAPI application that allows students to view and sign up
for extracurricular activities at Mergington High School.
"""

from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
import os
from pathlib import Path
from typing import Optional
from fastapi import Body
from uuid import uuid4

app = FastAPI(title="Mergington High School API",
              description="API for viewing and signing up for extracurricular activities")

# Mount the static files directory
current_dir = Path(__file__).parent
app.mount("/static", StaticFiles(directory=os.path.join(Path(__file__).parent,
          "static")), name="static")

# In-memory activity database
activities = {
    "Chess Club": {
        "description": "Learn strategies and compete in chess tournaments",
        "schedule": "Fridays, 3:30 PM - 5:00 PM",
        "max_participants": 12,
        "participants": ["michael@mergington.edu", "daniel@mergington.edu"],
        "content": [
            {"type": "text", "title": "Welcome", "body": "Join us for chess every Friday!"}
        ]
    },
    "Programming Class": {
        "description": "Learn programming fundamentals and build software projects",
        "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
        "max_participants": 20,
        "participants": ["emma@mergington.edu", "sophia@mergington.edu"],
        "content": []
    },
    "Gym Class": {
        "description": "Physical education and sports activities",
        "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
        "max_participants": 30,
        "participants": ["john@mergington.edu", "olivia@mergington.edu"],
        "content": []
    },
    "Soccer Team": {
        "description": "Join the school soccer team and compete in matches",
        "schedule": "Tuesdays and Thursdays, 4:00 PM - 5:30 PM",
        "max_participants": 22,
        "participants": ["liam@mergington.edu", "noah@mergington.edu"],
        "content": []
    },
    "Basketball Team": {
        "description": "Practice and play basketball with the school team",
        "schedule": "Wednesdays and Fridays, 3:30 PM - 5:00 PM",
        "max_participants": 15,
        "participants": ["ava@mergington.edu", "mia@mergington.edu"],
        "content": []
    },
    "Art Club": {
        "description": "Explore your creativity through painting and drawing",
        "schedule": "Thursdays, 3:30 PM - 5:00 PM",
        "max_participants": 15,
        "participants": ["amelia@mergington.edu", "harper@mergington.edu"],
        "content": []
    },
    "Drama Club": {
        "description": "Act, direct, and produce plays and performances",
        "schedule": "Mondays and Wednesdays, 4:00 PM - 5:30 PM",
        "max_participants": 20,
        "participants": ["ella@mergington.edu", "scarlett@mergington.edu"],
        "content": []
    },
    "Math Club": {
        "description": "Solve challenging problems and participate in math competitions",
        "schedule": "Tuesdays, 3:30 PM - 4:30 PM",
        "max_participants": 10,
        "participants": ["james@mergington.edu", "benjamin@mergington.edu"],
        "content": []
    },
    "Debate Team": {
        "description": "Develop public speaking and argumentation skills",
        "schedule": "Fridays, 4:00 PM - 5:30 PM",
        "max_participants": 12,
        "participants": ["charlotte@mergington.edu", "henry@mergington.edu"],
        "content": []
    }
}


@app.get("/")
def root():
    return RedirectResponse(url="/static/index.html")


@app.get("/activities")
def get_activities():
    return activities


@app.post("/activities/{activity_name}/signup")
async def signup_for_activity(
    activity_name: str,
    email: str = Form(...),
    photo: Optional[UploadFile] = File(None),
):
    """Sign up a student for an activity, optionally uploading a photo."""
    # Validate activity exists
    if activity_name not in activities:
        raise HTTPException(status_code=404, detail="Activity not found")

    # Get the specific activity
    activity = activities[activity_name]

    # Validate student is not already signed up
    if email in activity["participants"]:
        raise HTTPException(
            status_code=400,
            detail="Student is already signed up"
        )

    photo_url = None
    # If a photo was uploaded, validate and save it
    if photo is not None:
        # Basic content-type check
        if not (photo.content_type and photo.content_type.startswith("image/")):
            raise HTTPException(status_code=400, detail="Uploaded file must be an image")

        # Ensure uploads directory exists inside static
        uploads_dir = current_dir / "static" / "uploads"
        uploads_dir.mkdir(parents=True, exist_ok=True)

        # Generate unique filename while preserving extension
        original_name = Path(photo.filename).name
        ext = Path(original_name).suffix or ""
        filename = f"{uuid4().hex}{ext}"
        dest_path = uploads_dir / filename

        # Save file contents
        contents = await photo.read()
        with open(dest_path, "wb") as f:
            f.write(contents)

        photo_url = f"/static/uploads/{filename}"

        # Record the photo with the activity (non-persistent, in-memory)
        if "photos" not in activity:
            activity["photos"] = []
        activity["photos"].append({"email": email, "photo_url": photo_url})

    # Add student
    activity["participants"].append(email)

    resp = {"message": f"Signed up {email} for {activity_name}"}
    if photo_url is not None:
        resp["photo_url"] = photo_url
    return resp


@app.delete("/activities/{activity_name}/unregister")
def unregister_from_activity(activity_name: str, email: str):
    """Unregister a student from an activity"""
    # Validate activity exists
    if activity_name not in activities:
        raise HTTPException(status_code=404, detail="Activity not found")

    # Get the specific activity
    activity = activities[activity_name]

    # Validate student is signed up
    if email not in activity["participants"]:
        raise HTTPException(
            status_code=400,
            detail="Student is not signed up for this activity"
        )

    # Remove student
    activity["participants"].remove(email)
    return {"message": f"Unregistered {email} from {activity_name}"}


@app.get("/activities/{activity_name}/content")
def get_activity_content(activity_name: str):
    if activity_name not in activities:
        raise HTTPException(status_code=404, detail="Activity not found")
    return activities[activity_name]["content"]


@app.post("/activities/{activity_name}/content")
def add_activity_content(activity_name: str, content: dict = Body(...)):
    if activity_name not in activities:
        raise HTTPException(status_code=404, detail="Activity not found")
    if "type" not in content or content["type"] not in ["text", "link", "image", "video"]:
        raise HTTPException(status_code=400, detail="Content type must be one of: text, link, image, video")
    activities[activity_name]["content"].append(content)
    return {"message": f"Content added to {activity_name}", "content": content}


@app.put("/activities/{activity_name}/content/{content_idx}")
def update_activity_content(activity_name: str, content_idx: int, content: dict = Body(...)):
    if activity_name not in activities:
        raise HTTPException(status_code=404, detail="Activity not found")
    if content_idx < 0 or content_idx >= len(activities[activity_name]["content"]):
        raise HTTPException(status_code=404, detail="Content not found")
    if "type" not in content or content["type"] not in ["text", "link", "image", "video"]:
        raise HTTPException(status_code=400, detail="Content type must be one of: text, link, image, video")
    activities[activity_name]["content"][content_idx] = content
    return {"message": f"Content updated for {activity_name}", "content": content}


@app.delete("/activities/{activity_name}/content/{content_idx}")
def delete_activity_content(activity_name: str, content_idx: int):
    if activity_name not in activities:
        raise HTTPException(status_code=404, detail="Activity not found")
    if content_idx < 0 or content_idx >= len(activities[activity_name]["content"]):
        raise HTTPException(status_code=404, detail="Content not found")
    removed = activities[activity_name]["content"].pop(content_idx)
    return {"message": f"Content removed from {activity_name}", "content": removed}