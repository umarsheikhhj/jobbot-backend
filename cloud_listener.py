import asyncio
import firebase_admin
from firebase_admin import credentials, firestore

# Import the bot logic from your bot.py file
from bot import run_job_bot 

# ---------------------------------------------------------
# INITIALIZE FIREBASE
# ---------------------------------------------------------
# Replace 'path/to/serviceAccountKey.json' with your actual Firebase key file path
cred = credentials.Certificate("path/to/serviceAccountKey.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

# ---------------------------------------------------------
# THE CLOUD LISTENER (QUEUE MANAGER)
# ---------------------------------------------------------
async def listen_for_jobs():
    print("[*] Listening for new job requests from FlutterFlow...")
    
    while True:
        try:
            # Query Firebase for any documents where status is 'pending'
            docs = db.collection('job_commands').where('status', '==', 'pending').stream()
            
            for doc in docs:
                job_id = doc.id
                job_data = doc.to_dict()
                
                # Extract the fields from your database
                role = job_data.get('role', '')
                location = job_data.get('location', '')
                email = job_data.get('email', '')
                password = job_data.get('password', '')
                resume_link = job_data.get('resume', '')
                
                print(f"\n[+] Found new job {job_id} for {role} in {location}")
                
                # Mark as 'in_progress' so the queue doesn't process it twice
                db.collection('job_commands').document(job_id).update({'status': 'in_progress'})
                
                # Trigger the Playwright bot with the email and password
                success = await run_job_bot(role, location, email, password, resume_link)
                
                # Update final status in FlutterFlow based on execution result
                if success:
                    db.collection('job_commands').document(job_id).update({'status': 'completed'})
                    print(f"[+] Job {job_id} marked as completed.\n")
                else:
                    db.collection('job_commands').document(job_id).update({'status': 'failed'})
                    print(f"[-] Job {job_id} marked as failed.\n")
                    
        except Exception as e:
            print(f"[-] Database listening error: {e}")
            
        # Wait 10 seconds before polling the database again
        await asyncio.sleep(10)

# Run the listener loop
if __name__ == "__main__":
    asyncio.run(listen_for_jobs())