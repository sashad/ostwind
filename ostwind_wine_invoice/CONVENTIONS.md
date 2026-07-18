# Odoo 19 Invoice Redesign - Requirements &amp; Field Mapping

This canvas contains the complete requirements for redesigning the invoice template in Odoo 19 Community, along with the corresponding database field names for implementation.

---

## 📋 Requirements Summary


| #     | Requirement                                                                                                                |
| ----- | -------------------------------------------------------------------------------------------------------------------------- |
| **1** | Merge **"Invoice No"** into the **"Invoice"** title (e.g., *"Invoice 2026/0005"*) and place it **above the product list**. |
| **2** | Move **UID, VID, EORI** fields to the **template footer**.                                                                 |
| **3** | Remove **"Invoice Date Due", "Source", "Reference"** from the **top right box**.                                           |
| **4** | **Footer layout: 4 columns**                                                                                               |


- **Col 1:** Labels (*Seller Name, Phone, Email, Website*)
- **Col 2:** Values (*saler name, phone, email, website URL*)
- **Col 3:** Tax/Registration (*USt, HRB Nr, UID, VID, EORI*)
- **Col 4:** Bank Details (*Account owner, IBAN, BIC, Bank name*) |  
| **5** | **Top left box layout:**
- Line 1: Seller name (**value only**)
- Line 2: Seller's address
- Line 3: Buyer's name (**name only**)
- Line 4: Buyer's address |

---

## 🗃️ Odoo 19 Field Mapping


| **Your Requirement**   | **Odoo Model**     | **Field Name**                                                                                               | **Notes**                                                                                                                    |
| ---------------------- | ------------------ | ------------------------------------------------------------------------------------------------------------ | ---------------------------------------------------------------------------------------------------------------------------- |
| **Invoice No**         | `account.move`     | `name`                                                                                                       | The sequential invoice number (e.g., "2026/0005")                                                                            |
| **Invoice Date**       | `account.move`     | `invoice_date`                                                                                               | Date of the invoice                                                                                                          |
| **Delivery Date**      | `account.move`     | `invoice_date` (or custom field)                                                                             | *Note: Odoo doesn't natively store delivery dates on invoices; may need `sale_order_id.commitment_date` if linked to a sale* |
| **Seller Name**        | `res.company`      | `company_id.name`                                                                                            | Your company name                                                                                                            |
| **Seller Address**     | `res.company`      | `company_id.street`, `company_id.street2`, `company_id.city`, `company_id.zip`, `company_id.country_id.name` | Full address                                                                                                                 |
| **Seller Phone**       | `res.company`      | `company_id.phone`                                                                                           | Company phone                                                                                                                |
| **Seller Email**       | `res.company`      | `company_id.email`                                                                                           | Company email                                                                                                                |
| **Seller Website**     | `res.company`      | `company_id.website`                                                                                         | Company website                                                                                                              |
| **Buyer Name**         | `res.partner`      | `partner_id.name`                                                                                            | Customer name                                                                                                                |
| **Buyer Address**      | `res.partner`      | `partner_id.street`, `partner_id.street2`, `partner_id.city`, `partner_id.zip`, `partner_id.country_id.name` | Customer address                                                                                                             |
| **USt Number**         | `res.company`      | `company_id.vat`                                                                                             | VAT/Tax ID (Austrian USt)                                                                                                    |
| **HRB Nr**             | `res.company`      | *Custom field* (e.g., `company_id.hrb_nr`)                                                                   | Not native; needs custom field                                                                                               |
| **Bank Account Owner** | `res.partner.bank` | `company_id.bank_ids.owner_name`                                                                             | *Note: Requires `bank_ids` to be populated*                                                                                  |
| **IBAN**               | `res.partner.bank` | `company_id.bank_ids.acc_number`                                                                             | Bank account number (IBAN)                                                                                                   |
| **BIC**                | `res.partner.bank` | `company_id.bank_ids.bank_bic`                                                                               | Bank Identifier Code                                                                                                         |
| **Bank Name**          | `res.partner.bank` | `company_id.bank_ids.bank_name`                                                                              | Name of the bank                                                                                                             |


---

## 📌 Implementation Notes

### Custom Fields Required

- **HRB Nr**: Not a native Odoo field. Create a custom field on `res.company`:
  ```python
  hrb_nr = fields.Char(string="HRB Number")
  ```

### Bank Details Access

Odoo stores bank information in a separate model (`res.partner.bank`). Access via `company_id.bank_ids` (one2many field). Example QWeb usage:

```xml
<t t-foreach="doc.company_id.bank_ids" t-as="bank">
  IBAN: <t t-esc="bank.acc_number"/>
  BIC: <t t-esc="bank.bank_bic"/>
</t>
```

### UID/VID/EORI

Excluded as requested. These will be defined separately.

---

## 🎯 Next Steps

- [ ] Create custom fields (e.g., `hrb_nr`)
- [ ] Develop custom QWeb template using the field mapping above
- [ ] Test the redesigned invoice layouto 
