--Run this code in the SQL tab in the database


DELIMITER $$
delete from mysql.proc;
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

----------------------------------------------------------------------------------------

DELIMITER $$
CREATE PROCEDURE `sp_get_events_by_type` (
IN p_event_type VARCHAR(45)
)
BEGIN
    select * from events where event_type = p_event_type;
END$$
 
DELIMITER ;


DELIMITER $$
CREATE PROCEDURE `sp_get_messages_by_user` (
IN p_user_id int(8)
)
BEGIN
    select
    m.message_header,
    m.message_content, 
    m.creation_time,
    receiver.user_email,
    receiver.user_firstname,
    receiver.user_lastname,
    sender.user_email,
    sender.user_firstname,
    sender.user_lastname
    from messages m 
    inner join users receiver on receiver.user_id = m.to_user_id
    inner join users sender on sender.user_id = m.from_user_id
    where
    m.to_user_id = p_user_id;
END$$
DELIMITER ;;

----------------------------------------------------------------------------------------

DELIMITER $$
CREATE PROCEDURE `sp_get_event` (
IN p_event_id int(8)
)
BEGIN
    select * from events where event_id = p_event_id;
END$$
 
DELIMITER ;

