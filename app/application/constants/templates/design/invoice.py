from enum import Enum

from app.application.constants.templates.components.address import (
    AddressComponent,
)
from app.application.constants.templates.components.customer import (
    CustomerComponent,
)
from app.application.constants.templates.components.document import (
    DocumentComponent,
)
from app.application.constants.templates.components.invoice import (
    InvoiceComponent,
)
from app.application.constants.templates.components.invoice_item import (
    InvoiceItemComponent,
)
from app.application.constants.templates.components.payments import (
    PaymentsComponent,
)
from app.application.constants.templates.components.supplier import (
    SupplierComponent,
)
from app.application.constants.templates.variants.address import (
    AddressVariant,
)
from app.application.constants.templates.variants.customer import (
    CustomerVariant,
)
from app.application.constants.templates.variants.document import (
    DocumentVariant,
)
from app.application.constants.templates.variants.invoice import (
    InvoiceVariant,
)
from app.application.constants.templates.variants.invoice_item import (
    InvoiceItemVariant,
)
from app.application.constants.templates.variants.payments import (
    PaymentsVariant,
)
from app.application.constants.templates.variants.supplier import (
    SupplierVariant,
)


class InvoiceDesign(Enum):
    """
    Designs of the invoice. A design chooses the type of the document
    (which brings its header and footer), the layout of the invoice and
    the visual variant of each of its children.
    """

    CLASSIC = DocumentComponent(
        variant=DocumentVariant.STANDARD,
        content=InvoiceComponent(
            variant=InvoiceVariant.CLASSIC,
            supplier=SupplierComponent(
                variant=SupplierVariant.PLAIN,
                address=AddressComponent(variant=AddressVariant.LINES),
            ),
            customer=CustomerComponent(
                variant=CustomerVariant.PLAIN,
                address=AddressComponent(variant=AddressVariant.LINES),
            ),
            items=InvoiceItemComponent(variant=InvoiceItemVariant.ROW),
            payments=PaymentsComponent(variant=PaymentsVariant.TABLE),
        ),
    )
