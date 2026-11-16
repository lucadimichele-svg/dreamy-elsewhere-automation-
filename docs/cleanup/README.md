# Cleanup: deliberately disabled until verified

We want no long-term photo buildup in Google Drive.

Current safe design:
1. ChatGPT scheduled image task stores five images in the exact project
   `incoming/YYYY-MM-DD_SX` folder.
2. GitHub imports them and renders a Reel.
3. A **separate** publishing owner queues and verifies the Reel.
4. After confirmed public delivery (not just Buffer "scheduled") the
   source folder may be moved to `used/`.
5. At least 24 hours later, the five images and their slot folder may be
   deleted by a separate restricted Drive cleanup job.

Never delete from any non-Dreamy Drive folder. Never delete while a job is
pending, queued, failed or not independently verified on Instagram.

**Cleanup is not yet enabled**: automatic verification of actual Instagram
delivery and Drive folder-ID tracking are still outstanding.
