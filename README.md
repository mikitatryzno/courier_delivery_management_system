# Courier Delivery Management System

A web-based platform to manage local courier deliveries: package creation, assignment, real-time tracking, and delivery confirmation.

## Table of contents
- [Problem](#problem)
- [System overview](#system-overview)
- [User roles](#user-roles)
- [Technical details](#technical-details)
- [Running locally](#running-locally)

## Problem
Local courier services often face manual, fragmented processes that cause poor visibility, inefficient routing, communication gaps, and lack of accountability. This project provides a single platform connecting senders, couriers, recipients, and administrators with end-to-end delivery workflows and real-time updates.

## System overview
The backend provides a FastAPI-based REST API and WebSocket endpoints; the frontend is a React + Vite application. The system supports four user roles with role-based access control and JWT authentication.

## User roles
- **Administrator** — manage users, monitor system health and analytics.
- **Courier** — view assigned deliveries, update statuses, confirm deliveries.
- **Sender** — create packages and track shipments.
- **Recipient** — track and confirm incoming packages.

## Technical details
- Backend: FastAPI, SQLAlchemy, Alembic (migrations), pytest for tests.
- Frontend: React, TypeScript, Vite, Vitest (tests).
- Deployment: Docker / docker-compose (dev & prod variations).

## Running locally
See `scripts/docker-setup.sh` and the `docker-compose.dev.yml` for local development setup. Backend and frontend both include test targets (see `backend/src/tests` and `frontend/src/tests`).
User Roles & Functionality
1. Administrator
Primary Goal: Maintain system integrity and oversee all operations

Key Responsibilities:

Manage user accounts and permissions
Monitor system performance and delivery metrics
Configure system settings and business rules
Handle disputes and system issues
Access all system functions for support purposes
Core Features:

User management dashboard
System analytics and reporting
Configuration management
Audit logs and activity monitoring
2. Courier
Primary Goal: Efficiently manage and complete deliveries

Key Responsibilities:

View assigned deliveries and routes
Update delivery status in real-time
Communicate with senders and recipients
Confirm successful deliveries
Report delivery issues or exceptions
Core Features:

Personal delivery dashboard
Route optimization suggestions
Mobile-friendly status updates
Photo confirmation for deliveries
Communication tools
3. Sender (Package Creator)
Primary Goal: Send packages reliably with full visibility

Key Responsibilities:

Create delivery requests with package details
Schedule pickup times
Track package status throughout delivery
Communicate with couriers when needed
Manage delivery preferences
Core Features:

Package creation and scheduling
Real-time tracking dashboard
Delivery history and analytics
Communication with assigned courier
Delivery preferences management
4. Recipient
Primary Goal: Receive packages conveniently with advance notice

Key Responsibilities:

Track incoming deliveries
Set delivery preferences and availability
Confirm receipt of packages
Provide feedback on delivery experience
Communicate special delivery instructions
Core Features:

Incoming deliveries dashboard
Delivery time preferences
Real-time delivery tracking
Delivery confirmation
Feedback and rating system
Core Features & Workflows
Package Management
Create Package: Senders input package details, recipient information, and delivery preferences
Edit Package: Modify package details before courier assignment
Track Package: Real-time status updates from creation to delivery
Package History: Complete audit trail of all package activities
Delivery Workflow
Package Creation: Sender creates delivery request
Courier Assignment: System assigns courier based on location and availability
Pickup Scheduling: Courier schedules pickup with sender
Package Pickup: Courier collects package and updates status
In Transit: Real-time location tracking during delivery
Delivery Attempt: Courier attempts delivery to recipient
Delivery Confirmation: Recipient confirms receipt or reports issues
Completion: Delivery marked as complete with all parties notified
Communication System
In-app Messaging: Direct communication between all parties
Status Notifications: Automated updates for key delivery milestones
Issue Reporting: Structured process for handling delivery problems
Feedback Collection: Post-delivery feedback and ratings
User Stories
Administrator Stories
As an administrator, I want to view all system users so I can manage accounts and permissions
As an administrator, I want to see delivery analytics so I can monitor system performance
As an administrator, I want to resolve delivery disputes so I can maintain service quality
As an administrator, I want to configure system settings so I can adapt to business needs
Courier Stories
As a courier, I want to see my assigned deliveries so I can plan my route efficiently
As a courier, I want to update delivery status so all parties stay informed
As a courier, I want to communicate with senders and recipients so I can coordinate deliveries
As a courier, I want to confirm deliveries with photos so I can provide proof of completion
As a courier, I want to report delivery issues so problems can be resolved quickly
Sender Stories
As a sender, I want to create delivery requests so I can send packages to recipients
As a sender, I want to track my packages so I know their current status and location
As a sender, I want to schedule pickups so I can ensure someone is available
As a sender, I want to communicate with couriers so I can provide special instructions
As a sender, I want to view delivery history so I can track my shipping patterns
Recipient Stories
As a recipient, I want to track incoming packages so I can prepare for delivery
As a recipient, I want to set delivery preferences so packages arrive at convenient times
As a recipient, I want to communicate with couriers so I can provide access instructions
As a recipient, I want to confirm deliveries so the process is complete
As a recipient, I want to provide feedback so I can help improve service quality
Use Cases
Use Case 1: Standard Package Delivery
Actors: Sender, Courier, Recipient, System Preconditions: All users have accounts and are authenticated Main Flow:

Sender creates package with recipient details and delivery preferences
System assigns available courier based on location and capacity
Courier receives notification and schedules pickup with sender
Courier picks up package and updates status to "In Transit"
System provides real-time tracking to sender and recipient
Courier delivers package to recipient
Recipient confirms delivery and provides feedback
System marks delivery as complete and notifies all parties
Use Case 2: Failed Delivery Attempt
Actors: Courier, Recipient, System Preconditions: Package is out for delivery Main Flow:

Courier attempts delivery but recipient is unavailable
Courier updates status to "Delivery Failed" with reason
System notifies recipient of failed attempt
Recipient reschedules delivery through system
System updates courier with new delivery instructions
Courier reattempts delivery at scheduled time
Use Case 3: Package Modification
Actors: Sender, System Preconditions: Package exists but courier not yet assigned Main Flow:

Sender requests package modification
System checks if modification is allowed (pre-assignment)
Sender updates package details or delivery address
System validates new information
System updates package and notifies relevant parties
Use Case 4: Emergency Delivery
Actors: Sender, Administrator, Courier Preconditions: Urgent delivery request Main Flow:

Sender marks package as "Urgent" with justification
System notifies administrator of urgent request
Administrator approves and prioritizes delivery
System assigns nearest available courier
Courier receives high-priority notification
Expedited delivery process follows standard workflow
Technical Requirements
Functional Requirements
Multi-role user authentication and authorization
Real-time package tracking and status updates
Automated courier assignment based on location and availability
Communication system between all parties
Mobile-responsive interface for courier field operations
Delivery confirmation with digital signatures/photos
Comprehensive reporting and analytics
Non-Functional Requirements
Performance: System should handle 1000+ concurrent users
Availability: 99.5% uptime during business hours
Security: Encrypted data transmission and secure authentication
Usability: Intuitive interface requiring minimal training
Scalability: Architecture should support business growth
Compatibility: Works on modern web browsers and mobile devices
Success Metrics
Delivery Success Rate: >95% successful first-attempt deliveries
User Satisfaction: >4.5/5 average rating from all user types
System Adoption: >80% of deliveries processed through the system
Response Time: <2 seconds average page load time
Issue Resolution: <24 hours average resolution time for delivery problems