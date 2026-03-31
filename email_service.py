import smtplib
from email.message import EmailMessage

# --- CONFIGURATION ---
EMAIL_ADDRESS = "tosintestimony9@gmail.com"  # Your Gmail
EMAIL_PASSWORD = "hcgv nxqu kuoa oocx"    # The 16-character code from Step 1
RECEIVER_EMAIL = "adekunleaduragbemi63@gmail.com" # Where you want the workout sent

def send_workout_email(workout_title, workout_url):
    """Sends the daily workout link to your inbox."""
    
    msg = EmailMessage()
    msg['Subject'] = f"🏋️‍♂️ Your Workout for Today: {workout_title}"
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = RECEIVER_EMAIL
    
    # The Body of the Email
    content = f"""
    Hi CyberProto!
    
    Here is your selected workout for today:
    
    🔥 {workout_title}
    🔗 Watch here: {workout_url}
    
    Don't stop when you're tired, stop when you're done!
    """
    msg.set_content(content)

    try:
        # Connect to Gmail's Secure Server (Port 465)
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            smtp.send_message(msg)
        return True
    except Exception as e:
        print(f"Email failed to send: {e}")
        return False

# --- TEST BLOCK ---
if __name__ == "__main__":
    print("Testing Email Service...")
    success = send_workout_email("Test Workout", "https://youtube.com")
    if success:
        print("Email sent! Check your inbox. ✅")