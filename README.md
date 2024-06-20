## Demo

This project is a web server built using Flask for managing categories and recipes. It includes user authentication with JWT, database interactions, and role-based access control. The project demonstrates the use of various Flask features and best practices, including:

- **Database Connection Management**: Using a context manager to handle database connections.
- **Authentication and Authorization**: Implementing JWT-based authentication and role-based access control.
- **Route Handling**: Defining various routes for CRUD operations on users, categories, and recipes.
- **Decorator Functions**: Using decorators for code reuse, such as checking login status and user roles.
- **Template Rendering**: Serving HTML templates for certain routes.

### Features

- User registration, login, and logout
- Role-based access control
- CRUD operations for categories and recipes
- Token-based authentication with JWT
- Separation of concerns with database connection and request handling
