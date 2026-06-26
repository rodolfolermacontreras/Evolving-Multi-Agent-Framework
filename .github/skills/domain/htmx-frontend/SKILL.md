---
name: htmx-frontend
description: "EXAMPLE (Day-to-Day Agent host project). Use when working with HTMX + Jinja2 + Alpine.js frontends in a host project that follows the Day-to-Day Agent template conventions. NOT a framework default -- treat as a reference implementation showing what a domain skill looks like."
argument-hint: "What HTMX template, component, or UI flow should I work on?"
license: MIT
metadata:
  author: emf-framework
  version: '1.0'
  status: example
  origin: day-to-day-agent
---

> **STATUS: EXAMPLE SKILL.** This skill was extracted from the Day-to-Day Agent host
> project and ships with the framework as a reference implementation, not as a
> framework default. It demonstrates the shape of a `domain/` skill (project-specific
> frontend conventions) but its contents -- HTMX, the `base.html` shell, the
> `pages/` template layout, the `--accent-*` CSS variables -- are specific to that
> host project.
>
> Host projects that adopt the framework should either delete this skill or replace
> it with one tuned to their own frontend stack (React, Svelte, Blazor, etc.). See
> `.github/skills/domain/README.md`.

# HTMX Frontend (example)

Day-to-Day Agent frontend patterns: HTMX + Jinja2 templates, base.html shell, UI macros, Alpine.js for client state, and CSS conventions.

## When to Use

Load this skill when:
- Creating new pages or UI components
- Adding HTMX interactions (modals, toasts, partials)
- Styling with main.css conventions
- Using Alpine.js for UI state

Do NOT load when:
- Backend API development (use fastapi-routes)
- Testing (use pytest-runner)

## Template Organization

```
templates/
├── base.html                   # Shell: nav, toast container, head_scripts block
├── pages/
│   ├── dashboard.html         # Main dashboard page
│   ├── board.html             # Project board
│   ├── ideas.html             # Ideas management
│   ├── reminders.html         # Reminders page
│   ├── accountability.html    # Accountability log
│   └── calendar.html          # Calendar view
├── components/
│   ├── ui_macros.html         # Reusable macros (card, button, badge, modal)
│   ├── task_row.html          # Partial: single task row
│   ├── project_card.html      # Partial: project card
│   └── reminder_item.html     # Partial: reminder item
└── emails/
    └── status_report.html      # Email-safe HTML (no external CSS)
```

## Base Template (base.html)

All pages extend base.html:

```jinja2
{% extends "base.html" %}

{% block title %}Calendar - Day-to-Day{% endblock %}

{% block head_scripts %}
<!-- Page-specific JS/CSS -->
<script src="https://cdn.jsdelivr.net/npm/fullcalendar@6/index.global.min.js"></script>
{% endblock %}

{% block content %}
<div class="container">
    <h1>Calendar</h1>
    <!-- Page content -->
</div>
{% endblock %}
```

**Base shell provides**:
- Navigation bar
- Toast notification container
- HTMX, Alpine.js, and Tailwind CDN links
- Dark theme toggle
- WebSocket connection (for live updates)

## UI Macros (components/ui_macros.html)

### Import Macros

```jinja2
{% from 'components/ui_macros.html' import card, button, badge, modal, toast %}
```

### Card Component

```jinja2
{{ card(
    title="Project Status",
    content="All on track",
    footer_html='<a href="/projects">View all</a>',
    class_extra="bg-accent-light"
) }}
```

### Button Component

```jinja2
{{ button(
    text="Sync Calendar",
    hx_post="/calendar/sync",
    hx_target="#calendar-events",
    class_extra="btn-primary"
) }}
```

### Badge Component

```jinja2
{{ badge(text="P1", variant="error") }}
{{ badge(text="Active", variant="success") }}
{{ badge(text="In Progress", variant="warning") }}
```

### Modal Component

```jinja2
{{ modal(
    id="confirm-delete",
    title="Delete Task?",
    body="This action cannot be undone.",
    footer_html='<button class="btn-danger" hx-delete="/tasks/123">Delete</button>'
) }}
```

