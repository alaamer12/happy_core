import asyncio
import contextlib
import logging
from typing import Optional, Dict, Any, Callable

from happy.exceptions import OperationError, ServiceNotFoundError
from happy.types import BaaSProviderProtocol, ThirdPartyServiceProviderProtocol

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Handler Classes
class BaaSHandler:
    def __init__(self, baas_provider: BaaSProviderProtocol) -> None:
        self.baas_provider = baas_provider

    async def connect(self) -> None:
        try:
            await self.baas_provider.connect()
            logger.info("BaaS provider connected.")
        except Exception as e:
            logger.error(f"Failed to connect to BaaS provider: {e}")
            raise ConnectionError("Failed to connect to BaaS provider.") from e

    async def close_connection(self) -> None:
        try:
            await self.baas_provider.close_connection()
            logger.info("BaaS provider connection closed.")
        except Exception as e:
            logger.error(f"Failed to close connection to BaaS provider: {e}")
            raise ConnectionError("Failed to close connection to BaaS provider.") from e

    async def create_user(self, user_data: Dict[str, Any]) -> None:
        try:
            await self.baas_provider.create_user(user_data)
            logger.info(f"User created with data: {user_data}")
        except Exception as e:
            logger.error(f"Failed to create user: {e}")
            raise OperationError("Failed to create user.") from e

    async def get_user(self, user_id: str) -> Optional[Dict[str, Any]]:
        try:
            user = await self.baas_provider.get_user(user_id)
            logger.info(f"Fetched user with ID: {user_id}")
            return user
        except Exception as e:
            logger.error(f"Failed to get user: {e}")
            raise OperationError("Failed to get user.") from e

    # Additional methods (insert_data, update_data, etc.) can be similarly implemented


class ThirdPartyServicesHandler:
    def __init__(
            self,
            service_providers: Dict[str, ThirdPartyServiceProviderProtocol],
            concurrency_limit: int = 10
    ) -> None:
        self.service_providers = service_providers
        self.semaphore = asyncio.Semaphore(concurrency_limit)

    @classmethod
    def register(cls, config: Dict[str, Dict[str, str]],
                 provider_cls: Callable[..., ThirdPartyServiceProviderProtocol]) -> 'ThirdPartyServicesHandler':
        providers = {}
        for service_name, service_config in config.items():
            try:
                provider_cls.register(service_config)
                providers[service_name] = provider_cls()
                logger.info(f"Registered service provider: {service_name}")
            except Exception as e:
                logger.error(f"Failed to register service provider {service_name}: {e}")
                raise OperationError(f"Failed to register service provider {service_name}.") from e
        return cls(providers)

    @contextlib.asynccontextmanager
    async def run_service(self, service_name: str) -> None:
        if service_name not in self.service_providers:
            logger.error(f"Service '{service_name}' not found.")
            raise ServiceNotFoundError(f"Service '{service_name}' not found.")

        provider = self.service_providers[service_name]
        try:
            await provider.connect()
            logger.info(f"Service '{service_name}' connected.")
            yield
        except Exception as e:
            logger.error(f"Error running service '{service_name}': {e}")
            raise OperationError(f"Error running service '{service_name}'.") from e
        finally:
            try:
                await provider.close_connection()
                logger.info(f"Service '{service_name}' connection closed.")
            except Exception as e:
                logger.error(f"Failed to close service '{service_name}': {e}")
                raise ConnectionError(f"Failed to close service '{service_name}'.") from e

    async def connect(self, service_name: str) -> None:
        if service_name not in self.service_providers:
            logger.error(f"Service '{service_name}' not found.")
            raise ServiceNotFoundError(f"Service '{service_name}' not found.")
        try:
            await self.service_providers[service_name].connect()
            logger.info(f"Connected to service '{service_name}'.")
        except Exception as e:
            logger.error(f"Failed to connect to service '{service_name}': {e}")
            raise ConnectionError(f"Failed to connect to service '{service_name}'.") from e

    async def close_connection(self, service_name: str) -> None:
        if service_name not in self.service_providers:
            logger.error(f"Service '{service_name}' not found.")
            raise ServiceNotFoundError(f"Service '{service_name}' not found.")
        try:
            await self.service_providers[service_name].close_connection()
            logger.info(f"Connection to service '{service_name}' closed.")
        except Exception as e:
            logger.error(f"Failed to close connection to service '{service_name}': {e}")
            raise ConnectionError(f"Failed to close connection to service '{service_name}'.") from e

    async def connect_all(self) -> None:
        tasks = [self.connect(service) for service in self.service_providers]
        await asyncio.gather(*tasks, return_exceptions=True)

    async def close_connection_all(self) -> None:
        tasks = [self.close_connection(service) for service in self.service_providers]
        await asyncio.gather(*tasks, return_exceptions=True)


# Null Provider Implementation
class NullThirdPartyServiceProvider(ThirdPartyServiceProviderProtocol):
    async def connect(self) -> None:
        pass

    async def close_connection(self) -> None:
        pass

    @classmethod
    def register(cls, config: Dict[str, str]) -> None:
        pass

#
#
# # Example Concrete Implementation
# class SupabaseProvider(BaaSProviderProtocol):
#     def __init__(self, config: Optional[Dict[str, Any]] = None) -> None:
#         self.config = config or {}
#         self.connected = False
#
#
# async def main():
#     # Configuration for services
#     service_config = {
#         "Supabase": {
#             "url": "https://your-supabase-url.com",
#             "api_key": "your-supabase-api-key"
#         }
#     }
#
#     # Register and initialize the ThirdPartyServicesHandler
#     third_party_service = ThirdPartyServicesHandler.register(
#         config=service_config,
#         provider_cls=SupabaseProvider
#     )
#
#     # Connect to all services concurrently
#     await third_party_service.connect_all()
#
#     # Initialize BaaSHandler with the Supabase provider
#     supabase_provider = third_party_service.service_providers["Supabase"]
#     baas_handler = BaaSHandler(supabase_provider)
#
#     # Create a user
#     user_data = {"name": "Jane Doe", "email": "jane@example.com"}
#     await baas_handler.create_user(user_data)
#
#     # Fetch the user
#     user = await baas_handler.get_user("user_123")
#     logger.info(f"User Data: {user}")
#
#     # Close all connections
#     await third_party_service.close_connection_all()
#
#
# if __name__ == "__main__":
#     try:
#         asyncio.run(main())
#     except ThirdPartyServiceError as e:
#         logger.error(f"An error occurred: {e}")
