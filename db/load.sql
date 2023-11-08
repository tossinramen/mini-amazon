\COPY Users FROM 'Users.csv' WITH DELIMITER ',' NULL '' CSV
-- since id is auto-generated; we need the next command to adjust the counter
-- for auto-generation so next INSERT will not clash with ids loaded above:
SELECT pg_catalog.setval('public.users_id_seq',
                         (SELECT MAX(id)+1 FROM Users),
                         false);

\COPY Products FROM 'Products.csv' WITH DELIMITER ',' NULL '' CSV
SELECT pg_catalog.setval('public.products_id_seq',
                         (SELECT MAX(id)+1 FROM Products),
                         false);

\COPY Purchases FROM 'Purchases.csv' WITH DELIMITER ',' NULL '' CSV
SELECT pg_catalog.setval('public.purchases_id_seq',
                         (SELECT MAX(id)+1 FROM Purchases),
                         false);

\COPY Product_Rating FROM 'Product_Rating.csv' WITH DELIMITER ',' NULL '' CSV;  

\COPY Wishes FROM 'Wishes.csv' WITH DELIMITER ',' NULL '' CSV
SELECT pg_catalog.setval('public.wishes_id_seq',
                         (SELECT MAX(id)+1 FROM Wishes),
                         false);

\COPY Sellers FROM 'Sellers.csv' WITH DELIMITER ',' NULL '' CSV;

\COPY Seller_Inventory FROM 'Seller_Inventory.csv' WITH DELIMITER ',' NULL '' CSV;

\COPY Carts FROM 'Carts.csv' WITH DELIMITER ',' NULL '' CSV
SELECT pg_catalog.setval('public.carts_cid_seq',
                         (SELECT MAX(cid)+1 FROM Carts),
                         false);

\COPY CartLineItems FROM 'CartLineItems.csv' WITH DELIMITER ',' NULL '' CSV
SELECT pg_catalog.setval('public.lineitems_liid_seq',
                         (SELECT MAX(id)+1 FROM CartLineItems),
                         false);

\COPY BoughtLineItems FROM 'BoughtLineItems.csv' WITH DELIMITER ',' NULL '' CSV
SELECT pg_catalog.setval('public.lineitems_liid_seq',
                         (SELECT MAX(id)+1 FROM BoughtLineItems),
                         false);



