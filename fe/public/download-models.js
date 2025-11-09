/**
 * Script để tải face-api.js models tự động
 * Chạy script này trong Node.js để tải models về thư mục public/models
 */

const https = require('https');
const fs = require('fs');
const path = require('path');

const MODELS_DIR = path.join(__dirname, 'models');
const BASE_URL = 'https://raw.githubusercontent.com/justadudewhohacks/face-api.js/master/weights';

const models = [
    'tiny_face_detector_model-weights_manifest.json',
    'tiny_face_detector_model-shard1',
    'face_landmark_68_model-weights_manifest.json',
    'face_landmark_68_model-shard1',
    'face_recognition_model-weights_manifest.json',
    'face_recognition_model-shard1',
    'face_recognition_model-shard2',
    'face_expression_model-weights_manifest.json',
    'face_expression_model-shard1'
];

// Tạo thư mục models nếu chưa có
if (!fs.existsSync(MODELS_DIR)) {
    fs.mkdirSync(MODELS_DIR, { recursive: true });
    console.log('Đã tạo thư mục models');
}

function downloadFile(url, filepath) {
    return new Promise((resolve, reject) => {
        const file = fs.createWriteStream(filepath);
        https.get(url, (response) => {
            if (response.statusCode === 200) {
                response.pipe(file);
                file.on('finish', () => {
                    file.close();
                    resolve();
                });
            } else if (response.statusCode === 302 || response.statusCode === 301) {
                // Redirect
                file.close();
                fs.unlinkSync(filepath);
                downloadFile(response.headers.location, filepath).then(resolve).catch(reject);
            } else {
                file.close();
                fs.unlinkSync(filepath);
                reject(new Error(`Failed to download: ${response.statusCode}`));
            }
        }).on('error', (err) => {
            file.close();
            if (fs.existsSync(filepath)) {
                fs.unlinkSync(filepath);
            }
            reject(err);
        });
    });
}

async function downloadModels() {
    console.log('Bắt đầu tải face-api.js models...');
    
    for (const model of models) {
        const url = `${BASE_URL}/${model}`;
        const filepath = path.join(MODELS_DIR, model);
        
        try {
            console.log(`Đang tải: ${model}...`);
            await downloadFile(url, filepath);
            console.log(`✓ Đã tải: ${model}`);
        } catch (error) {
            console.error(`✗ Lỗi khi tải ${model}:`, error.message);
        }
    }
    
    console.log('\nHoàn thành! Models đã được tải vào thư mục:', MODELS_DIR);
}

downloadModels().catch(console.error);

