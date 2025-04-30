import sys
import os
import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime
import json

# Add the project root to the path for imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.models.pet import Pet  # Make sure you have this model defined
from app.models.user import User

def fetch_pet_data(url):
    """
    Fetch pet data from the given URL
    """
    print(f"Fetching data from {url}...")
    try:
        # Set a browser-like User-Agent to avoid being blocked
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            'Accept-Language': 'vi,en-US;q=0.9,en;q=0.8'
        }
        
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Raise an exception for HTTP errors
        
        return response.text
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data: {e}")
        return None

def parse_pet_data(html_content):
    """
    Parse HTML content to extract pet data
    """
    if not html_content:
        return []
    
    pets_data = []
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Check if this is a pet detail page
    pet_details_section = soup.select_one('.caption-adoption')
    
    if pet_details_section:
        # This is a detail page, process a single pet with full details
        pet = {}
        
        # Extract pet name
        name_element = pet_details_section.select_one('h2')
        pet['name'] = name_element.text.strip() if name_element else "Unknown"
        
        # Extract pet image (main profile image)
        img_element = soup.select_one('.avatar-animal img')
        pet['image_url'] = img_element['src'] if img_element and 'src' in img_element.attrs else ""
        
        # Extract pet details from list
        details_list = pet_details_section.select('ul.list-unstyled li')
        pet_details = {}
        
        for detail in details_list:
            if not detail.strong:
                continue
                
            key = detail.strong.text.strip().replace(':', '').strip().lower()
            # Remove the strong tag to get just the value text
            detail.strong.extract()
            value = detail.text.strip()
            
            # Map the keys to our standard keys
            if 'giống' in key:
                pet_details['breed'] = value
            elif 'màu sắc' in key:
                pet_details['color'] = value
            elif 'tuổi' in key:
                pet_details['age'] = value
            elif 'cân nặng' in key:
                pet_details['weight'] = value
            elif 'giới tính' in key:
                pet_details['gender'] = value
            elif 'mã' in key:
                pet_details['id'] = value
            else:
                # Store any other details with their original key
                pet_details[key] = value
        
        # Extract pet information list (vaccinations, friendliness, etc.)
        info_elements = soup.select('.info-animal .row')
        information_list = []
        
        for info in info_elements:
            info_text = info.select_one('.col-10')
            if info_text:
                information_list.append(info_text.text.strip())
        
        pet_details['information'] = information_list
        
        # Extract pet description
        description_section = soup.select_one('div:has(> h3:-soup-contains("Tìm hiểu về thú cưng"))')
        if description_section:
            # Get text after the header and hr elements
            description_text = description_section.get_text(strip=True)
            # Remove the header text
            description_text = description_text.replace("Tìm hiểu về thú cưng", "").strip()
            pet_details['description'] = description_text
        
        # Extract image gallery
        gallery_section = soup.select('.image-gallery .owl-item a')
        gallery_urls = []
        
        for gallery_item in gallery_section:
            if 'href' in gallery_item.attrs:
                gallery_urls.append(gallery_item['href'])
        
        pet_details['image_gallery'] = gallery_urls
        
        # Determine pet type (dog/cat)
        if 'breed' in pet_details and pet_details['breed']:
            breed = pet_details['breed'].lower()
            if any(dog_breed in breed for dog_breed in ['chó', 'phốc', 'poodle', 'husky', 'corgi', 'alaska', 'becgie']):
                pet['type'] = 'dog'
            elif any(cat_breed in breed for cat_breed in ['mèo', 'anh lông ngắn', 'tam thể']):
                pet['type'] = 'cat'
            else:
                pet['type'] = 'other'
        
        pet['details'] = pet_details
        pets_data.append(pet)
        
    else:
        # Process as a list page with multiple pet cards
        pet_cards = soup.select('.pet-card, .adoption-pet-card, .team-style2')
        
        for card in pet_cards:
            pet = {}
            
            # Extract pet name
            name_element = card.select_one('.pet-name, .adoption-pet-name, h3, .card-title, .team-header')
            pet['name'] = name_element.text.strip() if name_element else "Unknown"
            
            # Extract pet image
            img_element = card.select_one('img')
            pet['image_url'] = img_element['src'] if img_element and 'src' in img_element.attrs else ""
            
            # Extract pet details (age, gender, size)
            details_elements = card.select('li, .pet-details span, .adoption-pet-details span, .card-text')
            pet_details = {}
            
            for detail in details_elements:
                text = detail.text.strip()
                
                # Try to extract structured data with labels
                if detail.strong:
                    key = detail.strong.text.replace(':', '').strip().lower()
                    detail.strong.extract()  # Remove the strong tag
                    value = detail.text.strip()
                    
                    if 'giống' in key:
                        pet_details['breed'] = value
                    elif 'màu sắc' in key:
                        pet_details['color'] = value
                    elif 'tuổi' in key:
                        pet_details['age'] = value
                    elif 'cân nặng' in key:
                        pet_details['weight'] = value
                    elif 'giới tính' in key:
                        pet_details['gender'] = value
                    elif 'mã' in key:
                        pet_details['id'] = value
                    else:
                        pet_details[key] = value
                else:
                    # Try to infer the type of information from the text
                    if 'tuổi' in text.lower() or 'age' in text.lower():
                        pet_details['age'] = text
                    elif 'giới tính' in text.lower() or 'gender' in text.lower() or 'đực' in text.lower() or 'cái' in text.lower():
                        pet_details['gender'] = text
                    elif 'kích thước' in text.lower() or 'size' in text.lower():
                        pet_details['size'] = text
                    elif 'cân nặng' in text.lower() or 'weight' in text.lower():
                        pet_details['weight'] = text
                    elif 'giống' in text.lower() or 'breed' in text.lower():
                        pet_details['breed'] = text
                    elif 'màu' in text.lower() or 'color' in text.lower():
                        pet_details['color'] = textpet['details'] = pet_details
        
        # Extract description if available
        description_element = card.select_one('.pet-description, .adoption-pet-description, .card-text')
        pet['description'] = description_element.text.strip() if description_element else ""
        
        # Extract pet type (dog/cat)
        if 'chó' in pet['name'].lower() or 'dog' in pet['name'].lower():
            pet['type'] = 'dog'
        elif 'mèo' in pet['name'].lower() or 'cat' in pet['name'].lower():
            pet['type'] = 'cat'
        else:
            # Try to determine from the description or image URL
            if pet['description'] and ('chó' in pet['description'].lower() or 'dog' in pet['description'].lower()):
                pet['type'] = 'dog'
            elif pet['description'] and ('mèo' in pet['description'].lower() or 'cat' in pet['description'].lower()):
                pet['type'] = 'cat'
            elif pet['image_url'] and ('dog' in pet['image_url'].lower() or 'chó' in pet['image_url'].lower()):
                pet['type'] = 'dog'
            elif pet['image_url'] and ('cat' in pet['image_url'].lower() or 'mèo' in pet['image_url'].lower()):
                pet['type'] = 'cat'
            else:
                pet['type'] = 'other'
        
        pets_data.append(pet)
    
    print(f"Found {len(pets_data)} pets")
    return pets_data

