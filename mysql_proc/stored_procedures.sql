--Run this code in the SQL tab in the database


DELIMITER $$
CREATE DEFINER=`root`@`localhost` PROCEDURE `sp_createUser`(
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
CREATE DEFINER=`root`@`localhost` PROCEDURE `sp_validateSignIn`(
    IN p_email VARCHAR(255)
)
BEGIN
    select * from users where user_email = p_email;
END$$
DELIMITER ;