#!/usr/bin/env python3
"""
Cleanup script to remove old anonymous users that might have problematic password hashes.
Run this once to clean up the database after the bcrypt fix.
"""

import os
import sys
from pathlib import Path

# Add the app directory to the Python path
sys.path.insert(0, str(Path(__file__).parent))

from app.core.database import SessionLocal
from app.models import User

def cleanup_anonymous_users():
    """Remove old anonymous users that might cause bcrypt issues."""
    db = SessionLocal()
    try:
        # Find and delete old anonymous users
        old_anonymous = db.query(User).filter(User.email == "anonymous@local").all()
        
        if old_anonymous:
            print(f"Found {len(old_anonymous)} old anonymous users to delete...")
            for user in old_anonymous:
                db.delete(user)
            db.commit()
            print(f"✅ Deleted {len(old_anonymous)} old anonymous users")
        else:
            print("✅ No old anonymous users found")
            
        # Also clean up any guest users that might have long passwords
        # (This is optional - guest users are created fresh each time now)
        guest_users = db.query(User).filter(User.email.like("guest-%@anonymous.local")).all()
        if guest_users:
            print(f"Found {len(guest_users)} existing guest users")
            print("Note: These will be cleaned up automatically as they're session-based")
            
    except Exception as e:
        print(f"❌ Error during cleanup: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    print("🧹 Cleaning up anonymous users...")
    cleanup_anonymous_users()
    print("✅ Cleanup complete!")