def insert_pets_into_db(pets_data):
    """
    Insert pet data into the database
    """
    if not pets_data:
        print("No pet data to insert")
        return
    
    # Create a database session
    db = SessionLocal()
    
    try:
        # Get admin user for assigning pets
        admin_user = db.query(User).filter(User.role == "admin").first()
        if not admin_user:
            print("No admin user found. Using the first available user...")
            admin_user = db.query(User).first()
            
        if not admin_user:
            print("No users found in the database. Cannot assign pets.")
            return
            
        # Get the actual table structure from the database to see which columns exist
        from sqlalchemy import inspect
        inspector = inspect(db.bind)
        columns = [column['name'] for column in inspector.get_columns('pets')]
        print(f"Available columns in pets table: {columns}")
        
        # Insert each pet into the database
        for pet_data in pets_data:
            # Check if pet with this name already exists
            existing_pet = db.query(Pet).filter(Pet.name == pet_data['name']).first()
            
            if existing_pet:
                print(f"Pet '{pet_data['name']}' already exists, skipping...")
                continue
            
            # Extract gender, default to 'unknown'
            gender = 'unknown'
            if 'details' in pet_data and 'gender' in pet_data['details']:
                gender_text = pet_data['details']['gender'].lower()
                if 'đực' in gender_text or 'male' in gender_text:
                    gender = 'male'
                elif 'cái' in gender_text or 'female' in gender_text:
                    gender = 'female'
            
            # Extract age
            age = None
            if 'details' in pet_data and 'age' in pet_data['details']:
                # Try to extract numeric age from text
                age_text = pet_data['details']['age']
                age_match = re.search(r'(\d+)', age_text)
                if age_match:
                    age = int(age_match.group(1))
              # Create new pet record
            # Extract breed from details if available
            breed = None
            if 'details' in pet_data and 'breed' in pet_data['details']:
                breed = pet_data['details']['breed']
        
            
            # Check for description field
            description = ''
            if 'description' in pet_data:
                description = pet_data['description']
            elif 'details' in pet_data and 'description' in pet_data['details']:
                description = pet_data['details']['description']
                
            # Prepare the pet object with only the columns that exist in the database
            pet_data_dict = {
                'name': pet_data['name'],
                'breed': breed,
                'gender': gender,
                'age': age,
                'description': description,
                'image_url': pet_data['image_url'],
                'status': "available",
                'user_id': admin_user.id
            }
            
            # Only add the type column if it exists in your database schema
            # Add this as a try/except to handle potential column mismatch
            try:
                # Check if 'type' property exists in the pet_data
                if 'type' in pet_data:
                    pet_data_dict['type'] = pet_data['type']
                # If not, try to infer it from the breed
                elif breed:
                    if any(dog_term in breed.lower() for dog_term in ['chó', 'phốc', 'poodle', 'husky', 'corgi']):
                        pet_data_dict['breed'] = 'cat'
                    else:
                        pet_data_dict['breed'] = 'other'
            except:
                # If adding the type column fails, continue without it
                print("Note: 'type' column not added - may not exist in database schema")
            
            # Add details as JSON if the column exists
            if 'details' in pet_data:
                pet_data_dict['details'] = json.dumps(pet_data['details'])
            
            new_pet = Pet(**pet_data_dict)
            
            db.add(new_pet)
            print(f"Added pet: {pet_data['name']}")
        
        # Commit all changes
        db.commit()
        print(f"Successfully inserted pet data into the database")
    
    except Exception as e:
        db.rollback()
        print(f"Error inserting pet data: {str(e)}")
    finally:
        db.close()

def main():
    """Main function to run the crawler"""
    url = "https://www.hanoipetadoption.com/vi/thu-cung/bin-22891"
    
    # Fetch HTML content from the website
    html_content = fetch_pet_data(url)
    
    if not html_content:
        print("Failed to fetch data from the website.")
        return
    
    # Parse the HTML content to extract pet data
    pets_data = parse_pet_data(html_content)
    
    if not pets_data:
        print("No pet data found on the page.")
        return
    
    # Insert the extracted pet data into the database
    insert_pets_into_db(pets_data)

if __name__ == "__main__":
    main()
