from app.schemas.competitor import CompetitorProduct

COMPETITOR_A = CompetitorProduct(
    id="competitor-a",
    product_id="beauty-main-001",
    url="https://mock.shop/product/competitor-a",
    title="补水保湿精华液女烟酰胺提亮肤色面部护肤品学生党",
    brand="PureGlow",
    price=59,
    sales_hint="月销1万+",
    rating=4.7,
    review_count=8600,
    selling_points=["低价", "补水", "烟酰胺", "学生党"],
    main_image_texts=["平价补水精华", "学生党可入", "提亮保湿"],
    promotions=["第二件半价", "买一送一"],
    weakness_hints=["包装普通", "成分背书弱", "敏感肌顾虑明显"],
)

COMPETITOR_B = CompetitorProduct(
    id="competitor-b",
    product_id="beauty-main-001",
    url="https://mock.shop/product/competitor-b",
    title="高浓度烟酰胺修护精华液 改善暗沉 提亮肤色 屏障修护",
    brand="DermaLab",
    price=189,
    sales_hint="月销3000+",
    rating=4.8,
    review_count=4200,
    selling_points=["高浓度烟酰胺", "成分专业", "屏障修护", "功效护肤"],
    main_image_texts=["5%烟酰胺", "屏障修护", "成分党优选"],
    promotions=["赠送小样", "会员专享价"],
    weakness_hints=["价格偏高", "刺激性顾虑", "新手理解成本高"],
)

COMPETITOR_C = CompetitorProduct(
    id="competitor-c",
    product_id="beauty-main-001",
    url="https://mock.shop/product/competitor-c",
    title="敏感肌舒缓修护精华液 积雪草泛醇补水保湿换季维稳",
    brand="CalmCare",
    price=149,
    sales_hint="月销5000+",
    rating=4.9,
    review_count=6900,
    selling_points=["敏感肌", "舒缓泛红", "积雪草", "换季维稳"],
    main_image_texts=["换季维稳", "敏感肌安心用", "舒缓泛红"],
    promotions=["满减", "赠化妆棉"],
    weakness_hints=["提亮卖点弱", "见效慢", "油皮反馈一般"],
)

ALL_COMPETITORS = [COMPETITOR_A, COMPETITOR_B, COMPETITOR_C]
