## Project Overview

The **Local Listing Backend API** is a Django-based REST API designed to provide backend services for the local listing platform. The API handles multiple aspects of the application, including user management, listings, messaging, reviews, and more. This backend is intended to serve as the main point of interaction for the React front-end client, providing endpoints to create, read, update, and delete resources, as well as manage user sessions and interactions.

### Purpose

The purpose of this REST API is to provide a robust and scalable backend system that allows users to list and manage items for sale, connect with each other, and manage profiles. It is intended to serve as the data and business logic layer for a complete web application, handling all backend requirements and data processing.

### Features

- **User Management**: Registration, login, password management, and user profiles.
- **Listings**: Creating, updating, deleting, and viewing listings of items for sale, wanted items, services, events, etc.
- **Messaging**: Provides communication between users, allowing them to send messages related to specific listings.
- **Reviews**: Users can leave reviews for other users to enhance reliability and trust.
- **Admin Features**: Administrative endpoints for managing all presented features in the API.

### Objectives

The objective of this project is to build a REST API backend that supports all necessary features of a local listing platform. The API aims to:

- Provide a clean and scalable interface for data interaction.
- Ensure secure handling of user data, including authentication and authorization mechanisms.
- Offer an efficient and user-friendly approach to managing listings, reviews, and interactions.
- Facilitate a maintainable and extendable codebase, which adheres to best practices in API development.

## Features

### Key Features Summary

1. **User Management**

   - **Registration and Login**: Users can create accounts, log in, and manage their sessions. This includes support for password reset.
   - **Profile Management**: Users can update their personal details.

2. **Listings Management**

   - **Create Listings**: Users can create different types of listings.
   - **Update and Delete Listings**: Users can update the details of their listings or delete them when no longer needed.
   - **Category and Subcategory Support**: Listings are organized by categories and subcategories, providing better navigation and filtering capabilities.
   - **Listing Images**: Users can upload images to be associated with their listings, using integration with Cloudinary for image management. Images are deleted from Cloudinary when the listing is deleted or the user chooses to remove them in the update process.

3. **Search and Filter Listings**

   - **Advanced Filtering**: Users can filter listings based on price range, category, subcategory, location, condition, and more.
   - **Search Functionality**: Full-text search capabilities are provided to quickly find relevant listings.

4. **Messaging System**

   - **User Conversations**: Users can initiate conversations related to specific listings. Conversations between users are managed through a messaging system that allows users to ask questions and negotiate.
   - **Notifications**: Users receive notifications for new messages, ensuring prompt communication.

5. **Reviews and Ratings**

   - **Leave Reviews**: Users can leave reviews and ratings for other users based on past experience. This helps build trust within the platform.
   - **Manage Reviews**: Users can edit or delete the reviews they have left for others. A single review can be left per reviewed user.

6. **Admin and Staff Features**

   - **Admin Dashboard**: Administrators have access to endpoints that allow them to manage all aspects of the platform.
   - **User Management**: Admins can deactivate or delete listings and users.
   - **Listings Moderation**: Admins can approve, reject, or moderate listings to ensure compliance with platform guidelines. This is also a feature that can be extended in future iterations to develop user report mechanisms.

7. **Favorites and Wishlist**

   - **Favorite Listings**: Users can add listings to their favorites for easy access later. This helps users keep track of items they are interested in.

8. **Notifications and Alerts**

   - **Activity Notifications**: Users are notified of important activities and platform interactions, such as new messages, listing approvals, etc.

### Additional Features Summary

- **Password Reset via Email**: Users can reset their passwords using a secure link sent to their registered email address.

Note: In order to test this features, the email account used for account registration must be valid to receive the password reset email. In this current iteration, the email is not verified upon registration. The email service used for this feature is SendGrid.

- **Tokens and Refresh Tokens**: The API uses JWT tokens for authentication and refresh tokens to manage user sessions securely.
- **Multi-Image Upload**: Users can upload multiple images for a single listing, giving more context and details to potential buyers.
- **Cloudinary Integration**: Listings' images are handled using Cloudinary, providing efficient image storage, optimization, and delivery.
- **Responsive Design**: The API is designed to support both web and mobile clients, ensuring that data is accessible across devices.
- **Location-Based Filtering**: Users can filter listings based on location to find items near them. This feature can be extended to include distance-based filtering in future iterations.
- **Statistics and Analytics**: Listings have view counts, and admins can access basic analytics to track platform usage and popular categories.
- **Pagination**: The listings endpoint supports pagination to manage large datasets efficiently. Unfortunately, due to time constraints, the pagination feature is not yet implemented in the frontend client, but it was tested and works as expected in the backend.

