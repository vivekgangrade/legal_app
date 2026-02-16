# Legal CMS Frontend

This is the React frontend for the Legal Case Management System.

## Quick Start

1.  **Install Dependencies**:
    ```bash
    cd frontend
    npm install
    ```

2.  **Start Development Server**:
    ```bash
    npm run dev
    ```
    The app will be available at `http://localhost:5173`.

> **Note**: If you encounter issues with `npm run build` on Windows (e.g., PostCSS errors), use `npm run dev` for development and testing. The development server works correctly.

## Features

*   **Authentication**: Login with username/password (Connects to `/users/token`).
*   **Dashboard**: Overview of case statistics.
*   **Case List**: View, filter, and search cases.
*   **Create Case**: Add new cases to the system.

## API Configuration

The backend URL is configured in `src/services/api.js`. Default is `http://localhost:8000`.
Ensure your FastAPI backend is running before testing API features.

## Tech Stack

*   React + Vite
*   Tailwind CSS
*   Axios
*   React Router DOM
