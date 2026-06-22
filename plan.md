# Time Tracking Module Implementation Plan

## Goal

Implement a new time-tracking module that lets employees record the project, stage/task, time spent, and notes for each work entry. The system must automatically associate each entry with the authenticated employee, company, and work date, then expose historical and aggregated reports for project productivity, labor cost, estimation, and profitability analysis.

The implementation should follow the current project structure: one folder per domain module, with separate model, schema, service, route, template, and static files.

## Proposed Module Structure

Create a new module folder:

```text
time_tracking/
├── time_tracking_model.py
├── time_tracking_schema.py
├── time_tracking_services.py
└── time_tracking_route.py
```

Create frontend files:

```text
frontend/templates/time_tracking/
├── dashboard.html
├── add.html
└── reports.html

frontend/static/time_tracking/
└── time_tracking.css
```

Register the router in:

```text
core/main.py
```

Add relationships in:

```text
users/users_model.py
projects/projects_model.py
```

Add enums in:

```text
core/enum/enum.py
```

Add an Alembic migration in:

```text
alembic/versions/
```

## Database Design

### Main Table: TimeEntry

Create `TimeEntry` in `time_tracking/time_tracking_model.py`.

Recommended fields:

```python
class TimeEntry(base):
    __tablename__ = "time_entries"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    employee_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    employee = relationship("User", back_populates="time_entries")

    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False, index=True)
    company = relationship("Company", back_populates="company_time_entries")

    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False, index=True)
    project = relationship("Projects", back_populates="time_entries")

    stage = Column(SQLEnum(ProjectStageEnum), nullable=False, index=True)
    task = Column(String, nullable=True, index=True)
    description = Column(String, nullable=True)

    hours = Column(DECIMAL, nullable=False, index=True)
    work_date = Column(Date, default=date.today, nullable=False, index=True)
    created_at = Column(DateTime, default=lambda: datetime.now(ZoneInfo("America/Sao_Paulo")), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(ZoneInfo("America/Sao_Paulo")), nullable=False)
```

Use `DECIMAL` for `hours`, following the financial models, because hours are business numbers that may be used for cost calculations.

### Relationships

In `users/users_model.py`, add:

```python
time_entries = relationship("TimeEntry", back_populates="employee")
```

In `Company`, add:

```python
company_time_entries = relationship("TimeEntry", back_populates="company")
```

In `projects/projects_model.py`, add:

```python
time_entries = relationship("TimeEntry", back_populates="project", cascade="all, delete-orphan")
```

### Project Stage Enum

The project model already uses `StatusEnum` for project status. For time tracking, the stage should represent where the work happened, not necessarily the current project status. Add a dedicated enum in `core/enum/enum.py`.

Recommended:

```python
class ProjectStageEnum(str, Enum):
    planning = "Planejamento"
    cutting = "Corte"
    pre_assembly = "Pré-montagem"
    lamination = "Laminação"
    truck_loading = "Carregamento"
    installation = "Instalação"
    finishing = "Acabamento"
    correction = "Correção"
    other = "Outro"
```

This avoids changing project status every time an employee logs time.

## Schemas

Create `time_tracking/time_tracking_schema.py`.

Recommended schemas:

```python
class TimeEntryCreate(BaseModel):
    project_id: int
    stage: ProjectStageEnum
    task: Optional[str] = None
    description: Optional[str] = None
    hours: Decimal
    work_date: Optional[DATE] = None

    class Config:
        from_attributes = True


class TimeEntryUpdate(BaseModel):
    project_id: Optional[int] = None
    stage: Optional[ProjectStageEnum] = None
    task: Optional[str] = None
    description: Optional[str] = None
    hours: Optional[Decimal] = None
    work_date: Optional[DATE] = None

    class Config:
        from_attributes = True
```

Validation rules should live in services, matching the current codebase style.

## Services

Create `time_tracking/time_tracking_services.py`.

Core service functions:

```text
create_time_entry(user, session, data)
update_time_entry(user, session, entry_id, data)
delete_time_entry(user, session, entry_id)
show_time_entries(session, user)
get_time_entry_or_404(user, session, entry_id)
time_entries_to_dict(entries)
get_time_report(user, session, filters)
```

### create_time_entry

Responsibilities:

- Validate that the selected project exists.
- Validate that the project belongs to `user.company_id`.
- Automatically set:
  - `employee_id=user.id`
  - `company_id=user.company_id`
  - `work_date=date.today()` if not provided
- Validate that `hours > 0`.
- Optionally cap a single entry, for example `hours <= 24`.
- Commit and refresh the new entry.

### show_time_entries

Return a company-scoped query:

```python
session.query(TimeEntry).filter(TimeEntry.company_id == user.company_id)
```

Use `joinedload` for:

```text
TimeEntry.employee
TimeEntry.project
```

This follows the style used in `projects_services.show_projects`.

### get_time_report

Support filters:

```text
start_date
end_date
project_id
employee_id
stage
```

Return aggregated data:

```text
total_hours
hours_by_project
hours_by_stage
hours_by_employee
hours_by_date
hours_by_project_and_stage
```

Use SQLAlchemy `func.sum(TimeEntry.hours)` and `group_by`.

## Routes

Create `time_tracking/time_tracking_route.py`.

Router:

```python
time_tracking_router = APIRouter(prefix="/time-tracking", tags=["time_tracking"])
```

