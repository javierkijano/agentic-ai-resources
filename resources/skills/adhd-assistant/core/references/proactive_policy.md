# Proactive policy

## Purpose
Run the assistant regularly without becoming noise.

## Default cadence
- maintenance tick every 10 minutes
- quiet hours respected by default
- daily review once in the morning
- no outbound message unless there is a trigger

## Valid triggers
1. due reminder
2. overdue important task
3. appointment or event approaching
4. task postponed 3+ times
5. active day plan has gone stale
6. onboarding/config question worth surfacing
7. explicit recovery condition (day broken, zero progress, scattered fronts)

## Trigger priority
1. appointment/event risk
2. due or overdue important reminder
3. overdue high-value task
4. repeated postponement escalation
5. broken-day recovery nudge
6. daily review
7. low-priority coaching/reflection

## Rate limits
- non-urgent: at least 60 minutes between outbound nudges
- urgent: at least 15 minutes between outbound nudges
- daily review: once per day
- quote/reflection: maximum 1 by default in a normal day unless user changes it

## Reminder escalation policy
For important commitments, standard offsets are:
- 24h
- 6h
- 2h
- 1h
- 30m
- 10m
- due time
- overdue follow-up

## Postponement escalation
At 3 postponements:
- stop treating it as a normal reminder issue
- suggest one of:
  - 2-minute breach
  - smaller next step
  - deliberate reschedule with reason
  - delegation/cancellation review

## Quiet hours
During quiet hours:
- suppress non-critical nudges
- allow only critical appointment/event or user-explicit exceptions

## Output discipline
A proactive message should usually contain:
- one situational line
- one action
- optional one-line coaching support

Bad proactive message:
- long analysis
- five options
- generic motivation speech

Good proactive message:
- "Tienes esto abierto y vence hoy. Haz el primer paso ahora o posponlo conscientemente 1h."
