"""Payment, balance, and credit system SQLAlchemy models.

New file: shared_models/payment_models.py

Tables:
  - user_balance         — per-user balance aggregate (1 row per user)
  - balance_transactions — immutable ledger of every credit/debit movement
  - topup_requests       — stub for bank/payment topup
  - withdraw_requests    — stub for bank/card withdrawal
  - topic_votes          — forum topic upvotes (threshold >= 10 triggers reward)

Enums (TransactionType, TransactionStatus, WithdrawRequestStatus) live in
shared_models/schemas.py to avoid circular imports:
  schemas.py  <──  models.py  <──  payment_models.py  (imports enums from schemas)
"""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import List, Optional

from sqlalchemy import (
    JSON,
    DateTime,
    Enum,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from shared_models.models import Base
from shared_models.schemas import TransactionType, TransactionStatus, WithdrawRequestStatus


# NOTE: enums TransactionType / TransactionStatus / WithdrawRequestStatus
# are defined in shared_models/schemas.py (see schemas.py changes below).


class UserBalance(Base):
    """Per-user balance aggregate.

    One row per user (UNIQUE user_id).
    optimistic locking via ``version`` — always compare-and-swap before UPDATE.

    Do NOT update this table without simultaneously creating a BalanceTransaction.
    Use ``PaymentManager`` methods to keep them consistent.
    """

    __tablename__ = "user_balance"
    __table_args__ = (
        UniqueConstraint("user_id", name="uq_user_balance_user"),
        Index("ix_user_balance_user_id", "user_id"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )

    # ── Amounts — always NUMERIC(15,2), never float ──────────────────────
    available_credits: Mapped[Decimal] = mapped_column(
        Numeric(15, 2),
        nullable=False,
        default=Decimal("0.00"),
        comment="Credits freely available for spending",
    )
    reserved_credits: Mapped[Decimal] = mapped_column(
        Numeric(15, 2),
        nullable=False,
        default=Decimal("0.00"),
        comment="Credits frozen for pending bookings/transactions",
    )
    total_earned: Mapped[Decimal] = mapped_column(
        Numeric(15, 2),
        nullable=False,
        default=Decimal("0.00"),
        comment="Lifetime credits earned (rewards + topups + refunds received)",
    )
    total_spent: Mapped[Decimal] = mapped_column(
        Numeric(15, 2),
        nullable=False,
        default=Decimal("0.00"),
        comment="Lifetime credits spent (purchases + transfers out + withdrawals)",
    )

    # ── Optimistic locking ──────────────────────────────────────────────
    version: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=1,
        comment="Incremented on every update; compare before writing to detect races",
    )

    last_transaction_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    # ── Relationships ────────────────────────────────────────────────────
    user: Mapped["User"] = relationship("User", back_populates="balance")


class BalanceTransaction(Base):
    """Immutable ledger entry for every balance movement.

    This is the *source of truth*; UserBalance is an aggregate/cache.

    Rules:
    * ``amount`` is always >= 0 except for ``admin_adjustment`` (may be negative).
    * Direction implied by ``transaction_type``: earning types add to balance,
      spending types subtract.
    * Every row MUST have a unique ``idempotency_key`` — set by the caller
      to prevent duplicate charges/rewards.
    """

    __tablename__ = "balance_transactions"
    __table_args__ = (
        UniqueConstraint("idempotency_key", name="uq_btx_idempotency"),
        Index("ix_btx_user_created", "user_id", "created_at"),
        Index("ix_btx_type_status", "transaction_type", "status"),
        Index("ix_btx_reference", "reference_type", "reference_id"),
        Index("ix_btx_counterpart", "counterpart_user_id"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    # ── Ownership ────────────────────────────────────────────────────────
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="User whose balance is affected",
    )

    # ── Amount — NUMERIC(15,2), NEVER float ──────────────────────────────
    amount: Mapped[Decimal] = mapped_column(
        Numeric(15, 2),
        nullable=False,
        comment=(
            "Monetary amount. Always >= 0 except admin_adjustment which can be negative. "
            "Direction determined by transaction_type."
        ),
    )

    # ── Type & status ────────────────────────────────────────────────────
    transaction_type: Mapped[TransactionType] = mapped_column(
        Enum(TransactionType, name="transaction_type", native_enum=False),
        nullable=False,
        index=True,
    )
    status: Mapped[TransactionStatus] = mapped_column(
        Enum(TransactionStatus, name="transaction_status", native_enum=False),
        nullable=False,
        default=TransactionStatus.pending,
        index=True,
    )

    # ── Reference — what triggered the transaction ───────────────────────
    reference_type: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
        comment="Entity kind: 'topic','quiz','subject_schedule','ai_session', etc.",
    )
    reference_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
        comment="PK of the referenced entity",
    )

    # ── Transfer counterpart ─────────────────────────────────────────────
    counterpart_user_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
        comment="Other party in a transfer (mentor or student)",
    )

    # ── Human-readable note ──────────────────────────────────────────────
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # ── Idempotency ──────────────────────────────────────────────────────
    idempotency_key: Mapped[str] = mapped_column(
        String(128),
        nullable=False,
        unique=True,
        comment="Caller-generated unique key; prevents double charges/rewards",
    )

    # ── Admin tracking ───────────────────────────────────────────────────
    created_by_admin_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        comment="Set only for admin_adjustment type",
    )

    # ── AI token tracking (spend_ai_tokens only) ─────────────────────────
    ai_tokens_used: Mapped[Optional[int]] = mapped_column(
        Integer, nullable=True, comment="Total tokens consumed (prompt + completion)"
    )
    ai_tokens_prompt: Mapped[Optional[int]] = mapped_column(
        Integer, nullable=True, comment="OpenAI prompt tokens"
    )
    ai_tokens_completion: Mapped[Optional[int]] = mapped_column(
        Integer, nullable=True, comment="OpenAI completion tokens"
    )

    # ── Flexible metadata ────────────────────────────────────────────────
    extra_metadata: Mapped[Optional[dict]] = mapped_column(
        JSON,
        nullable=True,
        comment="Extra context: quiz title, model name, booking date, etc.",
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        index=True,
    )
    completed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # ── Relationships ────────────────────────────────────────────────────
    user: Mapped["User"] = relationship(
        "User",
        back_populates="transactions",
        foreign_keys=[user_id],
    )
    counterpart_user: Mapped[Optional["User"]] = relationship(
        "User",
        foreign_keys=[counterpart_user_id],
    )