## Technologies Used

### Languages

- **Python**: The primary language used to develop the backend logic and API endpoints.

### Frameworks & Libraries

- **Django**: A high-level Python web framework used to create the backend of the application.
- **Django REST Framework (DRF)**: Extends Django to provide a powerful toolkit for building Web APIs.
- **Django Filters**: Used to provide filtering capabilities for querysets in the API.
- **Cloudinary**: Integrated for handling media storage, specifically for listing images.

### Databases

- **PostgreSQL**: Used as the primary database for storing all application data, including user information, listings, reviews, and messages.

### Other Tools & Services

- **Cloudinary**: Provides cloud storage for user-uploaded images, optimizing and delivering images efficiently.
- **SendGrid**: Used to handle transactional emails, such as registration confirmation and password resets.
- **Gunicorn**: A Python WSGI HTTP server used for deploying the application.
- **Heroku**: Platform-as-a-service (PaaS) used for hosting and deploying the backend API.
- **Postman**: Utilized during development for testing the API endpoints.

## Information Architecture

### Database Schema (ERD Diagram)

The database schema consists of multiple interconnected models, each representing a key entity in the application. The primary models are **User**, **Listing**, **Category**, **Subcategory**, **Message**, **Review**, and **ListingImage**. The relationships between these models include:

- **User**: Represents the users of the platform. Each user can create multiple listings, leave reviews, and participate in conversations.
- **Listing**: Represents the items listed by users. Each listing is linked to a **User**, **Category**, and optionally a **Subcategory**. Listings can have multiple associated **ListingImage** entries.
- **Category and Subcategory**: Listings are categorized to improve searchability and user navigation. **Category** and **Subcategory** models define these relationships.
- **Message**: Represents messages exchanged between users related to listings. Each message is linked to a **User** and a **Listing**.
- **Review**: Represents user reviews for listings. Each review is linked to a **User** and a **Listing**.
- **ListingImage**: Represents images associated with a listing. Each image entry is linked to a specific **Listing**.

### Data Models Description

- **User Model**: Contains fields such as `username`, `email`, `password`, `profile_picture`, and `date_joined`. Users have role-based access to resources, and their relationships include creating listings, reviews, and messaging.
- **Listing Model**: Contains fields such as `title`, `description`, `price`, `condition`, `listing_type`, `category`, `subcategory`, `location`, `created_at`, and `updated_at`. Listings have foreign key relationships with **User**, **Category**, and **Subcategory**.
- **Category and Subcategory Models**: Categories contain general classification information, while subcategories provide more granularity. Fields include `name` and foreign key references to maintain relationships.
- **Message Model**: Contains `content`, `timestamp`, `sender`, and `listing` to support user-to-user communication regarding listings.
- **Review Model**: Contains `rating`, `comment`, `user`, `listing`, and `created_at` to manage user feedback for listings.
- **ListingImage Model**: Contains `listing`, `image`, and `created_at` fields, storing image URLs using Cloudinary integration.

### API Endpoints

The following is a summary of key API endpoints provided by the Local Listing Backend API:

