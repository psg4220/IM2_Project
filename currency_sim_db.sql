CREATE TABLE `currency` ( 
  `id` INT AUTO_INCREMENT NOT NULL,
  `name` VARCHAR(250) NOT NULL,
  `master_currency_balance_id` INT NULL,
  CONSTRAINT `PRIMARY` PRIMARY KEY (`id`)
);
CREATE TABLE `currency_balance` ( 
  `id` INT AUTO_INCREMENT NOT NULL,
  `account_id` INT NOT NULL,
  `currency_id` INT NOT NULL,
  `balance` DECIMAL(12,2) NOT NULL,
  CONSTRAINT `PRIMARY` PRIMARY KEY (`id`)
);
CREATE TABLE `transaction_record` ( 
  `id` INT AUTO_INCREMENT NOT NULL,
  `sender_currency_balance_id` INT NOT NULL,
  `receiver_currency_balance_id` INT NOT NULL,
  `amount` DECIMAL(12,2) NOT NULL,
  `time_created` DATETIME NOT NULL,
  CONSTRAINT `PRIMARY` PRIMARY KEY (`id`)
);
CREATE TABLE `username` ( 
  `id` INT AUTO_INCREMENT NOT NULL,
  `username` VARCHAR(250) NOT NULL,
  `pass` VARCHAR(250) NULL,
  CONSTRAINT `PRIMARY` PRIMARY KEY (`id`)
);
ALTER TABLE `currency_balance` ADD CONSTRAINT `FK_currency_balance_account_id` FOREIGN KEY (`account_id`) REFERENCES `username` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION;
ALTER TABLE `currency_balance` ADD CONSTRAINT `FK_currency_balance_currency_id` FOREIGN KEY (`currency_id`) REFERENCES `currency` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION;
ALTER TABLE `transaction_record` ADD CONSTRAINT `FK_transaction_record_receiver_currency_balance_id` FOREIGN KEY (`receiver_currency_balance_id`) REFERENCES `currency_balance` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION;
ALTER TABLE `transaction_record` ADD CONSTRAINT `FK_transaction_record_sender_currency_balance_id` FOREIGN KEY (`sender_currency_balance_id`) REFERENCES `currency_balance` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION;

CREATE VIEW `currency_balance_view` AS
SELECT
    cb.id AS balance_id,
    u.username AS account_name,
    c.name AS currency_name,
    cb.balance
FROM
    currency_sim_db.currency_balance cb
JOIN
    currency_sim_db.username u ON cb.account_id = u.id
JOIN
    currency_sim_db.currency c ON cb.currency_id = c.id
ORDER BY
    cb.id;


CREATE VIEW `transaction_record_view` AS
SELECT
    tr.id AS transaction_id,
    sender_username.username AS sender_account,
    receiver_username.username AS receiver_account,
    tr.amount,
    tr.time_created
FROM
    currency_sim_db.transaction_record tr
JOIN
    currency_sim_db.currency_balance sender ON tr.sender_currency_balance_id = sender.id
JOIN
    currency_sim_db.currency_balance receiver ON tr.receiver_currency_balance_id = receiver.id
JOIN
    currency_sim_db.username sender_username ON sender.account_id = sender_username.id
JOIN
    currency_sim_db.username receiver_username ON receiver.account_id = receiver_username.id
ORDER BY
    tr.id;

CREATE VIEW account_public AS
SELECT id, username
FROM username;



DELIMITER //

-- Procedures;

