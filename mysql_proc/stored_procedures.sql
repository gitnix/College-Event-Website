--Run this code in the SQL tab in the database


DELIMITER $$
CREATE DEFINER=`root`@`localhost` PROCEDURE `sp_create_user`(
    IN p_firstname VARCHAR(45),
    IN p_lastname VARCHAR(45),
    IN p_email VARCHAR(255),
    IN p_password VARCHAR(255)
)
BEGIN
    if ( select exists (select 1 from users where user_email = p_email) ) THEN
     
        select 'Username Exists !!';
     
    ELSE
     
        insert into users
        (
            user_firstname,
            user_lastname,
            user_email,
            user_password
        )
        values
        (
            p_firstname,
            p_lastname,
            p_email,
            p_password
        );
     
    END IF;
END$$
DELIMITER ;

----------------------------------------------------------------------------------------

DELIMITER $$
CREATE DEFINER=`root`@`localhost` PROCEDURE `sp_validate_signin`(
    IN p_email VARCHAR(255)
)
BEGIN
    select * from users where user_email = p_email;
END$$
DELIMITER ;

----------------------------------------------------------------------------------------

DELIMITER $$
CREATE DEFINER=`root`@`localhost` PROCEDURE `sp_create_event`(
    IN p_eventName VARCHAR(255),
    IN p_eventType VARCHAR(45),
    IN p_eventDescription VARCHAR(255),
    IN p_eventEmail VARCHAR(255),
    IN p_eventPhone VARCHAR(255)
)
BEGIN
    if ( select exists (select 1 from events where event_email = p_eventEmail) ) THEN
     
        select 'Event Exists !!';
     
    ELSE
     
        insert into events
        (
            event_name,
            event_type,
            event_description,
            event_email,
            event_phone
        )
        values
        (
            p_eventName,
            p_eventType,
            p_eventDescription,
            p_eventEmail,
            p_eventPhone
        );
     
    END IF;
END$$
DELIMITER ;