# Wine Invoice Module

## Overview

The Wine Invoice Module is designed to enhance the functionality of the Odoo Sales module for wine-related businesses. It provides additional features and customizations specifically tailored for managing wine invoices.

## Features

### 1. Total Liters Calculation

The module calculates the total liters of wine in each sale order. This is particularly useful for businesses that need to track the volume of wine sold.

### 2. Sparkling Wine Identification

The module identifies sparkling wine based on the product category. If a product belongs to the sparkling wine category or any of its parent categories, it is considered as sparkling wine.

### 3. UID, VID, and EORI Display

The module displays the UID (Unique Identification), VID (Vat Identification), and EORI (Economic Operators Registration and Identification) numbers on the invoice. These numbers are essential for tracking and identifying wine shipments.

## Configuration

### 1. Setting Up Sparkling Wine Category

To configure the sparkling wine category, follow these steps:

1. Go to the **Products** module.
2. Navigate to the **Product Categories** section.
3. Create a new category or select an existing one that represents sparkling wine.
4. Note down the ID of this category.
5. Go to the **Settings** module.
6. Navigate to the **Technical** section.
7. Find the **System Parameters** section.
8. Add a new parameter with the key `ostwind_wine_invoice.sparkling_category` and set its value to the Name of the sparkling wine category.

### 2. Setting Up UID, VID, and EORI

To configure the UID, VID, and EORI numbers, follow these steps:

1. Go to the **Settings** module.
2. Navigate to the **Technical** section.
3. Find the **Parameters** section.
4. Add a new parameter with the key `ostwind_wine_invoice.vid` and set its value to the VID number.
5. Add a new parameter with the key `ostwind_wine_invoice.eori` and set its value to the EORI number.

## Usage

### 1. Viewing Total Liters

The total liters of wine in each sale order are displayed on the invoice. This information is shown in the **Total in Liter** section.

### 2. Viewing Sparkling Wine Liters

The total liters of sparkling wine in each sale order are displayed on the invoice. This information is shown in the **Total in Liter Sparkling** section.

### 3. Viewing UID, VID, and EORI

The UID, VID, and EORI numbers are displayed on the invoice. These numbers are shown in the **UID**, **VID**, and **EORI** sections, respectively.

## Troubleshooting

### 1. Total Liters Not Displayed

If the total liters are not displayed on the invoice, ensure that the product units are correctly configured. The module expects the product units to have a name that starts with "Bottle" followed by the volume in liters (e.g., "Bottle 0.75").

### 2. Sparkling Wine Not Identified

If sparkling wine is not correctly identified, ensure that the sparkling wine category is correctly configured. The module checks the product category and its parent categories to identify sparkling wine.

### 3. UID, VID, and EORI Not Displayed

If the UID, VID, and EORI numbers are not displayed on the invoice, ensure that these parameters are correctly configured in the **Settings** module.

## Conclusion

The Wine Invoice Module provides valuable features for managing wine invoices in Odoo. By following the configuration and usage guidelines, you can effectively utilize the module to enhance your wine-related business operations.
