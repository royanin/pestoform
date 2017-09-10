"""empty message

Revision ID: 49b14e466cb2
Revises: 
Create Date: 2017-09-10 13:30:06.516037

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '49b14e466cb2'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('demo',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('email', sa.String(length=100), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_demo_email'), 'demo', ['email'], unique=True)
    op.create_table('reguser',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('social_nw', sa.String(length=64), nullable=True),
    sa.Column('nickname', sa.String(length=64), nullable=True),
    sa.Column('email', sa.String(length=100), nullable=True),
    sa.Column('password', sa.String(length=255), nullable=True),
    sa.Column('active', sa.Boolean(), nullable=True),
    sa.Column('last_seen', sa.DateTime(), nullable=True),
    sa.Column('affiliation', sa.String(length=100), nullable=True),
    sa.Column('confirmed_at', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_reguser_email'), 'reguser', ['email'], unique=True)
    op.create_index(op.f('ix_reguser_nickname'), 'reguser', ['nickname'], unique=True)
    op.create_table('role',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=80), nullable=True),
    sa.Column('description', sa.String(length=255), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name')
    )
    op.create_table('wantbeta',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('email', sa.String(length=100), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_wantbeta_email'), 'wantbeta', ['email'], unique=True)
    op.create_table('course',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('title', sa.String(length=100), nullable=True),
    sa.Column('type_course', sa.Integer(), nullable=True),
    sa.Column('level', sa.Integer(), nullable=True),
    sa.Column('sbj1', sa.String(length=100), nullable=True),
    sa.Column('sbj2', sa.String(length=100), nullable=True),
    sa.Column('sbj3', sa.String(length=100), nullable=True),
    sa.Column('timestamp', sa.DateTime(), nullable=True),
    sa.Column('live_stat', sa.Boolean(), nullable=True),
    sa.Column('reguser_id', sa.Integer(), nullable=False),
    sa.Column('note', sa.String(length=500), nullable=True),
    sa.ForeignKeyConstraint(['reguser_id'], ['reguser.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('roles_users',
    sa.Column('reguser_id', sa.Integer(), nullable=True),
    sa.Column('role_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['reguser_id'], ['reguser.id'], ),
    sa.ForeignKeyConstraint(['role_id'], ['role.id'], )
    )
    op.create_table('meeting',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('course_id', sa.Integer(), nullable=False),
    sa.Column('reguser_id', sa.Integer(), nullable=False),
    sa.Column('demo_email', sa.String(length=100), nullable=False),
    sa.Column('title', sa.String(length=100), nullable=True),
    sa.Column('type_meeting', sa.Integer(), nullable=True),
    sa.Column('close_stat', sa.Integer(), nullable=True),
    sa.Column('close_opt', sa.Integer(), nullable=True),
    sa.Column('timestamp', sa.DateTime(), nullable=True),
    sa.Column('url_string', sa.String(length=80), nullable=True),
    sa.Column('prompt', sa.String(length=300), nullable=True),
    sa.Column('live_till', sa.DateTime(), nullable=True),
    sa.Column('live_till_hours', sa.Integer(), nullable=True),
    sa.Column('note', sa.String(length=500), nullable=True),
    sa.Column('blank_response', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['course_id'], ['course.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['demo_email'], ['demo.email'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['reguser_id'], ['reguser.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('muddy',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('body', sa.String(length=700), nullable=True),
    sa.Column('like_count', sa.Integer(), nullable=True),
    sa.Column('timestamp', sa.DateTime(), nullable=True),
    sa.Column('meeting_id', sa.Integer(), nullable=False),
    sa.Column('reguser_id', sa.Integer(), nullable=False),
    sa.Column('demo_email', sa.String(length=100), nullable=False),
    sa.ForeignKeyConstraint(['demo_email'], ['demo.email'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['meeting_id'], ['meeting.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['reguser_id'], ['reguser.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('muddy')
    op.drop_table('meeting')
    op.drop_table('roles_users')
    op.drop_table('course')
    op.drop_index(op.f('ix_wantbeta_email'), table_name='wantbeta')
    op.drop_table('wantbeta')
    op.drop_table('role')
    op.drop_index(op.f('ix_reguser_nickname'), table_name='reguser')
    op.drop_index(op.f('ix_reguser_email'), table_name='reguser')
    op.drop_table('reguser')
    op.drop_index(op.f('ix_demo_email'), table_name='demo')
    op.drop_table('demo')
    # ### end Alembic commands ###
