from app.schemas.product import Product

MAIN_PRODUCT = Product(
    id="beauty-main-001",
    platform="mock_tmall",
    category="beauty_skincare",
    url="https://mock.shop/product/beauty-serum-main",
    title="植萃修护精华液 熬夜肌补水保湿敏感肌可用 30ml",
    brand="LumiSkin",
    price=129,
    original_price=169,
    sku_name="30ml 修护精华",
    specs=["30ml", "50ml", "套装"],
    main_image_texts=[
        "熬夜肌修护精华",
        "补水保湿 提亮肤色",
        "敏感肌可用",
        "植萃成分 温和修护",
    ],
    detail_sections=[
        "熬夜暗沉、干燥起皮、换季泛红",
        "烟酰胺、泛醇、积雪草提取物",
        "早晚洁面后使用，轻拍吸收",
        "适合干皮、混合皮、敏感肌",
    ],
    selling_points=[
        "补水保湿",
        "舒缓修护",
        "改善暗沉",
        "敏感肌可用",
    ],
    ingredients=["烟酰胺", "泛醇", "积雪草提取物", "透明质酸钠"],
    target_users=["熬夜党", "干皮", "换季敏感肌", "初抗老用户"],
    usage_scenarios=["熬夜后", "妆前保湿", "换季修护", "日常护肤"],
)
