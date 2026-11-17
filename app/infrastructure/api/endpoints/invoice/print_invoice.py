from urllib.parse import quote

from fastapi import APIRouter, Depends, Response, status

from app.application.dto.invoice.customer import CustomerIn
from app.application.dto.invoice.invoice import InvoiceIn
from app.application.dto.invoice.invoice_item import InvoiceItemIn
from app.application.dto.invoice.payments import PaymentsIn
from app.application.dto.invoice.supplier import SupplierIn
from app.application.dto.shared.address import AddressIn
from app.application.ports.document_renderer import DocumentRenderer
from app.application.ports.template_engine import TemplateEngine
from app.application.use_cases.invoices.print_invoice import PrintInvoice
from app.infrastructure.api.dependencies.printing import (
    get_document_renderer,
    get_template_engine,
)
from app.infrastructure.api.schemas.invoice.invoice import InvoiceSchemaIn

router = APIRouter()

@router.post(
    "/print",
    status_code=status.HTTP_200_OK,
    response_class=Response,
)
def print_invoice(
    invoice: InvoiceSchemaIn,
    template_engine: TemplateEngine = Depends(get_template_engine),
    document_renderer: DocumentRenderer = Depends(get_document_renderer),
):
    print_invoice = PrintInvoice(template_engine, document_renderer)

    result = print_invoice.execute(
        InvoiceIn(
            number=invoice.number,
            issue_date=invoice.issue_date,
            supplier=SupplierIn(
                name=invoice.supplier.name,
                company_id=invoice.supplier.company_id,
                vat_id=invoice.supplier.vat_id,
                address=AddressIn(**invoice.supplier.address.model_dump()),
            ),
            customer=CustomerIn(
                name=invoice.customer.name,
                company_id=invoice.customer.company_id,
                vat_id=invoice.customer.vat_id,
                address=AddressIn(**invoice.customer.address.model_dump()),
            ),
            items=[
                InvoiceItemIn(**item.model_dump()) for item in invoice.items
            ],
            payments=PaymentsIn(**invoice.payments.model_dump()),
        )
    )

    return Response(
        content=result.content,
        media_type=f"application/{result.document_format}",
        headers={
            "Content-Disposition": (
                f"inline; filename*=UTF-8''{quote(result.filename, safe='')}"
            ),
        },
    )
