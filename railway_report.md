# Practical Application of PaaS with Railway

## 1. Deployment Process

I developed a Flask web application and deployed it to Railway as a Platform-as-a-Service (PaaS) environment. Railway handled the build and deployment pipeline from the connected GitHub repository. The application is accessible through the Railway public URL.

## 2. Environment Configuration

Sensitive values were configured through environment variables instead of hard-coding them in the source code. The application reads `FLASK_SECRET_KEY` for session security and `DATABASE_URL` for the Railway-managed PostgreSQL database connection.

## 3. Database Integration

The app uses a tasks table with CRUD operations:

- Create task
- Read task list
- Update task completion status
- Delete task

### Database schema

See `schema.sql`.

### Sample data

See `sample_data.sql`.

## 4. Scalability Awareness

Railway’s usage-based pricing means the deployment cost rises as CPU, memory, storage, and network usage increase. If traffic grows, the app can be scaled by:

- Monitoring usage in Railway
- Moving to a larger service size if needed
- Adding database indexes for larger task volumes
- Keeping the app stateless so multiple instances can serve requests

## 5. CI/CD Workflow

The GitHub repository is linked to Railway so that pushing code triggers automatic redeployment. This reduces manual deployment work and keeps the hosted version aligned with the latest source code.

## 6. Monitoring and Logging

Railway logs were used to identify deployment and runtime issues. A useful debugging approach is to trigger the `/debug/raise` endpoint during testing and inspect Railway logs to confirm that errors are captured correctly. After identifying the cause, the issue can be fixed and redeployed.

## 7. Reflection and Comparison

Compared with Render, Railway offers a very similar developer experience, but Railway is especially convenient for quick app deployment with managed databases and automatic redeployments. Compared with Heroku, Railway is simpler for student projects because it makes environment variables and database provisioning easy to connect from one interface.

## 8. Conclusion

Railway provided a practical example of how PaaS abstracts infrastructure management while still supporting deployment, environment management, database integration, and CI/CD workflows.

## Deployed Application

https://gae-flask-lab.onrender.com/
