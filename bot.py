import logging
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

# --- CẤU HÌNH CỦA BẠN ---
TOKEN = '8779380808:AAFTftaEhJqqAp3Fkd3mDCJZUHDWDEBXkjs' 
ADMIN_ID = 8248041326  # ID của bạn đã được cập nhật
STK = "03034132011"
TEN_NH = "MB"
TEN_CHU_TK = "PHAM DINH LOI"

# Lưu trạng thái khách hàng đang chờ gửi bill
waiting_for_bill = {}

# Hàm tạo link QR động từ VietQR
def get_qr_url(amount, content):
    return f"https://img.vietqr.io/image/{TEN_NH}-{STK}-compact2.jpg?amount={amount}&addInfo={content}"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🟣 Key Fluorite Tây (280k/Tuần)", callback_query_data='f_week')],
        [InlineKeyboardButton("🟣 Key Fluorite Tây (550k/Tháng)", callback_query_data='f_month')],
        [InlineKeyboardButton("Menu DS (70k/Tuần) 📤", callback_query_data='ds_week')],
        [InlineKeyboardButton("Menu DS (150k/Tháng) 📤", callback_query_data='ds_month')],
        [InlineKeyboardButton("💎 Thông tin liên hệ", callback_query_data='info')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    welcome_text = (
        "💎 **DINH LOI STORE** 💎\n\n"
        "Chào mừng bạn! Vui lòng chọn gói cần mua bên dưới để nhận mã thanh toán QR tự động."
    )
    await update.message.reply_text(welcome_text, reply_markup=reply_markup, parse_mode='Markdown')

async def handle_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user = query.from_user
    # Lấy Username hoặc ID nếu khách không có Username
    user_info = user.username if user.username else f"User_{user.id}"
    
    items = {
        'f_week': (280000, "Fluorite_Tuan"),
        'f_month': (550000, "Fluorite_Thang"),
        'ds_week': (70000, "MenuDS_Tuan"),
        'ds_month': (150000, "MenuDS_Thang")
    }

    if query.data in items:
        price, label = items[query.data]
        # Nội dung chuyển khoản tự động
        content = f"{user_info}_{label}"
        qr_image = get_qr_url(price, content)
        
        caption = (
            f"✅ **THÔNG TIN ĐƠN HÀNG** ✅\n\n"
            f"📦 Gói: `{label}`\n"
            f"💰 Giá: `{price:,} VNĐ`\n"
            f"🏦 Ngân hàng: **MBBANK**\n"
            f"🔢 STK: `{STK}`\n"
            f"👤 Chủ TK: **{TEN_CHU_TK}**\n"
            f"📝 Nội dung: `{content}`\n\n"
            "⚠️ **Lưu ý:** Quét mã QR trên để thanh toán nhanh nhất.\n"
            "Sau khi chuyển khoản thành công, hãy bấm nút bên dưới để gửi Bill."
        )
        confirm_keyboard = [[InlineKeyboardButton("📸 Tôi đã thanh toán (Gửi Bill)", callback_query_data='confirm_pay')]]
        await query.message.reply_photo(photo=qr_image, caption=caption, reply_markup=InlineKeyboardMarkup(confirm_keyboard), parse_mode='Markdown')
        await query.answer()

    elif query.data == 'confirm_pay':
        waiting_for_bill[user.id] = True
        await query.message.reply_text("✨ Vui lòng gửi **Ảnh chụp màn hình Bill** vào đây. Admin sẽ check và gửi Key ngay!")
        await query.answer()

    elif query.data == 'info':
        info_text = (
            "💎 **LIÊN HỆ & CỘNG ĐỒNG** 💎\n\n"
            "👤 Admin: @thaitufaifai\n"
            "📞 Hỗ trợ: @thaitufaifao\n"
            "🐺 Chanel: @loitrumfile\n"
            "👥 Group: @dinhloibot\n"
            "🥇 Check scam: @checksocam"
        )
        await query.message.reply_text(info_text)
        await query.answer()

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    # Kiểm tra xem khách có đang trong trạng thái chờ gửi bill không
    if user.id in waiting_for_bill:
        # Gửi Bill về cho bạn (ADMIN)
        await context.bot.send_photo(
            chat_id=ADMIN_ID,
            photo=update.message.photo[-1].file_id,
            caption=f"📩 **CÓ BILL MỚI CẦN CHECK!**\n\n👤 Khách: @{user.username}\n🆔 ID: {user.id}\n📝 Tên: {user.full_name}\n📱 Link: tg://user?id={user.id}",
            parse_mode='Markdown'
        )
        # Báo cho khách
        await update.message.reply_text("✅ Đã gửi bill thành công! Vui lòng đợi Admin duyệt trong vài phút.")
        # Xóa trạng thái chờ sau khi đã gửi xong
        del waiting_for_bill[user.id]
    else:
        await update.message.reply_text("Liên hệ Admin @thaitufaifai để được hỗ trợ trực tiếp.")

def main():
    application = Application.builder().token(TOKEN).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(handle_click))
    application.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    
    print("--- Bot Dinh Loi Store đã sẵn sàng trên iOS ---")
    application.run_polling()

if __name__ == '__main__':
    main()