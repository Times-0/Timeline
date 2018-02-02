-- phpMyAdmin SQL Dump
-- version 4.7.4
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: Jan 20, 2018 at 05:16 PM
-- Server version: 10.1.28-MariaDB
-- PHP Version: 7.1.10

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
SET AUTOCOMMIT = 0;
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `times-cp`
--

-- --------------------------------------------------------

--
-- Table structure for table `bans`
--

CREATE TABLE `bans` (
  `id` int(11) NOT NULL,
  `player` int(11) NOT NULL,
  `moderator` int(11) NOT NULL,
  `comment` text NOT NULL,
  `expire` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `type` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

--
-- Dumping data for table `bans`
--

INSERT INTO `bans` (`id`, `player`, `moderator`, `comment`, `expire`, `time`, `type`) VALUES
(1, 3, 4, 'Ban test', '2017-11-07 13:20:00', '2017-11-07 12:56:02', 1);

-- --------------------------------------------------------

--
-- Table structure for table `currencies`
--

CREATE TABLE `currencies` (
  `id` int(11) NOT NULL,
  `pid` int(11) NOT NULL,
  `GOLDEN_NUGGETS` int(11) NOT NULL DEFAULT '0',
  `quest` text NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;


-- --------------------------------------------------------

--
-- Table structure for table `epfcoms`
--

CREATE TABLE `epfcoms` (
  `id` int(11) NOT NULL,
  `mascot` int(11) NOT NULL,
  `message` text NOT NULL,
  `time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

--
-- Dumping data for table `epfcoms`
--

INSERT INTO `epfcoms` (`id`, `mascot`, `message`, `time`) VALUES
(1, 16, 'Welcome agent. This server is powered by Timeline. Recruit more agents, Herbert\'s on the way.', '2017-11-12 04:02:40');

-- --------------------------------------------------------

--
-- Table structure for table `friends`
--

CREATE TABLE `friends` (
  `id` int(11) NOT NULL,
  `swid` varchar(40) NOT NULL,
  `friends` text NOT NULL,
  `requests` text NOT NULL,
  `ignored` text NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
-- --------------------------------------------------------

--
-- Table structure for table `igloos`
--

CREATE TABLE `igloos` (
  `id` int(11) NOT NULL,
  `owner` int(11) NOT NULL,
  `type` int(11) NOT NULL DEFAULT '1',
  `floor` int(11) NOT NULL DEFAULT '0',
  `music` int(11) NOT NULL DEFAULT '0',
  `furniture` text NOT NULL,
  `location` int(11) NOT NULL DEFAULT '0',
  `likes` text NOT NULL,
  `locked` tinyint(4) NOT NULL DEFAULT '1'
) ENGINE=InnoDB DEFAULT CHARSET=latin1;


-- --------------------------------------------------------

--
-- Table structure for table `mails`
--

CREATE TABLE `mails` (
  `id` int(11) NOT NULL,
  `to_user` int(11) NOT NULL,
  `from_user` int(11) NOT NULL,
  `type` int(11) NOT NULL,
  `description` text NOT NULL,
  `sent_on` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `opened` tinyint(4) NOT NULL DEFAULT '0',
  `junk` tinyint(4) NOT NULL DEFAULT '0'
) ENGINE=InnoDB DEFAULT CHARSET=latin1;


-- --------------------------------------------------------

--
-- Table structure for table `musictracks`
--

CREATE TABLE `musictracks` (
  `id` int(11) NOT NULL,
  `pid` int(11) NOT NULL,
  `data` text NOT NULL,
  `hash` varchar(40) NOT NULL,
  `deleted` int(11) NOT NULL,
  `likes` int(11) NOT NULL,
  `created_on` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

--
-- Dumping data for table `musictracks`
--

INSERT INTO `musictracks` (`id`, `pid`, `data`, `hash`, `deleted`, `likes`, `created_on`) VALUES
(1, 103, 'Choice,3,1000000000|0,1100000000|57b,1102000000|bfd,1102400000|34bb,1102410000|dcf7,1202410000|e4ee,1210410000|e9f4,1210110000|ed6c,1210180000|f0a0,1210180040|f48c,1210180080|f8bd,2210180000|fff1,2208180000|1069e,2208120000|10bd1,2208120002|11125,8208120000|1185c,8088120000|11c76,80a0120000|1204a,80a0820000|12486,80a0808000|12716,80a0808100|12d35,8a0808000|133b8,888808000|13697,888880000|138d6,888880001|13c66,888808000|1427d,a08808000|14615,a08208000|1484d,8208208000|14b39,8208209000|14f13,820820c000|1543d,8088208000|15a0f,8088808000|15c57,808880c000|160b2,8088208000|163bb,8208208000|1664f,8088208000|16b7f,8088808000|16dbf,2088808000|172a2,2088820000|1753a,2088820100|1816b,4088820000|184f4,4208820000|1892d,4210820000|18d0c,4210840000|18efd,8210840000|19675,8410840000|19d86,8420840000|19ed2,8421040000|1a020,8421080000|1a1ca,c21080000|1a535,c03080000|1aba9,c02180000|1ae8e,842180000|1b0d2,842108000|1b3b9,FFFF|1c271', '97a9d66fe12bd4209d0c0f5f9fe21257', 0, 0, '2018-01-20 13:29:46');

-- --------------------------------------------------------

--
-- Table structure for table `ninjas`
--

CREATE TABLE `ninjas` (
  `id` int(11) NOT NULL COMMENT 'penguin id',
  `pid` int(11) NOT NULL,
  `belt` int(2) NOT NULL DEFAULT '0',
  `fire` int(11) NOT NULL DEFAULT '0',
  `water` int(11) NOT NULL DEFAULT '0',
  `snow` int(11) NOT NULL DEFAULT '0',
  `cards` text NOT NULL,
  `matches` text NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;


-- --------------------------------------------------------

--
-- Table structure for table `penguins`
--

CREATE TABLE `penguins` (
  `id` int(11) NOT NULL,
  `username` varchar(12) NOT NULL,
  `swid` char(38) NOT NULL,
  `nickname` varchar(20) NOT NULL,
  `password` varchar(32) NOT NULL,
  `email` varchar(50) NOT NULL,
  `hash` text,
  `create` timestamp NULL DEFAULT NULL,
  `last_update` timestamp NOT NULL DEFAULT '0000-00-00 00:00:00' ON UPDATE CURRENT_TIMESTAMP,
  `membership` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'membership expiry',
  `inventory` text,
  `coins` int(11) NOT NULL DEFAULT '500',
  `head` int(11) NOT NULL DEFAULT '0',
  `face` int(11) NOT NULL DEFAULT '0',
  `neck` int(11) NOT NULL DEFAULT '0',
  `feet` int(11) NOT NULL DEFAULT '0',
  `hand` int(11) NOT NULL DEFAULT '0',
  `body` int(11) NOT NULL DEFAULT '0',
  `photo` int(11) NOT NULL DEFAULT '0',
  `pin` int(11) NOT NULL DEFAULT '0',
  `color` int(11) NOT NULL DEFAULT '1',
  `igloo` int(11) NOT NULL DEFAULT '0',
  `igloos` text NOT NULL,
  `furnitures` text NOT NULL,
  `floors` text NOT NULL,
  `locations` text NOT NULL,
  `care` text NOT NULL,
  `stamps` text NOT NULL,
  `cover` text NOT NULL,
  `agent` int(1) NOT NULL DEFAULT '0',
  `epf` varchar(50) NOT NULL DEFAULT '0%0',
  `search_msg` text
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

--
-- Dumping data for table `penguins`
--

INSERT INTO `penguins` (`id`, `username`, `swid`, `nickname`, `password`, `email`, `hash`, `create`, `last_update`, `membership`, `inventory`, `coins`, `head`, `face`, `neck`, `feet`, `hand`, `body`, `photo`, `pin`, `color`, `igloo`, `igloos`, `furnitures`, `floors`, `locations`, `care`, `stamps`, `cover`, `agent`, `epf`) VALUES
(103, 'test', '{882977da-bf7d-11e7-ac97-a02bb82e593b}', 'Peanut', '5f4dcc3b5aa765d61d8327deb882cf99', 'peanutlabs@bill.com', NULL, '2017-02-21 18:30:00', '2017-12-17 12:24:02', '2018-01-30 18:30:00', '1%2%606%607%608%3032%821%8006%8010%8011%4026%4027%6158%4809%1560%3159%5220%118%469%412%184%326%3205%5080%4032%4033%104%4883%4154%4039', 1633, 1004, 0, 0, 0, 0, 24200, 9304, 0, 2, 12, '0|1509593153,1|1509593153,73|1509865708', '793|1509593153|1,2208|1509865415|1,2046|1509865436|3,2058|1509865439|2,2054|1509865442|2,2059|1509865444|2,2062|1509865449|2,749|1509865720|1,810|1509865735|1,507|1515848912|6,370|1515851495|1,149|1515935989|1,616|1516085616|1,786|1516102877|2', '0|1509593153,21|1509865462,11|1509865467', '4|1509872170', '', '14,1512891565|63,1512892202|21,1515849336', '2|4|4|2%1|606|372|240|225|17%1|608|368|134|0|16%1|607|378|338|0|15', 1, '0%0');
--
-- Triggers `penguins`
--
DELIMITER $$
CREATE TRIGGER `penguins_OnInsert` BEFORE INSERT ON `penguins` FOR EACH ROW SET NEW.`create` = NOW(),
NEW.`swid` = CONCAT('{', uuid(), '}')
$$
DELIMITER ;

-- --------------------------------------------------------

--
-- Table structure for table `puffles`
--

CREATE TABLE `puffles` (
  `id` int(11) NOT NULL,
  `owner` int(11) NOT NULL,
  `name` varchar(20) NOT NULL,
  `type` int(11) NOT NULL,
  `subtype` int(11) NOT NULL DEFAULT '0',
  `adopted` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `food` int(11) NOT NULL DEFAULT '100',
  `play` int(11) NOT NULL DEFAULT '100',
  `rest` int(11) NOT NULL DEFAULT '100',
  `clean` int(11) NOT NULL DEFAULT '100',
  `hat` int(11) NOT NULL DEFAULT '0',
  `backyard` int(11) NOT NULL DEFAULT '0',
  `walking` int(11) NOT NULL DEFAULT '0',
  `lastcare` text NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

--
-- Indexes for dumped tables
--

--
-- Indexes for table `bans`
--
ALTER TABLE `bans`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `currencies`
--
ALTER TABLE `currencies`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `epfcoms`
--
ALTER TABLE `epfcoms`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `igloos`
--
ALTER TABLE `igloos`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `mails`
--
ALTER TABLE `mails`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `musictracks`
--
ALTER TABLE `musictracks`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `ninjas`
--
ALTER TABLE `ninjas`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `pid` (`pid`);

--
-- Indexes for table `penguins`
--
ALTER TABLE `penguins`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `swid` (`swid`),
  ADD UNIQUE KEY `igloo` (`igloo`);

--
-- Indexes for table `puffles`
--
ALTER TABLE `puffles`
  ADD PRIMARY KEY (`id`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `bans`
--
ALTER TABLE `bans`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;

--
-- AUTO_INCREMENT for table `currencies`
--
ALTER TABLE `currencies`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=22;

--
-- AUTO_INCREMENT for table `epfcoms`
--
ALTER TABLE `epfcoms`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;

--
-- Indexes for table `friends`
--
ALTER TABLE `friends`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `swid` (`swid`);

--
-- AUTO_INCREMENT for table `igloos`
--
ALTER TABLE `igloos`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=27;

--
-- AUTO_INCREMENT for table `mails`
--
ALTER TABLE `mails`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=91;

--
-- AUTO_INCREMENT for table `musictracks`
--
ALTER TABLE `musictracks`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=4;

--
-- AUTO_INCREMENT for table `ninjas`
--
ALTER TABLE `ninjas`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT COMMENT 'penguin id', AUTO_INCREMENT=22;

--
-- AUTO_INCREMENT for table `penguins`
--
ALTER TABLE `penguins`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=107;

--
-- AUTO_INCREMENT for table `puffles`
--
ALTER TABLE `puffles`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=66;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
