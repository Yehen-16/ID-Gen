import random
import string
import copy
from app.storage import get_db

ALPHANUM = string.ascii_uppercase + string.digits

class RecordManager:
    def __init__(self):
        self.records = {}
        self._load()

    def _load(self):
        self.records = {}
        with get_db() as conn:
            for row in conn.execute("SELECT * FROM records"):
                record = {
                    "id": row[0],
                    "name": row[1],
                    "gender": row[2],
                    "age": row[3],
                    "arc": bool(row[4]) if row[4] is not None else None,
                    "arc_link": row[5],
                    "phone": row[6],

                }
                self.records[record["id"]] = record


    def _save(self, record):
        with get_db() as conn:
            conn.execute("""
                INSERT OR REPLACE INTO records
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                record["id"],
                record["name"],
                record["gender"],
                record["age"],
                int(record["arc"]) if record["arc"] is not None else None,
                record["arc_link"],
                record["phone"]
            ))



    def _generate_id(self, gender, age_provided):
        while True:
            chars = list(ALPHANUM)

            #gen rule
            if gender == "Female":
                chars.append("F")
            else:
                chars = [c for c in chars if c!= "F"]
            
            #age rule
            if age_provided:
                base = random.choices(chars, k=6)
                base.append("#")
                random.shuffle(base)
                candidate = "".join(base)
            else:
                candidate = "".join(random.choices(chars, k =7))


            #RULES

            if gender == "Female" and "F" not in candidate:
                continue
            if gender == "Male" and "F" in candidate:
                continue

            if candidate not in self.records:
                return candidate


            
            

    def add_record(self, **record):
        if "id" not in record or not record["id"]:
            record["id"] = self._generate_id(record["gender"], record.get("age") is not None)
        self.records[record["id"]] = record
        self._save(record)
        return record



    def edit_record(self, record_id, **updates):

        record = copy.deepcopy(self.records[record_id])
        original = copy.deepcopy(record)

        if record_id not in self.records:
            raise KeyError("Record not found")

        record = self.records[record_id]
        original = record.copy()


        for key, value in updates.items():
            record[key] = value

        if record.get("gender") == "Male":
            record["arc"] = None
            record["arc_link"] = None
        elif record.get("arc") is None:
            record["arc"] = False



        editable_fields = ["name", "age", "phone", "arc_link"]

        if record.get("gender") == "Male" and "arc_link" in editable_fields:
            editable_fields.remove("arc_link")


        if record.get("gender") != original.get("gender"):
            has_changes = True
        else: 
            has_changes = any(
                record.get(field) != original.get(field)
                for field in editable_fields
            )

        has_changes = any(record.get(field) != original.get(field) for field in editable_fields)
        if not has_changes:
            raise ValueError("No changes detected")


        new_id = self._generate_id(record["gender"], record.get("age") is not None)
        record["id"] = new_id


        with get_db() as conn:
            conn.execute("DELETE FROM records WHERE id=?", (record_id,))

        del self.records[record_id]
        self.records[new_id] = record
        self._save(record)

        
        return record




    def delete_record(self, record_id):
        with get_db() as conn:
            conn.execute("DELETE FROM records WHERE id=?", (record_id,))
        del self.records[record_id]



    def search(self, query):
        query = query.lower().strip()
    
        if not query:  
            return list(self.records.values())
    
        return [
            r for r in self.records.values()
            if query in r["id"].lower() or query in r["name"].lower()
        ]
