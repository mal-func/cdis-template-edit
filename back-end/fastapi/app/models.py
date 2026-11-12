from datetime import datetime
from sqlalchemy import DateTime, Float, ForeignKey, Index, Integer, JSON, String, Table, Column, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base
user_roles = Table("user_roles", Base.metadata,
    Column("userId", ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
    Column("roleId", ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True),
    Column("assignedAt", DateTime, nullable=False, server_default=func.now()))
Index("ix_user_roles_roleId", user_roles.c.roleId)
role_permissions = Table("role_permissions", Base.metadata,
    Column("roleId", ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True),
    Column("permissionId", ForeignKey("permissions.id", ondelete="CASCADE"), primary_key=True))
Index("ix_role_permissions_permissionId", role_permissions.c.permissionId)
class User(Base):
    __tablename__ = "users"
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(255))
    password_hash: Mapped[str] = mapped_column("passwordHash", String(255))
    failed_login_attempts: Mapped[int] = mapped_column("failedLoginAttempts", Integer, default=0)
    locked_until: Mapped[datetime | None] = mapped_column("lockedUntil", DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column("createdAt", DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column("updatedAt", DateTime, server_default=func.now(), onupdate=func.now())
    deleted_at: Mapped[datetime | None] = mapped_column("deletedAt", DateTime, nullable=True, index=True)
    roles: Mapped[list["Role"]] = relationship(secondary=user_roles, lazy="selectin")
    refresh_tokens: Mapped[list["RefreshToken"]] = relationship(back_populates="user", cascade="all, delete-orphan")
class Role(Base):
    __tablename__ = "roles"
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True)
    description: Mapped[str | None] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column("createdAt", DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column("updatedAt", DateTime, server_default=func.now(), onupdate=func.now())
    deleted_at: Mapped[datetime | None] = mapped_column("deletedAt", DateTime, nullable=True)
    permissions: Mapped[list["Permission"]] = relationship(secondary=role_permissions, lazy="selectin")
class Permission(Base):
    __tablename__ = "permissions"
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    key: Mapped[str] = mapped_column(String(150), unique=True)
    description: Mapped[str | None] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column("createdAt", DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column("updatedAt", DateTime, server_default=func.now(), onupdate=func.now())
class RefreshToken(Base):
    __tablename__ = "refresh_tokens"
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    user_id: Mapped[str] = mapped_column("userId", ForeignKey("users.id", ondelete="CASCADE"), index=True)
    token_hash: Mapped[str] = mapped_column("tokenHash", String(255), unique=True)
    expires_at: Mapped[datetime] = mapped_column("expiresAt", DateTime)
    revoked_at: Mapped[datetime | None] = mapped_column("revokedAt", DateTime)
    replaced_by_token_id: Mapped[str | None] = mapped_column("replacedByTokenId", ForeignKey("refresh_tokens.id", ondelete="SET NULL"), unique=True)
    created_by_ip: Mapped[str | None] = mapped_column("createdByIp", String(64))
    user_agent: Mapped[str | None] = mapped_column("userAgent", String(255))
    created_at: Mapped[datetime] = mapped_column("createdAt", DateTime, server_default=func.now())
    user: Mapped[User] = relationship(back_populates="refresh_tokens")
class DemoStateMetric(Base):
    __tablename__ = "demo_state_metrics"
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    state_code: Mapped[str] = mapped_column("stateCode", String(10), unique=True)
    state_name: Mapped[str] = mapped_column("stateName", String(100))
    project_count: Mapped[int] = mapped_column("projectCount", Integer)
    activity_intensity: Mapped[int] = mapped_column("activityIntensity", Integer)
    created_at: Mapped[datetime] = mapped_column("createdAt", DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column("updatedAt", DateTime, server_default=func.now(), onupdate=func.now())
class DemoChartDataset(Base):
    __tablename__ = "demo_chart_datasets"
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    slug: Mapped[str] = mapped_column(String(150), unique=True)
    title: Mapped[str] = mapped_column(String(150))
    chart_type: Mapped[str] = mapped_column("chartType", String(30))
    description: Mapped[str | None] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column("createdAt", DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column("updatedAt", DateTime, server_default=func.now(), onupdate=func.now())
    points: Mapped[list["DemoChartPoint"]] = relationship(order_by="DemoChartPoint.sort_order", cascade="all, delete-orphan")
class DemoChartPoint(Base):
    __tablename__ = "demo_chart_points"
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    dataset_id: Mapped[str] = mapped_column("datasetId", ForeignKey("demo_chart_datasets.id", ondelete="CASCADE"), index=True)
    label: Mapped[str] = mapped_column(String(100))
    series: Mapped[str | None] = mapped_column(String(100))
    value: Mapped[float] = mapped_column(Float)
    sort_order: Mapped[int] = mapped_column("sortOrder", Integer, default=0)
class DemoTableDataset(Base):
    __tablename__ = "demo_table_datasets"
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    slug: Mapped[str] = mapped_column(String(150), unique=True)
    title: Mapped[str] = mapped_column(String(150))
    description: Mapped[str | None] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column("createdAt", DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column("updatedAt", DateTime, server_default=func.now(), onupdate=func.now())
    rows: Mapped[list["DemoTableRow"]] = relationship(order_by="DemoTableRow.sort_order", cascade="all, delete-orphan")
class DemoTableRow(Base):
    __tablename__ = "demo_table_rows"
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    dataset_id: Mapped[str] = mapped_column("datasetId", ForeignKey("demo_table_datasets.id", ondelete="CASCADE"), index=True)
    data: Mapped[dict] = mapped_column(JSON)
    sort_order: Mapped[int] = mapped_column("sortOrder", Integer, default=0)
