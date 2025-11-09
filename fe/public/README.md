# Public Assets

Thư mục này chứa các file tĩnh được phục vụ trực tiếp bởi Vite.

## Face-API.js Models

Để game CV hoạt động, cần tải các model files của face-api.js vào thư mục `models/`:

1. Tạo thư mục: `fe/public/models/`
2. Tải các file từ: https://github.com/justadudewhohacks/face-api.js/tree/master/weights

Hoặc chạy script tự động (nếu có Node.js):
```bash
node download-models.js
```

## Các file cần tải

- `tiny_face_detector_model-weights_manifest.json`
- `tiny_face_detector_model-shard1`
- `face_landmark_68_model-weights_manifest.json`
- `face_landmark_68_model-shard1`
- `face_recognition_model-weights_manifest.json`
- `face_recognition_model-shard1`
- `face_recognition_model-shard2`
- `face_expression_model-weights_manifest.json`
- `face_expression_model-shard1`

