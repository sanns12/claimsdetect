"""Database module placeholder aligned with the backend project structure.

Replace these stubs with your actual database client implementation.
"""


async def init_db() -> None:
    """Initialize database resources."""
    return None


async def get_users_collection():
    raise NotImplementedError("Implement get_users_collection in backend/database.py")


async def get_claims_collection():
    raise NotImplementedError("Implement get_claims_collection in backend/database.py")


async def get_claim_files_collection():
    raise NotImplementedError("Implement get_claim_files_collection in backend/database.py")


async def get_status_history_collection():
    raise NotImplementedError("Implement get_status_history_collection in backend/database.py")


async def get_companies_collection():
    raise NotImplementedError("Implement get_companies_collection in backend/database.py")
