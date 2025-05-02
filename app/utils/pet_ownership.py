from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.models.pet import Pet

def verify_pet_ownership(db: Session, user_id: int, pet_id: int) -> None:
    """
    Verify that the user has ownership or access rights to the pet.
    Raises HTTPException if not authorized.
    """
    # Check if pet exists
    pet = db.query(Pet).filter(Pet.id == pet_id).first()
    if not pet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pet not found"
        )
    
    # Check if user is admin (can access all pets)
    # For future implementation: Check user role
    
    # Check if user is the owner of the pet
    if pet.user_id != user_id:
        # For future implementation: Check adoption records
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to access this pet's records"
        )
    
    return True
