# UrbanSight architecture notes

Event path: BUS / EDGE → AI EVENT → BACKEND API → EVENT PROCESSING → POSTGRESQL / POSTGIS → WEBSOCKET → DASHBOARD.

Every event follows a common shape: eventId, busId, routeId, eventType, confidence, latitude, longitude, timestamp, severity and evidenceUrl.

For a new detection, the backend should query unresolved issues within a small spatial radius and match compatible event types. A matching observation is attached to the existing issue; otherwise a new issue is created. Confidence is recalculated from independent observations with diminishing returns.

Severity is a reviewable score using confidence, issue type, estimated size, traffic density, nearby pedestrians, road importance, observation frequency and time unresolved. The interface exposes the factors so operators can validate the recommendation.

Use OAuth/JWT authentication, role-based authorization, signed evidence URLs, input validation, audit logs and rate-limited ingestion. Cluster map points and paginate tables for large fleets.
