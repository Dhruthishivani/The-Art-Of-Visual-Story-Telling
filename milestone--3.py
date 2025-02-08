from groq import Groq
import streamlit as st
import os
import base64
from dotenv import load_dotenv
load_dotenv()

groq_api_key = os.getenv("GROQ_API_KEY")

# Function to encode the image
def encode_image(uploaded_image):
    return base64.b64encode(uploaded_image.read()).decode('utf-8')

st.set_page_config(page_title="Story Generation from Image", layout="wide")

# CSS Styling for a Professional Look
st.markdown("""
    <style>
    .main {
        font-family: 'Arial', sans-serif;
        background-color: #f0f0f5;
    }
    .title {
        color: #2F4F4F;
        font-size: 36px;
        font-weight: bold;
        text-align: center;
        margin-top: 30px;
    }
    .subheader {
        color: #4B0082;
    }
    .description-box {
        background-color: #ffffff;
        padding: 15px;
        border-radius: 8px;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
    }
    .button {
        background-color: #4CAF50;
        color: white;
        font-size: 16px;
        font-weight: bold;
        padding: 10px 20px;
        border-radius: 5px;
        margin-top: 20px;
        width: 100%;
    }
    .button:hover {
        background-color: #45a049;
    }
    .file-download {
        background-color: #008CBA;
        color: white;
        font-size: 16px;
        font-weight: bold;
        padding: 10px 20px;
        border-radius: 5px;
    }
    .file-download:hover {
        background-color: #007bb5;
    }
    .image-box {
        border: 5px solid #dddddd;
        border-radius: 10px;
        box-shadow: 0px 4px 15px rgba(0, 0, 0, 0.1);
        padding: 10px;
        margin: 20px 0;
    }
    .sidebar-title {
        font-size: 20px;
        font-weight: bold;
        color: #2F4F4F;
    }
    .main-title {
        text-align: center;
        font-size: 30px;
        font-weight: bold;
        color: #2F4F4F;
    }
    </style>
""", unsafe_allow_html=True)

st.title('Turn Pictures into Stories')

# Sidebar for uploading image and preferences
st.sidebar.header("Upload Image & Set Preferences")
uploaded_image = st.sidebar.file_uploader("Choose an image", type=["jpg", "jpeg", "png"])

# Genre, Length, Character Count selection
genre = st.sidebar.selectbox("Select the genre of your story:", ["Adventure", "Fantasy", "Romance", "Mystery", "Science Fiction", "Horror", "Comedy", "Drama"])

length = st.sidebar.selectbox("Select the length of your story:", ["Short", "Medium", "Long"])

num_characters = st.sidebar.slider("Select the number of characters in the story:", min_value=100, max_value=2000, step=100, value=500)

client = Groq(api_key=groq_api_key)
llava_model = 'llama-3.2-11b-vision-preview'
llama31_model = 'llama-3.3-70b-versatile'

# Function to generate image description (4 lines)
def describe_image(client, model, base64_image):
    prompt = "Describe the image in 4 lines."
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_image}",
                        },
                    },
                ],
            }
        ],
        model=model
    )
    return chat_completion.choices[0].message.content

# Function to generate story
def short_story_generation(client, image_description, genre, length, num_characters):
    genre_prompts = {
        "Adventure": "Write an adventurous story based on the image description.",
        "Fantasy": "Create a fantasy story with magical elements based on the image description.",
        "Romance": "Write a romantic story based on the scene in the image.",
        "Mystery": "Write a mystery story based on the clues found in the image.",
        "Science Fiction": "Create a sci-fi story set in the future based on the image description.",
        "Horror": "Write a horror story based on the eerie elements in the image.",
        "Comedy": "Write a comedic story based on the image description.",
        "Drama": "Write a dramatic story based on the emotional elements in the image."
    }

    prompt = genre_prompts.get(genre, "Write a general story based on the image description.")

    length_prompts = {
        "Short": "Write a brief story with about 150-300 words.",
        "Medium": "Write a medium-length story with about 500-700 words.",
        "Long": "Write a detailed and elaborate story with more than 1000 words."
    }
    length_prompt = length_prompts.get(length, "Write a general-length story.")

    character_count_prompt = f"Ensure the story has around {num_characters} characters."

    full_prompt = f"{prompt} {image_description} {length_prompt} {character_count_prompt}"

    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": "You are an expert in writing stories based on genres, length, and character count. Follow the prompts to craft a unique story.",
            },
            {
                "role": "user",
                "content": full_prompt,
            }
        ],
        model=llama31_model
    )
    return chat_completion.choices[0].message.content

# Function to save story to a file
def save_story_to_file(story, filename="generated_story.txt"):
    with open(filename, "w") as f:
        f.write(story)
    return filename

def main():
    st.title("Generate Your Story from Image")

    if uploaded_image:
        # Display the uploaded image with a border
        st.markdown('<div class="image-box">', unsafe_allow_html=True)
        st.image(uploaded_image, caption="Uploaded Image", use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

        # Encode the image to base64
        base64_image = encode_image(uploaded_image)

        # Show progress bar
        progress_bar = st.progress(0)

        with st.spinner("Generating story... this might take a few moments."):
            # Step 1: Generate a brief description of the image (4 lines)
            image_description = describe_image(client, llava_model, base64_image)
            progress_bar.progress(30)

            # Display the description
            st.markdown(f"<div class='description-box'><b>Image Description:</b><br>{image_description}</div>", unsafe_allow_html=True)
            progress_bar.progress(60)

            # Step 2: Generate the story based on selected preferences
            story = short_story_generation(client, image_description, genre, length, num_characters)
            progress_bar.progress(100)

            # Display the generated story in a card layout
            st.markdown(f"<div class='description-box'><b>Generated {genre} Story:</b><br>{story}</div>", unsafe_allow_html=True)

            # Provide download option
            story_file = save_story_to_file(story)
            st.download_button(
                label="Download Story as Text File",
                data=open(story_file, "r").read(),
                file_name="generated_story.txt",
                mime="text/plain",
                use_container_width=True,
                key="download_story"
            )

if __name__ == "__main__":
    main()
