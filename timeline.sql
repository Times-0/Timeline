SET sql_mode = '';
--
-- Table structure for table `ASSETs`
--

CREATE TABLE IF NOT EXISTS `assets` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `penguin_id` int(11) DEFAULT NULL,
  `item` int(11) NOT NULL COMMENT 'igloo/furniture/location/floor id',
  `type` varchar(3) NOT NULL COMMENT 'i = igloo, f = furn, l = location, fl = floor',
  `purchased` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `quantity` smallint(2) NOT NULL DEFAULT '1',
  PRIMARY KEY (`id`)
) ;

-- --------------------------------------------------------

--
-- Table structure for table `avatars`
--

CREATE TABLE IF NOT EXISTS `avatars` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `penguin_id` int(11) DEFAULT NULL,
  `avatar` int(11) NOT NULL DEFAULT '0',
  `head` int(11) NOT NULL DEFAULT '0',
  `face` int(11) NOT NULL DEFAULT '0',
  `neck` int(11) NOT NULL DEFAULT '0',
  `feet` int(11) NOT NULL DEFAULT '0',
  `hand` int(11) NOT NULL DEFAULT '0',
  `body` int(11) NOT NULL DEFAULT '0',
  `photo` int(11) NOT NULL DEFAULT '0',
  `pin` int(11) NOT NULL DEFAULT '0',
  `color` int(11) NOT NULL DEFAULT '1',
  `language` tinyint(2) NOT NULL DEFAULT '1',
  PRIMARY KEY (`id`),
  UNIQUE KEY `penguin` (`penguin_id`)
) ;

-- --------------------------------------------------------

--
-- Table structure for table `bans`
--

DROP TABLE IF EXISTS `bans`;
CREATE TABLE IF NOT EXISTS `bans` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `penguin_id` int(11) DEFAULT NULL,
  `moderator` int(11) NOT NULL DEFAULT '0',
  `comment` text NOT NULL,
  `expire` timestamp NOT NULL,
  `time` timestamp NOT NULL,
  `type` tinyint(1) NOT NULL DEFAULT '1',
  PRIMARY KEY (`id`)
) ;

-- --------------------------------------------------------

--
-- Table structure for table `care_items`
--

DROP TABLE IF EXISTS `care_items`;
CREATE TABLE IF NOT EXISTS `care_items` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `penguin_id` int(11) DEFAULT NULL,
  `item` int(11) NOT NULL,
  `quantity` smallint(2) NOT NULL DEFAULT '1',
  `last_used` timestamp NOT NULL,
  `purchased` timestamp NOT NULL,
  PRIMARY KEY (`id`)
) ;

-- --------------------------------------------------------

--
-- Table structure for table `coins`
--

DROP TABLE IF EXISTS `coins`;
CREATE TABLE IF NOT EXISTS `coins` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `penguin_id` int(11) NOT NULL,
  `transaction` int(11) NOT NULL,
  `comment` text NOT NULL,
  `time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ;

-- --------------------------------------------------------

--
-- Table structure for table `currencies`
--

DROP TABLE IF EXISTS `currencies`;
CREATE TABLE IF NOT EXISTS `currencies` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `penguin_id` int(11) DEFAULT NULL,
  `GOLDEN_NUGGETS` int(11) DEFAULT 0,
  `quest` text NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `penguin` (`penguin_id`)
) ;

-- --------------------------------------------------------

--
-- Table structure for table `epfcoms`
--

DROP TABLE IF EXISTS `epfcoms`;
CREATE TABLE IF NOT EXISTS `epfcoms` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `mascot` int(11) NOT NULL,
  `message` text NOT NULL,
  `time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ;

INSERT INTO `epfcoms` (`id`, `mascot`, `message`, `time`) VALUES (NULL, '1', 'Squad! welcome to the Elite Penguin Force. This is powered by Timeline.', CURRENT_TIMESTAMP);
-- --------------------------------------------------------

--
-- Table structure for table `friends`
--

DROP TABLE IF EXISTS `friends`;
CREATE TABLE IF NOT EXISTS `friends` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `penguin_id` int(11) DEFAULT NULL,
  `penguin_swid` varchar(40) NOT NULL,
  `friend` varchar(40) NOT NULL,
  `befriended` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `bff` tinyint(1) NOT NULL DEFAULT '0',
  PRIMARY KEY (`id`),
  UNIQUE KEY `penguin_id` (`penguin_id`,`friend`)
) ;