## HTMX Patterns

### Partial Swap (Update Fragment)

```html
<!-- Button triggers endpoint that returns partial HTML -->
<button 
    hx-post="/tasks/toggle/123"
    hx-target="#task-123"
    hx-swap="outerHTML">
    Toggle
</button>

<!-- Target element -->
<div id="task-123">
    <!-- This div gets replaced with response from /tasks/toggle/123 -->
</div>
```

**Endpoint returns**:
```python
@router.post("/tasks/toggle/{id}", response_class=HTMLResponse)
def toggle_task(id: str):
    task = get_task(id)
    task.completed = not task.completed
    return templates.TemplateResponse("components/task_row.html", {"task": task})
```

### Form Submission

```html
<form 
    hx-post="/ideas/create"
    hx-target="#ideas-list"
    hx-swap="afterbegin"
    hx-on::after-request="this.reset()">
    
    <input type="text" name="title" required>
    <button type="submit">Add Idea</button>
</form>

<!-- New idea prepended here -->
<div id="ideas-list">
    <!-- Existing ideas -->
</div>
```

### Toast Notifications

```python
# Backend sets HX-Trigger header
from fastapi import Response

@router.post("/tasks/create")
def create_task(request: CreateTaskRequest):
    task = create(request)
    
    # Trigger toast on client
    response = Response(content=task_html)
    response.headers["HX-Trigger"] = json.dumps({
        "showToast": {"message": "Task created", "variant": "success"}
    })
    return response
```

```javascript
// Frontend listens for trigger (in base.html)
document.body.addEventListener("showToast", (event) => {
    showToast(event.detail.message, event.detail.variant);
});
```

### Loading States

```html
<button 
    hx-post="/calendar/sync"
    hx-indicator="#sync-spinner">
    Sync Calendar
</button>

<div id="sync-spinner" class="htmx-indicator">
    Syncing...
</div>
```

## Alpine.js for UI State

### Toggle Visibility

```html
<div x-data="{ open: false }">
    <button @click="open = !open">Toggle Details</button>
    
    <div x-show="open" x-transition>
        <!-- Collapsible content -->
    </div>
</div>
```

### Tabs

```html
<div x-data="{ tab: 'active' }">
    <div class="tabs">
        <button @click="tab = 'active'" :class="{ 'active': tab === 'active' }">Active</button>
        <button @click="tab = 'done'" :class="{ 'active': tab === 'done' }">Done</button>
    </div>
    
    <div x-show="tab === 'active'">
        <!-- Active tasks -->
    </div>
    
    <div x-show="tab === 'done'">
        <!-- Done tasks -->
    </div>
</div>
```

### Modal Control

```html
<div x-data="{ showModal: false }">
    <button @click="showModal = true">Open Modal</button>
    
    <div x-show="showModal" class="modal-overlay" @click.away="showModal = false">
        <div class="modal-content">
            <h2>Modal Title</h2>
            <button @click="showModal = false">Close</button>
        </div>
    </div>
</div>
```

## CSS Conventions (static/css/main.css)

### Color Variables (Dark Theme)

```css
:root {
    --accent-primary: #3b82f6;      /* Blue */
    --accent-secondary: #8b5cf6;    /* Purple */
    --accent-light: #1f2937;        /* Dark gray */
    --accent-success: #10b981;      /* Green */
    --accent-warning: #f59e0b;      /* Orange */
    --accent-error: #ef4444;        /* Red */
    --text-primary: #f9fafb;
    --text-secondary: #d1d5db;
}
```

### Utility Classes

