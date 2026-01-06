# Update S3 Bucket Policy for Media Files

Your current bucket policy only allows public access to `static/*` files. You need to add a statement for `media/*` files.

## Current Policy (What you have now)

```json
{
	"Version": "2012-10-17",
	"Statement": [
		{
			"Sid": "PublicReadGetObject",
			"Effect": "Allow",
			"Principal": "*",
			"Action": "s3:GetObject",
			"Resource": "arn:aws:s3:::kouekam-hub-assets/static/*"
		}
	]
}
```

## Updated Policy (What you need)

Replace your entire bucket policy with this:

```json
{
	"Version": "2012-10-17",
	"Statement": [
		{
			"Sid": "PublicReadGetObjectStatic",
			"Effect": "Allow",
			"Principal": "*",
			"Action": "s3:GetObject",
			"Resource": "arn:aws:s3:::kouekam-hub-assets/static/*"
		},
		{
			"Sid": "PublicReadGetObjectMedia",
			"Effect": "Allow",
			"Principal": "*",
			"Action": "s3:GetObject",
			"Resource": "arn:aws:s3:::kouekam-hub-assets/media/*"
		}
	]
}
```

## Steps to Update

1. **Go to AWS S3 Console**
   - Navigate to: https://console.aws.amazon.com/s3/
   - Click on your bucket: `kouekam-hub-assets`

2. **Edit Bucket Policy**
   - Click the "Permissions" tab
   - Scroll to "Bucket policy"
   - Click "Edit"

3. **Replace the Policy**
   - Delete the entire existing policy
   - Paste the updated policy above (with both statements)
   - Click "Save changes"

4. **Verify**
   - After saving, your images should be accessible
   - Test by visiting an image URL directly:
     ```
     https://kouekam-hub-assets.s3.eu-north-1.amazonaws.com/media/profile_photos/your-image.jpg
     ```

## What Changed

- Added a second statement for `media/*` files
- Changed the first statement's Sid from "PublicReadGetObject" to "PublicReadGetObjectStatic" for clarity
- Both statements now allow public read access to their respective paths

## Security Note

This makes all files in the `media/` folder publicly readable. This is necessary for profile photos and project images to display on your website. If you need to keep some media files private, you'll need a more complex policy or use signed URLs.



