## Admin Password Reset

If admin forgets their password, run this command on the server:

```python
python3 -c "
from app.database import SessionLocal
from app.models.user import User
from app.core.security import hash_password

db = SessionLocal()
admin = db.query(User).filter(User.email == 'admin@school.com').first()
admin.password_hash = hash_password('NewPassword123!')
admin.must_change_password = True
db.commit()
db.close()
print('Done')
"
```

Then inform admin of the new temporary password.