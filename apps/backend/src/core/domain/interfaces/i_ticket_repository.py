"""Interface for ticket repository."""

from typing import Protocol
from uuid import UUID

from usipipo_commons.domain.entities import Ticket, TicketCategory, TicketMessage, TicketStatus


class ITicketRepository(Protocol):
    """Contract for ticket repository."""

    def save(self, ticket: Ticket) -> Ticket:
        """Saves a new ticket."""

    def get_by_id(self, ticket_id: UUID) -> Ticket | None:
        """Gets a ticket by its ID."""

    def get_by_simple_id(self, simple_id: int) -> Ticket | None:
        """Gets a ticket by its simplified ID (int)."""

    def get_by_user(self, user_id: UUID) -> list[Ticket]:
        """Gets all tickets from a user."""

    def update(self, ticket: Ticket) -> Ticket:
        """Updates an existing ticket."""

    def get_by_status(self, status: TicketStatus) -> list[Ticket]:
        """Gets tickets by status."""

    def get_by_category(self, category: TicketCategory) -> list[Ticket]:
        """Gets tickets by category."""

    def get_all_open(self) -> list[Ticket]:
        """Gets all open tickets (OPEN or RESPONDED)."""

    def save_message(self, message: TicketMessage) -> TicketMessage:
        """Saves a ticket message."""

    def get_messages(self, ticket_id: UUID) -> list[TicketMessage]:
        """Gets all messages from a ticket."""

    def count_open(self) -> int:
        """Counts open tickets."""
