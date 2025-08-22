# 🚨 UserStatus Relationship Error - Fix Guide

## Problem Description
The error occurs because the learn-service container is using an outdated version of the shared-models package that still has the incorrect relationship configuration:

```
sqlalchemy.exc.InvalidRequestError: back_populates on relationship 'UserStatus.user' refers to attribute 'User.status' that is not a relationship.
```

## Root Cause
The UserStatus model was trying to back_populate to `User.status` (which is a column), instead of `User.user_status` (which is the correct relationship).

## ✅ Fix Applied in shared-models v1.1.2

### Changes Made:
1. **Added missing relationship in User model:**
   ```python
   user_status: Mapped[Optional["UserStatus"]] = relationship(
       "UserStatus", back_populates="user", cascade="all, delete-orphan"
   )
   ```

2. **Fixed UserStatus back_populates:**
   ```python
   # BEFORE (incorrect):
   user: Mapped["User"] = relationship("User", back_populates="status")
   
   # AFTER (correct):
   user: Mapped["User"] = relationship("User", back_populates="user_status")
   ```

## 🔧 Solution Steps

### For learn-service:

1. **Update shared-models dependency to v1.1.2:**
   ```bash
   # In your learn-service pyproject.toml or requirements.txt
   shared-models = "git+https://github.com/ViachaslauKazakou/shared-models.git@v1.1.2"
   ```

2. **Rebuild the container:**
   ```bash
   docker-compose down
   docker-compose build --no-cache learn_app
   docker-compose up -d
   ```

3. **Or update without rebuilding (if using pip):**
   ```bash
   docker exec learn-service-learn_app-1 pip install --upgrade git+https://github.com/ViachaslauKazakou/shared-models.git@v1.1.2
   docker-compose restart learn_app
   ```

### Alternative: Force dependency update
If the above doesn't work, force reinstall:
```bash
docker exec learn-service-learn_app-1 pip uninstall shared-models -y
docker exec learn-service-learn_app-1 pip install git+https://github.com/ViachaslauKazakou/shared-models.git@v1.1.2
docker-compose restart learn_app
```

## 🔍 Verification

After updating, test that the fix worked:

```python
# Test script to run in the container
from shared_models.models import UserStatus
from sqlalchemy.orm import configure_mappers

try:
    configure_mappers()
    print("✅ All relationships configured successfully!")
except Exception as e:
    print(f"❌ Error: {e}")
```

## 📝 Current Versions
- **shared-models**: v1.1.2 (contains the fix)
- **Fix commit**: `50705b3 fix user relations`

## 🚀 Prevention
To prevent this in the future:
- Always pin specific versions of shared-models in your services
- Use automated dependency update workflows
- Test relationship configurations in CI/CD

---
*Generated on: $(date)*
