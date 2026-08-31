from sqlalchemy import Column, DateTime, Integer, String, Text
from datetime import datetime

from database import Base


class Report(Base):
    __tablename__ = "reports"

    id = Column(Integer, primary_key=True, index=True)
    company_name = Column(String, nullable=False, index=True)

    overview = Column(Text, nullable=True)
    key_people = Column(Text, nullable=True)
    news = Column(Text, nullable=True)
    financials = Column(Text, nullable=True)
    risks = Column(Text, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)