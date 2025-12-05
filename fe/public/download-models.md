# Hướng dẫn tải Face-API.js Models

Game CV cần các model files của face-api.js để nhận diện cảm xúc.

## Cách 1: Tải tự động (Khuyến nghị)

1. Tạo thư mục `models` trong thư mục `fe/public/`:
   ```
   fe/public/models/
   ```

2. Tải các file model từ GitHub:
   - Truy cập: https://github.com/justadudewhohacks/face-api.js/tree/master/weights
   - Tải các file sau:
     - `tiny_face_detector_model-weights_manifest.json`
     - `tiny_face_detector_model-shard1`
     - `face_landmark_68_model-weights_manifest.json`
     - `face_landmark_68_model-shard1`
     - `face_recognition_model-weights_manifest.json`
     - `face_recognition_model-shard1`
     - `face_recognition_model-shard2`
     - `face_expression_model-weights_manifest.json`
     - `face_expression_model-shard1`

3. Đặt tất cả các file vào thư mục `fe/public/models/`

## Cách 2: Sử dụng CDN (Tự động)

Game sẽ tự động thử tải từ CDN nếu không tìm thấy models trong thư mục local.

## Kiểm tra

Sau khi tải models, khởi động lại frontend và kiểm tra console browser. Nếu thấy "Face-api.js models loaded successfully" thì đã thành công.

