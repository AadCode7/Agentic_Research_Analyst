# Research Analyst AI

**Research Analyst AI** is an intelligent, end-to-end platform designed to automate the traditionally manual processes of qualitative research. By leveraging AI-driven workflows, this application acts as a virtual researcher: it interacts with users to conduct dynamic interviews, gathers insights, and automatically synthesizes that raw data into comprehensive research reports.

At the heart of the application are two distinct AI workflows that handle the heavy lifting of research:

* **The Interview Engine (`interview_workflow.py`)**: Instead of static surveys, this workflow powers dynamic, conversational interviews. It adapts to user responses, probing for deeper insights just like a human research analyst would.


* **The Report Generator (`report_generator_workflow.py`)**: Once interview data is collected, this workflow takes over. It processes the qualitative data, identifies key trends and insights, and structures them into a polished analytical report.



## Detailed Architecture & Project Components

The project is built as a full-stack web application, strictly organizing its backend, frontend, and AI components for maximum scalability.

### 1. Web Interface & Dashboard (`api/templates/` & `api/static/`)

The application is fully accessible via a built-in web portal:

* **User Authentication**: Includes dedicated pages for user onboarding (`signup.html`) and access (`login.html`).


* **The Dashboard (`dashboard.html`)**: The central hub where users can initiate new research tasks and view existing data.


* **Real-Time Tracking (`report_progress.html`)**: Because AI report generation can take time, this dedicated UI keeps the user informed of the AI's progress as it synthesizes the data.


* **Styling**: The visual identity of these pages is managed via a dedicated stylesheet (`static/css/style.css`).



### 2. API & Service Layer (`api/`)

The application routes data between the user interface and the AI workflows using a modular backend:

* **Routing & Services**: Client requests are handled by `report_routes.py`, which delegates the heavy business logic to `report_service.py`.


* **Data Validation**: Ensures that incoming data (like user interview answers or report requests) is strictly formatted using defined models (`request.models.py` and `schemas/models.py`).



### 3. AI Prompt Management (`prompt_lib/`)

To keep the AI's behavior predictable and accurate, all instructions sent to the AI are centralized. The `prompt_locator.py` acts as a library, fetching the correct context, persona, and instructions for the AI depending on whether it is conducting an interview or writing a report.

### 4. Infrastructure & Utilities

The project is built with enterprise-grade stability in mind, featuring several foundational modules:

* **Configuration Managers (`config/` & `utils/`)**: Instead of hardcoding settings, the app reads from `configuration.yaml` via a `config_loader.py`. AI models themselves are dynamically initialized using the `model_loader.py`.


* **Database Integration (`database/db_config.py`)**: Manages the connections required to securely store user credentials, interview transcripts, and final reports.


* **Observability (`logger/` & `exception/`)**: The system features custom implementations for tracking system events (`custom_logger.py`) and gracefully catching and handling errors (`custom_exception.py`) so the application doesn't crash unexpectedly.
