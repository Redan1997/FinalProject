import mysql.connector
from mysql.connector import Error
import time

class ConnectDatabase:
    def __init__(self):
        self._host = "junction.proxy.rlwy.net"
        self._user = "root"
        self._password = "AdGzajmAwcJPccXxoWqeFGAEiQISUGeM"
        self._database = "railway"
        self._port = 22274
        
        self.con = None
        self.cursor = None

    def get_connection(self):
        """Create a new database connection"""
        try:
            connection = mysql.connector.connect(
                host=self._host,
                user=self._user,
                password=self._password,
                database=self._database,
                port=self._port
            )
            return connection
        except Error as e:
            print(f"Error connecting to MySQL database: {e}")
            return None

    def register(self, name, email, password):
        connection = None
        cursor = None
        try:
            connection = self.get_connection()
            if not connection:
                print("Failed to establish database connection")
                return "Database connection failed"

            cursor = connection.cursor(dictionary=True)

            # Check if user exists first
            cursor.execute("SELECT * FROM users WHERE Email = %s", (email,))
            if cursor.fetchone():
                print(f"Email {email} already exists")
                return "Email already exists"

            # Insert new user
            sql = "INSERT INTO users (Name, Email, Password) VALUES (%s, %s, %s)"
            
            try:
                cursor.execute(sql, (name, email, password))
                connection.commit()
                print(f"User {email} registered successfully!")
                return "success"
            except mysql.connector.Error as insert_error:
                print(f"Insert Error Details: Errno: {insert_error.errno}, SQLState: {insert_error.sqlstate}, Msg: {insert_error}")
                connection.rollback()
                return f"Insert error: {insert_error}"

        except mysql.connector.Error as e:
            print(f"MySQL Error Details: Errno: {e.errno}, SQLState: {e.sqlstate}, Msg: {e}")
            if connection:
                connection.rollback()
            return f"Registration error: {e}"
        except Exception as e:
            print(f"Unexpected error during registration: {e}")
            if connection:
                connection.rollback()
            return f"Unexpected error: {e}"
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()

    def login(self, email, password):
        connection = None
        cursor = None
        try:
            connection = self.get_connection()
            if not connection:
                return "Database connection failed"

            cursor = connection.cursor(dictionary=True)

            # Check if user exists
            cursor.execute("SELECT * FROM users WHERE Email = %s", (email,))
            user = cursor.fetchone()

            if not user:
                return "Email does not exist"

            # Verify password
            if user['Password'] == password:
                return "True details"
            else:
                return "Incorrect password"

        except Error as e:
            print(f"Login error: {e}")
            return str(e)
        finally:
            if connection:
                if cursor:
                    cursor.close()
                connection.close()
    
    def get_user_name(self, email):
        connection = None
        cursor = None
        try:
            connection = self.get_connection()  # Get the connection
            if not connection:
                return None  # Return None if connection fails

            cursor = connection.cursor()  # Create the cursor from the connection

            query = "SELECT Name FROM users WHERE Email = %s"
            cursor.execute(query, (email,))
            result = cursor.fetchone()

            return result[0] if result else None

        except Error as e:
            print(f"Error fetching user name: {e}")
            return None
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()
    
    def get_user_id(self, email):
        connection = None
        cursor = None
        try:
            connection = self.get_connection()  # Get the connection
            if not connection:
                return None  # Return None if connection fails

            cursor = connection.cursor()  # Create the cursor from the connection

            query = "SELECT user_id FROM users WHERE Email = %s"
            cursor.execute(query, (email,))
            result = cursor.fetchone()

            return result[0] if result else None

        except Error as e:
            print(f"Error fetching id: {e}")
            return None
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()
    
    # Save visual acuity test result
    def VisualAcuity_save_test_result(self, user_id, right_eye_level, right_eye_incorrect, left_eye_level, left_eye_incorrect, feedback):
        try:
            con = self.get_connection()
            cursor = con.cursor()

            cursor.execute('''
                INSERT INTO visual_acuity(user_id, right_eye_max_level, right_eye_incorrect, left_eye_max_level, left_eye_incorrect, feedback)
                VALUES (%s, %s, %s, %s, %s, %s)
            ''', (user_id, right_eye_level, right_eye_incorrect, left_eye_level, left_eye_incorrect, feedback))

            con.commit()
            con.close()

            return True  # Return True if the operation was successful
        except Exception as e:
            print(f"Error saving to DB: {e}")
            return False  # Return False if an error occurred
        
    def ColorVision_save_test_result(self,user_id,correctAnswers,incorrectAnswers,feedBack):
        try:
            con = self.get_connection()
            cursor = con.cursor()

            cursor.execute('''
                INSERT INTO color_vision(user_id,correct_answers,incorrect_answers,feedback)
                VALUES (%s, %s, %s, %s)
            ''', (user_id,correctAnswers,incorrectAnswers,feedBack))

            con.commit()
            con.close()

            return True  # Return True if the operation was successful
        except Exception as e:
            print(f"Error saving to DB: {e}")
            return False  # Return False if an error occurred
        
    def ContrastVision_save_test_result(self, user_id, score, incorrect_answers, feedback):
        try:
            con = self.get_connection()
            if not con:
                print("Failed to get database connection")
                return False
                
            cursor = con.cursor()
            cursor.execute('''
                INSERT INTO contrast_vision(user_id, score, incorrect_answers, feedback)
                VALUES (%s, %s, %s, %s)
            ''', (user_id, score, incorrect_answers, feedback))

            con.commit()
            return True
            
        except Exception as e:
            print(f"Error saving contrast vision results: {e}")
            if con:
                con.rollback()
            return False
            
        finally:
            if cursor:
                cursor.close()
            if con:
                con.close()

    def BlurCheck_save_test_result(self, user_id, score, incorrect_answers, feedback):
        try:
            con = self.get_connection()
            cursor = con.cursor()

            cursor.execute('''
                INSERT INTO blur_check(user_id, score, incorrect_answers, feedback)
                VALUES (%s, %s, %s, %s)
            ''', (user_id, score, incorrect_answers, feedback))

            con.commit()
            con.close()
            return True
        except Exception as e:
            print(f"Error saving to DB: {e}")
            return False

    def WatchDot_save_test_result(self, user_id, score, incorrect_answers, feedback):
        try:
            con = self.get_connection()
            cursor = con.cursor()

            cursor.execute('''
                INSERT INTO watch_dot(user_id, score, incorrect_answers, feedback)
                VALUES (%s, %s, %s, %s)
            ''', (user_id, score, incorrect_answers, feedback))

            con.commit()
            con.close()
            return True
        except Exception as e:
            print(f"Error saving to DB: {e}")
            return False

    def get_total_tests_count(self, user_id):
        connection = None
        cursor = None
        try:
            connection = self.get_connection()
            if not connection:
                return 0

            cursor = connection.cursor()
            
            # Combined query to count tests from all tables
            query = """
                SELECT COUNT(*) AS total_tests
                FROM (
                    SELECT test_id FROM blur_check WHERE user_id = %s
                    UNION ALL
                    SELECT test_id FROM color_vision WHERE user_id = %s
                    UNION ALL
                    SELECT test_id FROM contrast_vision WHERE user_id = %s
                    UNION ALL
                    SELECT test_id FROM visual_acuity WHERE user_id = %s
                    UNION ALL
                    SELECT test_id FROM watch_dot WHERE user_id = %s
                ) AS all_tests;
            """
            cursor.execute(query, (user_id, user_id, user_id, user_id, user_id))
            return cursor.fetchone()[0]

        except Exception as e:
            print(f"Error getting total tests count: {e}")
            return 0
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()


    def update_profile(self, user_id, username, email):
        connection = None
        cursor = None
        try:
            connection = self.get_connection()
            if not connection:
                return "Database connection failed"
            cursor = connection.cursor(dictionary=True)
            
            # Check if email is already in use by another user
            cursor.execute("SELECT user_id FROM users WHERE Email = %s AND user_id != %s", (email, user_id))
            if cursor.fetchone():
                return "Email already in use"
            # Update user profile
            cursor.execute("UPDATE users SET Name = %s, Email = %s WHERE user_id = %s", 
                        (username, email, user_id))
            connection.commit()
            return "success"
        except Error as e:
            print(f"Profile update error: {e}")
            return str(e)
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()
    def change_password(self, user_id, current_password, new_password):
        connection = None
        cursor = None
        try:
            connection = self.get_connection()
            if not connection:
                return "Database connection failed"
            cursor = connection.cursor(dictionary=True)
            
            # Verify current password
            cursor.execute("SELECT Password FROM users WHERE user_id = %s", (user_id,))
            user = cursor.fetchone()
            
            if not user or user['Password'] != current_password:
                return "Current password is incorrect"
            # Update password
            cursor.execute("UPDATE users SET Password = %s WHERE user_id = %s", 
                        (new_password, user_id))
            connection.commit()
            return "success"
        except Error as e:
            print(f"Password change error: {e}")
            return str(e)
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()
    def delete_account(self, user_id):
        connection = None
        cursor = None
        try:
            connection = self.get_connection()
            if not connection:
                return "Database connection failed"
            cursor = connection.cursor()
            
            # Delete all related records first
            cursor.execute("DELETE FROM visual_acuity WHERE user_id = %s", (user_id,))
            cursor.execute("DELETE FROM color_vision WHERE user_id = %s", (user_id,))
            
            # Delete user account
            cursor.execute("DELETE FROM users WHERE user_id = %s", (user_id,))
            connection.commit()
            return "success"
        except Error as e:
            print(f"Account deletion error: {e}")
            return str(e)
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()


    def test_count(self, user_id):
        connection = None
        cursor = None
        try:
            connection = self.get_connection()
            if not connection:
                return {}

            cursor = connection.cursor()

            # Single query to count tests from all tables
            query = """
                SELECT 'visual_acuity' AS test_name, COUNT(*) AS test_count FROM visual_acuity WHERE user_id = %s
                UNION ALL
                SELECT 'color_vision', COUNT(*) FROM color_vision WHERE user_id = %s
                UNION ALL
                SELECT 'contrast_vision', COUNT(*) FROM contrast_vision WHERE user_id = %s
                UNION ALL
                SELECT 'blur_check', COUNT(*) FROM blur_check WHERE user_id = %s
                UNION ALL
                SELECT 'watch_dot', COUNT(*) FROM watch_dot WHERE user_id = %s
            """
            cursor.execute(query, (user_id, user_id, user_id, user_id, user_id))
            
            # Fetch all results into a dictionary
            results = cursor.fetchall()
            return {row[0]: row[1] for row in results}

        except Exception as e:
            print(f"Error getting test counts: {e}")
            return {}
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()



