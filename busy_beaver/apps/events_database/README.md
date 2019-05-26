# Events Database

This feature polls Meetup once a day and
adds new events to the application's database.

## Notes

This needs to go into a data migration

```python
user = ApplicationUser(name="ChiPy")
db.session.add(user)
db.session.commit()
```
