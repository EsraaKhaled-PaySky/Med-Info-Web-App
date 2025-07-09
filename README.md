# Medicine Information Web App (MedInfo Pro)

A comprehensive web-based medicine information system built with Flask, designed to manage patient data, medicine records, and healthcare workflows efficiently.

## 🏥 Features

- **User Authentication System**
  - Secure login and signup functionality
  - Password reset capabilities
  - User profile management

- **Medical Dashboard**
  - Centralized dashboard for medical information
  - Patient data visualization
  - Quick access to medical records

- **Search Functionality**
  - Advanced search for medical records
  - Drug information lookup via RxNorm API
  - FDA data integration for medication details

- **Profile Management**
  - User profile customization
  - Medical professional profiles
  - Patient information management

- **API Integration**
  - Real-time FDA drug information
  - RxNorm standardized drug nomenclature
  - Up-to-date medication data

## 🚀 Tech Stack

- **Backend**: Python Flask
- **Database**: MongoDB
- **APIs**: FDA OpenData API, RxNorm API
- **Authentication**: Custom authentication system
- **Frontend**: HTML templates with responsive design
- **Static Assets**: CSS, JavaScript, and media files

## 📁 Project Structure

```
MED-INFO-WEB-APP/
├── app/
│   ├── __pycache__/           # Python cache files
│   ├── static/                # Static assets (CSS, JS, images)
│   ├── templates/             # HTML templates
│   │   ├── base.html          # Base template
│   │   ├── change_password.html
│   │   ├── dashboard.html     # Main dashboard
│   │   ├── forgot_password.html
│   │   ├── home.html          # Homepage
│   │   ├── login.html         # User login
│   │   ├── profile.html       # User profile
│   │   ├── reset_password.html
│   │   ├── search_results.html
│   │   ├── search.html        # Search functionality
│   │   └── signup.html        # User registration
│   ├── utils/                 # Utility functions
│   ├── __init__.py            # App initialization
│   ├── authpy                 # Authentication module
│   └── db.py                  # Database operations
└── README.md
```

## 🛠️ Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/med-info-web-app.git
   cd med-info-web-app
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install flask pymongo requests python-dotenv
   # Or if you have a requirements.txt:
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   export FLASK_APP=app
   export FLASK_ENV=development
   export SECRET_KEY=your-secret-key-here
   export MONGODB_URI=mongodb://localhost:27017/medical_app
   export FDA_API_KEY=your-fda-api-key
   ```

5. **Set up MongoDB**
   ```bash
   # Make sure MongoDB is running
   mongod
   ```

6. **Initialize the database**
   ```bash
   python -c "from app.db import init_db; init_db()"
   ```

7. **Run the application**
   ```bash
   flask run
   ```

## 🔧 Configuration

Create a `.env` file in the root directory:

```env
SECRET_KEY=your-very-secret-key-here
MONGODB_URI=mongodb://localhost:27017/medical_app
FDA_API_KEY=your-fda-api-key-here
RXNORM_API_BASE_URL=https://rxnav.nlm.nih.gov/REST/
FLASK_ENV=development
DEBUG=True
```

## 📱 Usage

1. **Access the Application**
   - Navigate to `http://localhost:5000`
   - Create a new account or login with existing credentials

2. **Dashboard Navigation**
   - Use the dashboard to access different medical modules
   - Search for patients or medical records
   - Manage user profiles and settings

3. **Authentication Features**
   - Secure login/logout functionality
   - Password reset via email
   - Profile management

## 🔐 Security Features

- Secure password hashing
- Session management
- Input validation and sanitization
- CSRF protection
- SQL injection prevention

## 📊 Database Schema

The application uses MongoDB with the following main collections:
- Users (authentication and profiles)
- Medical records
- Patient information
- Search history
- Drug information cache (FDA/RxNorm data)

## 🔌 API Integration

### FDA OpenData API
- Access to comprehensive drug information
- Adverse event reporting data
- Drug labeling information
- Real-time updates from FDA databases

### RxNorm API
- Standardized drug nomenclature
- Drug concept relationships
- Medication identification
- Dosage and strength information

**API Usage Example:**
```python
# FDA API call for drug information
response = requests.get(f"https://api.fda.gov/drug/label.json?search=brand_name:{drug_name}")

# RxNorm API call for drug concepts
response = requests.get(f"https://rxnav.nlm.nih.gov/REST/drugs.json?name={drug_name}")
```

## 🚀 Deployment

### Local Development
```bash
python app.py
```

### Production Deployment
1. Set environment variables for production
2. Configure a production database
3. Set up a web server (nginx/Apache)
4. Use a WSGI server like Gunicorn

```bash
gunicorn --bind 0.0.0.0:8000 app:app
```

## 🧪 Testing

```bash
# Run tests
python -m pytest tests/

# Run with coverage
python -m pytest --cov=app tests/
```

## 📝 API Documentation

The application provides RESTful endpoints for:
- User authentication (`/auth/`)
- Medical records (`/medical/`)
- Search functionality (`/search/`)
- Profile management (`/profile/`)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 📞 Support

For support and questions:
- Create an issue in the repository
- 
## 🔄 Changelog

### v1.0.0
- Initial release
- Basic authentication system
- Dashboard implementation
- Search functionality
- Profile management

## 👥 Authors

- **Christopher Ochigbo Ameh** - [Github](https://github.com/Pharmchrisameh1)
- **Esraa Khaled** - [Github](https://github.com/EsraaKhaled-PaySky) | [Github](https://github.com/EsraaKhaled94)
- **Victor Joseph** - [Github](https://github.com/Victorjoseph93)
- **Emmanuel Ubani Oti-Owom** - [Github](https://github.com/OTI-OWOM)

## 🙏 Acknowledgments

- Flask community for the excellent framework
- FDA for providing open access to drug information APIs
- National Library of Medicine for the RxNorm API
- MongoDB team for the robust database solution
- Medical professionals who provided requirements
- Open source contributors

---

**Note**: This is a medical information system. Ensure compliance with healthcare regulations (HIPAA, GDPR, etc.) in your jurisdiction before deploying in a production environment.
