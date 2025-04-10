
# from tap_razorpay.streams.profiles import ProfilesStream
# from tap_razorpay.streams.portfolios import PortfoliosStream

# Sponsored Products
# from tap_razorpay.streams.sponsored_products_targeting_clauses import SponsoredProductsTargetingClausesStream
# from tap_razorpay.streams.sponsored_products_report import SponsoredProductsReportCampaignsStream, SponsoredProductsReportTargetingStream, SponsoredProductsReportSearchTermsStream, SponsoredProductsReportAdvertisedProductStream, SponsoredProductsReportPurchasedProductStream, SponsoredProductsReportGrossAndInvalidTrafficStream

# Razorpay Stream 
from tap_razorpay.streams.orders import OrdersStream


AVAILABLE_STREAMS = [
    
    # Sponsored Products

   OrdersStream
]

__all__ = [
    "OrdersStream"
   
]
