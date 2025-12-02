# Hướng dẫn sử dụng Node.js version cho project này

Project này yêu cầu **Node.js >= 20.19.0** (do Vite 7.2.2 yêu cầu).

## Cách 1: Sử dụng script tự động (Khuyến nghị)

1. Mở PowerShell trong thư mục `fe`
2. Chạy lệnh:
   ```powershell
   .\use-node-version.ps1
   ```
   hoặc
   ```powershell
   powershell -ExecutionPolicy Bypass -File .\use-node-version.ps1
   ```

Script sẽ tự động:
- Kiểm tra Node.js 20.19.0 đã được cài chưa
- Nếu chưa có, sẽ tự động cài đặt
- Chuyển sang version đó cho terminal hiện tại

## Cách 2: Sử dụng nvm thủ công

1. Cài Node.js 20.19.0 (nếu chưa có):
   ```powershell
   nvm install 20.19.0
   ```

2. Chuyển sang version đó:
   ```powershell
   nvm use 20.19.0
   ```

3. Kiểm tra version:
   ```powershell
   node --version
   ```

## Cách 3: Tự động chuyển khi vào thư mục (PowerShell Profile)

Thêm vào PowerShell profile (`$PROFILE`):

```powershell
function Set-NodeVersion {
    if (Test-Path ".nvmrc") {
        $version = Get-Content ".nvmrc" -Raw | ForEach-Object { $_.Trim() }
        nvm use $version 2>$null
    }
}

# Tự động chạy khi cd vào thư mục có .nvmrc
function cd {
    param([string]$path)
    Set-Location $path
    Set-NodeVersion
}
```

## Lưu ý

- **Version chỉ áp dụng cho terminal hiện tại** - mỗi terminal mới cần chạy lại `nvm use`
- **Các project khác không bị ảnh hưởng** - nvm chỉ thay đổi version cho terminal hiện tại
- Để quay lại Node.js 18.20.2 cho project khác, chỉ cần chạy: `nvm use 18.20.2`

## Kiểm tra version hiện tại

```powershell
node --version
```

