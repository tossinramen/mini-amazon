\COPY Users FROM 'Users.csv' WITH DELIMITER ',' NULL '' CSV

\COPY Sellers FROM 'Sellers.csv' WITH DELIMITER ',' NULL '' CSV;

\COPY Products FROM 'Products.csv' WITH DELIMITER ',' NULL '' CSV
SELECT pg_catalog.setval('public.products_id_seq',
                         (SELECT MAX(id)+1 FROM Products),
                         false);

\COPY Seller_Inventory FROM 'Seller_Inventory.csv' WITH DELIMITER ',' NULL '' CSV;
-- since id is auto-generated; we need the next command to adjust the counter
-- for auto-generation so next INSERT will not clash with ids loaded above:
SELECT pg_catalog.setval('public.users_id_seq',
                         (SELECT MAX(id)+1 FROM Users),
                         false);



\COPY Purchases FROM 'Purchases.csv' WITH DELIMITER ',' NULL '' CSV

\COPY BoughtLineItems FROM 'BoughtLineItems.csv' WITH DELIMITER ',' NULL '' CSV

-- \COPY Product_Rating FROM 'Product_Rating.csv' WITH DELIMITER ',' NULL '' CSV;  

-- \COPY Wishes FROM 'Wishes.csv' WITH DELIMITER ',' NULL '' CSV
-- SELECT pg_catalog.setval('public.wishes_id_seq',
--                          (SELECT MAX(id)+1 FROM Wishes),
--                          false);

\COPY Carts FROM 'Carts.csv' WITH DELIMITER ',' NULL '' CSV

\COPY CartLineItems FROM 'CartLineItems.csv' WITH DELIMITER ',' NULL '' CSV
