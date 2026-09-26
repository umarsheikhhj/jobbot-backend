import asyncio
import firebase_admin
from firebase_admin import credentials, firestore
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
import os

# Import the bot logic from your bot.py file
from bot import run_job_bot 

# ---------------------------------------------------------
# INITIALIZE FIREBASE
# ---------------------------------------------------------
# The path must exactly match the filename since they are in the same folder now
cred = credentials.Certificate("serviceAccountKey.json")
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
                
                role = job_data.get('role', '')
                location = job_data.get('location', '')
                email = job_data.get('email', '')
                password = job_data.get('password', '')
                resume_link = job_data.get('resume', '')
                
                print(f"\n[+] Found new job {job_id} for {role} in {location}")
                
                # Mark as 'in_progress'
                db.collection('job_commands').document(job_id).update({'status': 'in_progress'})
                
                # Trigger the Playwright bot
                success = await run_job_bot(role, location, email, password, resume_link)
                
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

# ---------------------------------------------------------
# DUMMY WEB SERVER (Tricks Render into keeping the free tier alive)
# ---------------------------------------------------------
def run_dummy_server():
    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"Bot is alive!")
    
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(('0.0.0.0', port), Handler)
    print(f"[*] Dummy web server running on port {port}")
    server.serve_forever()

if __name__ == "__main__":
    # Start the dummy web server in the background
    threading.Thread(target=run_dummy_server, daemon=True).start()
    # Start the actual database listener
    asyncio.run(listen_for_jobs())
