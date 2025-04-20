USE ghhn;

SET foreign_key_checks = 0;
DROP TABLE IF EXISTS STORE;
DROP TABLE IF EXISTS VENDOR;
DROP TABLE IF EXISTS BRAND;
DROP TABLE IF EXISTS PRODUCT;
DROP TABLE IF EXISTS SELL;
DROP TABLE IF EXISTS CUSTOMER;
DROP TABLE IF EXISTS ORDERS;
DROP TABLE IF EXISTS REORDER_REQUEST;
DROP TABLE IF EXISTS SHIPMENT;
DROP TABLE IF EXISTS PACKAGE_TYPE;
DROP TABLE IF EXISTS PRODUCT_TYPE;
DROP TABLE IF EXISTS ORDER_INCLUDES;


-- Table: STORE
CREATE TABLE STORE (
    store_id INT PRIMARY KEY AUTO_INCREMENT,
    store_country VARCHAR(70) NOT NULL,
    store_region VARCHAR(70) NOT NULL,
    store_street_address VARCHAR(100) NOT NULL UNIQUE,
    store_city VARCHAR(70) NOT NULL,
    store_zip VARCHAR(10) NOT NULL,
    store_phone VARCHAR(10) NOT NULL,

    Monday BOOLEAN,
    M_open TIME,
    M_close TIME,

    Tuesday BOOLEAN,
    T_open TIME,
    T_close TIME,

    Wednesday BOOLEAN,
    W_open TIME,
    W_close TIME,

    Thursday BOOLEAN,
    Th_open TIME,
    Th_close TIME,

    Friday BOOLEAN,
    F_open TIME,
    F_close TIME,

    Saturday BOOLEAN,
    Sa_open TIME,
    Sa_close TIME,

    Sunday BOOLEAN,
    Su_open TIME,
    Su_close TIME
);


-- Table: VENDOR
CREATE TABLE VENDOR (
    vendor_id INT PRIMARY KEY AUTO_INCREMENT,
    vendor_name VARCHAR(50) NOT NULL,
    vendor_phone VARCHAR(50) NOT NULL UNIQUE,
    vendor_email VARCHAR(50) NOT NULL UNIQUE,
    quantity INT NOT NULL,
    unit_price DECIMAL(10, 2) NOT NULL
);

-- Table: BRAND
CREATE TABLE BRAND (
    brand_id INT PRIMARY KEY AUTO_INCREMENT,
    brand_name VARCHAR(30) NOT NULL,
    vendor_id INT, 
    FOREIGN KEY (vendor_id) REFERENCES VENDOR(vendor_id) ON DELETE CASCADE
);

-- Table: PRODUCT
CREATE TABLE PRODUCT (
    UPC CHAR(16) PRIMARY KEY,
    product_name VARCHAR(100) NOT NULL,
    source_nation VARCHAR(70) NOT NULL,
    package_length NUMERIC(3,3),
    package_width NUMERIC(3,3),
    package_height NUMERIC(3,3), 
    std_price NUMERIC(10, 2) NOT NULL,
    brand_id INT,
    FOREIGN KEY (brand_id) REFERENCES BRAND(brand_id)
);

-- Table: SELL
CREATE TABLE SELL (
    store_id INT,
    UPC CHAR(16),
    max_inventory INT NOT NULL,
    current_inventory INT,
    overriden__price NUMERIC(10,2) NOT NULL,
    PRIMARY KEY (store_id, upc),
    FOREIGN KEY (store_id) REFERENCES STORE(store_id),
    FOREIGN KEY (UPC) REFERENCES PRODUCT(UPC)
);

-- Table: CUSTOMER
CREATE TABLE CUSTOMER (
    customer_id INT AUTO_INCREMENT PRIMARY KEY,
    customer_name VARCHAR(200) NOT NULL,
    customer_email VARCHAR(30) UNIQUE NOT NULL,
    customer_phone VARCHAR(15) UNIQUE NOT NULL,
    customer_country VARCHAR(70),
    customer_region VARCHAR(70),
    customer_st_addr VARCHAR(100),
    customer_city VARCHAR(70),
    customer_zip VARCHAR(10),
    app_user BOOLEAN
);
-- TABLE: ORDER
CREATE TABLE ORDERS (
  order_id INT AUTO_INCREMENT PRIMARY KEY,
  order_type BOOLEAN NOT NULL, 
  order_status BOOLEAN NOT NULL,
  order_date DATETIME NOT NULL,
  total_order_price NUMERIC(20, 2) NOT NULL,
  store_id INT,
  customer_id INT, 
  FOREIGN KEY (store_id) REFERENCES STORE(store_id) ON DELETE CASCADE, 
  FOREIGN KEY (customer_id) REFERENCES CUSTOMER(customer_id) ON DELETE CASCADE
);

-- TABLE: REORDER REQUEST
CREATE TABLE REORDER_REQUEST(
  reorder_id INT PRIMARY KEY AUTO_INCREMENT,
  reorder_date DATETIME NOT NULL,
  quantity_requested INT NOT NULL,
  total_cost NUMERIC(20, 2) NOT NULL,
  seen_status BOOLEAN NOT NULL,
  vendor_id INT,
  UPC CHAR(16), 
  store_id INT,
  FOREIGN KEY (vendor_id) REFERENCES VENDOR(vendor_id) ON DELETE CASCADE,
  FOREIGN KEY (UPC) REFERENCES PRODUCT(UPC) ON DELETE CASCADE,
  FOREIGN KEY (store_id) REFERENCES STORE(store_id) ON DELETE CASCADE
);

-- TABLE: SHIPMENT
CREATE TABLE SHIPMENT (
  reorder_id INT,
  PRIMARY KEY (reorder_id), FOREIGN KEY (reorder_id) REFERENCES REORDER_REQUEST(reorder_id),
  shipment_no INT NOT NULL,
  expected_delivery DATETIME NOT NULL,
  received_date DATETIME
);

-- Table for Packaging Material
CREATE TABLE PACKAGE_TYPE (
    UPC CHAR(16) NOT NULL,
    package_type VARCHAR(50),
    PRIMARY KEY (UPC, package_type),
    FOREIGN KEY(UPC) REFERENCES PRODUCT(UPC)
);

-- Table for Product types and Descriptions
CREATE TABLE PRODUCT_TYPE (
    UPC CHAR(16) NOT NULL,
    product_type VARCHAR(50),
    PRIMARY KEY (UPC, product_type),
    FOREIGN KEY(UPC) REFERENCES PRODUCT(UPC)
);

-- Table for the types of products included in the online order
CREATE TABLE ORDER_INCLUDES (
    order_id INT NOT NULL,
    UPC CHAR(16) NOT NULL,
    buying_quantity INT,
    PRIMARY KEY (order_id, UPC),
    FOREIGN KEY (order_id) REFERENCES ORDERS(order_id),
    FOREIGN KEY(UPC) REFERENCES PRODUCT(UPC)
);

COMMIT;
SHOW TABLES;
