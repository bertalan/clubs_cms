# Website models package
from .pages import (  # noqa: F401
    AboutPage,
    BoardPage,
    ContactPage,
    EventDetailPage,
    EventPageTag,
    EventsPage,
    GalleryPage,
    HomePage,
    NewsIndexPage,
    NewsPage,
    NewsPageTag,
    PressPage,
    PrivacyPage,
    TransparencyPage,
)

from .snippets import (  # noqa: F401
    AidSkill,
    BrandAsset,
    ColorScheme,
    EventCategory,
    FAQ,
    Footer,
    FooterMenuItem,
    FooterSocialLink,
    Navbar,
    NavbarItem,
    NewsCategory,
    PartnerCategory,
    PhotoTag,
    PressRelease,
    Product,
    Testimonial,
)

from .partners import PartnerIndexPage, PartnerPage  # noqa: F401

from .verification import VerificationLog  # noqa: F401

from .uploads import PhotoUpload  # noqa: F401

from .settings import SiteSettings, PaymentSettings  # noqa: F401
