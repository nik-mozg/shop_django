# shop/urls.py
from django.urls import path
from django.views.generic import TemplateView

from .views import get_tags
from .views_auth import post_sign_in, post_sign_out, post_sign_up
from .views_basket import basket_view
from .views_catalog import (
    get_banners,
    get_catalog,
    get_categories,
    get_products_limited,
    get_products_popular,
    get_sales,
)
from .views_orders import get_history_order, order_view, orders_view
from .views_payments import (
    create_payment,
    payment_success,
    post_payment,
    retry_payment,
)  # noqa: F401
from .views_product import get_product_item, post_product_review
from .views_profile import post_profile_avatar, post_profile_password, profile_view

urlpatterns = [
    path("", TemplateView.as_view(template_name="frontend/index.html")),
    path("about/", TemplateView.as_view(template_name="frontend/about.html")),
    path("cart/", TemplateView.as_view(template_name="frontend/cart.html")),
    path("catalog/", TemplateView.as_view(template_name="frontend/catalog.html")),
    path(
        "catalog/<int:id>/", TemplateView.as_view(template_name="frontend/catalog.html")
    ),
    path(
        "history-order/",
        TemplateView.as_view(template_name="frontend/historyorder.html"),
    ),
    path(
        "order-detail/<int:id>/",
        TemplateView.as_view(template_name="frontend/oneorder.html"),
    ),
    path("orders/<int:id>/", TemplateView.as_view(template_name="frontend/order.html")),
    # path(
    #     "payment/<int:id>/", TemplateView.as_view(template_name="frontend/payment.html")
    # ),
    path(
        "payment-someone/",
        TemplateView.as_view(template_name="frontend/paymentsomeone.html"),
    ),
    path(
        "product/<int:id>/", TemplateView.as_view(template_name="frontend/product.html")
    ),
    path("profile/", TemplateView.as_view(template_name="frontend/profile.html")),
    path(
        "progress-payment/",
        TemplateView.as_view(template_name="frontend/progressPayment.html"),
    ),
    path("sale/", TemplateView.as_view(template_name="frontend/sale.html")),
    path("sign-in/", TemplateView.as_view(template_name="frontend/signIn.html")),
    path("sign-up/", TemplateView.as_view(template_name="frontend/signUp.html")),
    path("api/sign-in/", post_sign_in, name="api_sign_in"),
    path("api/sign-out", post_sign_out, name="api_sign_out"),
    path("api/sign-up/", post_sign_up, name="api_sign_up"),
    path("api/profile/avatar", post_profile_avatar, name="api_profile_avatar"),
    path("api/profile/", profile_view, name="api_profile"),
    path("api/profile/password", post_profile_password, name="api_profile_password"),
    path("api/product/<int:id>", get_product_item, name="get_product_item"),
    path(
        "api/product/<int:id>/reviews", post_product_review, name="post_product_review"
    ),
    path("api/tags", get_tags, name="get_tags"),
    path("api/categories", get_categories, name="get_categories"),
    path("api/catalog/", get_catalog, name="get_catalog"),
    path("api/products/popular", get_products_popular, name="get_products_popular"),
    path("api/products/limited", get_products_limited, name="get_products_limited"),
    path("api/sales/", get_sales, name="get_sales"),
    path("api/banners", get_banners, name="get_banners"),
    path("api/basket", basket_view, name="basket_view"),
    path("api/orders/", orders_view, name="orders_view"),
    path("api/orders/<int:id>/", order_view, name="order_view"),
    path("/payment/<int:id>/", create_payment, name="create_payment"),
    path("api/history-order", get_history_order, name="get_history_order"),
    path("api/payment/<int:id>/", post_payment, name="post_payment"),
    path("api/create-payment/<int:id>/", create_payment, name="create_payment"),
    path("payment-success/", payment_success, name="payment_success"),
    path("retry-payment/<int:order_id>/", retry_payment, name="retry_payment"),
]
