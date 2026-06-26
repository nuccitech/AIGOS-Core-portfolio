from dataclasses import dataclass

from webapp.services.content_service import ContentService
from webapp.services.policy_service import PolicyService
from webapp.services.storage_service import MockStorageService


@dataclass
class ServiceContainer:
    content: ContentService
    policy: PolicyService
    storage: MockStorageService


def build_container() -> ServiceContainer:
    return ServiceContainer(
        content=ContentService(),
        policy=PolicyService(),
        storage=MockStorageService(),
    )
