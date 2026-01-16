-- Users table
CREATE TABLE residential_proxy_user (
    id SERIAL PRIMARY KEY,
    proxy_user_id VARCHAR(255) UNIQUE NOT NULL,
    proxy_user_password VARCHAR(255) NOT NULL,
    proxy_user_available_bandwidth numeric NOT NULL
);

-- Proxies table
CREATE TABLE residential_proxy (
    residential_proxy_id SERIAL PRIMARY KEY,
    residential_proxy_ip_address_v4 inet NOT NULL,
    residential_proxy_port INTEGER NOT NULL,
    country_id VARCHAR(2) NOT NULL,
    city_id VARCHAR(255) NOT NULL,
    residential_proxy_supported_protocol VARCHAR(10) NOT NULL CHECK (residential_proxy_supported_protocol IN ('http', 'socks5'))
);

-- Seed users
INSERT INTO residential_proxy_user (proxy_user_id, proxy_user_password, proxy_user_available_bandwidth) VALUES
    ('alice_residential', 'secretpass123', 10737418240),
    ('bob_residential', 'hunter2', 5368709120),
    ('charlie_residential', 'password456', 0),
    ('testuser_residential', 'testpass', 1073741824);

-- Seed proxies
INSERT INTO residential_proxy (residential_proxy_ip_address_v4, residential_proxy_port, country_id, city_id, residential_proxy_supported_protocol) VALUES
    ('192.168.1.1', 8080, 'us', 'new_york', 'http'),
    ('192.168.1.2', 8080, 'us', 'los_angeles', 'http'),
    ('192.168.1.3', 1080, 'us', 'chicago', 'socks5'),
    ('192.168.1.4', 8080, 'gb', 'london', 'http'),
    ('192.168.1.5', 1080, 'gb', 'manchester', 'socks5'),
    ('192.168.1.6', 8080, 'de', 'berlin', 'http'),
    ('192.168.1.7', 1080, 'de', 'munich', 'socks5'),
    ('192.168.1.8', 8080, 'fr', 'paris', 'http');
