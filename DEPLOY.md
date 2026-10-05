# Deploy StoryMap Việt Nam to the Internet

## GitHub
1. Create a new repository, e.g. `storymap-vietnam`.
2. Upload all files in this folder (not the parent folder itself).
3. Do not upload `.venv`, `storymap.db`, or private secrets.

## Render
1. Create an account at Render and connect GitHub.
2. New -> Web Service -> select the repository.
3. Build Command: `pip install -r requirements.txt`
4. Start Command: `gunicorn app:app`
5. Add `SECRET_KEY` as a secret (Render can generate it).
6. Deploy.

The site will get an HTTPS `onrender.com` URL. The free web service may sleep after inactivity.

## Important storage note
This MVP uses SQLite and a local `uploads/` directory. On cloud hosting with ephemeral storage, data/files are not a safe permanent store. For a real public launch, move the database to PostgreSQL and media to object storage (S3-compatible/Supabase Storage/Cloudinary, etc.) before inviting many users.
