USE ghhn;

-- PRODUCT
INSERT INTO PRODUCT (UPC, product_name, source_nation, package_length, package_width, package_height, std_price, brand_id)
VALUES
('0000000000000001', 'Blood Cleaner', 'USA', 0.210, 0.320, 0.150, 19.99, 1),
('0000000000000002', 'Wallet', 'Italy', 0.085, 0.055, 0.020, 24.99, 2),
('0000000000000003', 'Detergent', 'Germany', 0.500, 0.400, 0.350, 9.49, 3),
('0000000000000004', 'Energy Drink', 'South Korea', 0.130, 0.050, 0.050, 2.99, 4),
('0000000000000005', 'Chainsaw', 'Canada', 0.950, 0.850, 0.600, 89.99, 1),
('0000000000000006', 'Backpack', 'Vietnam', 0.720, 0.500, 0.200, 49.99, 2),
('0000000000000007', 'Toothpaste', 'India', 0.170, 0.030, 0.030, 1.99, 3),
('0000000000000008', 'Laptop Stand', 'China', 0.680, 0.500, 0.060, 34.99, 4),
('0000000000000009', 'Shampoo', 'UK', 0.250, 0.050, 0.050, 5.99, 1),
('0000000000000010', 'Notebook', 'Japan', 0.300, 0.210, 0.010, 3.49, 2),
('0000000000000011', 'Electric Kettle', 'France', 0.330, 0.250, 0.300, 29.99, 1),
('0000000000000012', 'Hair Dryer', 'Brazil', 0.290, 0.180, 0.250, 39.99, 3);

-- CUSTOMER
INSERT INTO CUSTOMER (
    customer_name, customer_email, customer_phone, 
    customer_country, customer_region, customer_st_addr, 
    customer_city, customer_zip, app_user
)
VALUES
('Hadi Imtiaz', 'hadi@iwu.edu', '309-123-4567', 'USA', 'Illinois', '123 Main St', 'Bloomington', '61701', TRUE),
('Harsh Patel', 'harsh@cvs.com', '403-984-6677', 'USA', 'Illinois', '456 Broadway', 'South Elgin', '67321', FALSE),
('Grace Poulton', 'grace@email.com', '152-334-4556', 'USA', 'Texas', '904 Lecter St', 'San Antonio', '80333', TRUE),
('Nawvatin Azhar', 'Nawvatin@deeplearning.com', '759-323-9823', 'USA', 'New York', '456 7th Ave', 'New York','91936', FALSE);


-- SELL
INSERT INTO SELL (store_id, product_id, sell_price)
VALUES
(1, 1, 3.99), (1, 2, 1.99), (1, 3, 8.49),
(2, 4, 25.00), (2, 5, 2.49), (2, 6, 1.49),
(3, 7, 6.99), (3, 8, 49.99), (3, 9, 3.49),
(4, 10, 2.99), (4, 11, 5.49), (4, 12, 89.99),
(5, 1, 3.79), (5, 6, 1.39),
(6, 3, 8.29), (6, 11, 5.29);

