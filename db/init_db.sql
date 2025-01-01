PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS Searches (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date_created TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    date_modified TIMESTAMP,
    name TEXT,
    min_price DECIMAL(10, 2) NOT NULL,
    max_price DECIMAL(10, 2) NOT NULL,
    type VARCHAR(16) CHECK (type IN ('auction', 'bin')),
    url TEXT NOT NULL,
    is_active INTEGER NOT NULL DEFAULT 1 CHECK (is_active IN (0, 1)),
    CHECK (min_price < max_price)
);

-- trigger to add date modified column to table
CREATE TRIGGER searches_update_date_modified
AFTER UPDATE ON Searches
FOR EACH ROW
BEGIN
    UPDATE Searches
    SET date_modified = CURRENT_TIMESTAMP
    WHERE id = OLD.id;
END;

CREATE TABLE IF NOT EXISTS bin_listings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    search_id INTEGER NOT NULL,
    ebay_listing_id INTEGER NOT NULL UNIQUE,
    date_created TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    url TEXT NOT NULL,
    accepts_best_offer INTEGER NOT NULL DEFAULT 0 CHECK (accepts_best_offer IN (0, 1)),
    price DECIMAL(10, 2) NOT NULL,
    FOREIGN KEY (search_id) REFERENCES Searches (id) ON DELETE RESTRICT
);

CREATE TABLE IF NOT EXISTS auction_listings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    search_id INTEGER NOT NULL,
    ebay_listing_id INTEGER NOT NULL UNIQUE,
    date_created TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    date_ending TIMESTAMP NOT NULL,
    url TEXT NOT NULL,
    accepts_best_offer INTEGER NOT NULL DEFAULT 0 CHECK (accepts_best_offer IN (0, 1)),
    price DECIMAL(10, 2) NOT NULL,
    FOREIGN KEY (search_id) REFERENCES Searches (id) ON DELETE RESTRICT,
    CHECK (date_ending > date_created)
);