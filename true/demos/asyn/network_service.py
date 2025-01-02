"""Example of a network service using Asyn for task management."""

import asyncio
import logging
from typing import Dict, Set, Optional
from true.asyn import Asyn, TaskState

class NetworkService:
    """A simple network service that manages client connections."""
    
    def __init__(self, host: str = 'localhost', port: int = 8888):
        self.host = host
        self.port = port
        self._clients: Dict[str, Asyn] = {}
        self._server: Optional[asyncio.AbstractServer] = None
        self._service: Optional[Asyn] = None
        self._monitor: Optional[Asyn] = None

    def _get_client_id(self, writer: asyncio.StreamWriter) -> str:
        """Get a unique identifier for a client connection."""
        peername = writer.get_extra_info('peername')
        return f"client_{peername}"

    async def handle_client(self, reader: asyncio.StreamReader, 
                          writer: asyncio.StreamWriter, 
                          client: Asyn) -> None:
        """Handle a client connection."""
        client_id = self._get_client_id(writer)
        try:
            while True:
                # Read data from client
                data = await reader.read(100)
                if not data:
                    break

                message = data.decode()
                addr = writer.get_extra_info('peername')
                print(f"Received {message!r} from {addr!r}")

                # Echo back to client
                print(f"Send: {message!r}")
                writer.write(data)
                await writer.drain()

        except asyncio.CancelledError:
            print(f"Client {client_id} connection cancelled")
            raise
        except Exception as e:
            print(f"Error handling client {client_id}: {e}")
            raise
        finally:
            # Clean up
            writer.close()
            try:
                await writer.wait_closed()
            except Exception:
                pass
            self._clients.pop(client_id, None)

    async def cleanup_monitor(self) -> None:
        """Monitor and cleanup disconnected clients."""
        try:
            while True:
                await asyncio.sleep(5)  # Check every 5 seconds
                for client_id, client in list(self._clients.items()):
                    if client.info.state in (TaskState.COMPLETED, TaskState.FAILED, TaskState.CANCELLED):
                        print(f"Cleaning up disconnected client {client_id}")
                        self._clients.pop(client_id, None)
        except asyncio.CancelledError:
            print("Cleanup monitor cancelled")
            raise

    async def client_connected_cb(self, reader: asyncio.StreamReader, 
                                writer: asyncio.StreamWriter) -> None:
        """Callback for new client connections."""
        client_id = self._get_client_id(writer)
        print(f"New connection from {client_id}")
        
        # Create a new task for this client
        async with await self._service.create_task(
            self.handle_client(reader, writer, None),
            name=client_id
        ) as client:
            self._clients[client_id] = client
            try:
                await client.run(self.handle_client(reader, writer, client))
            except Exception as e:
                print(f"Client {client_id} error: {e}")

    async def start(self) -> None:
        """Start the network service."""
        # Create main service task
        async with Asyn(name="network_service") as service:
            self._service = service
            
            # Start server
            self._server = await asyncio.start_server(
                self.client_connected_cb,
                self.host,
                self.port
            )
            
            addr = self._server.sockets[0].getsockname()
            print(f'Serving on {addr}')

            # Start cleanup monitor
            async with await service.create_task(
                self.cleanup_monitor(),
                name="cleanup_monitor"
            ) as monitor:
                self._monitor = monitor
                
                # Run server
                async with self._server:
                    await self._server.serve_forever()

async def run_client(host: str, port: int, messages: list) -> None:
    """Run a test client."""
    async with Asyn(name=f"client_{port}") as client:
        try:
            reader, writer = await asyncio.open_connection(host, port)
            
            try:
                for msg in messages:
                    print(f'Client sending: {msg!r}')
                    writer.write(msg.encode())
                    await writer.drain()

                    data = await reader.read(100)
                    print(f'Client received: {data.decode()!r}')
                    await asyncio.sleep(0.5)  # Add delay between messages
            finally:
                writer.close()
                try:
                    await writer.wait_closed()
                except Exception:
                    pass
        except Exception as e:
            print(f"Client error: {e}")

async def main():
    """Run the example."""
    # Start server
    service = NetworkService()
    server_task = asyncio.create_task(service.start())

    # Wait for server to start
    await asyncio.sleep(0.5)  # Increased delay to ensure server is ready

    # Run test clients sequentially to avoid conflicts
    for i in range(3):
        messages = [f"Hello {i} {j}" for j in range(2)]
        await run_client('localhost', 8888, messages)
        await asyncio.sleep(0.1)  # Add delay between clients

    # Clean up server
    server_task.cancel()
    try:
        await server_task
    except asyncio.CancelledError:
        pass

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
