# Time Tracking Subplan: Start Time, End Time, and Total Minutes

## Feasibility Check

The client's proposed approach is possible with the current codebase.

The existing project already has the required foundations:

- Authenticated users are resolved through `verify_token`.
- Users already belong to a company through `user.company_id`.
- Projects already belong to a company through `Projects.company_id`.
- The app already follows a modular structure with separate model, schema, service, route, template, and static files.
- SQLAlchemy models already use `Date`, `DateTime`, `Integer`, `ForeignKey`, relationships, and company-scoped queries.

So the time-tracking module can safely create each work log by automatically using:

- `employee_id` from the authenticated user
- `company_id` from the authenticated user
- `work_date` from the submitted date or `date.today()`
- `project_id` from the selected project
- `stage` or task from the selected project stage/task

The user should only input the business data:

- project
- stage/task
- start time
- end time
- optional description

The system calculates `total_minutes`.

## Is This a Standard Time-Tracking Approach?

Yes. This is a normal and practical software-development pattern for employee time tracking.

Most time-tracking systems use one of these models:

1. Manual duration entry: user directly enters `1.5 hours` or `90 minutes`.
2. Start/end entry: user enters `08:00` and `09:30`, and the system calculates `90 minutes`.
3. Timer mode: user clicks start and stop, and the system records timestamps automatically.

The client's proposal is option 2. It is a good first version because it is simple for employees and better for reporting than storing only a decimal hour value.

Saving `total_minutes` as an integer is also standard. It avoids decimal rounding issues and makes reports easier:

```text
total_hours = total_minutes / 60
remaining_minutes = total_minutes % 60
```

The formula provided by the client is correct for converting a duration into minutes:

```text
total_minutes = (hours * 60) + minutes
```

For this module, the system should calculate the duration from start and end time first, then save the result in minutes.

## Recommended Database Design

The client mentioned only three database fields:

```text
start_time
end_time
total_time
```

Those three fields are not enough by themselves because the system also needs to know who worked, which company owns the record, which project was worked on, which stage/task was performed, and which date the work happened.

Recommended model:

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

    work_date = Column(Date, default=date.today, nullable=False, index=True)
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)
    total_minutes = Column(Integer, nullable=False, index=True)

    created_at = Column(DateTime, default=lambda: datetime.now(ZoneInfo("America/Sao_Paulo")), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(ZoneInfo("America/Sao_Paulo")), nullable=False)
