🔥 Task #13 — File Sharing System (FastAPI + In-Memory)
You're building a secure temporary file sharing system. Users can upload a file, get a shareable link (with a UUID), and others can download the file using that link — but only once.

📦 Requirements
✅ 1. Upload File

Authenticated users can upload a file (multipart/form-data).
File is saved in memory (simulate with a dictionary: {uuid: {file: ..., owner: ..., downloaded: False}})
Return a unique download link like: /files/download/{uuid}
✅ 2. Download File

Anyone (no auth) can download the file with the UUID.
Once downloaded, mark it as downloaded: True and block any further access to that link.
If the link is reused, return 410 Gone.
✅ 3. List Uploaded Files (Owner only)

Authenticated user can view a list of their uploaded files with:
UUID
filename
download status
✅ 4. Security

Files can only be listed by the uploader.
Download is anonymous, but only works once.
💾 Simulated "Storage"
Use this structure for in-memory file simulation:

file_storage = {
    uuid_str: {
        "filename": "example.txt",
        "content": b"...",
        "owner": "username",
        "downloaded": False
    }
}
🎯 Bonuses (Optional)
Add an expiry (file auto-invalid after X minutes).
Add file size limit (e.g., <5MB).