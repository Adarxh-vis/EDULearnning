from flask import Flask
from config import Config
from extensions import mongo
from modles.course import Course
from bson import ObjectId

app = Flask(__name__)
app.config.from_object(Config)
mongo.init_app(app)

sample_courses = [
    {
        "_id": "101",
        "title": "Introduction to Machine Learning",
        "description": "Learn the fundamentals of machine learning algorithms and applications",
        "category": "Data Science",
        "instructor": "Dr. Emily Chen",
        "price": 79.99,
        "isPublished": True,
        "courseId": "101",
        "modules": [
            {
                "id": "module1",
                "title": "What is Machine Learning?",
                "lessons": [
                    {
                        "id": "lesson1",
                        "title": "ML Overview",
                        "videoUrl": "https://www.youtube.com/embed/ukzFI9rgwfU",
                        "duration": "18:45",
                        "completed": False
                    },
                    {
                        "id": "lesson2",
                        "title": "Types of ML",
                        "videoUrl": "https://www.youtube.com/embed/4E1JiDFxFGk",
                        "duration": "22:30",
                        "completed": False
                    }
                ]
            },
            {
                "id": "module2",
                "title": "Supervised Learning",
                "lessons": [
                    {
                        "id": "lesson3",
                        "title": "Linear Regression",
                        "videoUrl": "https://www.youtube.com/embed/nk2CQITm_eo",
                        "duration": "25:15",
                        "completed": False
                    },
                    {
                        "id": "lesson4",
                        "title": "Logistic Regression",
                        "videoUrl": "https://www.youtube.com/embed/yIYKR4sgzI8",
                        "duration": "20:40",
                        "completed": False
                    }
                ]
            }
        ]
    },
    {
        "_id": "102",
        "title": "Advanced React Development",
        "description": "Master advanced React concepts including hooks, context, and performance optimization",
        "category": "Web Development",
        "instructor": "Alex Rodriguez",
        "price": 89.99,
        "isPublished": True,
        "courseId": "102",
        "modules": [
            {
                "id": "module1",
                "title": "React Hooks Deep Dive",
                "lessons": [
                    {
                        "id": "lesson1",
                        "title": "useState and useEffect",
                        "videoUrl": "https://www.youtube.com/embed/0ZJgIjIuY7U",
                        "duration": "28:20",
                        "completed": False
                    },
                    {
                        "id": "lesson2",
                        "title": "Custom Hooks",
                        "videoUrl": "https://www.youtube.com/embed/6ThXsUwLWvc",
                        "duration": "24:15",
                        "completed": False
                    }
                ]
            },
            {
                "id": "module2",
                "title": "Performance Optimization",
                "lessons": [
                    {
                        "id": "lesson3",
                        "title": "React.memo and useMemo",
                        "videoUrl": "https://www.youtube.com/embed/DEPwA3mv_R8",
                        "duration": "19:50",
                        "completed": False
                    },
                    {
                        "id": "lesson4",
                        "title": "Code Splitting",
                        "videoUrl": "https://www.youtube.com/embed/zUEZ2vK9Vpk",
                        "duration": "21:35",
                        "completed": False
                    }
                ]
            }
        ]
    },
    {
        "_id": "103",
        "title": "Cybersecurity Fundamentals",
        "description": "Learn essential cybersecurity concepts and best practices",
        "category": "Security",
        "instructor": "Marcus Thompson",
        "price": 69.99,
        "isPublished": True,
        "courseId": "103",
        "modules": [
            {
                "id": "module1",
                "title": "Introduction to Cybersecurity",
                "lessons": [
                    {
                        "id": "lesson1",
                        "title": "What is Cybersecurity?",
                        "videoUrl": "https://www.youtube.com/embed/inWWhr5tnEA",
                        "duration": "16:30",
                        "completed": False
                    },
                    {
                        "id": "lesson2",
                        "title": "Common Threats",
                        "videoUrl": "https://www.youtube.com/embed/9v9vKQ2Z0Ks",
                        "duration": "20:45",
                        "completed": False
                    }
                ]
            },
            {
                "id": "module2",
                "title": "Network Security",
                "lessons": [
                    {
                        "id": "lesson3",
                        "title": "Firewalls and VPNs",
                        "videoUrl": "https://www.youtube.com/embed/5TNWCqN0V8E",
                        "duration": "23:10",
                        "completed": False
                    },
                    {
                        "id": "lesson4",
                        "title": "Encryption Basics",
                        "videoUrl": "https://www.youtube.com/embed/NuyzuNBFWxQ",
                        "duration": "18:25",
                        "completed": False
                    }
                ]
            }
        ]
    },
    {
        "_id": "104",
        "title": "Mobile App Development with Flutter",
        "description": "Build cross-platform mobile apps using Flutter and Dart",
        "category": "Mobile Development",
        "instructor": "Lisa Wang",
        "price": 74.99,
        "isPublished": True,
        "courseId": "104",
        "modules": [
            {
                "id": "module1",
                "title": "Flutter Basics",
                "lessons": [
                    {
                        "id": "lesson1",
                        "title": "Getting Started with Flutter",
                        "videoUrl": "https://www.youtube.com/embed/x0uinJvhNxI",
                        "duration": "21:40",
                        "completed": False
                    },
                    {
                        "id": "lesson2",
                        "title": "Dart Programming",
                        "videoUrl": "https://www.youtube.com/embed/Ej_Pcr4uC2Q",
                        "duration": "26:15",
                        "completed": False
                    }
                ]
            },
            {
                "id": "module2",
                "title": "Building UI Components",
                "lessons": [
                    {
                        "id": "lesson3",
                        "title": "Widgets and Layouts",
                        "videoUrl": "https://www.youtube.com/embed/1ukrFxPVA8U",
                        "duration": "29:20",
                        "completed": False
                    },
                    {
                        "id": "lesson4",
                        "title": "State Management",
                        "videoUrl": "https://www.youtube.com/embed/4v6vWy5UYkE",
                        "duration": "24:50",
                        "completed": False
                    }
                ]
            }
        ]
    },
    {
        "_id": "105",
        "title": "Cloud Computing with AWS",
        "description": "Master Amazon Web Services and cloud architecture",
        "category": "Cloud Computing",
        "instructor": "David Kumar",
        "price": 94.99,
        "isPublished": True,
        "courseId": "105",
        "modules": [
            {
                "id": "module1",
                "title": "AWS Fundamentals",
                "lessons": [
                    {
                        "id": "lesson1",
                        "title": "Introduction to AWS",
                        "videoUrl": "https://www.youtube.com/embed/k1RI5locZE4",
                        "duration": "19:35",
                        "completed": False
                    },
                    {
                        "id": "lesson2",
                        "title": "EC2 Instances",
                        "videoUrl": "https://www.youtube.com/embed/mMQ-YcNYOHY",
                        "duration": "27:40",
                        "completed": False
                    }
                ]
            },
            {
                "id": "module2",
                "title": "Storage and Databases",
                "lessons": [
                    {
                        "id": "lesson3",
                        "title": "S3 and CloudFront",
                        "videoUrl": "https://www.youtube.com/embed/6ELuVOzCdS4",
                        "duration": "22:55",
                        "completed": False
                    },
                    {
                        "id": "lesson4",
                        "title": "RDS and DynamoDB",
                        "videoUrl": "https://www.youtube.com/embed/8KkE8H6VcBM",
                        "duration": "25:30",
                        "completed": False
                    }
                ]
            }
        ]
    },
    {
        "_id": "python101",
        "title": "Python Programming Fundamentals",
        "description": "Learn the basics of Python programming from scratch",
        "category": "Programming",
        "instructor": "John Smith",
        "price": 49.99,
        "isPublished": True,
        "courseId": "python101",
        "modules": [
            {
                "id": "module1",
                "title": "Getting Started with Python",
                "lessons": [
                    {
                        "id": "lesson1",
                        "title": "Introduction to Python",
                        "videoUrl": "https://www.youtube.com/embed/rfscVS0vtbw",
                        "duration": "15:30",
                        "completed": False
                    },
                    {
                        "id": "lesson2",
                        "title": "Installing Python",
                        "videoUrl": "https://www.youtube.com/embed/9o4gDQvVkLU",
                        "duration": "12:45",
                        "completed": False
                    },
                    {
                        "id": "lesson3",
                        "title": "Your First Python Program",
                        "videoUrl": "https://www.youtube.com/embed/kqtD5dpn9C8",
                        "duration": "18:20",
                        "completed": False
                    }
                ]
            },
            {
                "id": "module2",
                "title": "Variables and Data Types",
                "lessons": [
                    {
                        "id": "lesson4",
                        "title": "Understanding Variables",
                        "videoUrl": "https://www.youtube.com/embed/Z1Yd7upQsXY",
                        "duration": "14:15",
                        "completed": False
                    },
                    {
                        "id": "lesson5",
                        "title": "Data Types in Python",
                        "videoUrl": "https://www.youtube.com/embed/gCCVsvgR2KU",
                        "duration": "16:40",
                        "completed": False
                    },
                    {
                        "id": "lesson6",
                        "title": "Type Conversion",
                        "videoUrl": "https://www.youtube.com/embed/2WFNjqp7YVo",
                        "duration": "11:25",
                        "completed": False
                    }
                ]
            }
        ]
    },
    {
        "_id": "javascript101",
        "title": "JavaScript for Beginners",
        "description": "Master JavaScript fundamentals and build interactive web applications",
        "category": "Web Development",
        "instructor": "Sarah Johnson",
        "price": 59.99,
        "isPublished": True,
        "courseId": "javascript101",
        "modules": [
            {
                "id": "module1",
                "title": "JavaScript Basics",
                "lessons": [
                    {
                        "id": "lesson1",
                        "title": "What is JavaScript?",
                        "videoUrl": "https://www.youtube.com/embed/W6NZfCO5SIk",
                        "duration": "13:45",
                        "completed": False
                    },
                    {
                        "id": "lesson2",
                        "title": "Variables and Constants",
                        "videoUrl": "https://www.youtube.com/embed/81G0dXkagpQ",
                        "duration": "17:30",
                        "completed": False
                    },
                    {
                        "id": "lesson3",
                        "title": "Data Types",
                        "videoUrl": "https://www.youtube.com/embed/7bQMgvQaH0I",
                        "duration": "19:15",
                        "completed": False
                    }
                ]
            },
            {
                "id": "module2",
                "title": "Functions and Objects",
                "lessons": [
                    {
                        "id": "lesson4",
                        "title": "Creating Functions",
                        "videoUrl": "https://www.youtube.com/embed/C5FEA7LsaZ8",
                        "duration": "21:10",
                        "completed": False
                    },
                    {
                        "id": "lesson5",
                        "title": "Objects and Arrays",
                        "videoUrl": "https://www.youtube.com/embed/oSQ8x3l5Wq8",
                        "duration": "24:35",
                        "completed": False
                    }
                ]
            }
        ]
    },
    {
        "_id": "webdev101",
        "title": "Web Development Fundamentals",
        "description": "Learn HTML, CSS, and JavaScript to build modern websites",
        "category": "Web Development",
        "instructor": "Mike Davis",
        "price": 69.99,
        "isPublished": True,
        "courseId": "webdev101",
        "modules": [
            {
                "id": "module1",
                "title": "HTML Basics",
                "lessons": [
                    {
                        "id": "lesson1",
                        "title": "Introduction to HTML",
                        "videoUrl": "https://www.youtube.com/embed/UB1O30fR-EE",
                        "duration": "16:20",
                        "completed": False
                    },
                    {
                        "id": "lesson2",
                        "title": "HTML Structure",
                        "videoUrl": "https://www.youtube.com/embed/0iqz4tcKN58",
                        "duration": "14:50",
                        "completed": False
                    }
                ]
            },
            {
                "id": "module2",
                "title": "CSS Styling",
                "lessons": [
                    {
                        "id": "lesson3",
                        "title": "CSS Fundamentals",
                        "videoUrl": "https://www.youtube.com/embed/yfoY53QXEnI",
                        "duration": "22:15",
                        "completed": False
                    },
                    {
                        "id": "lesson4",
                        "title": "CSS Layout",
                        "videoUrl": "https://www.youtube.com/embed/tXIhdp5R7sc",
                        "duration": "25:40",
                        "completed": False
                    }
                ]
            }
        ]
    }
]

with app.app_context():
    try:
        # Clear existing courses
        mongo.db.courses.delete_many({})

        # Insert sample courses
        for course_data in sample_courses:
            course_id = course_data["_id"]
            course_data["_id"] = ObjectId()
            mongo.db.courses.insert_one(course_data)
            print(f"Inserted course: {course_id}")

        print("Sample courses created successfully!")

    except Exception as e:
        print(f"Error creating sample courses: {e}")
