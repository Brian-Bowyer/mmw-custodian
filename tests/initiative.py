from app.controllers import initiative


def test_it_creates_an_initiative(db):
    result = initiative.create_initiative("123456")
    assert result

    db_entry = db.fetch_one("SELECT * FROM initiative WHERE channel_id = '123456'")
    assert db_entry["channel_id"] == "123456"