```

This keeps the client's simple time calculation while preserving the data needed for company reports.

## Why Store `total_minutes`?

Even though `total_minutes` can be recalculated from `start_time` and `end_time`, storing it is useful here.

Benefits:

- Reports can sum one integer field directly.
- Queries are simpler and faster.
- The value represents the duration approved at the moment of saving.
- The app can display hours/minutes without recalculating everywhere.

The service must still treat `total_minutes` as a calculated field. The frontend should not decide the final value.

## Time Calculation Rule

Use the submitted `work_date`, `start_time`, and `end_time`.

Basic rule:

```python
start_dt = datetime.combine(work_date, start_time)
end_dt = datetime.combine(work_date, end_time)
total_minutes = int((end_dt - start_dt).total_seconds() // 60)
```

Validation:

```text
end_time must be greater than start_time
total_minutes must be greater than 0
total_minutes should not exceed a reasonable daily limit
```

Recommended first-version limit:

```text
total_minutes <= 1440
```

For stricter business validation:

```text
total_minutes <= 720
```

That means 12 hours maximum per entry.

## Overnight Work

For the first version, reject overnight entries.

Example rejected case:

```text
start_time = 22:00
end_time = 02:00
```

Reason:

The current requirement is about daily employee work records, and the app does not currently have shift management. Supporting overnight work would require either:

- `start_datetime` and `end_datetime`, or
- `work_date`, `start_time`, `end_time`, and `ends_next_day`

If the client needs night shifts later, add that as a second version.

## Schema Plan

Create `time_tracking/time_tracking_schema.py`.

Recommended schema:

```python
class TimeEntryCreate(BaseModel):
    project_id: int
    stage: ProjectStageEnum
    task: Optional[str] = None
    description: Optional[str] = None
    work_date: Optional[DATE] = None
    start_time: TIME
    end_time: TIME

    class Config:
        from_attributes = True
```

For edits:

```python
class TimeEntryUpdate(BaseModel):
    project_id: Optional[int] = None
    stage: Optional[ProjectStageEnum] = None
    task: Optional[str] = None
    description: Optional[str] = None
    work_date: Optional[DATE] = None
    start_time: Optional[TIME] = None
    end_time: Optional[TIME] = None

    class Config:
        from_attributes = True
```

Do not accept `total_minutes` from the client request. It must be calculated by the backend.

## Service Plan

Create `time_tracking/time_tracking_services.py`.

Main functions:

```text
calculate_total_minutes(work_date, start_time, end_time)
create_time_entry(user, session, data)
update_time_entry(user, session, entry_id, data)
delete_time_entry(user, session, entry_id)
show_time_entries(session, user)
get_time_report(user, session, filters)
```

### calculate_total_minutes

Responsibilities:

- Combine `work_date` with `start_time`.
- Combine `work_date` with `end_time`.
- Subtract start from end.
- Convert seconds to minutes.
- Reject zero or negative durations.
- Return integer minutes.

### create_time_entry

Responsibilities:

- Get the project by `data.project_id`.
- Confirm `project.company_id == user.company_id`.
- Set `employee_id = user.id`.
- Set `company_id = user.company_id`.
- Set `work_date = data.work_date or date.today()`.
- Calculate `total_minutes`.
- Save the entry.

### update_time_entry

Responsibilities:

- Find the entry by `entry_id`.
- Confirm `entry.company_id == user.company_id`.
- Allow normal employees to update only their own entries.
- Allow `admin` or `owner` to update company entries.
- If start, end, or date changes, recalculate `total_minutes`.

### delete_time_entry

Responsibilities:

- Find the entry by `entry_id`.
- Confirm `entry.company_id == user.company_id`.
- Apply the same ownership/admin permission rules as update.
- Delete and commit.

## Route Plan

Create `time_tracking/time_tracking_route.py`.

Router:

```python
time_tracking_router = APIRouter(prefix="/time-tracking", tags=["time_tracking"])
```

Endpoints:

```text
POST   /time-tracking/add
PUT    /time-tracking/{entry_id}
DELETE /time-tracking/{entry_id}
GET    /time-tracking/report/data
GET    /time-tracking/projects/search
```

Views:

```text
GET /time-tracking/dashboard
GET /time-tracking/add
GET /time-tracking/reports
```

All routes must use:

```python
user: User = Depends(verify_token)
session: Session = Depends(CreateSession)
```

Mutating routes should use `@limiter.limit(...)`, following the style in `projects_route.py` and `financery_route.py`.

## Reporting Plan

Reports should aggregate `total_minutes`, not `start_time` or `end_time`.

### Project Total

Answer:

```text
How much time was invested in this project?
```

Query:

```text
group by project_id
sum(total_minutes)
```

### Stage Total

Answer:

```text
Which stage consumes the most time?
```

Query:

```text
group by stage
sum(total_minutes)
```

Example result:

```text
Cutting: 90 minutes
Assembly: 70 minutes
Installation: 30 minutes
```

### Employee Total

Answer:

```text
How many hours did each employee work?
```

Query:

```text
group by employee_id
sum(total_minutes)
```

### Project and Stage Breakdown

Answer:

```text
How much time did each project stage take inside each project?
```

Query:

```text
group by project_id, stage
sum(total_minutes)
```

### Date Range Filter

Every report should support:

```text
start_date
end_date
project_id
employee_id
stage
```

## Frontend Form Plan

The add/edit form should show:

```text
Project
Stage
Task
Work date
Start time
End time
Description
```

Use HTML time inputs:

```html
<input type="time" name="start_time" required>
<input type="time" name="end_time" required>
```

The UI may preview the calculated time for convenience, but the backend must calculate and save the official `total_minutes`.

## Implementation Order

1. Add `ProjectStageEnum` in `core/enum/enum.py`.
2. Create `time_tracking/time_tracking_model.py`.
3. Add relationships in `User`, `Company`, and `Projects`.
4. Create `time_tracking/time_tracking_schema.py`.
5. Create calculation and CRUD services.
6. Create routes and views.
7. Register the router in `core/main.py`.
8. Create templates and CSS.
9. Add report aggregation queries using `sum(total_minutes)`.
10. Generate and review Alembic migration.
11. Manually test same-company security and duration calculations.

## Final Recommendation

The client's start-time/end-time proposal is correct and should replace the previous direct `hours` input approach.

The final model should not save only `hours` as a decimal. It should save:

```text
start_time
end_time
total_minutes
```

alongside the required relational fields:

```text
employee_id
company_id
project_id
stage
work_date
```

This design is simple for employees, standard for time-tracking software, and better for reports because all aggregation can use `total_minutes`.