```html
<!-- Layout -->
<div class="container">                     <!-- Max-width, centered -->
<div class="grid grid-cols-2 gap-4">        <!-- 2-column grid -->

<!-- Spacing -->
<div class="p-4">                           <!-- Padding 1rem -->
<div class="mt-8 mb-4">                     <!-- Margin top 2rem, bottom 1rem -->

<!-- Typography -->
<h1 class="text-3xl font-bold">             <!-- Large, bold heading -->
<p class="text-secondary">                  <!-- Secondary text color -->

<!-- Buttons -->
<button class="btn-primary">                <!-- Primary button (blue) -->
<button class="btn-danger">                 <!-- Danger button (red) -->
<button class="btn-secondary">              <!-- Secondary button (gray) -->

<!-- Badges -->
<span class="badge-success">On Track</span>
<span class="badge-warning">At Risk</span>
<span class="badge-error">Blocked</span>

<!-- Cards -->
<div class="card">                          <!-- Standard card -->
<div class="card bg-accent-light">          <!-- Dark card -->
```

### Responsive Design

```html
<!-- Stack on mobile, 2 columns on desktop -->
<div class="grid grid-cols-1 md:grid-cols-2 gap-4">
    <div>Column 1</div>
    <div>Column 2</div>
</div>

<!-- Hide on mobile, show on desktop -->
<div class="hidden md:block">Desktop only</div>

<!-- Show on mobile, hide on desktop -->
<div class="block md:hidden">Mobile only</div>
```

## Examples

### Example 1: Create New Page

```jinja2
{# templates/pages/calendar.html #}
{% extends "base.html" %}
{% from 'components/ui_macros.html' import card, button %}

{% block title %}Calendar - Day-to-Day{% endblock %}

{% block content %}
<div class="container mt-8">
    <div class="flex justify-between items-center mb-6">
        <h1 class="text-3xl font-bold">Calendar</h1>
        {{ button(
            text="Sync Now",
            hx_post="/calendar/sync",
            hx_target="#events",
            hx_indicator="#sync-spinner",
            class_extra="btn-primary"
        ) }}
    </div>
    
    <div id="sync-spinner" class="htmx-indicator">Syncing...</div>
    
    <div id="events" class="grid gap-4">
        {% for event in events %}
            {% include 'components/event_card.html' %}
        {% endfor %}
    </div>
</div>
{% endblock %}
```

### Example 2: Create Partial Component

```jinja2
{# templates/components/event_card.html #}
<div id="event-{{ event.id }}" class="card">
    <div class="flex justify-between">
        <div>
            <h3 class="font-semibold">{{ event.title }}</h3>
            <p class="text-secondary text-sm">
                {{ event.start_time.strftime('%I:%M %p') }} - {{ event.end_time.strftime('%I:%M %p') }}
            </p>
        </div>
        <button 
            hx-post="/tasks/from-event/{{ event.id }}"
            hx-target="#tasks-list"
            hx-swap="afterbegin"
            class="btn-secondary btn-sm">
            Create Task
        </button>
    </div>
</div>
```

### Example 3: Interactive Form with Alpine.js

```html
<div x-data="{ priority: 'P2', showAdvanced: false }">
    <form hx-post="/tasks/create" hx-target="#tasks-list" hx-swap="afterbegin">
        <input type="text" name="title" placeholder="Task title" required>
        
        <!-- Priority selector -->
        <select name="priority" x-model="priority">
            <option value="P1">P1 - Critical</option>
            <option value="P2">P2 - High</option>
            <option value="P3">P3 - Medium</option>
            <option value="P4">P4 - Low</option>
        </select>
        
        <!-- Conditional advanced options -->
        <button type="button" @click="showAdvanced = !showAdvanced" class="text-sm">
            Advanced Options
        </button>
        
        <div x-show="showAdvanced" x-transition>
            <input type="date" name="due_date">
            <input type="text" name="project" placeholder="Project">
        </div>
        
        <button type="submit" class="btn-primary">Create Task</button>
    </form>
</div>
```

## Common Mistakes

- Not extending base.html - loses nav, toast, WebSocket
- Using inline styles - violates main.css conventions
- Not using ui_macros.html - duplicates component code
- Forgetting hx-target - response replaces entire page
- Using --success/--error/--warning instead of --accent-* - wrong variable names
- Not using Alpine.js for client state - causes page refreshes
- Returning full page HTML from HTMX endpoints - should return partials
- Not setting HX-Trigger for toast notifications - user doesn't see feedback
