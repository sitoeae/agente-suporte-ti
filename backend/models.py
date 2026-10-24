from sqlalchemy import Column, String, DateTime, Text, Date
from database import Base
import uuid
from datetime import datetime, timezone

class Profile(Base):
    __tablename__ = "profiles"
    id = Column(String, primary_key=True)
    email = Column(String)
    role = Column(String, default="user")

class Ticket(Base):
    __tablename__ = "tickets"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String)
    title = Column(String, nullable=False)
    description = Column(Text)
    category = Column(String)
    priority = Column(String, default="media")
    status = Column(String, default="aberto")
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

class Device(Base):
    __tablename__ = "devices"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    asset_tag = Column(String, unique=True, nullable=False)
    type = Column(String, nullable=False)
    manufacturer = Column(String)
    model = Column(String)
    serial_number = Column(String)
    specs = Column(Text)
    
    assigned_to = Column(String)
    location = Column(String)
    status = Column(String, default="Em uso")
    
    # Novos campos de rede e servidor
    network_name = Column(String)
    ip_address = Column(String)
    mac_address = Column(String)
    ip_type = Column(String, default="Dinâmico")
    server_role = Column(String)
    os = Column(String)
    
    purchase_date = Column(Date)
    supplier = Column(String)
    warranty_end = Column(Date)
    software_licenses = Column(Text)
    
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))