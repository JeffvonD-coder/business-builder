# Business Builder App

A Streamlit application that helps entrepreneurs develop and refine their business ideas using AI-powered analysis.

## Features

- Business idea analysis with AI
- Clarity assessment and niche strategy development
- Action plan generation
- PDF and TXT report generation
- Multi-language support (English/Dutch)
- Secure user authentication with MongoDB
- Credit-based usage system
- Admin dashboard for user management

## Security Features

- Secure password hashing with bcrypt
- Environment-based configuration
- No hardcoded credentials
- MongoDB Atlas for secure data storage
- Input sanitization and validation
- Role-based access control
- Rate limiting for login attempts
- Secure session management

## Prerequisites

- Python 3.11 or higher
- MongoDB Atlas account
- DeepSeek API key
- Git

## Local Setup

1. Clone the repository:
```bash
git clone https://github.com/your-username/business-builder.git
cd business-builder
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file from the template:
```bash
cp .env.example .env
```

4. Configure your environment:
   - Get a DeepSeek API key from [DeepSeek](https://platform.deepseek.com)
   - Create a MongoDB Atlas account and database
   - Update `.env` with your credentials:
     ```
     DEEPSEEK_API_KEY=your_api_key_here
     MONGODB_URI=your_mongodb_connection_string
     ```

5. Run the application:
```bash
streamlit run app.py
```

## MongoDB Setup

1. Create a MongoDB Atlas account at [mongodb.com](https://www.mongodb.com/cloud/atlas/register)
2. Create a new cluster (free tier is sufficient)
3. Set up database access:
   - Create a database user
   - Use a strong password
4. Set up network access:
   - Add your IP address
   - For development, you can allow access from anywhere (0.0.0.0/0)
5. Get your connection string:
   - Click "Connect"
   - Choose "Connect your application"
   - Copy the connection string
   - Replace `<password>` with your database user's password

## Deployment on Streamlit Cloud

1. Fork or push this repository to your GitHub account
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your repository
4. Add the following secrets in Streamlit Cloud settings:
   ```toml
   # .streamlit/secrets.toml
   DEEPSEEK_API_KEY = "your-api-key"
   MONGODB_URI = "your-mongodb-connection-string"
   ```
5. Deploy!

## Security Best Practices

1. Environment Variables:
   - Never commit `.env` file
   - Use `.env.example` as a template
   - Keep API keys and connection strings secure

2. Database Security:
   - Use strong MongoDB Atlas passwords
   - Enable IP whitelist when possible
   - Regular security audits
   - Monitor database access

3. User Management:
   - Passwords are hashed using bcrypt
   - Minimum password requirements enforced
   - Rate limiting on login attempts
   - Session management and timeouts

4. Code Security:
   - Input validation and sanitization
   - Secure file handling
   - Error handling without information disclosure
   - Regular dependency updates

## File Structure

```
business-builder/
├── app.py                 # Main Streamlit application
├── main.py               # Business logic implementation
├── requirements.txt      # Python dependencies
├── .env.example         # Environment variables template
├── .gitignore           # Git ignore rules
├── README.md            # This file
├── pages/              # Streamlit pages
│   └── 01_user_management.py
├── utils/              # Utility functions
│   ├── database.py     # MongoDB integration
│   ├── security.py     # Security utilities
│   ├── rate_limiter.py # Rate limiting
│   └── file_manager.py # File operations
└── generated_files/    # Generated reports (gitignored)
    ├── pdf/
    └── txt/
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## Security Considerations

- Never commit sensitive data
- Keep dependencies updated
- Follow security best practices
- Regular security audits
- Monitor application logs

## Support

Contact the administrator for:
- Database management scripts
- User management
- Security concerns
- Bug reports

## License

MIT License - See LICENSE file for details 