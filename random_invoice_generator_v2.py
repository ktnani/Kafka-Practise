from datetime import datetime
import time,random,json
from faker import Faker
import uuid

faker = Faker()
# Load products
with open("realistic_product_catalog_3000.json", "r") as f:
    products = json.load(f)

# Load coupons
with open("coupon_codes.json", "r") as f:
    coupons = json.load(f)

# Load store locations
with open("store_locations.json", "r") as f:
    stores = json.load(f)

# Generate a unique 16-character invoice number using UUID
def generate_invoice_number():
    return f"INV-{uuid.uuid4().hex[:16].upper()}"

# Helper to create a realistic line item
def create_realistic_line_item(products):
    product = random.choice(products)
    qty = random.randint(1, 5)
    total = round(product["FinalPrice"] * qty, 2)
    return {
        "ItemCode": product["ItemCode"],
        "ItemName": product["ItemName"],
        "Category": product["Category"],
        "Brand": product["Brand"],
        "ItemPrice": product["Price"],
        "DiscountPercent": product["DiscountPercent"],
        "FinalPrice": product["FinalPrice"],
        "ItemQty": qty,
        "TotalValue": total
    }

# Helper to apply a coupon
def apply_coupon(total, category_counts, coupons):
    if random.random() > 0.5:
        coupon = random.choice(coupons)
        if any(cat in coupon["ApplicableCategories"] for cat in category_counts.keys()):
            if coupon["MinTotalAmount"] and total < coupon["MinTotalAmount"]:
                return None, 0.0
            discount = round(total * (coupon["Discount"] / 100), 2) if coupon["Type"] == "percent" else coupon["Discount"]
            return coupon["Code"], discount
    return None, 0.0

# The main function to create a realistic invoice
def create_realistic_invoice(products, coupons, stores):
    num_items = random.randint(1, 5)
    line_items = [create_realistic_line_item(products) for _ in range(num_items)]
    total_amount = round(sum(item["TotalValue"] for item in line_items), 2)
    
    
    
    category_counts = {}
    for item in line_items:
        category_counts[item["Category"]] = category_counts.get(item["Category"], 0) + 1

    coupon_code, coupon_discount = apply_coupon(total_amount, category_counts, coupons)
    disc_total = total_amount - coupon_discount
    taxable_amount = round(disc_total * 0.9, 2)
    cgst = round(taxable_amount * 0.05, 2)
    sgct = round(taxable_amount * 0.05, 2)
    final_total=round(disc_total+cgst+sgct)
    store = random.choice(stores)

    invoice = {
        "timestamp": datetime.now().isoformat(),
        "timestamp_epoch_ms": int(time.time() * 1000),
        "InvoiceNumber": generate_invoice_number(),
        "CreatedTime": int(time.time()),
        "CustomerCardNo": faker.credit_card_number(),
        "TotalAmount": total_amount,
        "TaxableAmount": taxable_amount,
        "CGST": cgst,
        "SGCT": sgct,
        "CouponCode": coupon_code,
        "CouponDiscount": coupon_discount,
        "FinalAmount": round(final_total, 2),
        "NumberOfItem": num_items,
        "PaymentMethod": random.choice(["CASH", "CARD", "UPI"]),
        "InvoiceLineItems": line_items,
        "StoreID": store["StoreID"],
        "StoreLocation": {
            "City": store["City"],
            "State": store["State"],
            "ZipCode": store["ZipCode"]
        },
        "PosID": f"POS-{random.randint(100, 999)}",
        "CustomerType": random.choice(["REGULAR", "PRIME"]),
        "DeliveryType": random.choice(["HOME-DELIVERY", "PICK-UP"]),
        "DeliveryAddress": {
            "AddressLine": faker.street_address(),
            "City": faker.city(),
            "State": faker.state(),
            "PinCode": faker.postcode(),
            "ContactNumber": faker.phone_number() if random.random() > 0.3 else None
        }
    }
    return invoice

# Example usage:
invoice_sample = create_realistic_invoice(products, coupons, stores)
print(invoice_sample)
