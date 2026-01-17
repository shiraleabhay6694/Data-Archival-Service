USE production;

CREATE TABLE IF NOT EXISTS orders (
    id INT AUTO_INCREMENT PRIMARY KEY,
    customer_id INT NOT NULL,
    order_number VARCHAR(50) NOT NULL,
    total_amount DECIMAL(10, 2) NOT NULL,
    status VARCHAR(20) DEFAULT 'pending',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_created_at (created_at),
    INDEX idx_customer_id (customer_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS customers (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    phone VARCHAR(20),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_created_at (created_at),
    INDEX idx_email (email)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS products (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    price DECIMAL(10, 2) NOT NULL,
    stock_quantity INT DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Sample Customers
INSERT INTO customers (name, email, phone, created_at) VALUES
('John Doe', 'john.doe@example.com', '555-0001', DATE_SUB(NOW(), INTERVAL 400 DAY)),
('Jane Smith', 'jane.smith@example.com', '555-0002', DATE_SUB(NOW(), INTERVAL 380 DAY)),
('Bob Johnson', 'bob.johnson@example.com', '555-0003', DATE_SUB(NOW(), INTERVAL 200 DAY)),
('Alice Williams', 'alice.williams@example.com', '555-0004', DATE_SUB(NOW(), INTERVAL 50 DAY)),
('Charlie Brown', 'charlie.brown@example.com', '555-0005', DATE_SUB(NOW(), INTERVAL 10 DAY));

-- Sample Products
INSERT INTO products (name, description, price, stock_quantity, created_at) VALUES
('Widget A', 'High-quality widget for everyday use', 19.99, 100, DATE_SUB(NOW(), INTERVAL 500 DAY)),
('Gadget B', 'Advanced gadget with modern features', 49.99, 50, DATE_SUB(NOW(), INTERVAL 300 DAY)),
('Tool C', 'Professional-grade tool', 99.99, 25, DATE_SUB(NOW(), INTERVAL 150 DAY)),
('Device D', 'Smart device for home automation', 149.99, 75, DATE_SUB(NOW(), INTERVAL 30 DAY));


INSERT INTO orders (customer_id, order_number, total_amount, status, created_at) VALUES
(1, 'ORD-2024-001', 99.99, 'completed', DATE_SUB(NOW(), INTERVAL 365 DAY)),
(2, 'ORD-2024-002', 149.99, 'completed', DATE_SUB(NOW(), INTERVAL 360 DAY)),
(3, 'ORD-2024-003', 199.99, 'completed', DATE_SUB(NOW(), INTERVAL 355 DAY)),
(1, 'ORD-2024-004', 299.99, 'completed', DATE_SUB(NOW(), INTERVAL 350 DAY)),
(2, 'ORD-2024-005', 399.99, 'completed', DATE_SUB(NOW(), INTERVAL 345 DAY));

INSERT INTO orders (customer_id, order_number, total_amount, status, created_at) VALUES
(3, 'ORD-2024-006', 79.99, 'completed', DATE_SUB(NOW(), INTERVAL 300 DAY)),
(4, 'ORD-2024-007', 159.99, 'completed', DATE_SUB(NOW(), INTERVAL 280 DAY)),
(1, 'ORD-2024-008', 249.99, 'completed', DATE_SUB(NOW(), INTERVAL 250 DAY)),
(2, 'ORD-2024-009', 89.99, 'completed', DATE_SUB(NOW(), INTERVAL 220 DAY)),
(5, 'ORD-2025-001', 129.99, 'completed', DATE_SUB(NOW(), INTERVAL 190 DAY));

INSERT INTO orders (customer_id, order_number, total_amount, status, created_at) VALUES
(1, 'ORD-2025-002', 79.99, 'pending', DATE_SUB(NOW(), INTERVAL 90 DAY)),
(2, 'ORD-2025-003', 129.99, 'processing', DATE_SUB(NOW(), INTERVAL 60 DAY)),
(3, 'ORD-2025-004', 89.99, 'completed', DATE_SUB(NOW(), INTERVAL 30 DAY)),
(4, 'ORD-2025-005', 159.99, 'pending', DATE_SUB(NOW(), INTERVAL 15 DAY)),
(5, 'ORD-2025-006', 199.99, 'processing', DATE_SUB(NOW(), INTERVAL 7 DAY)),
(1, 'ORD-2025-007', 49.99, 'pending', NOW());


INSERT INTO orders (customer_id, order_number, total_amount, status, created_at) VALUES
(1, 'ORD-2024-010', 79.99, 'pending', DATE_SUB(NOW(), INTERVAL 590 DAY)),
(2, 'ORD-2024-011', 129.99, 'processing', DATE_SUB(NOW(), INTERVAL 560 DAY)),
(3, 'ORD-2024-014', 89.99, 'completed', DATE_SUB(NOW(), INTERVAL 530 DAY)),
(4, 'ORD-2024-015', 159.99, 'pending', DATE_SUB(NOW(), INTERVAL 515 DAY)),
(5, 'ORD-2024-016', 199.99, 'processing', DATE_SUB(NOW(), INTERVAL 557 DAY));