# 🎥 Professional Video Quiz Application

A modern, full-stack video quiz application built with Django REST Framework and React. Features real-time progress tracking, professional certificate generation, and a clean, event-driven architecture.

## ✨ Key Features

### 🎯 Core Functionality
- **Video-Based Learning**: Interactive video content with embedded quizzes
- **Real-Time Progress Tracking**: Live dashboard updates without page refreshes
- **Professional Certificates**: PDF certificate generation and download
- **User Management**: Complete authentication and profile management
- **Smart Ribbon System**: Visual progress indicators (COMPLETED, FAILED, NEXT UP, LOCKED)

### 🚀 Technical Highlights
- **Event-Driven Architecture**: No manual refresh buttons or polling
- **Professional UI/UX**: Clean, modern interface with Tailwind CSS
- **Responsive Design**: Works seamlessly on desktop and mobile
- **JWT Authentication**: Secure token-based authentication
- **Dynamic Progress Calculation**: Real-time progress updates
- **Error Handling**: Graceful error management throughout the app

## 🏗️ Architecture

```
video_quiz_app/
├── backend/               # Django REST API
│   ├── video_quiz_project/    # Main Django project
│   ├── users/                 # User management & authentication
│   ├── videos/                # Video content management
│   ├── quizzes/               # Quiz logic & questions
│   └── manage.py
├── frontend/              # React SPA
│   ├── src/
│   │   ├── components/        # Reusable UI components
│   │   ├── pages/             # Page components
│   │   ├── contexts/          # React contexts (Auth, AppState)
│   │   ├── services/          # API service layer
│   │   └── utils/             # Helper utilities
│   └── public/
└── media/                 # Video files storage
```

## 🛠️ Technology Stack

### Backend
- **Django 4.2+** - Web framework
- **Django REST Framework** - API framework
- **JWT Authentication** - Token-based auth
- **SQLite** - Database (easily configurable for PostgreSQL/MySQL)
- **Python 3.8+** - Programming language

### Frontend
- **React 18** - Frontend framework
- **React Router** - Client-side routing
- **Tailwind CSS** - Utility-first CSS framework
- **Axios** - HTTP client
- **Context API** - State management

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Node.js 16+
- npm or yarn

### Backend Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/satish030587/video_quiz_app.git
   cd video_quiz_app
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   
   # macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run database migrations**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

5. **Create superuser (optional)**
   ```bash
   python manage.py createsuperuser
   ```

6. **Start development server**
   ```bash
   python manage.py runserver
   ```

The Django API will be available at `http://localhost:8000`

### Frontend Setup

1. **Navigate to frontend directory**
   ```bash
   cd frontend
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Start development server**
   ```bash
   npm start
   ```

The React app will be available at `http://localhost:3001`

## 📱 Usage

### For Students
1. **Register/Login** - Create an account or sign in
2. **Watch Videos** - View educational content
3. **Take Quizzes** - Complete quizzes after watching videos
4. **Track Progress** - Monitor your learning journey on the dashboard
5. **Earn Certificates** - Generate and download completion certificates

### For Administrators
1. **Admin Panel** - Access Django admin at `/admin`
2. **Manage Content** - Add/edit videos and quiz questions
3. **User Management** - Monitor user progress and activities
4. **Content Control** - Enable/disable videos and manage quiz settings

## 🔧 Configuration

### Environment Variables
Create a `.env` file in the project root:

```env
# Django Settings
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database (optional - defaults to SQLite)
DATABASE_URL=sqlite:///db.sqlite3

# Frontend URL (for CORS)
FRONTEND_URL=http://localhost:3001
```

### Video Storage
- Place video files in the `media/videos/` directory
- Supported formats: MP4, WebM, OGV
- Videos are automatically served by Django

## 🎨 Features in Detail

### Real-Time Dashboard
- **Event-Driven Updates**: No page refreshes needed
- **Smart Caching**: Efficient data management
- **Visual Progress**: Ribbon system shows status at a glance
- **Responsive Design**: Works on all screen sizes

### Quiz System
- **Timed Quizzes**: Configurable time limits
- **Multiple Attempts**: Allow retry with limits
- **Auto-Save**: Progress saved automatically
- **Immediate Feedback**: Instant results after completion

### Certificate Generation
- **Professional Design**: Clean, printable certificates
- **Unique IDs**: Each certificate has a unique identifier
- **PDF Download**: High-quality PDF generation
- **Automatic Eligibility**: Based on completion criteria

## 🔐 Security Features

- **JWT Authentication**: Secure token-based auth
- **CORS Protection**: Configured for frontend domain
- **Input Validation**: Comprehensive data validation
- **Error Handling**: Secure error responses
- **File Upload Security**: Protected media serving

## 📊 API Documentation

### Authentication Endpoints
```
POST /api/auth/token/          # Login
POST /api/auth/users/register/ # Register
GET  /api/auth/users/me/       # Get current user
PUT  /api/auth/users/me/       # Update profile
```

### Video & Quiz Endpoints
```
GET  /api/videos/              # List all videos
GET  /api/videos/{id}/         # Get video details
GET  /api/quizzes/questions/{video_id}/ # Get quiz questions
POST /api/quizzes/submit/      # Submit quiz answers
```

### Progress & Certificates
```
GET  /api/auth/progress/my_progress/    # Get user progress
GET  /api/certificates/                # List certificates
POST /api/certificates/generate/       # Generate certificate
```

## 🧪 Testing

### Backend Tests
```bash
python manage.py test
```

### Frontend Tests
```bash
cd frontend
npm test
```

## 📦 Deployment

### Backend (Django)
1. **Configure production settings**
2. **Set up database** (PostgreSQL recommended)
3. **Configure static files** with WhiteNoise or CDN
4. **Set environment variables**
5. **Deploy to platform** (Heroku, DigitalOcean, AWS, etc.)

### Frontend (React)
1. **Build production version**
   ```bash
   npm run build
   ```
2. **Deploy static files** to CDN or hosting service
3. **Configure API endpoints** for production

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with modern web technologies
- Inspired by online learning platforms
- Focus on user experience and performance

## 📞 Support

For support, email: [your-email@example.com] or create an issue in the GitHub repository.

---

## 🎯 Project Status

✅ **Completed Features:**
- User authentication and profile management
- Video content management
- Quiz system with timer and auto-save
- Real-time progress tracking
- Professional certificate generation
- Responsive UI with modern design
- Event-driven architecture (no manual refreshes)

🚀 **Ready for Production**

---

*Last updated: July 30, 2025*