class TopupRequest(Base):
    """Stub for a bank / payment-system topup request.

    Workflow (MVP):
    1. User creates a request via UI (amount, payment_method).
    2. Admin reviews and marks status = completed / failed.
    3. On completed: PaymentManager creates a ``BalanceTransaction(topup_stub)``.
    """

    __tablename__ = "topup_requests"
    __table_args__ = (Index("ix_topup_user_created", "user_id", "created_at"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    amount_requested: Mapped[Decimal] = mapped_column(
        Numeric(15, 2), nullable=False, comment="Credits requested"
    )
    # Payment info — store only reference/masked data, never raw card numbers
    payment_method: Mapped[Optional[str]] = mapped_column(
        String(50), nullable=True, comment="e.g. 'bank_transfer', 'stripe_stub'"
    )
    external_reference: Mapped[Optional[str]] = mapped_column(
        String(200),
        nullable=True,
        comment="External payment ID (masked if sensitive)",
    )
    status: Mapped[WithdrawRequestStatus] = mapped_column(
        Enum(WithdrawRequestStatus, name="topup_request_status", native_enum=False),
        nullable=False,
        default=WithdrawRequestStatus.pending,
        index=True,
    )
    processed_by_admin_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    transaction_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("balance_transactions.id", ondelete="SET NULL"), nullable=True
    )
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    processed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    user: Mapped["User"] = relationship("User", foreign_keys=[user_id])
    transaction: Mapped[Optional["BalanceTransaction"]] = relationship(
        "BalanceTransaction", foreign_keys=[transaction_id]
    )


class WithdrawRequest(Base):
    """Stub for withdrawal to bank / card.

    Workflow (MVP):
    1. User submits request (amount, masked payout details).
    2. Admin marks status = processing → completed / failed.
    3. On completed: PaymentManager creates ``BalanceTransaction(withdraw_stub)``.

    SECURITY: Never store full card/account numbers.
    Only store masked references (e.g. '**** 1234').
    """

    __tablename__ = "withdraw_requests"
    __table_args__ = (Index("ix_withdraw_user_created", "user_id", "created_at"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    amount_requested: Mapped[Decimal] = mapped_column(
        Numeric(15, 2), nullable=False, comment="Credits to withdraw"
    )
    payout_method: Mapped[Optional[str]] = mapped_column(
        String(50), nullable=True, comment="e.g. 'bank_transfer', 'card_stub'"
    )
    payout_details_masked: Mapped[Optional[str]] = mapped_column(
        String(200),
        nullable=True,
        comment="Masked destination e.g. '**** **** **** 1234'",
    )
    status: Mapped[WithdrawRequestStatus] = mapped_column(
        Enum(
            WithdrawRequestStatus, name="withdraw_request_status", native_enum=False
        ),
        nullable=False,
        default=WithdrawRequestStatus.pending,
        index=True,
    )
    processed_by_admin_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    transaction_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("balance_transactions.id", ondelete="SET NULL"), nullable=True
    )
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    processed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    user: Mapped["User"] = relationship("User", foreign_keys=[user_id])
    transaction: Mapped[Optional["BalanceTransaction"]] = relationship(
        "BalanceTransaction", foreign_keys=[transaction_id]
    )


class TopicVote(Base):
    """A single upvote on a forum topic.

    Unique per (topic_id, user_id).
    Topic rating = count of TopicVote rows for that topic.
    When rating reaches >= 10, the topic author earns a ``reward_forum_topic``
    BalanceTransaction (handled by PaymentManager.reward_topic_if_threshold).
    """

    __tablename__ = "topic_votes"
    __table_args__ = (
        UniqueConstraint("topic_id", "user_id", name="uq_topic_vote"),
        Index("ix_topic_votes_topic_id", "topic_id"),
        Index("ix_topic_votes_user_id", "user_id"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    topic_id: Mapped[int] = mapped_column(
        ForeignKey("topics.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    topic: Mapped["Topic"] = relationship("Topic", back_populates="votes")
    user: Mapped["User"] = relationship("User")
