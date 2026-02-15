"""Business logic for loyalty transactions."""
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Optional, List
from uuid import UUID

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status

from app.models.loyalty import Customer, LoyaltyAccount, LoyaltyLedger
from app.core.logging import logger


# Business Rules
EARN_RATE_PERCENT = Decimal("1.5")  # 1.5% earn rate
POINTS_PER_EURO = 10000  # 1 EUR = 10000 points
EXPIRATION_MONTHS = 12  # Points expire after 12 months


class LoyaltyService:
    """Service for loyalty transaction business logic."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_customer(self, customer_id: UUID) -> Customer:
        """Get customer by ID or raise 404."""
        result = await self.db.execute(
            select(Customer).where(Customer.customer_id == customer_id)
        )
        customer = result.scalar_one_or_none()
        
        if not customer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "error_code": "CUSTOMER_NOT_FOUND",
                    "error_message": f"Customer {customer_id} does not exist",
                }
            )
        
        return customer
    
    async def get_or_create_account(self, customer_id: UUID) -> LoyaltyAccount:
        """Get or create loyalty account for customer."""
        result = await self.db.execute(
            select(LoyaltyAccount).where(LoyaltyAccount.customer_id == customer_id)
        )
        account = result.scalar_one_or_none()
        
        if not account:
            # Create new account
            account = LoyaltyAccount(
                customer_id=customer_id,
                current_balance_points=0,
                current_balance_euros=Decimal("0.00"),
                total_earned_points=0,
                total_redeemed_points=0,
            )
            self.db.add(account)
            await self.db.flush()
            logger.info(f"Created new loyalty account for customer {customer_id}")
        
        return account
    
    def calculate_points_earned(self, order_amount: Decimal) -> tuple[int, Decimal]:
        """
        Calculate points earned from order amount.
        
        Returns: (points, euros)
        """
        euros_earned = order_amount * (EARN_RATE_PERCENT / Decimal("100"))
        euros_earned = euros_earned.quantize(Decimal("0.01"))  # Round to 2 decimals
        points_earned = int(euros_earned * POINTS_PER_EURO)
        
        return points_earned, euros_earned
    
    def euros_to_points(self, euros: Decimal) -> int:
        """Convert euros to points."""
        return int(euros * POINTS_PER_EURO)
    
    def points_to_euros(self, points: int) -> Decimal:
        """Convert points to euros."""
        return Decimal(points) / POINTS_PER_EURO
    
    async def get_current_balance(self, customer_id: UUID) -> tuple[int, Decimal]:
        """
        Get current balance from ledger.
        
        Returns: (points, euros)
        """
        result = await self.db.execute(
            select(func.coalesce(func.sum(LoyaltyLedger.points_delta), 0))
            .where(LoyaltyLedger.customer_id == customer_id)
        )
        total_points = result.scalar() or 0
        total_euros = self.points_to_euros(total_points)
        
        return int(total_points), total_euros
    
    async def get_latest_balance_after(self, customer_id: UUID) -> tuple[int, Decimal]:
        """
        Get balance from most recent ledger entry.
        
        Returns: (points, euros)
        """
        result = await self.db.execute(
            select(LoyaltyLedger)
            .where(LoyaltyLedger.customer_id == customer_id)
            .order_by(LoyaltyLedger.ledger_sequence.desc())
            .limit(1)
        )
        latest = result.scalar_one_or_none()
        
        if latest:
            return latest.balance_after, self.points_to_euros(latest.balance_after)
        else:
            return 0, Decimal("0.00")
    
    async def append_to_ledger(
        self,
        customer_id: UUID,
        account_id: UUID,
        transaction_type: str,
        points_delta: int,
        amount_euros: Decimal,
        order_id: Optional[str],
        order_amount: Optional[Decimal],
        source_type: str,
        source_reference: Optional[str],
        terminal_id: Optional[str],
        channel: str,
        description: str,
        idempotency_key: str,
        earn_rate: Optional[Decimal] = None,
        reverses_ledger_id: Optional[UUID] = None,
    ) -> LoyaltyLedger:
        """
        Append transaction to immutable ledger.
        """
        # Get current balance
        current_points, current_euros = await self.get_latest_balance_after(customer_id)
        
        # Calculate new balance
        new_balance_points = current_points + points_delta
        
        # Validate non-negative balance
        if new_balance_points < 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "error_code": "INSUFFICIENT_BALANCE",
                    "error_message": "Customer has insufficient balance",
                    "details": {
                        "requested_points": abs(points_delta),
                        "requested_euros": float(abs(amount_euros)),
                        "available_points": current_points,
                        "available_euros": float(current_euros),
                    }
                }
            )
        
        # Calculate expiration date for earned points
        expiration_date = None
        if transaction_type == "earn":
            expiration_date = (datetime.utcnow() + timedelta(days=EXPIRATION_MONTHS * 30)).date()
        
        # Create ledger entry
        ledger_entry = LoyaltyLedger(
            customer_id=customer_id,
            account_id=account_id,
            transaction_type=transaction_type,
            transaction_date=datetime.utcnow(),
            points_delta=points_delta,
            balance_after=new_balance_points,
            amount_euros=amount_euros,
            source_type=source_type,
            source_reference=source_reference,
            order_id=order_id,
            order_amount_eur=order_amount,
            earn_rate_percent=earn_rate,
            description=description,
            expiration_date=expiration_date,
            idempotency_key=idempotency_key,
            reverses_ledger_id=reverses_ledger_id,
            terminal_id=terminal_id,
            channel=channel,
            created_by="api_v1",
        )
        
        self.db.add(ledger_entry)
        await self.db.flush()
        
        # Update cached balance in account
        account = await self.get_or_create_account(customer_id)
        account.current_balance_points = new_balance_points
        account.current_balance_euros = self.points_to_euros(new_balance_points)
        account.last_transaction_date = datetime.utcnow()
        
        if transaction_type == "earn":
            account.total_earned_points += points_delta
        elif transaction_type == "redeem":
            account.total_redeemed_points += abs(points_delta)
        
        await self.db.flush()
        
        logger.info(
            f"Ledger entry created: {transaction_type} {points_delta} points for customer {customer_id}, "
            f"new balance: {new_balance_points}"
        )
        
        return ledger_entry
    
    async def find_transactions_by_order_id(self, order_id: str) -> List[LoyaltyLedger]:
        """Find all transactions for a given order ID."""
        result = await self.db.execute(
            select(LoyaltyLedger)
            .where(LoyaltyLedger.order_id == order_id)
            .where(LoyaltyLedger.reversed_by_ledger_id.is_(None))  # Not already reversed
            .order_by(LoyaltyLedger.ledger_sequence)
        )
        return list(result.scalars().all())
    
    async def get_expiring_points(
        self, 
        customer_id: UUID, 
        days_ahead: int = 30
    ) -> Optional[tuple[int, Decimal, str]]:
        """
        Get points expiring within specified days.
        
        Returns: (points, euros, expiry_date) or None
        """
        cutoff_date = (datetime.utcnow() + timedelta(days=days_ahead)).date()
        
        result = await self.db.execute(
            select(
                func.sum(LoyaltyLedger.points_delta).label('total_points'),
                func.min(LoyaltyLedger.expiration_date).label('earliest_expiry')
            )
            .where(LoyaltyLedger.customer_id == customer_id)
            .where(LoyaltyLedger.transaction_type == "earn")
            .where(LoyaltyLedger.expiration_date <= cutoff_date)
            .where(LoyaltyLedger.expiration_date >= datetime.utcnow().date())
            .where(LoyaltyLedger.expired_by_ledger_id.is_(None))
        )
        row = result.one_or_none()
        
        if row and row.total_points and row.total_points > 0:
            points = int(row.total_points)
            euros = self.points_to_euros(points)
            expiry_date = row.earliest_expiry.isoformat()
            return points, euros, expiry_date
        
        return None
    
    async def get_transaction_count(self, customer_id: UUID) -> int:
        """Get total transaction count for customer."""
        result = await self.db.execute(
            select(func.count(LoyaltyLedger.ledger_id))
            .where(LoyaltyLedger.customer_id == customer_id)
        )
        return result.scalar() or 0
