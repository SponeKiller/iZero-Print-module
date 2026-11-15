from dataclasses import asdict

from app.application.constants.document_formats import DocumentFormat
from app.application.constants.templates.design.invoice import (
    InvoiceDesign,
)
from app.application.constants.templates.labels.invoice import InvoiceLabel
from app.application.dto.invoice.invoice import InvoiceIn
from app.application.dto.invoice.print_invoice import PrintInvoiceOut
from app.application.dto.shared.document import DocumentOut
from app.application.exceptions.printing import (
    DocumentRenderingError,
    InvalidDocumentDataError,
    TemplateFillingError,
)
from app.application.ports.document_renderer import DocumentRenderer
from app.application.ports.template_engine import TemplateEngine
from app.application.use_cases.invoices.format_invoice import FormatInvoice
from app.domain.invoices.entities.customer import Customer
from app.domain.invoices.entities.invoice import Invoice
from app.domain.invoices.entities.invoice_item import InvoiceItem
from app.domain.invoices.entities.payments import Payments
from app.domain.invoices.entities.supplier import Supplier
from app.domain.shared.exceptions.validation import DomainValidationError
from app.domain.shared.value_objects.address import Address
from app.domain.shared.value_objects.company_id import CompanyId
from app.domain.shared.value_objects.iban import Iban
from app.domain.shared.value_objects.vat_id import VatId


class PrintInvoice:

    def __init__(
        self,
        template_engine: TemplateEngine,
        document_renderer: DocumentRenderer,
    ) -> None:
        """
        Initialize use-case

        Args:
            template_engine: Engine filling the document templates
            document_renderer: Renderer of the filled template
        """
        self.template_engine = template_engine
        self.document_renderer = document_renderer

    def execute(self, dto: InvoiceIn) -> PrintInvoiceOut:
        """
        Print an invoice (UC-1): validate the supplied data, format it
        (`FormatInvoice`), fill the template and render the document.
        Nothing is stored.

        Args:
            dto: Supplied invoice data

        Returns:
            Printed invoice

        Raises:
            InvalidDocumentDataError: If the data is invalid; nothing is
             filled or rendered (BR-2)
            TemplateFillingError: If filling the template fails (BR-6)
            DocumentRenderingError: If rendering fails (BR-6)
        """
        # The domain objects are built here, one by one from the inside
        # out - an entity never builds another entity.
        try:
            supplier = Supplier.create(
                name=dto.supplier.name,
                company_id=(
                    CompanyId(dto.supplier.company_id)
                    if dto.supplier.company_id
                    else None
                ),
                vat_id=(
                    VatId(dto.supplier.vat_id)
                    if dto.supplier.vat_id
                    else None
                ),
                address=Address(**asdict(dto.supplier.address)),
            )

            customer = Customer.create(
                name=dto.customer.name,
                company_id=(
                    CompanyId(dto.customer.company_id)
                    if dto.customer.company_id
                    else None
                ),
                vat_id=(
                    VatId(dto.customer.vat_id)
                    if dto.customer.vat_id
                    else None
                ),
                address=Address(**asdict(dto.customer.address)),
            )

            items = [
                InvoiceItem.create(**asdict(item)) for item in dto.items
            ]

            payments = Payments.create(
                iban=Iban(dto.payments.iban),
                amount_to_pay=dto.payments.amount_to_pay,
                currency=dto.payments.currency,
                variable_symbol=dto.payments.variable_symbol,
                due_date=dto.payments.due_date,
            )

            invoice = Invoice.create(
                number=dto.number,
                issue_date=dto.issue_date,
                supplier=supplier,
                customer=customer,
                items=items,
                payments=payments,
            )
        except DomainValidationError as e:
            raise InvalidDocumentDataError(e.problem) from e

        formatted_invoice = FormatInvoice().execute(invoice)

        try:
            document = self.template_engine.fill(
                InvoiceDesign.CLASSIC.value,
                DocumentOut(
                    title=f"{InvoiceLabel.TITLE} {formatted_invoice.number}",
                    content=formatted_invoice,
                ),
            )
        except Exception as e:
            raise TemplateFillingError("Filling the template failed") from e

        try:
            content = self.document_renderer.render(
                document, DocumentFormat.PDF
            )
        except Exception as e:
            raise DocumentRenderingError("Rendering failed") from e

        return PrintInvoiceOut(
            invoice_number=invoice.number,
            content=content,
            document_format=DocumentFormat.PDF,
        )
