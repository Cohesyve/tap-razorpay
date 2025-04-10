
# from tap_razorpay.streams.profiles import ProfilesStream
# from tap_razorpay.streams.portfolios import PortfoliosStream

# Sponsored Products
# from tap_razorpay.streams.sponsored_products_targeting_clauses import SponsoredProductsTargetingClausesStream
# from tap_razorpay.streams.sponsored_products_report import SponsoredProductsReportCampaignsStream, SponsoredProductsReportTargetingStream, SponsoredProductsReportSearchTermsStream, SponsoredProductsReportAdvertisedProductStream, SponsoredProductsReportPurchasedProductStream, SponsoredProductsReportGrossAndInvalidTrafficStream

# Razorpay Stream 
from tap_razorpay.streams.orders import OrdersStream
from tap_razorpay.streams.customers import CustomersStream
from tap_razorpay.streams.disputes import DisputesStream
from tap_razorpay.streams.payments import PaymentsStream
from tap_razorpay.streams.refunds import RefundsStream
from tap_razorpay.streams.settlements import SettlementsStream


AVAILABLE_STREAMS = [

   OrdersStream,
   CustomersStream,
   DisputesStream,
   PaymentsStream,
   RefundsStream,
   SettlementsStream
]

__all__ = [
    "OrdersStream",
     "CustomersStream",
   "DisputesStream",
   "PaymentsStream",
   "RefundsStream",
   "SettlementsStream"
   
]