-- --------------------------------------------------------

--
-- Table structure for table `igloos`
--

DROP TABLE IF EXISTS `igloos`;
CREATE TABLE IF NOT EXISTS `igloos` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `penguin_id` int(11) NOT NULL,
  `type` int(11) NOT NULL DEFAULT '1',
  `floor` int(11) NOT NULL DEFAULT '0',
  `music` int(11) NOT NULL DEFAULT '0',
  `location` int(11) NOT NULL DEFAULT '1',
  `locked` tinyint(1) NOT NULL DEFAULT '1',
  PRIMARY KEY (`id`)
) ;

-- --------------------------------------------------------

--
-- Table structure for table `igloo_furnitures`
--

DROP TABLE IF EXISTS `igloo_furnitures`;
CREATE TABLE IF NOT EXISTS `igloo_furnitures` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `igloo_id` int(11) NOT NULL,
  `furn_id` int(11) NOT NULL,
  `x` int(11) NOT NULL,
  `y` int(11) NOT NULL,
  `rotate` int(11) NOT NULL,
  `frame` int(11) NOT NULL,
  PRIMARY KEY (`id`)
) ;

-- --------------------------------------------------------

--
-- Table structure for table `igloo_likes`
--

DROP TABLE IF EXISTS `igloo_likes`;
CREATE TABLE IF NOT EXISTS `igloo_likes` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `igloo_id` int(11) NOT NULL,
  `penguin_swid` varchar(40) NOT NULL,
  `likes` int(11) NOT NULL,
  `time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `penguin_swid` (`penguin_swid`,`igloo_id`)
) ;

-- --------------------------------------------------------

--
-- Table structure for table `ignores`
--

DROP TABLE IF EXISTS `ignores`;
CREATE TABLE IF NOT EXISTS `ignores` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `penguin_id` int(11) DEFAULT NULL,
  `ignored` int(11) NOT NULL,
  `ignored_on` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `penguin_id` (`penguin_id`,`ignored`)
) ;

-- --------------------------------------------------------

--
-- Table structure for table `inventories`
--

DROP TABLE IF EXISTS `inventories`;
CREATE TABLE IF NOT EXISTS `inventories` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `penguin_id` int(11) DEFAULT NULL,
  `item` int(11) NOT NULL,
  `purchased` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `comments` text NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `penguin_id` (`penguin_id`,`item`)
) ;

-- --------------------------------------------------------

--
-- Table structure for table `mails`
--

DROP TABLE IF EXISTS `mails`;
CREATE TABLE IF NOT EXISTS `mails` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `penguin_id` int(11) NOT NULL COMMENT 'to_user',
  `from_user` int(11) NOT NULL,
  `type` int(11) NOT NULL,
  `description` varchar(100) NOT NULL,
  `sent_on` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `opened` tinyint(1) NOT NULL DEFAULT '0',
  `junk` tinyint(1) NOT NULL DEFAULT '0',
  PRIMARY KEY (`id`)
) ;

-- --------------------------------------------------------

--
-- Table structure for table `memberships`
--

DROP TABLE IF EXISTS `memberships`;
CREATE TABLE IF NOT EXISTS `memberships` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `penguin_id` int(11) DEFAULT NULL,
  `redeemed_on` timestamp NOT NULL,
  `expires` timestamp NOT NULL,
  `comments` text NOT NULL,
  PRIMARY KEY (`id`)
) ;

-- --------------------------------------------------------

--
-- Table structure for table `music_tracks`
--

DROP TABLE IF EXISTS `music_tracks`;
CREATE TABLE IF NOT EXISTS `music_tracks` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `penguin_id` int(11) DEFAULT NULL,
  `data` text NOT NULL,
  `hash` varchar(40) NOT NULL,
  `deleted` tinyint(1) NOT NULL,
  `likes` int(11) NOT NULL,
  `created_on` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ;

-- --------------------------------------------------------

--
-- Table structure for table `ninjas`
--

DROP TABLE IF EXISTS `ninjas`;
CREATE TABLE IF NOT EXISTS `ninjas` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `penguin_id` int(11) NOT NULL,
  `belt` int(11) NOT NULL,
  `fire` tinyint(3) NOT NULL DEFAULT '0',
  `water` tinyint(3) NOT NULL DEFAULT '0',
  `snow` tinyint(3) NOT NULL DEFAULT '0',
  `cards` text NOT NULL,
  `matches` text,
  `fire_matches` text,
  `water_matches` text,
  PRIMARY KEY (`id`),
  UNIQUE KEY `penguin_id` (`penguin_id`)
) ;

-- --------------------------------------------------------

--
-- Table structure for table `penguins`
--

DROP TABLE IF EXISTS `penguins`;
CREATE TABLE IF NOT EXISTS `penguins` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `username` varchar(12) NOT NULL,
  `password` text NOT NULL,
  `swid` char(38) NOT NULL,
  `nickname` varchar(20) NOT NULL,
  `email` varchar(50) NOT NULL,
  `hash` text,
  `create` timestamp NOT NULL,
  `last_update` timestamp NOT NULL,
  `moderator` tinyint(1) NOT NULL DEFAULT '0',
  `igloo` int(11) NOT NULL DEFAULT '0',
  `search_msg` text,
  `cover_color` int(11) DEFAULT '0',
  `cover_highlight` int(11) DEFAULT '0',
  `cover_pattern` int(11) DEFAULT '0',
  `cover_icon` int(11) DEFAULT '0',
  `agent` INT(1) NOT NULL DEFAULT '0',
  `epf` VARCHAR(50) NOT NULL DEFAULT '0%0',
  PRIMARY KEY (`id`),
  UNIQUE KEY `swid` (`swid`),
  UNIQUE KEY `username` (`username`)
) ;
-- --------------------------------------------------------
--
-- Dumping data for table `penguins`
--

INSERT INTO `penguins` (`id`, `username`, `password`, `swid`, `nickname`, `email`, `hash`, `create`, `last_update`, `moderator`, `igloo`, `search_msg`, `cover_color`, `cover_highlight`, `cover_pattern`, `cover_icon`) VALUES
(103, 'test', '5f4dcc3b5aa765d61d8327deb882cf99', '{3ed9b6d7-fd16-11e8-aad3-00f48d43ccb2}', 'Peanut', 'peanutlabs@bill.com', '', '2017-02-21 18:30:00', '2018-12-13 05:56:51', 1, 26, NULL, 2, 4, 4, 2);

-- --------------------------------------------------------
--
-- Triggers `penguins`
--
DROP TRIGGER IF EXISTS `penguins_OnInsert`;

CREATE TRIGGER `penguins_OnInsert` BEFORE INSERT ON `penguins` FOR EACH ROW IF NEW.`swid` IS NULL OR NEW.`swid` = '' THEN
	SET NEW.`swid` = CONCAT('{', uuid(), '}');
END IF
;

-- --------------------------------------------------------

--
-- Table structure for table `puffles`
--

-- DROP TABLE IF EXISTS `puffles`;
CREATE TABLE IF NOT EXISTS `puffles` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `penguin_id` int(11) DEFAULT NULL,
  `name` varchar(20) NOT NULL,
  `type` int(11) NOT NULL,
  `subtype` int(11) NOT NULL,
  `adopted` timestamp NOT NULL,
  `food` smallint(3) NOT NULL DEFAULT '100',
  `play` smallint(3) NOT NULL DEFAULT '100',
  `rest` smallint(3) NOT NULL DEFAULT '100',
  `clean` smallint(3) NOT NULL DEFAULT '100',
  `hat` int(11) NOT NULL DEFAULT '0',
  `backyard` tinyint(1) NOT NULL DEFAULT '0',
  `walking` tinyint(1) NOT NULL DEFAULT '0',
  `lastcare` text NOT NULL,
  PRIMARY KEY (`id`)
) ;

-- --------------------------------------------------------

--
-- Table structure for table `requests`
--

-- DROP TABLE IF EXISTS `requests`;
CREATE TABLE IF NOT EXISTS `requests` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `penguin_id` int(11) DEFAULT NULL,
  `penguin_swid` varchar(40) NOT NULL,
  `requested_by` varchar(40) NOT NULL,
  `applied_on` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `penguin_swid` (`penguin_swid`),
  UNIQUE KEY `penguin_id` (`penguin_id`,`requested_by`)
) ;

-- --------------------------------------------------------

--
-- Table structure for table `stamps`
--

-- DROP TABLE IF EXISTS `stamps`;
CREATE TABLE IF NOT EXISTS `stamps` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `penguin_id` int(11) DEFAULT NULL,
  `stamp` int(11) NOT NULL,
  `earned` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `penguin_id` (`penguin_id`,`stamp`)
) ;

-- --------------------------------------------------------

--
-- Table structure for table `stamp_covers`
--

-- DROP TABLE IF EXISTS `stamp_covers`;
CREATE TABLE IF NOT EXISTS `stamp_covers` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `penguin_id` int(11) DEFAULT NULL,
  `stamp` int(11) NOT NULL,
  `type` int(11) NOT NULL,
  `x` int(11) NOT NULL,
  `y` int(11) NOT NULL,
  `rotation` int(11) NOT NULL,
  `depth` int(11) NOT NULL,
  PRIMARY KEY (`id`)
) ;

-- --------------------------------------------------------

COMMIT;
------- PROCEDURES ------------- 
DROP FUNCTION IF EXISTS `SPLIT_STRING`;
CREATE DEFINER=`root`@`localhost` FUNCTION `SPLIT_STRING` (`s` VARCHAR(1024), `del` CHAR(1), `i` INT) RETURNS VARCHAR(1024) CHARSET latin1 BEGIN

    DECLARE n INT ;

    -- get max number of items
    SET n = LENGTH(s) - LENGTH(REPLACE(s, del, '')) + 1;

    IF i > n THEN
        RETURN NULL ;
    ELSE
        RETURN SUBSTRING_INDEX(SUBSTRING_INDEX(s, del, i) , del , -1 ) ;        
    END IF;

END;
-- --------------------------------------------------------
DROP PROCEDURE IF EXISTS `IMPORT_ASSETS_FROM_CP_STRUCT`;
CREATE DEFINER=`root`@`localhost` PROCEDURE `IMPORT_ASSETS_FROM_CP_STRUCT` ()  BEGIN
    DECLARE str VARCHAR(255) ; DECLARE n INT ; DECLARE pn INT; DECLARE total INT; DECLARE time_start TIMESTAMP; DECLARE time_end TIMESTAMP;
    DECLARE X INT; DECLARE _id INT; DECLARE _date TIMESTAMP; DECLARE _qty INT;
    
    SET time_start = CURRENT_TIMESTAMP;
        
    SELECT COUNT(*) FROM `times-cp`.`penguins` INTO n ;
    
    SET pn = 0 ; 
    SET total = 0;
    
    WHILE pn < n DO 
        SELECT `id`, `igloos`, `furnitures`, `floors`, `locations`, `care` INTO @id, @igloo, @furn, @floor, @loc, @care FROM `times-cp`.`penguins` LIMIT pn, 1;
        SET X = 1;
        
        loop_label: 
            WHILE TRUE DO
            SET str = SPLIT_STRING(@igloo, ',', X) ; 
            IF str IS NULL THEN 
                SET total = total + x;
                LEAVE loop_label ;
            END IF;
            
            SET _id = SPLIT_STRING(str, '|', 1);
            SET _date = SPLIT_STRING(str, '|', 2);
            
            INSERT IGNORE INTO `timeline`.`assets` (`penguin_id`, `item`, `type`, `purchased`, `quantity`) VALUES (@id, _id, 'i', _date, 1);
            
            SET X = X + 1 ;
        END WHILE ;
        
        SET X = 1;
        
        loop_label: 
            WHILE TRUE DO
            SET str = SPLIT_STRING(@floor, ',', X) ; 
            IF str IS NULL THEN 
                SET total = total + x;
                LEAVE loop_label ;
            END IF;
            
            SET _id = SPLIT_STRING(str, '|', 1);
            SET _date = SPLIT_STRING(str, '|', 2);
            
            INSERT IGNORE INTO `timeline`.`assets` (`penguin_id`, `item`, `type`, `purchased`, `quantity`) VALUES (@id, _id, 'fl', _date, 1);
            
            SET X = X + 1 ;
        END WHILE ;
        
        SET X = 1;
        
        loop_label: 
            WHILE TRUE DO
            SET str = SPLIT_STRING(@loc, ',', X) ; 
            IF str IS NULL THEN 
                SET total = total + x;
                LEAVE loop_label ;
            END IF;
            
            SET _id = SPLIT_STRING(str, '|', 1);
            SET _date = SPLIT_STRING(str, '|', 2);
            
            INSERT IGNORE INTO `timeline`.`assets` (`penguin_id`, `item`, `type`, `purchased`, `quantity`) VALUES (@id, _id, 'l', _date, 1);
            
            SET X = X + 1 ;
        END WHILE ;
        
        SET X = 1;
        
        loop_label: 
            WHILE TRUE DO
            SET str = SPLIT_STRING(@furn, ',', X) ; 
            IF str IS NULL THEN 
                SET total = total + x;
                LEAVE loop_label ;
            END IF;
            
            SET _id = SPLIT_STRING(str, '|', 1);
            SET _date = SPLIT_STRING(str, '|', 2);
            SET _qty = SPLIT_STRING(str, '|', 3);
            
            INSERT IGNORE INTO `timeline`.`assets` (`penguin_id`, `item`, `type`, `purchased`, `quantity`) VALUES (@id, _id, 'f', _date, _qty);
            
            SET X = X + 1 ;
        END WHILE ;
        SET X = 1;
        
        loop_label: 
            WHILE TRUE DO
            SET str = SPLIT_STRING(@care, '%', X) ; 
            IF str IS NULL THEN 
                SET total = total + x;
                LEAVE loop_label ;
            END IF;
            
            SET _id = SPLIT_STRING(str, '|', 1);
            SET _qty = SPLIT_STRING(str, '|', 2);
            
            INSERT IGNORE INTO `timeline`.`care_items` (`penguin_id`, `item`, `quantity`) VALUES (@id, _id, _qty);
            
            SET X = X + 1 ;
        END WHILE ;
        
        SET pn = pn + 1 ;
    END WHILE ;
    
    SET time_END = CURRENT_TIMESTAMP;
    
    SELECT n AS "Total penguin assets parsed", CONCAT(TIMESTAMPDIFF(SECOND, time_start, time_end), " (s)") AS "Parsed in"; 
END;
-- --------------------------------------------------------
DROP PROCEDURE IF EXISTS `IMPORT_FRIENDS_FROM_CP_STRUCT`;
CREATE DEFINER=`root`@`localhost` PROCEDURE `IMPORT_FRIENDS_FROM_CP_STRUCT` ()  BEGIN
    DECLARE str VARCHAR(255) ; DECLARE n INT ; DECLARE pn INT; DECLARE total INT; DECLARE time_start TIMESTAMP; DECLARE time_end TIMESTAMP;
    DECLARE n1 INT; DECLARE n2 INT; DECLARE n3 INT; DECLARE X INT;

    SET time_start = CURRENT_TIMESTAMP;
        
    SELECT COUNT(*) FROM `times-cp`.`friends` INTO n;
    SET pn = 0;
    
    loop1:
        WHILE pn < n DO
            SELECT `id`, `swid`, `friends`, `requests` INTO @lol, @pswid, @friends, @requests FROM `times-cp`.`friends` LIMIT pn, 1;
            SELECT `id` INTO @pid FROM `times-cp`.`penguins` WHERE `swid` = @pswid;
            
            SET pn = pn + 1;

            IF @pid IS NOT NULL THEN
                
            
			SET X = 1;
            loop_labe1:
            	WHILE TRUE DO
                SET str = SPLIT_STRING(@friends, ',', X);
                IF str IS NULL THEN 
                	LEAVE loop_labe1;
            	END IF;
            	
                
                SET @fid = SPLIT_STRING(str, '|', 1);
                SET @fbff = SPLIT_STRING(str, '|', 2);
                
                INSERT IGNORE INTO `timeline`.`friends` VALUES (NULL, @pid, @pswid, @fid, CURRENT_TIMESTAMP, @fbff);
                
                SET X = X + 1;
                
                END WHILE;
            
            SET X = 1;
            loop_labe2:
            	WHILE TRUE DO
                SET str = SPLIT_STRING(@requests, ',', X);
                IF str IS NULL THEN 
                	LEAVE loop_labe2;
            	END IF;
               
                SET @fid = SPLIT_STRING(str, '|', 1);
                
                INSERT IGNORE INTO `requests` VALUES (NULL, @pid, @pswid, @fid, CURRENT_TIMESTAMP);
                
                SET X = X + 1;
                
                END WHILE;
            
            END IF;
			
            
        END WHILE;        
    SET time_END = CURRENT_TIMESTAMP;
    
    SELECT "Parsed", CONCAT(n, " in ", TIMESTAMPDIFF(SECOND, time_start, time_end), " (s)") as "Friend data";
END;
-- --------------------------------------------------------
DROP PROCEDURE IF EXISTS `IMPORT_INVENTORY_FROM_CP_STRUCT`;
CREATE DEFINER=`root`@`localhost` PROCEDURE `IMPORT_INVENTORY_FROM_CP_STRUCT` ()  BEGIN
    DECLARE
        X INT ; DECLARE str VARCHAR(255) ; DECLARE n INT ; DECLARE pn INT; DECLARE total INT; DECLARE time_start TIMESTAMP; DECLARE time_end TIMESTAMP;
    
    SET time_start = CURRENT_TIMESTAMP;
        
    SELECT COUNT(*) FROM `times-cp`.`penguins` INTO n ;
    
	SET pn = 0 ; 
    SET total = 0;
    
    WHILE pn < n DO	
		SET X = 1 ; 
        SELECT id, inventory INTO @id, @inv FROM `times-cp`.`penguins` LIMIT pn, 1;
        
        loop_label: 
        	WHILE TRUE DO
			SET	str = SPLIT_STRING(@inv, '%', X) ; 
            IF str IS NULL THEN 
            	SET total = total + x;
            	LEAVE loop_label ;
			     END IF;
           INSERT IGNORE INTO `timeline`.`inventories` (`penguin_id`, `item`, `comments`) VALUES (@id, str, "Imported from old CP-Styled database");

          
            
			SET X = X + 1 ;
		END WHILE ;
        
		SET pn = pn + 1 ;
	END WHILE ;
    SET time_END = CURRENT_TIMESTAMP;
    
    SELECT n AS "Total penguins parsed", total as "Total inventory items parsed", CONCAT(TIMESTAMPDIFF(SECOND, time_start, time_end), " (s)") AS "Parsed in"; 
END;
-- --------------------------------------------------------
DROP PROCEDURE IF EXISTS `IMPORT_PENGUIN_FROM_CP_STRUCT`;
CREATE DEFINER=`root`@`localhost` PROCEDURE `IMPORT_PENGUIN_FROM_CP_STRUCT` ()  BEGIN
    DECLARE str VARCHAR(255) ; DECLARE n INT ; DECLARE pn INT; DECLARE total INT; DECLARE time_start TIMESTAMP; DECLARE time_end TIMESTAMP;
    
    SET time_start = CURRENT_TIMESTAMP;
        
    SELECT COUNT(*) FROM `times-cp`.`penguins` INTO n ;
    
    SET pn = 0 ; 
    SET total = 0;
    
    WHILE pn < n DO 
        SELECT `cover` INTO @cov FROM `times-cp`.`penguins` LIMIT pn, 1;
        
        SET @c = SPLIT_STRING(@cov, '%', 1);
        SET @c1 = SPLIT_STRING(@c, '|', 1);
        SET @c2 = SPLIT_STRING(@c, '|', 2);
        SET @c3 = SPLIT_STRING(@c, '|', 3);
        SET @c4 = SPLIT_STRING(@c, '|', 4);
        
        INSERT IGNORE INTO `timeline`.`penguins` (SELECT `id`, `username`, `password`, `swid`, `nickname`, `email`, `hash`, `create`, `last_update`, `moderator`, `igloo`, `search_msg`, @c1, @c2, @c3, @c4 FROM `times-cp`.`penguins` LIMIT pn, 1);
        INSERT IGNORE INTO `timeline`.`avatars` (SELECT NULL, `id`, 0, `head`, `face`, `neck`, `feet`, `hand`, `body`, `photo`, `pin`, `color`, 1 FROM `times-cp`.`penguins` LIMIT pn, 1);
        INSERT IGNORE INTO `timeline`.`coins` (SELECT NULL, `id`, `coins`, "Imported coins from old-db structure.", CURRENT_TIMESTAMP FROM `times-cp`.`penguins` LIMIT pn, 1);
        INSERT IGNORE INTO `timeline`.`memberships` (SELECT NULL, `id`, CURRENT_TIMESTAMP, `membership`, "Imported membership from old-db structure." FROM `times-cp`.`penguins` LIMIT pn, 1);
        
        SET pn = pn + 1 ;
    END WHILE ;
    SET time_END = CURRENT_TIMESTAMP;
    
    SELECT n AS "Total penguin data parsed", CONCAT(TIMESTAMPDIFF(SECOND, time_start, time_end), " (s)") AS "Parsed in"; 
END;
-- --------------------------------------------------------
DROP PROCEDURE IF EXISTS `IMPORT_PUFFLE_FROM_CP_STRUCT`;
-- --------------------------------------------------------
CREATE DEFINER=`root`@`localhost` PROCEDURE `IMPORT_PUFFLE_FROM_CP_STRUCT` ()  BEGIN
    DECLARE str VARCHAR(255) ; DECLARE n INT ; DECLARE pn INT; DECLARE total INT; DECLARE time_start TIMESTAMP; DECLARE time_end TIMESTAMP;
    DECLARE n1 INT; DECLARE n2 INT; DECLARE n3 INT; DECLARE n4 INT; DECLARE n5 INT; DECLARE X INT;

    SET time_start = CURRENT_TIMESTAMP;
        
    SELECT COUNT(*) FROM `times-cp`.`puffles` INTO n ;
    SELECT COUNT(*) FROM `times-cp`.`ninjas` INTO n1;
    SELECT COUNT(*) FROM `times-cp`.`mails` INTO n2;
    SELECT COUNT(*) FROM `times-cp`.`igloos` INTO n3;
    SELECT COUNT(*) FROM `times-cp`.`bans` INTO n4;
    SELECT COUNT(*) FROM `times-cp`.`currencies` INTO n5;
    
    INSERT IGNORE INTO `timeline`.`puffles` (SELECT * FROM `times-cp`.`puffles`);
    INSERT IGNORE INTO `timeline`.`ninjas` (SELECT * FROM `times-cp`.`ninjas`);
    INSERT IGNORE INTO `timeline`.`mails` (SELECT * FROM `times-cp`.`mails`);
    INSERT IGNORE INTO `timeline`.`bans` (SELECT * FROM `times-cp`.`bans`);
    INSERT IGNORE INTO `timeline`.`currencies` (SELECT * FROM `times-cp`.`currencies`);
    INSERT IGNORE INTO `timeline`.`igloos` (SELECT `id`, `owner`, `type`, `floor`, `music`, `location`, `locked` FROM `times-cp`.`igloos`);
    INSERT IGNORE INTO `timeline`.`epfcoms` (SELECT * FROM `times-cp`.`epfcoms`);   
    INSERT IGNORE INTO `timeline`.`music_tracks` (SELECT * FROM `times-cp`.`musictracks`);   
    
	SET pn = 0 ; 
    
    loop1:
    WHILE pn < n3 DO	
		SET X = 1 ; 
        SELECT `id`, `furniture` INTO @igloo_id, @furn FROM `times-cp`.`igloos` LIMIT pn, 1;
        
        loop_label: 
        	WHILE TRUE DO
			SET	str = SPLIT_STRING(@furn, ',', X) ; 
            IF str IS NULL THEN 
            	LEAVE loop_label ;
			END IF;
			
			SET @furn_id    = SPLIT_STRING(str, '|', 1);
			SET @x          = SPLIT_STRING(str, '|', 2);
			SET @y          = SPLIT_STRING(str, '|', 3);
			SET @rotate     = SPLIT_STRING(str, '|', 4);
			SET @frame      = SPLIT_STRING(str, '|', 5);
            
            INSERT IGNORE INTO `timeline`.`igloo_furnitures` (`igloo_id`, `furn_id`, `x`, `y`, `rotate`, `frame`) VALUES (@igloo_id, @furn_id, @x, @y, @rotate, @frame);
            
			SET X = X + 1 ;
		END WHILE ;
        
		SET pn = pn + 1 ;
	END WHILE ;
    
        
    SET time_END = CURRENT_TIMESTAMP;
    
    SELECT "Parsed", CONCAT(n, " in ", TIMESTAMPDIFF(SECOND, time_start, time_end), " (s)") as "Puffles", 
        CONCAT(n1, " in ", TIMESTAMPDIFF(SECOND, time_start, time_end), " (s)") as "Ninjas",
        CONCAT(n2, " in ", TIMESTAMPDIFF(SECOND, time_start, time_end), " (s)") as "Mails",
        CONCAT(n3, " in ", TIMESTAMPDIFF(SECOND, time_start, time_end), " (s)") as "Igloos",
        CONCAT(n4, " in ", TIMESTAMPDIFF(SECOND, time_start, time_end), " (s)") as "Bans",
        CONCAT(n5, " in ", TIMESTAMPDIFF(SECOND, time_start, time_end), " (s)") as "Currencies";
END;
-- --------------------------------------------------------
DROP PROCEDURE IF EXISTS `IMPORT_STAMP_FROM_CP_STRUCT`;
-- --------------------------------------------------------
CREATE DEFINER=`root`@`localhost` PROCEDURE `IMPORT_STAMP_FROM_CP_STRUCT` ()  BEGIN
    DECLARE
        X INT ; DECLARE str VARCHAR(255) ; DECLARE n INT ; DECLARE pn INT; DECLARE total INT; DECLARE time_start TIMESTAMP; DECLARE time_end TIMESTAMP;
    
    SET time_start = CURRENT_TIMESTAMP;
        
    SELECT COUNT(*) FROM `times-cp`.`penguins` INTO n ;
    
    SET pn = 0 ; 
    SET total = 0;
    
    WHILE pn < n DO 
        SET X = 2 ; 
        SELECT id, stamps, cover INTO @id, @stm, @cover FROM `times-cp`.`penguins` LIMIT pn, 1;
        
        loop_label1: 
            WHILE TRUE DO
            SET str = SPLIT_STRING(@cover, '%', X) ; 
            IF str IS NULL THEN 
                LEAVE loop_label1 ;
            END IF;
            
            SET @st = SPLIT_STRING(str, '|', 1);
            SET @sid = SPLIT_STRING(str, '|', 2);
            SET @sx = SPLIT_STRING(str, '|', 3);
            SET @sy = SPLIT_STRING(str, '|', 4);
            SET @srot = SPLIT_STRING(str, '|', 5);
            SET @sdpth = SPLIT_STRING(str, '|', 6);
            
            
            INSERT IGNORE INTO `timeline`.`stamp_covers` VALUES (NULL, @id, @sid, @st, @sx, @sy, @srot, @sdpth);
            
            SET X = X + 1 ;
        END WHILE ;
        
        SET X = 1;
        
        loop_label: 
            WHILE TRUE DO
            SET str = SPLIT_STRING(@stm, '|', X) ; 
            IF str IS NULL THEN 
                SET total = total + x;
                LEAVE loop_label ;
            END IF;
            
            SET @sid = SPLIT_STRING(str, ',', 1);
            SET @sdt = SPLIT_STRING(str, ',', 2);
            
            INSERT IGNORE INTO `timeline`.`stamps` VALUES (NULL, @id, @sid, @sdt);
            
            SET X = X + 1 ;
        END WHILE ;
        
        SET pn = pn + 1 ;
    END WHILE ;
    SET time_END = CURRENT_TIMESTAMP;
    
    SELECT n AS "Total StampBook parsed", total as "Total stamps items parsed", CONCAT(TIMESTAMPDIFF(SECOND, time_start, time_end), " (s)") AS "Parsed in"; 
END;
-- --------------------------------------------------------
-- --------------------------------------------------------
-- --------------------------------------------------------
COMMIT;
