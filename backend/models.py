from sqlalchemy import Column, Integer, String
from database import Base


class WasteRecord(Base):

    __tablename__ = "waste_records"

    id = Column(Integer, primary_key=True, index=True)

    waste_name = Column(String)

    category = Column(String)

    bin_type = Column(String)

    location = Column(String)

    status = Column(String)

class ImageRecord(Base):

    __tablename__ = "image_records"

    id = Column(Integer, primary_key=True, index=True)

    filename = Column(String)

    file_path = Column(String)

    status = Column(String)

class SanitizationRecord(Base):

    __tablename__ = "sanitization_records"

    id = Column(Integer, primary_key=True, index=True)

    location = Column(String)

    sanitization_type = Column(String)

    status = Column(String)

    notes = Column(String)