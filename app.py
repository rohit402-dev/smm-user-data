import streamlit as st
from pymongo import MongoClient
from bson.objectid import ObjectId
from datetime import datetime
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# ---- MongoDB Connection ----
MONGO_URI = os.getenv("MONGO_URL")
DB_NAME = os.getenv("DB_NAME", "prod")  # Default to "prod" if not set

# Check if MONGO_URI is set
if not MONGO_URI:
    st.error("❌ MONGO_URI environment variable is not set!")
    st.info("Please create a `.env` file with your MongoDB URI and restart the application.")
    st.code("""
# Create a .env file in your project root with:
MONGO_URI=mongodb+srv://username:password@cluster.mongodb.net/database?retryWrites=true&w=majority&family=4
DB_NAME=prod
    """)
    st.stop()

try:
    client = MongoClient(MONGO_URI)
    client.admin.command('ping')
    db = client[DB_NAME]
except Exception as e:
    st.error(f"❌ Failed to connect to MongoDB: {str(e)}")
    st.info("Please check your MONGO_URI in the .env file")
    st.stop()

media_collection = db["media"]
ai_generations_collection = db["ai_generations"]

# ---- Helper Functions ----
def format_datetime(dt):
    """Format datetime nicely for display."""
    if isinstance(dt, dict) and "$date" in dt:
        dt = dt["$date"]
    if isinstance(dt, str):
        try:
            dt = datetime.fromisoformat(dt.replace("Z", "+00:00"))
        except:
            return dt
    return dt.strftime("%Y-%m-%d %H:%M:%S") if isinstance(dt, datetime) else str(dt)

def s3_full_url(path):
    """Generate full S3 URL for stored media."""
    return f"https://cdn-2.styldod.com/{path}"  # Replace with actual S3 URL base

# ---- Streamlit UI ----
st.set_page_config(page_title="AI Generation Dashboard", layout="wide")
st.title("SMM User Usage")

# Input for User ID
email = st.text_input("Enter User Email:", "")

EMAIL_TO_UUID = {
    "prithvi@styldod.com": "0841a3b0-5001-7066-b2d0-6967bce2d9fa",
    "arul.p@styldod.com": "085123d0-a021-706c-78b4-1da037a46564",
    "arika.srivastava@olx.com": "08d19300-10e1-7033-450d-c9c9678a6fe9",
    "rohit.panda@styldod.com": "18215390-b061-70ff-2b0a-0c77¢46ealaa",
    "hannan@styldod.com": "281103f0-6031-7021-bdcb-30969efbf44c",
    "deepak.pandey@styldod.com": "3811f3f0-f051-7062-1c0e-62d9bb1e2093",
    "prithvi+1@styldod.com": "38315380-30f1-70F1-851c-a545b18670eF",
    "akhilesh@styldod.com": "38c13370-1071-7030-b9ae-43f920318F7e",
    "siddhanta.gupta@styidod.com": "38e1d350-a0d1-70e0-a168-698c58946bf4",
    "todd@styldod.com": "4831c3d0-8041-70f2-c63e-2F1fb1fbd782",
    "maximillian.diez@gmail.com": "48b163b0-a0c1-70d0-639c-b89afbb0b721",
    "rj@styldod.com": "48d11330-3021-70e5-bdb6-3a79034d0f33",
    "kiran@styldod.com": "58612370-e021-70c5-d694-930f7f88042e",
    "samardip.mandal@styldod.com": "58b12310-a081-7013-060e-d06ebb25b419",
    "komal@styldod.com": "68f133d0-7011-707a-3549-7d68d1e1ab13",
    "akash.shitole@styldod.com": "883173f0-f091-7000-73d6-fa137d086a8d",
    "akash.shitole.5595@gmail.com": "88412350-30a1-70e4-29da-1e06a1e42b25",
    "prithvi.pr1011@gmail.com": "8841f340-b081-7024-016c-cd63e147fbOF",
    "kyniemvui91@gmail.com": "8861f3c0-80b1-7069-c2ff-B8e855eTceccd",
    "manjunath.bc@styldod.com": "88e1f3d0-70c1-70b1-bfc3-6163e9e65¢75",
    "abhishek.rath@styldod.com": "9811b3c0-€031-70f7-d10a-e6F4fcde1abb",
    "zeeshan.noor@styldod.com": "a871e350-7031-70ec-Scbb-9d3840b6395",
    "adam.dabrowski@olx.pl": "a891f5c0-b041-70ef-e8e1-69fb4039668C",
    "dray@recore.net": "e8e1d390-7051-70fc-2391-5d6d8c017e57",
    "shital@styldod.com":"b8a1c320-30b1-7019-4609-c871a9c78b53",
    "tuannm.ifc@gmail.com":"e87163f0-c081-7022-81c0-deec1d713efe",
    "rohit.thorat@styldod.com":"f8016340-8021-70b3-d001-64ee38251d37",
}

user_id = EMAIL_TO_UUID.get(email)


if user_id:

    # Fetch user's media
    media_docs = list(media_collection.find({
        "UserId": user_id,
        "DeletedYN": False
    }))

    if not media_docs:
        st.warning("No media found for this user.")
    else:
        for media in media_docs:
            st.markdown("---")

            # Layout: Original image on left, AI generations on right
            col1, col2 = st.columns([1, 2])

            # ---- LEFT COLUMN: Original Image ----
            with col1:
                st.write("#### Original Image")
                media_url = media.get("MediaURL", "")
                if media_url:
                    st.image(s3_full_url(media_url), 
                             use_container_width=True)

            # ---- RIGHT COLUMN: AI Outputs Gallery ----
            with col2:
                st.write("#### Generated Outputs")

                generations = list(ai_generations_collection.find({
                    "MediaId": media["_id"]
                }))

                if not generations:
                    st.info("No AI generations for this media.")
                else:
                    # Display in a grid layout
                    cols_per_row = 3
                    for i in range(0, len(generations), cols_per_row):
                        cols = st.columns(cols_per_row)
                        for idx, gen in enumerate(generations[i:i+cols_per_row]):
                            with cols[idx]:
                                output_url = gen.get("Output", {}).get("OutputURL")
                                if output_url:
                                    st.image(s3_full_url(output_url),
                                             use_container_width=True)

                                # Show minimal details below each image
                                st.markdown(f"""
                                **Process Type:** {gen.get('ProcessType', 'N/A')}  
                                **Transformation Type:** {gen.get('TransformationType', 'N/A')}  
                                **GenerationWorkflowId:** {gen.get('GenerationWorkflowId', 'N/A')}  
                                **Created At:** {format_datetime(gen.get('CreatedAt'))}
                                """)