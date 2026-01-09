from typing import Dict, List


class MockStorageService:
    def __init__(self):
        self._items: List[Dict[str, object]] = []

    def save(self, item: Dict[str, object]) -> Dict[str, object]:
        self._items.append(item)
        return {"storage_id": len(self._items), "status": "stored-mock"}
