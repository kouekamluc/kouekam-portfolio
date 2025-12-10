# S3 CORS Configuration Setup

## Problem
Your CSS file is being blocked by CORS policy when loaded from S3. The browser shows:
```
Access to CSS stylesheet at 'https://kouekam-hub-assets.s3.eu-north-1.amazonaws.com/static/css/output.css' 
from origin 'https://kouekamkamgou.uk' has been blocked by CORS policy: 
No 'Access-Control-Allow-Origin' header is present on the requested resource.
```

## Solution: Configure CORS on S3 Bucket

### Option 1: AWS Console (Easiest)

1. **Go to AWS Console**
   - Navigate to: https://console.aws.amazon.com/s3/
   - Select your bucket: `kouekam-hub-assets`

2. **Open Permissions Tab**
   - Click on the "Permissions" tab
   - Scroll down to "Cross-origin resource sharing (CORS)"

3. **Edit CORS Configuration**
   - Click "Edit"
   - Paste the following JSON configuration:

```json
[
    {
        "AllowedHeaders": [
            "*"
        ],
        "AllowedMethods": [
            "GET",
            "HEAD"
        ],
        "AllowedOrigins": [
            "https://kouekamkamgou.uk",
            "https://www.kouekamkamgou.uk",
            "http://localhost:8000",
            "http://127.0.0.1:8000"
        ],
        "ExposeHeaders": [
            "ETag",
            "Content-Length",
            "Content-Type"
        ],
        "MaxAgeSeconds": 3000
    }
]
```

4. **Save Changes**
   - Click "Save changes"
   - Wait a few seconds for the changes to propagate

5. **Test**
   - Clear your browser cache (Ctrl+Shift+Delete or Cmd+Shift+Delete)
   - Hard refresh the page (Ctrl+F5 or Cmd+Shift+R)
   - The CSS should now load properly!

### Option 2: AWS CLI (If you have it installed)

If you have AWS CLI configured, you can run:

```bash
aws s3api put-bucket-cors \
    --bucket kouekam-hub-assets \
    --cors-configuration file://s3-cors-config.json
```

### Option 3: Using boto3 (Python)

If you prefer to configure it programmatically, you can use this Python script:

```python
import boto3
import json

s3_client = boto3.client('s3',
    aws_access_key_id='YOUR_ACCESS_KEY',
    aws_secret_access_key='YOUR_SECRET_KEY',
    region_name='eu-north-1'
)

cors_configuration = [
    {
        "AllowedHeaders": ["*"],
        "AllowedMethods": ["GET", "HEAD"],
        "AllowedOrigins": [
            "https://kouekamkamgou.uk",
            "https://www.kouekamkamgou.uk",
            "http://localhost:8000",
            "http://127.0.0.1:8000"
        ],
        "ExposeHeaders": ["ETag", "Content-Length", "Content-Type"],
        "MaxAgeSeconds": 3000
    }
]

s3_client.put_bucket_cors(
    Bucket='kouekam-hub-assets',
    CORSConfiguration={'CORSRules': cors_configuration}
)

print("CORS configuration updated successfully!")
```

## Verification

After configuring CORS, you can verify it's working by:

1. **Check the response headers** in browser DevTools:
   - Open Network tab
   - Find the `output.css` request
   - Look for `Access-Control-Allow-Origin` header in the response

2. **Test the endpoint directly**:
   ```bash
   curl -H "Origin: https://kouekamkamgou.uk" \
        -H "Access-Control-Request-Method: GET" \
        -X OPTIONS \
        https://kouekam-hub-assets.s3.eu-north-1.amazonaws.com/static/css/output.css \
        -v
   ```

## Notes

- CORS changes can take a few seconds to propagate
- Make sure to clear browser cache after making changes
- The `AllowedOrigins` includes your production domain and localhost for development
- `MaxAgeSeconds: 3000` means browsers will cache the CORS preflight response for 50 minutes

