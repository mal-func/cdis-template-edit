from app.database import Base
from app import models  # noqa: F401

def test_prisma_compatible_column_names_are_mapped():
    assert "passwordHash" in Base.metadata.tables["users"].c
    assert "failedLoginAttempts" in Base.metadata.tables["users"].c
    assert "createdAt" in Base.metadata.tables["users"].c
    assert "tokenHash" in Base.metadata.tables["refresh_tokens"].c
    assert "replacedByTokenId" in Base.metadata.tables["refresh_tokens"].c
    assert "stateCode" in Base.metadata.tables["demo_state_metrics"].c
    assert "chartType" in Base.metadata.tables["demo_chart_datasets"].c

def test_join_table_lookup_indexes_exist():
    user_role_indexes = {index.name for index in Base.metadata.tables["user_roles"].indexes}
    role_permission_indexes = {index.name for index in Base.metadata.tables["role_permissions"].indexes}
    assert "ix_user_roles_roleId" in user_role_indexes
    assert "ix_role_permissions_permissionId" in role_permission_indexes
