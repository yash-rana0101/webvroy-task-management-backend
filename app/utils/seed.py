"""Database seed utility for initial sample data."""

from datetime import datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.comment import Comment
from app.models.task import Task
from app.models.user import User


async def seed_database(session: AsyncSession) -> None:
    """Seed the database with sample users, tasks, and comments."""
    # Check if data already exists
    result = await session.scalars(select(User).limit(1))
    if result.first() is not None:
        return

    now = datetime.now(timezone.utc)

    # Create users
    users = [
        User(name="Alice Johnson", email="alice@example.com", role="admin"),
        User(name="Bob Smith", email="bob@example.com", role="manager"),
        User(name="Carol Williams", email="carol@example.com", role="member"),
        User(name="David Brown", email="david@example.com", role="member"),
        User(name="Eva Martinez", email="eva@example.com", role="member"),
    ]
    session.add_all(users)
    await session.flush()

    # Create tasks with varied data
    tasks_data = [
        ("Fix login page bug", "Users report intermittent login failures on mobile devices", "in_progress", "high", 1, -2),
        ("Update API documentation", "Add missing endpoint docs for v2 API", "pending", "medium", 2, 5),
        ("Design new dashboard", "Create wireframes and mockups for the analytics dashboard", "in_progress", "high", 3, 7),
        ("Implement search feature", "Add full-text search to the task list with filters", "pending", "urgent", 1, 3),
        ("Review pull requests", "Review and merge pending PRs from the team", "completed", "medium", 2, -1),
        ("Set up CI/CD pipeline", "Configure GitHub Actions for automated testing and deployment", "completed", "high", 4, -5),
        ("Write unit tests", "Increase test coverage to 80% for core modules", "in_progress", "medium", 3, 10),
        ("Fix payment gateway issue", "Payment processing fails for international cards", "blocked", "urgent", 1, 1),
        ("Optimize database queries", "Slow queries on the reports page need optimization", "pending", "high", 4, 8),
        ("Create onboarding flow", "Design and implement new user onboarding experience", "pending", "medium", 5, 14),
        ("Update dependencies", "Upgrade all npm packages to latest versions", "completed", "low", 3, -3),
        ("Mobile responsive fixes", "Fix layout issues on tablets and small screens", "in_progress", "medium", 5, 4),
        ("Add email notifications", "Send email alerts for task assignments and due dates", "pending", "low", None, 21),
        ("Security audit", "Conduct security review of authentication system", "blocked", "urgent", 2, 2),
        ("Refactor user module", "Clean up user management code and add proper validation", "pending", "medium", 4, 12),
        ("Create reporting module", "Build weekly and monthly task reports with charts", "pending", "high", None, 18),
        ("Fix notification system", "Push notifications not delivered on iOS devices", "in_progress", "high", 1, -1),
        ("Database backup script", "Automate daily database backups to cloud storage", "completed", "medium", 4, -7),
        ("API rate limiting", "Implement rate limiting for public API endpoints", "pending", "low", 2, 15),
        ("User feedback system", "Add in-app feedback widget for users to report issues", "pending", "medium", 5, 20),
    ]

    tasks = []
    for title, desc, status, priority, assignee_idx, due_offset in tasks_data:
        assigned_to = users[assignee_idx - 1].id if assignee_idx else None
        due_date = now + timedelta(days=due_offset)
        task = Task(
            title=title,
            description=desc,
            status=status,
            priority=priority,
            assigned_to=assigned_to,
            due_date=due_date,
        )
        tasks.append(task)

    session.add_all(tasks)
    await session.flush()

    # Create sample comments
    comments = [
        Comment(task_id=tasks[0].id, user_id=users[0].id, comment="I've identified the root cause. It's a session timeout issue on mobile browsers."),
        Comment(task_id=tasks[0].id, user_id=users[1].id, comment="Great find! Can you push a fix by end of day?"),
        Comment(task_id=tasks[2].id, user_id=users[2].id, comment="First draft of wireframes is ready for review."),
        Comment(task_id=tasks[3].id, user_id=users[0].id, comment="I'll start on this after the login bug is fixed."),
        Comment(task_id=tasks[7].id, user_id=users[1].id, comment="We're waiting on the payment provider to resolve their API issue."),
        Comment(task_id=tasks[7].id, user_id=users[0].id, comment="I've contacted their support team. Expected resolution: 48 hours."),
    ]
    session.add_all(comments)
    await session.flush()
    await session.commit()
