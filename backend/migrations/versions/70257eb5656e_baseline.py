"""baseline (no-op)"""

from alembic import op
import sqlalchemy as sa

# 既存のIDはそのままにしてください
revision = "70257eb5656e"
down_revision = "f7a4f609f084"
branch_labels = None
depends_on = None

def upgrade() -> None:
    # 何もしない（DBは現状のまま採用）
    pass

def downgrade() -> None:
    # 何もしない
    pass