1. **User Endpoints**

   - **POST /api/users/register/**: Register a new user.
   - **POST /api/users/login/**: User login to obtain authentication token.
   - **POST /api/users/password-reset-request/**: Request a password reset email.
   - **POST /api/users/password-reset-confirm/**: Confirm a password reset using the token.
   - **POST /api/users/change-password/**: Change the user password.
   - **GET /api/users/profile/**: Retrieve the logged-in user's profile.
   - **PUT /api/users/profile/update/**: Update user profile details.
   - **POST /api/users/logout/**: Log out the user and blacklist the refresh token.

2. **Listing Endpoints**

   - **GET /api/listings/**: Retrieve a list of all listings with optional filters.
   - **POST /api/listings/create/**: Create a new listing.
   - **GET /api/listings/{id}/**: Retrieve details of a specific listing.
   - **PUT /api/listings/{id}/update/**: Update an existing listing.
   - **DELETE /api/listings/{id}/delete/**: Delete a listing.
   - **PATCH /api/listings/{id}/update-status/**: Update the status of a specific listing.
   - **GET /api/my-listings/**: Retrieve all listings created by the authenticated user.

3. **Category and Subcategory Endpoints**

   - **GET /api/categories/**: Retrieve all categories.
   - **GET /api/categories/{id}/**: Retrieve details of a specific category.
   - **GET /api/subcategories/**: Retrieve all subcategories.
   - **GET /api/subcategories/{id}/**: Retrieve details of a specific subcategory.
   - **GET /api/subcategories/by-category/{category_id}/**: Retrieve subcategories under a specific category

   Note: The categories and subcategories can me managed only in the admin panel, users utilize them as read-only data.

4. **Messaging Endpoints**

   - **GET /api/conversations/**: Retrieve all conversations of the authenticated user or create a new one.
   - **POST /api/conversations/{conversation_id}/messages/**: Send a message within a specific conversation.
   - **POST /api/conversations/{conversation_id}/mark-as-read/**: Mark messages in a conversation as read.
   - **GET /api/unread-messages/**: Retrieve the count of unread messages for the authenticated user.
   - **GET /api/listing/{listing_id}/messages/**: Retrieve incoming messages for a specific listing.

   Note: In this current iteration, the messages cannot be deleted or updated by the user. This feature can be extended in future iterations.

5. **Review Endpoints**

   - **POST /api/users/{user_id}/reviews/**: Create or update a review for a user.
   - **GET /api/users/{user_id}/reviews/**: Retrieve all reviews for a specific user.
   - **GET /api/reviews/{id}/**: Retrieve details of a specific review.
   - **DELETE /api/reviews/{id}/delete/**: Delete a specific review.

6. **Profile Endpoints**

   - **GET /api/profiles/profile/**: Retrieve the authenticated user's profile.
   - **GET /api/profiles/{username}/**: Retrieve the public profile of a specific user by username.
   - **GET /api/listings/user/{username}/**: Retrieve all active listings for a specific user.

7. **Favorite Listings Endpoints**
   - **GET /api/favorites/**: Retrieve all listings favorited by the authenticated user.
   - **POST /api/listings/{id}/favorite/**: Add or remove a listing from the user's favorites.

## Agile Methodology

The development of the Local Listing Backend API followed an **Agile methodology**, specifically using **Kanban** for task management.

- **Kanban Board**: A Kanban board was used to manage tasks, allowing for better visualization of progress and bottlenecks. Each task was categorized as "To Do", "In Progress", "In Review", or "Done", making it easy to track the development flow.

- **User Stories**: User stories were defined to capture the requirements from an end-user perspective. Each feature, such as user registration, listing creation, messaging, and review management, was documented as a user story to ensure it delivered value to the user. User stories were prioritized based on their impact and complexity using MOSCOW prioritization.

- **GitHub Project Board**: A GitHub project board was used to track issues and user stories. Tasks were created as issues, and the Kanban board was employed to manage their status. This helped ensure that development remained focused on delivering value in small, manageable increments.

## Version Control

Throughout the development process, Git was used for version control, with Visual Studio Code (VS Code) as the primary Integrated Development Environment (IDE). GitHub was used to host the remote repository.

### Tools and Workflow

1. **Development Environment**:

   - **VS Code**: Utilized as the primary IDE for developing the API. Its integrated terminal was used for running Django commands and managing the virtual environment.

2. **Source Control Panel**:

   - VS Code's **Source Control** panel was used extensively to manage code changes, particularly when working on multiple apps, views, and URLs. This panel allowed easy visualization of changes and helped in logically grouping updates into meaningful commits.

3. **Commit Strategy**:

   - Given the interconnected nature of the Django project, changes often spanned across multiple files, such as models, views, serializers, and URL configurations. The **diff viewer** in VS Code was used to carefully review changes before creating commits.
   - The commit messages were kept descriptive to ensure clarity of the project's evolution, making it easier for future maintainability.

4. **Key Git Commands**:

   - **`git add <file>`** or **`git add .`**: To stage changes.
   - **`git commit -m "descriptive message"`**: To commit changes with a meaningful message.
   - **`git push`**: To push the local commits to the GitHub repository.

5. **Remote Synchronization**:
   - Regularly used **`git pull`** to sync the local repository with the latest changes on the remote GitHub repository. This practice helped avoid conflicts after modifying the project board or issues.

### GitHub Project Management

- **GitHub Project Board**: A Kanban board on GitHub was used to track user stories, tasks, and issues. This helped ensure smooth management and prioritization of features throughout the project. Due to the nature of this project, the board was shared with the frontend.

By leveraging Git and GitHub's integration with VS Code, a clean and understandable version history was maintained, even while managing the complex architecture of the Django REST API project.

## Deployment

The Local Listing Backend API was deployed using **Heroku**, a cloud Platform-as-a-Service (PaaS) that simplifies deployment and scaling of web applications. The deployment process involved setting up the necessary environment, pushing the code to Heroku, and ensuring that all services were running smoothly.

### Deployment Steps

1. **Heroku Setup**:

   - Created a new application on the Heroku platform via the Heroku dashboard.
   - Configured the necessary environment variables, such as database credentials, secret keys, and API keys, using the Heroku Config Vars feature.

2. **Procfile and Gunicorn**:

   - A **Procfile** was added to the project to specify the command that Heroku should use to start the application. This included using **Gunicorn** as the WSGI HTTP server.
   - The **Procfile** content was as follows:
     ```
     web: gunicorn project_name.wsgi --log-file -
     ```
     where `project_name` refers to the name of the Django project.

3. **Dependencies**:

   - All project dependencies were listed in the **`requirements.txt`** file, which was used by Heroku during the build process to install the necessary packages.
   - **Whitenoise** was used to serve static files, ensuring efficient handling of assets.

4. **Database Configuration**:

   - **PostgreSQL** was used as the production database. The database is provided by Code Institute.
   - Django settings were updated to use `dj-database-url` for parsing the database URL provided by Heroku.

5. **Static Files**:

   - **Whitenoise** was configured to handle static files.

6. **Deployment Process**:

   - The code was pushed to the Heroku remote repository using Git:
     ```
     git push heroku main
     ```
   - Heroku then built the application, installed dependencies, and started the web server using Gunicorn.

7. **Monitoring and Logs**:

   - **Heroku Logs**: Logs were monitored using the command:
     ```
     heroku logs --tail
     ```
     This helped in identifying any issues during deployment and in ensuring that the application was running smoothly.

### Deployment Summary

Deploying the API to Heroku allowed for a seamless and scalable deployment process, leveraging Heroku's managed services to handle the complexities of server setup. By using **Gunicorn**, **Whitenoise**, and **Code Institute Postgres Database**, the application was able to serve both dynamic content and static assets efficiently, providing a smooth user experience.

## Installation and Local Setup

To set up the Local Listing Backend API locally, follow these instructions to ensure that all dependencies are installed correctly, the development server runs as expected, and the environment is properly configured.

### Prerequisites

- **Python 3.8+**: Ensure Python is installed. You can download it from [python.org](https://www.python.org/downloads/).
- **Git**: Version control system to clone the repository. Install from [git-scm.com](https://git-scm.com/).
- **PostgreSQL**: Required for the database setup.

### Installation Steps

1. **Clone the Repository**

   - Use Git to clone the project repository from GitHub:
     ```
     git clone https://github.com/username/project_name.git
     ```
   - Navigate into the project directory:
     ```
     cd project_name
     ```

2. **Create a Virtual Environment**

   - It is recommended to use a virtual environment to keep dependencies isolated:
     ```
     python -m venv venv
     ```
   - Activate the virtual environment:
     - On Windows:
       ```
       venv\Scripts\activate
       ```
     - On macOS/Linux:
       ```
       source venv/bin/activate
       ```

3. **Install Dependencies**

   - Install the required packages using **`pip`**:
     ```
     pip install -r requirements.txt
     ```

4. **Environment Variables**

   - Create a **`.env`** file in the root of your project to store environment variables. Add the following variables:
     ```
     SECRET_KEY=your_secret_key
     DEBUG=True
     DATABASE_URL=your_postgresql_database_url
     ```

5. **Database Migration**

   - Apply migrations to set up the database:
     ```
     python manage.py migrate
     ```

6. **Create a Superuser**

   - Create an admin user to access the Django admin interface:
     ```
     python manage.py createsuperuser
     ```
   - Follow the prompts to set up the superuser credentials.

7. **Collect Static Files**

   - Collect all static files to be served:
     ```
     python manage.py collectstatic
     ```

8. **Run the Development Server**
   - Start the development server to test the application locally:
     ```
     python manage.py runserver
     ```
   - The API should now be accessible at `http://127.0.0.1:8000/`.

### Additional Setup

- **Postman**: Use [Postman](https://www.postman.com/) to test the API endpoints. Import the provided collection or create your own requests to interact with the API.
- **Heroku CLI** (Optional): If you wish to deploy the project to Heroku, install the [Heroku CLI](https://devcenter.heroku.com/articles/heroku-cli) to manage your Heroku applications from the terminal.

### Summary

These steps will set up the Local Listing Backend API on your local machine, allowing you to explore, modify, and test the application in a development environment. Ensure all configurations are set correctly to avoid issues during runtime.

## Testing

Testing was a crucial aspect of the development process for ensuring the robustness and reliability of the Local Listing Backend API. The project used a combination of manual testing and automated testing frameworks to validate the functionality of the API endpoints and ensure that they performed as expected.

### Testing Tools

- **Django's Test Framework**: Used to create and run unit tests for the various components of the application.
- **Postman**: Used extensively for manual testing of the API endpoints during development.
- **Coverage.py**: Used to measure the test coverage of the application, ensuring that all important parts of the code were tested.

### Types of Tests

1. **Unit Tests**

   - Unit tests were created for models, views, and serializers to ensure that each individual component worked correctly.
   - Example command to run unit tests:
     ```
     python manage.py test
     ```

2. **End-to-End (E2E) Tests**
   - Postman was used to manually test complete user flows, such as creating a user, adding a listing, and sending messages. This helped verify that the system behaved as expected from the user's perspective.

### Running Tests

- To run all tests for the application, use the following command:
  ```
  python manage.py test
  ```
  The result of the tests can be visualized in the following screenshot:

### Manual Testing

- **Postman** was used to manually test each API endpoint during development to confirm proper functionality.
- Test cases included verifying correct responses for various request types (GET, POST, PUT, DELETE) and ensuring appropriate error messages were returned for invalid requests.

### Summary

Testing the Local Listing Backend API involved a combination of unit and manual tests to ensure the functionality and reliability of the application. By using Django's built-in test framework and Postman for manual testing, the project achieved a stable and reliable backend service.

## Unsolved Issues and Bugs

During the development and testing phases of the Local Listing Backend API, several issues were found and solved. Below is a summary of the known fixed issues and some improvements that could be made in future iterations. Due to time constraints, the issues listed as unsolved were not addressed in the current version.

### 1. Messaging System Delay

- **Issue**: There is a delay in real-time messaging updates between users. This may lead to users not seeing new messages immediately.
- **Cause**: The delay is related to the polling interval set for retrieving new messages.
- **Proposed Solution**: Future iterations could include integrating WebSockets to provide real-time messaging updates between users.

### 2. Image Upload Timeout for Large Files

- **Issue**: Uploading very large images (over 10MB) can sometimes result in a timeout error.
- **Cause**: The issue is related to both the server’s upload size limit and the Cloudinary integration.
- **Proposed Solution**: Future iterations could include client-side image resizing before upload or server-side chunked uploads to handle large files more efficiently.

TODO: Add solved issues

## Future Features

To further enhance the Local Listing Backend API and provide an even better user experience, several features are planned for future development. These features aim to improve usability, increase engagement, and add new capabilities to the platform. Some of these features are already mentioned in the related sections.

### 1. Real-Time Messaging

- **Feature**: Upgrade the existing messaging system to support real-time communication using WebSockets.
- **Benefit**: This will provide users with a seamless chat experience, similar to popular messaging platforms, reducing delays and improving interaction quality.

### 2. Advanced Search and Filtering

- **Feature**: Implement more sophisticated search options, including fuzzy matching, keyword relevance, and advanced filters based on user preferences.
- **Benefit**: Users will be able to find listings more easily, even if their search terms are slightly misspelled or if they want more specific results.

### 3. Location-Based Listing Suggestions

- **Feature**: Integrate a location-based recommendation engine that suggests listings based on the user's geographic location.
- **Benefit**: This will improve the relevance of listings shown to users, making it easier to find items and services nearby.

### 4. Listing Analytics for Users

- **Feature**: Provide listing owners with detailed analytics on their listings, such as view counts, interest rates, and user interactions.
- **Benefit**: Listing owners will gain insights into how well their listings are performing, allowing them to optimize their descriptions or adjust prices based on user behavior.

### 5. Advanced User Settings

- **Feature**: Expand user settings to include preferences for notifications, privacy settings, and custom profile options.
- **Benefit**: Users will have more control over their experience on the platform, allowing them to tailor it to their needs and preferences.

### 6. User Badges and Reputation System

- **Feature**: Introduce a badge and reputation system based on user activity, successful transactions, and positive reviews.
- **Benefit**: This will encourage trust within the platform, rewarding users who contribute positively and fostering a sense of community.

### 7. Scheduled Listing Expiry

- **Feature**: Allow users to set an expiry date for their listings, after which the listing will automatically be archived.
- **Benefit**: This will help keep the platform updated with relevant listings and reduce clutter from outdated posts.

### 8. Multi-Language Support

- **Feature**: Add multi-language support to the API, enabling the platform to serve a more diverse user base.
- **Benefit**: Users from different regions will be able to use the platform in their preferred language, enhancing accessibility and user satisfaction.

### 9. In-App Notifications

- **Feature**: Implement in-app notifications in addition to email notifications, allowing users to receive updates directly within the application.
- **Benefit**: Users will have a more integrated experience, reducing the need to check their email for important alerts.

### 10. Report and Moderation System

- **Feature**: Introduce a reporting system for users to flag inappropriate content or behavior, with moderation tools for administrators.
- **Benefit**: This will help maintain a safe and respectful environment on the platform, ensuring that users can report issues and receive timely responses.

### 11. Featured Listings and Promotions

- **Feature**: Offer users the option to promote their listings for a fee, featuring them prominently on the platform.
- **Benefit**: This will provide users with additional visibility for their listings, helping them reach a larger audience and increase sales.

### Summary

The future features of the Local Listing Backend API are focused on improving the overall user experience, enhancing engagement, and making the platform more interactive and accessible. These planned upgrades will ensure the platform remains competitive and continues to meet the evolving needs of its user base.

## Credits

The development of the Local Listing Backend API was made possible thanks to various tools, and resources, Below is a list of credits for code, media, and tools that were instrumental in building this project.

A special thank to my mentor Spence, who provided valuable guidance and feedback throughout the development process.

### Code and Packages

- **Django**: The Django framework was used to build the backend API. The official documentation and community forums provided valuable support throughout the development process.
- **Django REST Framework (DRF)**: Used for building the RESTful API. Special thanks to the DRF maintainers and contributors for providing a comprehensive and flexible toolkit.
- **Cloudinary**: Integrated for handling media storage. The Cloudinary Python SDK and tutorials made media handling efficient and straightforward.
- **SendGrid**: Used for sending password reset emails. The SendGrid API documentation and Python library were instrumental in setting up the email service.

### Content and Inspiration

- **Code Institute Learning Materials**: The Django Full Stack Developer course provided the foundational knowledge and guidance for building the Local Listing Backend API.
- **Python Documentation**: The Python documentation was a valuable resource for understanding the language features and best practices.
- **Django Official Documentation**: The official documentation served as the primary resource for understanding Django’s capabilities and implementing best practices.

### Tools

- **Visual Studio Code (VS Code)**: The main IDE used for development. The extensions for Python, Django, and Git made the coding process smoother and more productive.
- **GitHub**: Used for version control and collaborative development.
- **Postman**: Essential for testing API endpoints during the development cycle, ensuring that each feature functioned as intended.
- **Heroku**: Provided the deployment platform for the API.