Recommended endpoints:

```text
POST   /time-tracking/add
PUT    /time-tracking/{entry_id}
DELETE /time-tracking/{entry_id}
GET    /time-tracking/projects/search
GET    /time-tracking/users/search
GET    /time-tracking/report/data
```

Recommended views:

```text
GET /time-tracking/dashboard
GET /time-tracking/add
GET /time-tracking/reports
```

Use the same dependencies as existing modules:

```python
user: User = Depends(verify_token)
session: Session = Depends(CreateSession)
```

Use `@limiter.limit(...)` on mutating routes, consistent with `projects_route.py` and `financery_route.py`.

### Permissions

Suggested permissions:

- Any verified company employee can create their own time entries.
- Employees can edit/delete only their own entries.
- `admin` and `owner` can view company-wide entries and reports.
- `admin` and `owner` can edit/delete entries within their company if business rules require it.

Keep all queries scoped by `company_id` to avoid cross-company data leaks.

## Frontend Views

### Dashboard

`frontend/templates/time_tracking/dashboard.html`

Purpose:

- List recent time entries.
- Show project, employee, stage, task, hours, and date.
- Provide filters by project, employee, stage, and date range.
- Link to add entry and reports.

### Add Entry

`frontend/templates/time_tracking/add.html`

Fields:

```text
project autocomplete
stage select
task text input
hours numeric input
work_date date input
description textarea
```

The employee should not be selectable. It must come from the logged-in user.

### Reports

`frontend/templates/time_tracking/reports.html`

Show aggregated sections:

```text
total hours
hours by project
hours by project stage
hours by employee
hours over time
project-stage breakdown
```

Use JSON endpoints for chart data if needed, following the existing `financery` dashboard approach.

## Integration With Existing Modules

### core/main.py

Import and register:

```python
from time_tracking.time_tracking_route import time_tracking_router

app.include_router(time_tracking_router)
```

### Projects

Project detail pages should eventually show a time summary:

```text
total hours logged
hours by stage
employees who worked on the project
latest time entries
```

This can be added after the core module is working.

### Financery

To compare labor invested against the amount charged to the client, the system needs a reliable link between project revenue and the project.

Current `Sells` records do not appear to have `project_id`. Add one of these:

Preferred:

```python
project_id = Column(Integer, ForeignKey("projects.id"), nullable=True, index=True)
project = relationship("Projects")
```

Alternative:

Add a charged amount directly to `Projects`, but linking `Sells` is cleaner because revenue already belongs in `financery`.

Once linked, reports can calculate:

```text
project charged amount
project total logged hours
estimated labor cost
gross labor profitability
```

If employee hourly rates are needed later, add a separate `employee_cost_rate` field or a dedicated rate history table. Do not add it to the first version unless the client confirms cost rules.

## Reporting Queries

### Total Hours by Project

Group by:

```text
TimeEntry.project_id
Projects.name
```

Result:

```text
project name
total hours
```

### Total Hours by Stage

Group by:

```text
TimeEntry.stage
```

Result:

```text
stage
total hours
```

### Total Hours by Employee

Group by:

```text
TimeEntry.employee_id
User.fullname
```

Result:

```text
employee name
total hours
```

### Total Hours by Date

Group by:

```text
TimeEntry.work_date
```

Result:

```text
date
total hours
```

### Project Profitability Support

Group by project and join with revenue when `Sells.project_id` exists:

```text
project
charged amount
logged hours
labor cost estimate
remaining margin
```

## Migration Plan

1. Add `ProjectStageEnum` to `core/enum/enum.py`.
2. Add `time_tracking/time_tracking_model.py`.
3. Add relationships in `User`, `Company`, and `Projects`.
4. Generate migration:

```bash
alembic revision --autogenerate -m "add time tracking"
```

5. Review migration manually.
6. Apply:

```bash
alembic upgrade head
```

If adding `Sells.project_id`, include it in a separate migration or the same migration if the client wants profitability reporting in the first release.

## Implementation Order

1. Add model and relationships.
2. Add schema.
3. Add service functions.
4. Add routes and register router in `core/main.py`.
5. Add basic templates and CSS.
6. Add search endpoints for projects and users.
7. Add reporting service queries.
8. Add reports page and JSON data route.
9. Add project detail time summary.
10. Add optional `Sells.project_id` integration for profitability.
11. Create and apply Alembic migration.
12. Manually test create, list, edit, delete, and reports.

## Manual Test Checklist

Test as a normal employee:

```text
can create own entry
employee is assigned automatically
company is assigned automatically
date defaults to today
cannot log time to another company's project
can edit own entry
can delete own entry
```

Test as owner/admin:

```text
can see company-wide dashboard
can filter by employee
can filter by project
can filter by stage
can filter by date range
reports show correct sums
```

Test security:

```text
unauthenticated user is redirected/blocked
cross-company project IDs are rejected
cross-company entry IDs are rejected
report data is company-scoped
```

## First Version Scope

Include in v1:

```text
manual time entry
project selection
stage selection
task/description
hours
automatic employee/company/date association
dashboard
basic aggregated reports
company-scoped permissions
```

Defer unless explicitly required:

```text
timer start/stop
employee hourly rate history
approval workflow
timesheet locking
export to PDF/Excel
payroll integration
advanced profitability formulas
```