CREATE PROCEDURE transfer_funds(
    IN p_sender_account_id INT,
    IN p_sender_password VARCHAR(250),
    IN p_receiver_account_id INT,
    IN p_currency_id INT,
    IN p_amount DECIMAL(12,2)
)
BEGIN
    DECLARE sender_balance DECIMAL(12,2);
    DECLARE receiver_balance DECIMAL(12,2);
    DECLARE receiver_account_count INT;

    -- Check if sender account exists and password is correct
    SELECT balance INTO sender_balance
    FROM currency_balance cb
    INNER JOIN username u ON cb.account_id = u.id
    WHERE cb.account_id = p_sender_account_id AND cb.currency_id = p_currency_id AND u.pass = p_sender_password;

    -- Check if receiver account has a row for the specified currency
    SELECT balance INTO receiver_balance
    FROM currency_balance
    WHERE account_id = p_receiver_account_id AND currency_id = p_currency_id;

    -- Check if reciever account exists
    SELECT COUNT(*) INTO receiver_account_count
    FROM username
    WHERE id = p_receiver_account_id AND p_receiver_account_id != 0;

    IF receiver_account_count = 0 THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Receiver account doesnt exist';
    END IF;

    IF p_amount <= 0 THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Amount must be greater than zero';
    END IF;

    IF sender_balance IS NOT NULL AND sender_balance >= p_amount THEN
        -- Update sender's balance
        UPDATE currency_balance
        SET balance = balance - p_amount
        WHERE account_id = p_sender_account_id AND currency_id = p_currency_id;

        IF receiver_balance IS NOT NULL THEN
            -- Update receiver's balance
            UPDATE currency_balance
            SET balance = balance + p_amount
            WHERE account_id = p_receiver_account_id AND currency_id = p_currency_id;
        ELSE
            -- Insert a new row for the receiver
            INSERT INTO currency_balance (account_id, currency_id, balance)
            VALUES (p_receiver_account_id, p_currency_id, p_amount);
        END IF;

        -- Record the transaction
        INSERT INTO transaction_record (
            sender_currency_balance_id,
            receiver_currency_balance_id,
            amount,
            time_created
        ) VALUES (
            (SELECT id FROM currency_balance WHERE account_id = p_sender_account_id AND currency_id = p_currency_id),
            COALESCE((SELECT id FROM currency_balance WHERE account_id = p_receiver_account_id AND currency_id = p_currency_id), LAST_INSERT_ID()),
            p_amount,
            NOW() -- You can use the current timestamp function of your DBMS
        );

        SELECT 'Transaction successful' AS status;
    ELSE
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Transaction failed. Either insufficient Balance or Invalid sender ID';
    END IF;
END

CREATE PROCEDURE `create_currency`(
    IN in_currency_name VARCHAR(250),
    IN in_master_currency_id INT,
    IN in_master_currency_pass VARCHAR(250),
    IN in_max_supply DECIMAL(12,2)
)
BEGIN
    -- Check if the currency with the given name already exists
    DECLARE currency_count INT;

    IF NOT EXISTS (SELECT 1 FROM username WHERE id = in_master_currency_id AND pass = in_master_currency_pass) THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Account doesnt exist';
    END IF;

    SELECT COUNT(*) INTO currency_count FROM currency WHERE name = in_currency_name;

    IF currency_count > 0 THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Currency with this name already exists';
    END IF;

    -- Insert new currency
    INSERT INTO currency(name, master_currency_balance_id)
    VALUES (in_currency_name, in_master_currency_id);

    INSERT INTO currency_balance(account_id, currency_id, balance)
    VALUES (in_master_currency_id, LAST_INSERT_ID(), in_max_supply);
    SET @last_currency_id := LAST_INSERT_ID();
    INSERT INTO transaction_record(sender_currency_balance_id, receiver_currency_balance_id, amount, time_created)
    VALUES (@last_currency_id, @last_currency_id, in_max_supply, NOW());

END

CREATE PROCEDURE `create_account`(
    IN p_username VARCHAR(250),
    IN p_pass VARCHAR(250)
)
BEGIN

    IF EXISTS(SELECT 1 FROM username WHERE username = p_username) THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Account already exist';
    END IF;

    INSERT INTO username(username, pass)
    VALUES (p_username, p_pass);

END

CREATE PROCEDURE delete_account(
    IN p_username VARCHAR(250),
    IN p_password VARCHAR(250)
)
BEGIN
    DELETE FROM username WHERE username = p_username AND pass = p_password;
END

-- Triggers;

CREATE TRIGGER is_same_sender_receiver
BEFORE INSERT
ON transaction_record
FOR EACH ROW
BEGIN
    DECLARE source_number INT;

    -- Count the number of records with the same sender and receiver currency balance IDs
    SELECT COUNT(*) INTO source_number
    FROM transaction_record
    WHERE sender_currency_balance_id = NEW.sender_currency_balance_id
    AND receiver_currency_balance_id = NEW.receiver_currency_balance_id
    AND NEW.sender_currency_balance_id = NEW.receiver_currency_balance_id;

    -- Check if there is already a record with the same sender and receiver
    IF source_number = 1 THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Sender and receiver currency balance IDs cannot be the same';
    END IF;
END

CREATE TRIGGER account_deleted
BEFORE DELETE
ON username
FOR EACH ROW
BEGIN
    UPDATE currency SET master_currency_balance_id = 0 WHERE master_currency_balance_id = OLD.id;
    UPDATE currency_balance SET account_id = 0 WHERE account_id = OLD.id;
END

//

DELIMITER ;

