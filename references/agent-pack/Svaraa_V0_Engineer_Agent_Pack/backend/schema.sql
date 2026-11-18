-- Logical starter only. Add reviewed identity/household/FK/RLS/retention policies.
CREATE TABLE device_events (
 device_id text NOT NULL, event_id uuid NOT NULL, incident_id uuid,
 mode text NOT NULL CHECK(mode IN ('live','drill')), drill_id uuid,
 body jsonb NOT NULL, body_hash text NOT NULL, original_receipt jsonb NOT NULL,
 received_at timestamptz NOT NULL DEFAULT now(), PRIMARY KEY(device_id,event_id),
 CHECK((mode='live' AND drill_id IS NULL) OR (mode='drill' AND drill_id IS NOT NULL))
);
CREATE TABLE incidents (
 id uuid PRIMARY KEY, device_id text NOT NULL, household_id uuid NOT NULL,
 mode text NOT NULL, state text NOT NULL, revision bigint NOT NULL DEFAULT 1,
 cancel_requested boolean NOT NULL DEFAULT false,
 acknowledged_by uuid, acknowledged_at timestamptz, resolved_at timestamptz
);
CREATE TABLE notification_outbox (
 id uuid PRIMARY KEY, event_id uuid NOT NULL, channel text NOT NULL,
 mode text NOT NULL, body jsonb NOT NULL, state text NOT NULL DEFAULT 'pending',
 attempts integer NOT NULL DEFAULT 0, available_at timestamptz NOT NULL DEFAULT now(),
 UNIQUE(event_id,channel)
);
CREATE TABLE device_commands (
 id uuid PRIMARY KEY, device_id text NOT NULL, incident_id uuid,
 body jsonb NOT NULL, expires_at timestamptz NOT NULL,
 state text NOT NULL DEFAULT 'pending', action_id uuid UNIQUE
);
