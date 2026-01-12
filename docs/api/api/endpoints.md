# API Endpoints Summary

Generated from OpenAPI specification v1.0.0

## Authentication

### POST /api/auth/login

**Summary:** User Login

**Description:** Authenticate user with email and password to receive access token

---

### POST /api/auth/register

**Summary:** User Registration

**Description:** Register a new user account

---

### GET /api/auth/me

**Summary:** Get Current User

**Description:** Get information about the currently authenticated user

---

### POST /api/auth/refresh

**Summary:** Refresh Access Token

**Description:** Get a new access token using refresh token

---

### POST /api/auth/logout

**Summary:** User Logout

**Description:** Logout user (client should discard tokens)

---

### GET /api/auth/token-info

**Summary:** Token Information

**Description:** Return decoded token information for the provided access token

---

### POST /api/auth/change-password

**Summary:** Change Password

**Description:** Change password for the authenticated user

---

### GET /api/auth/validate

**Summary:** Validate Token

**Description:** Validate provided access token and return status

---

## Packages

### POST /api/packages/

**Summary:** Create Package

**Description:** Create a new package for delivery

---

### GET /api/packages/

**Summary:** List Packages

**Description:** Get list of packages based on user role and filters

---

### GET /api/packages/available

**Summary:** Get Available Packages

**Description:** Get packages available for courier assignment

---

### GET /api/packages/my-deliveries

**Summary:** Get My Deliveries

**Description:** Get packages assigned to current courier

---

### GET /api/packages/stats

**Summary:** Get Package Statistics

**Description:** Get package statistics based on user role

---

### GET /api/packages/{package_id}

**Summary:** Get Package Details

**Description:** Get detailed information about a specific package

---

### PUT /api/packages/{package_id}

**Summary:** Update Package

**Description:** Update package information

---

### DELETE /api/packages/{package_id}

**Summary:** Delete Package

**Description:** Delete a package (Admin or sender only)

---

### PUT /api/packages/{package_id}/status

**Summary:** Update Package Status

**Description:** Update package delivery status

---

### PUT /api/packages/{package_id}/assign

**Summary:** Assign Package to Courier

**Description:** Assign package to a specific courier

---

### GET /api/packages/search/{search_term}

**Summary:** Search Packages

**Description:** Search packages by various criteria

---

## Users

### GET /api/users/

**Summary:** List Users

**Description:** Get list of users (Admin only)

---

### GET /api/users/me

**Summary:** Get Current User Profile

**Description:** Get current user's profile information

---

### PUT /api/users/me

**Summary:** Update Current User Profile

**Description:** Update current user's profile information

---

### GET /api/users/{user_id}

**Summary:** Get User by ID

**Description:** Get user information by ID (Admin or own profile)

---

### PUT /api/users/{user_id}

**Summary:** Update User

**Description:** Update user information (Admin only)

---

### DELETE /api/users/{user_id}

**Summary:** Delete User

**Description:** Delete user account (Admin only)

---

### PUT /api/users/{user_id}/role

**Summary:** Update User Role

**Description:** Update user role (Admin only)

---

### GET /api/users/role/{role}

**Summary:** Get Users by Role

**Description:** Get users filtered by role

---

### GET /api/users/stats/summary

**Summary:** Get User Statistics

**Description:** Get user statistics summary (Admin only)

---

## Health

### GET /api/health/

**Summary:** Health Check

**Description:** Basic health check.

---

### GET /api/health/database

**Summary:** Database Health Check

**Description:** Database health check.

---

### GET /api/health/detailed

**Summary:** Detailed Health Check

**Description:** Detailed health check with database statistics.

---

## Root

### GET /

**Summary:** Read Root

**Description:** Root endpoint providing basic API information.

Returns welcome message and links to documentation.

---

