import logging
from typing import List, Optional

from sqlalchemy.orm import Session

from app.auth.auth import AuthService
from app.db.models import Company, Lead, User
from app.schemas.schemas import CompanyCreate, CompanyUpdate, LeadCreate, LeadUpdate, UserCreate

user_logger = logging.getLogger("user_logger")
user_logger.setLevel(logging.INFO)
user_logger.addHandler(logging.StreamHandler())

company_logger = logging.getLogger("company_logger")
company_logger.setLevel(logging.INFO)
company_logger.addHandler(logging.StreamHandler())

lead_logger = logging.getLogger("lead_logger")
lead_logger.setLevel(logging.INFO)
lead_logger.addHandler(logging.StreamHandler())


class UserCRUD:
    @staticmethod
    def create_user(db: Session, user: UserCreate) -> User:
        hashed_password = AuthService.get_password_hash(user.password)
        db_user = User(username=user.username, email=user.email, hashed_password=hashed_password)
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        user_logger.info(f"User created: {db_user.id}")
        return db_user

    @staticmethod
    def get_user(db: Session, user_id: int) -> Optional[User]:
        user = db.query(User).filter(User.id == user_id).first()
        if user:
            user_logger.info(f"User retrieved: {user.id}")
        else:
            user_logger.info(f"User not found: {user_id}")
        return user

    @staticmethod
    def get_user_by_username(db: Session, username: str) -> Optional[User]:
        user = db.query(User).filter(User.username == username).first()
        if user:
            user_logger.info(f"User retrieved: {user.id}")
        else:
            user_logger.info(f"User not found: {username}")
        return user

    @staticmethod
    def get_user_by_email(db: Session, email: str) -> Optional[User]:
        user = db.query(User).filter(User.email == email).first()
        if user:
            user_logger.info(f"User retrieved: {user.id}")
        else:
            user_logger.info(f"User not found: {email}")
        return user


class CompanyCRUD:
    @staticmethod
    def create_company(db: Session, company: CompanyCreate, owner_id: int) -> Company:
        db_company = Company(name=company.name, sector=company.sector, owner_id=owner_id)
        db.add(db_company)
        db.commit()
        db.refresh(db_company)
        company_logger.info(f"Company created: {db_company.id}")
        return db_company

    @staticmethod
    def get_company(db: Session, company_id: int, owner_id: int) -> Optional[Company]:
        company = (
            db.query(Company).filter(Company.id == company_id, Company.owner_id == owner_id).first()
        )
        if company:
            company_logger.info(f"Company retrieved: {company.id}")
        else:
            company_logger.info(f"Company not found: {company_id}")
        return company

    @staticmethod
    def get_companies(db: Session, owner_id: int, skip: int = 0, limit: int = 100) -> List[Company]:
        companies = (
            db.query(Company).filter(Company.owner_id == owner_id).offset(skip).limit(limit).all()
        )
        company_logger.info(f"Companies retrieved: {len(companies)}")
        return companies

    @staticmethod
    def update_company(
        db: Session, company_id: int, company_update: CompanyUpdate, owner_id: int
    ) -> Optional[Company]:
        company = (
            db.query(Company).filter(Company.id == company_id, Company.owner_id == owner_id).first()
        )

        if not company:
            company_logger.info(f"Company not found: {company_id}")
            return None

        update_data = company_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(company, field, value)

        db.commit()
        db.refresh(company)
        company_logger.info(f"Company updated: {company.id}")
        return company

    @staticmethod
    def delete_company(db: Session, company_id: int, owner_id: int) -> bool:
        db_company = (
            db.query(Company).filter(Company.id == company_id, Company.owner_id == owner_id).first()
        )

        if not db_company:
            return False

        db.delete(db_company)
        db.commit()
        company_logger.info(f"Company deleted: {company_id}")
        return True


class LeadCRUD:
    @staticmethod
    def create_lead(db: Session, lead: LeadCreate, owner_id: int) -> Optional[Lead]:
        company = (
            db.query(Company)
            .filter(Company.id == lead.company_id, Company.owner_id == owner_id)
            .first()
        )

        if not company:
            lead_logger.info(f"Company not found: {lead.company_id}")
            return None

        lead = Lead(
            title=lead.title,
            description=lead.description,
            status=lead.status.value,
            company_id=lead.company_id,
            owner_id=owner_id,
        )
        db.add(lead)
        db.commit()
        db.refresh(lead)
        lead_logger.info(f"Lead created: {lead.id}")
        return lead

    @staticmethod
    def get_lead(db: Session, lead_id: int, owner_id: int) -> Optional[Lead]:
        lead = db.query(Lead).filter(Lead.id == lead_id, Lead.owner_id == owner_id).first()
        if lead:
            lead_logger.info(f"Lead retrieved: {lead.id}")
        else:
            lead_logger.info(f"Lead not found: {lead_id}")
        return lead

    @staticmethod
    def get_leads(
        db: Session,
        owner_id: int,
        status: Optional[str] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Lead]:
        query = db.query(Lead).filter(Lead.owner_id == owner_id)

        if status:
            query = query.filter(Lead.status == status)

        leads = query.offset(skip).limit(limit).all()
        lead_logger.info(f"Leads retrieved: {len(leads)}")
        return leads

    @staticmethod
    def update_lead(
        db: Session, lead_id: int, lead_update: LeadUpdate, owner_id: int
    ) -> Optional[Lead]:
        lead = db.query(Lead).filter(Lead.id == lead_id, Lead.owner_id == owner_id).first()

        if not lead:
            lead_logger.info(f"Lead not found: {lead_id}")
            return None

        update_data = lead_update.model_dump(exclude_unset=True)

        if "company_id" in update_data:
            company = (
                db.query(Company)
                .filter(
                    Company.id == update_data["company_id"],
                    Company.owner_id == owner_id,
                )
                .first()
            )
            if not company:
                lead_logger.info(f"Company not found: {update_data['company_id']}")
                return None

        if "status" in update_data and update_data["status"]:
            update_data["status"] = update_data["status"].value
            lead_logger.info(f"Status updated: {update_data['status']}")

        for field, value in update_data.items():
            setattr(lead, field, value)
            lead_logger.info(f"{field} updated: {value}")

        db.commit()
        db.refresh(lead)
        lead_logger.info(f"Lead updated: {lead.id}")
        return lead

    @staticmethod
    def delete_lead(db: Session, lead_id: int, owner_id: int) -> bool:
        db_lead = db.query(Lead).filter(Lead.id == lead_id, Lead.owner_id == owner_id).first()

        if not db_lead:
            lead_logger.info(f"Lead not found: {lead_id}")
            return False

        db.delete(db_lead)
        db.commit()
        lead_logger.info(f"Lead deleted: {lead_id}")
        return True
