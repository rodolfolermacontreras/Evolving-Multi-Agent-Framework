# syntax=docker/dockerfile:1.7
# Bridge dashboard container image -- single-user Azure Container App deployment.
# See spec-driven-development/specs/2026-05-16-cloud-dashboard/DESIGN.md
FROM python:3.13-slim

# Install git so state_builder can run `git log` for the Recent Commits panel.
RUN apt-get update \
 && apt-get install -y --no-install-recommends git ca-certificates \
 && rm -rf /var/lib/apt/lists/*

RUN groupadd -r app && useradd -r -g app -u 10001 -m -d /home/app app

WORKDIR /repo

# Mark /repo as a safe git directory regardless of UID mismatch
RUN git config --system --add safe.directory /repo

# Copy the whole checked-out repo (artifacts + ledger + cli) -- stdlib only,
# no pip install needed.
COPY --chown=app:app . /repo

USER app
EXPOSE 8080
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

CMD ["python", "spec-driven-development/cli/state_builder.py", "serve", \
     "--host", "0.0.0.0", "--port", "8080", "--no-open"]
