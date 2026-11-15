import pytest

from app.domain.shared.exceptions.validation import (
    DomainValidationError,
    ProblemCode,
)
from app.domain.shared.value_objects.address import Address
from app.domain.shared.value_objects.company_id import CompanyId
from app.domain.shared.value_objects.iban import Iban
from app.domain.shared.value_objects.vat_id import VatId
from tests.support import VALID_IBAN

VALID_ADDRESS = {
    "street": "Dlouhá 12",
    "city": "Praha",
    "postal_code": "110 00",
    "country": "Česká republika",
}


def problem_of(build) -> tuple[str, ProblemCode]:
    with pytest.raises(DomainValidationError) as raised:
        build()

    return (raised.value.problem.field, raised.value.problem.code)


class TestIban:
    @pytest.mark.parametrize(
        "value",
        [
            VALID_IBAN,
            "CZ6608000000192000145399",  # wrong check digits
            "6508000000192000145399CZ",  # country code not first
            "CZ65080000",  # short
            "CZ65" + "0" * 30,  # longest allowed (34)
        ],
    )
    def test_checks_only_the_length(self, value):
        assert Iban(value).value == value

    def test_keeps_the_value_as_supplied(self):
        value = "cz65 0800 0000 1920 0014 5399"

        assert Iban(value).value == value

    def test_rejects_too_long_iban(self):
        assert problem_of(lambda: Iban("CZ65" + "0" * 31)) == (
            "iban",
            ProblemCode.TOO_LONG,
        )

    @pytest.mark.parametrize("value", [None, "", "   "])
    def test_rejects_missing_iban(self, value):
        assert problem_of(lambda: Iban(value)) == (
            "iban",
            ProblemCode.REQUIRED,
        )


class TestCompanyId:
    @pytest.mark.parametrize("value", ["12345678", "1234567", "1234567A"])
    def test_accepts_up_to_eight_characters(self, value):
        assert CompanyId(value).value == value

    def test_rejects_too_long_value(self):
        assert problem_of(lambda: CompanyId("123456789")) == (
            "company_id",
            ProblemCode.TOO_LONG,
        )

    @pytest.mark.parametrize("value", [None, "", "   "])
    def test_rejects_missing_value(self, value):
        assert problem_of(lambda: CompanyId(value)) == (
            "company_id",
            ProblemCode.REQUIRED,
        )


class TestVatId:
    @pytest.mark.parametrize(
        "value", ["CZ12345678", "SK2020123456", "12345678", "cz1"]
    )
    def test_accepts_up_to_twelve_characters(self, value):
        assert VatId(value).value == value

    def test_rejects_too_long_value(self):
        assert problem_of(lambda: VatId("CZ12345678901")) == (
            "vat_id",
            ProblemCode.TOO_LONG,
        )


class TestAddress:
    def test_accepts_valid_address(self):
        assert Address(**VALID_ADDRESS).city == "Praha"

    @pytest.mark.parametrize(
        ("field", "value", "expected"),
        [
            ("street", None, ProblemCode.REQUIRED),
            ("street", "x" * 101, ProblemCode.TOO_LONG),
            ("city", "   ", ProblemCode.REQUIRED),
            ("city", "x" * 101, ProblemCode.TOO_LONG),
            ("postal_code", None, ProblemCode.REQUIRED),
            ("postal_code", "1" * 11, ProblemCode.TOO_LONG),
            ("country", "", ProblemCode.REQUIRED),
            ("country", "x" * 51, ProblemCode.TOO_LONG),
        ],
    )
    def test_rejects_invalid_value(self, field, value, expected):
        assert problem_of(
            lambda: Address(**VALID_ADDRESS | {field: value})
        ) == (field, expected)

    def test_country_is_a_free_text(self):
        address = Address(
            **VALID_ADDRESS | {"country": "Spojené státy americké"}
        )

        assert address.country == "Spojené státy americké"
