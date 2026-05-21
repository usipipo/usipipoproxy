"""Ticket service for support ticket management."""

import logging
from uuid import UUID

from usipipo_commons.domain.entities import (
    Ticket,
    TicketCategory,
    TicketMessage,
    TicketPriority,
    TicketStatus,
)

from src.core.domain.interfaces.i_ticket_repository import ITicketRepository

logger = logging.getLogger(__name__)


class TicketService:
    """Service for support ticket management."""

    # Category to priority mapping
    CATEGORY_PRIORITY = {
        TicketCategory.VPN_FAIL: TicketPriority.HIGH,
        TicketCategory.PAYMENT: TicketPriority.MEDIUM,
        TicketCategory.ACCOUNT: TicketPriority.LOW,
        TicketCategory.OTHER: TicketPriority.LOW,
    }

    def __init__(self, ticket_repo: ITicketRepository):
        self.ticket_repo = ticket_repo

    def _get_priority_for_category(self, category: TicketCategory) -> TicketPriority:
        """Determines automatic priority based on category."""
        return self.CATEGORY_PRIORITY.get(category, TicketPriority.LOW)

    def create_ticket(
        self, user_id: UUID, category: TicketCategory, subject: str, message: str
    ) -> Ticket:
        """Creates a new support ticket."""
        priority = self._get_priority_for_category(category)

        ticket = Ticket(user_id=user_id, category=category, priority=priority, subject=subject)

        saved_ticket = self.ticket_repo.save(ticket)
        logger.info(f"Ticket created: {saved_ticket.ticket_number} by user {user_id}")

        # Add initial message
        ticket_message = TicketMessage(
            ticket_id=saved_ticket.id,
            from_user_id=user_id,
            message=message,
            from_admin=False,
        )
        self.ticket_repo.save_message(ticket_message)

        return saved_ticket

    def get_user_tickets(self, user_id: UUID) -> list[Ticket]:
        """Gets user's tickets ordered by date."""
        return self.ticket_repo.get_by_user(user_id)

    def get_ticket_with_messages(
        self, ticket_id: UUID
    ) -> tuple[Ticket, list[TicketMessage]] | None:
        """Gets ticket with all its messages."""
        ticket = self.ticket_repo.get_by_id(ticket_id)
        if not ticket:
            return None

        messages = self.ticket_repo.get_messages(ticket_id)
        return (ticket, messages)

    def get_ticket_by_simple_id(self, simple_id: int) -> Ticket | None:
        """Gets ticket by simplified ID."""
        return self.ticket_repo.get_by_simple_id(simple_id)

    def add_user_message(
        self, ticket_id: UUID, user_id: UUID, message: str
    ) -> TicketMessage | None:
        """Adds user message to ticket."""
        ticket = self.ticket_repo.get_by_id(ticket_id)
        if not ticket or ticket.user_id != user_id:
            return None

        ticket_message = TicketMessage(
            ticket_id=ticket_id,
            from_user_id=user_id,
            message=message,
            from_admin=False,
        )
        saved = self.ticket_repo.save_message(ticket_message)

        # Update ticket status if it was responded
        if ticket.status == TicketStatus.RESPONDED:
            ticket.status = TicketStatus.OPEN
            self.ticket_repo.update(ticket)

        return saved

    def add_admin_response(
        self, ticket_id: UUID, admin_id: UUID, message: str
    ) -> TicketMessage | None:
        """Adds admin response and updates status."""
        ticket = self.ticket_repo.get_by_id(ticket_id)
        if not ticket:
            return None

        ticket_message = TicketMessage(
            ticket_id=ticket_id,
            from_user_id=admin_id,
            message=message,
            from_admin=True,
        )
        saved = self.ticket_repo.save_message(ticket_message)

        # Update status to responded
        if ticket.status in [TicketStatus.OPEN, TicketStatus.RESPONDED]:
            ticket.status = TicketStatus.RESPONDED
            self.ticket_repo.update(ticket)

        return saved

    def resolve_ticket(
        self, ticket_id: UUID, admin_id: UUID, notes: str | None = None
    ) -> Ticket | None:
        """Marks ticket as resolved."""
        ticket = self.ticket_repo.get_by_id(ticket_id)
        if not ticket:
            return None

        ticket.update_status(TicketStatus.RESOLVED, admin_id)
        if notes:
            ticket.admin_notes = notes

        updated = self.ticket_repo.update(ticket)
        logger.info(f"Ticket {ticket.ticket_number} resolved by admin {admin_id}")
        return updated

    def close_ticket(
        self, ticket_id: UUID, user_id: UUID, is_admin: bool = False
    ) -> Ticket | None:
        """Closes ticket (by user or admin)."""
        ticket = self.ticket_repo.get_by_id(ticket_id)
        if not ticket:
            return None

        # User can only close their own tickets
        if not is_admin and ticket.user_id != user_id:
            return None

        ticket.update_status(TicketStatus.CLOSED, user_id if is_admin else None)
        updated = self.ticket_repo.update(ticket)
        logger.info(
            f"Ticket {ticket.ticket_number} closed by {'admin' if is_admin else 'user'} {user_id}"
        )
        return updated

    def reopen_ticket(self, ticket_id: UUID, admin_id: UUID) -> Ticket | None:
        """Reopens a closed ticket (admin only)."""
        ticket = self.ticket_repo.get_by_id(ticket_id)
        if not ticket:
            return None

        if ticket.status != TicketStatus.CLOSED:
            return None

        ticket.update_status(TicketStatus.OPEN)
        updated = self.ticket_repo.update(ticket)
        logger.info(f"Ticket {ticket.ticket_number} reopened by admin {admin_id}")
        return updated

    def get_pending_tickets(self) -> list[Ticket]:
        """Gets pending tickets for admin."""
        return self.ticket_repo.get_all_open()

    def get_tickets_by_category(self, category: TicketCategory) -> list[Ticket]:
        """Gets tickets by category."""
        return self.ticket_repo.get_by_category(category)

    def count_open_tickets(self) -> int:
        """Counts open tickets."""
        return self.ticket_repo.count_open()
