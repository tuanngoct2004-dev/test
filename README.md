# Sky Runner

Trò chơi lái máy bay đơn giản viết bằng Python và thư viện `pygame`.

## Cài đặt

1. Tạo môi trường ảo (khuyến khích):
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # Trên Windows dùng `.venv\\Scripts\\activate`
   ```
2. Cài các phụ thuộc:
   ```bash
   pip install -r requirements.txt
   ```

## Chạy trò chơi

```bash
python plane_game.py
```

## Cách chơi

- Di chuyển máy bay bằng các phím mũi tên hoặc WASD.
- Tránh va chạm với máy bay địch màu đỏ.
- Thu thập các bình nhiên liệu màu vàng để tăng điểm.
- Trò chơi sẽ tăng độ khó theo thời gian. Khi hết năng lượng, nhấn `Enter` để chơi lại hoặc `Esc` để thoát.
