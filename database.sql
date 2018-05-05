-- phpMyAdmin SQL Dump
-- version 4.7.4
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: May 05, 2018 at 06:19 AM
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
  `matches` text NOT NULL,
  `fire_matches` text NOT NULL,
  `water_matches` text NOT NULL
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
  `moderator` int(1) NOT NULL DEFAULT '0',
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

-- --------------------------------------------------------
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
-- Indexes for table `friends`
--
ALTER TABLE `friends`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `swid` (`swid`);

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
  ADD UNIQUE KEY `swid` (`swid`);

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
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=24;

--
-- AUTO_INCREMENT for table `epfcoms`
--
ALTER TABLE `epfcoms`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;

--
-- AUTO_INCREMENT for table `friends`
--
ALTER TABLE `friends`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=6;

--
-- AUTO_INCREMENT for table `igloos`
--
ALTER TABLE `igloos`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=30;

--
-- AUTO_INCREMENT for table `mails`
--
ALTER TABLE `mails`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=99;

--
-- AUTO_INCREMENT for table `musictracks`
--
ALTER TABLE `musictracks`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=5;

--
-- AUTO_INCREMENT for table `ninjas`
--
ALTER TABLE `ninjas`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT COMMENT 'penguin id', AUTO_INCREMENT=7;

--
-- AUTO_INCREMENT for table `penguins`
--
ALTER TABLE `penguins`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=125;

--
-- AUTO_INCREMENT for table `puffles`
--
ALTER TABLE `puffles`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=66;

COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
