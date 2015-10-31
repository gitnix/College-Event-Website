-- Run this code in the SQL tab in the database


CREATE TABLE `users` (
 `user_id` int(8) NOT NULL AUTO_INCREMENT,
 `user_email` varchar(255) NOT NULL,
 `user_password` varchar(255) NOT NULL,
 `user_firstname` varchar(45) NOT NULL,
 `user_lastname` varchar(45) NOT NULL,
 PRIMARY KEY (`user_id`),
 UNIQUE KEY `email` (`user_email`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

CREATE TABLE `universities` (
 `university_id` int(8) NOT NULL AUTO_INCREMENT,
 `university_name` int(255) NOT NULL,
 `university_domain` varchar(45) NOT NULL,
 `university_location` varchar(255) NOT NULL,
 PRIMARY KEY (`university_id`),
 UNIQUE KEY `university_name` (`university_name`,`university_domain`,`university_location`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

CREATE TABLE `user_associates_university` (
 `user_id` int(8) NOT NULL,
 `university_id` int(8) NOT NULL,
 KEY `user_id` (`user_id`),
 KEY `university_id` (`university_id`),
 CONSTRAINT `user_associates_university_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`) ON DELETE CASCADE ON UPDATE CASCADE,
 CONSTRAINT `user_associates_university_ibfk_2` FOREIGN KEY (`university_id`) REFERENCES `universities` (`university_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=latin1;