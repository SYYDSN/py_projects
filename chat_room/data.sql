/*
SQLyog Ultimate v11.27 (32 bit)
MySQL - 5.6.11 : Database - chat_room
*********************************************************************
*/

/*!40101 SET NAMES utf8 */;

/*!40101 SET SQL_MODE=''*/;

/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;
CREATE DATABASE /*!32312 IF NOT EXISTS*/`chat_room` /*!40100 DEFAULT CHARACTER SET utf8mb4 */;

USE `chat_room`;

/*Table structure for table `chartroom_black_ip_list` */

DROP TABLE IF EXISTS `chartroom_black_ip_list`;

CREATE TABLE `chartroom_black_ip_list` (
  `sn` int(11) NOT NULL AUTO_INCREMENT,
  `i_ip` varchar(45) NOT NULL,
  PRIMARY KEY (`sn`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

/*Data for the table `chartroom_black_ip_list` */

/*Table structure for table `chartroom_dialog` */

DROP TABLE IF EXISTS `chartroom_dialog`;

CREATE TABLE `chartroom_dialog` (
  `guest_id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) DEFAULT NULL,
  `user_name` varchar(45) DEFAULT NULL,
  `teacher_id` int(11) DEFAULT NULL,
  `dialog_message` varchar(500) NOT NULL DEFAULT '',
  `dialog_type` varchar(45) NOT NULL,
  `dialog_date` datetime NOT NULL,
  `page_url` varchar(200) NOT NULL DEFAULT '',
  `ip` varchar(45) NOT NULL DEFAULT '',
  PRIMARY KEY (`guest_id`)
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=utf8mb4;

/*Data for the table `chartroom_dialog` */

insert  into `chartroom_dialog`(`guest_id`,`user_id`,`user_name`,`teacher_id`,`dialog_message`,`dialog_type`,`dialog_date`,`page_url`,`ip`) values (1,1,NULL,0,'','login','2017-07-23 04:59:30','营销直播室','127.0.0.1'),(2,1,NULL,0,'','login','2017-07-23 04:59:30','营销直播室','127.0.0.1'),(3,1,NULL,0,'','login','2017-07-23 04:59:31','营销直播室','127.0.0.1'),(4,1,NULL,0,'','login','2017-07-23 05:00:07','营销直播室','127.0.0.1'),(5,1,NULL,0,'','login','2017-07-23 05:02:06','营销直播室','127.0.0.1'),(6,1,NULL,0,'','login','2017-07-23 05:02:06','营销直播室','127.0.0.1'),(7,1,NULL,0,'','login','2017-07-23 05:02:07','营销直播室','127.0.0.1'),(8,1,NULL,0,'','login','2017-07-23 05:09:50','营销直播室','127.0.0.1');

/*Table structure for table `chartroom_talks` */

DROP TABLE IF EXISTS `chartroom_talks`;

CREATE TABLE `chartroom_talks` (
  `message_id` varchar(45) NOT NULL,
  `message` varchar(500) NOT NULL DEFAULT '',
  `come_from` varchar(300) NOT NULL DEFAULT '',
  `user_level` int(11) NOT NULL DEFAULT '1',
  `time` varchar(45) NOT NULL DEFAULT '',
  `name` varchar(45) NOT NULL DEFAULT '',
  `page_url` varchar(200) NOT NULL DEFAULT '',
  `ip` varchar(45) NOT NULL DEFAULT '',
  `save_date` datetime NOT NULL,
  PRIMARY KEY (`message_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

/*Data for the table `chartroom_talks` */

/*Table structure for table `chartroom_user_day_count` */

DROP TABLE IF EXISTS `chartroom_user_day_count`;

CREATE TABLE `chartroom_user_day_count` (
  `sn` int(11) NOT NULL AUTO_INCREMENT,
  `u_id` int(11) NOT NULL,
  `day_count` int(11) NOT NULL,
  PRIMARY KEY (`sn`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

/*Data for the table `chartroom_user_day_count` */

/*Table structure for table `class_table` */

DROP TABLE IF EXISTS `class_table`;

CREATE TABLE `class_table` (
  `begin_time` datetime NOT NULL,
  `end_time` datetime NOT NULL,
  `Monday` varchar(45) NOT NULL,
  `Tuesday` varchar(45) NOT NULL,
  `Wednesday` varchar(45) NOT NULL,
  `Thursday` varchar(45) NOT NULL,
  `Friday` varchar(45) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

/*Data for the table `class_table` */

/*Table structure for table `everyday_tip` */

DROP TABLE IF EXISTS `everyday_tip`;

CREATE TABLE `everyday_tip` (
  `e_id` int(11) NOT NULL AUTO_INCREMENT,
  `e_title` varchar(45) NOT NULL,
  `e_content` varchar(500) NOT NULL,
  `e_author` varchar(45) NOT NULL,
  `e_datetime` datetime NOT NULL,
  PRIMARY KEY (`e_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

/*Data for the table `everyday_tip` */

/*Table structure for table `guest_action_recode` */

DROP TABLE IF EXISTS `guest_action_recode`;

CREATE TABLE `guest_action_recode` (
  `sn` int(11) NOT NULL AUTO_INCREMENT,
  `Guest_id` varchar(45) NOT NULL,
  `Referer` varchar(200) NOT NULL DEFAULT '',
  `Page_url` varchar(200) NOT NULL DEFAULT '',
  `Event_type` varchar(45) NOT NULL DEFAULT '',
  `Event_Date` datetime NOT NULL,
  `Ip` varchar(24) NOT NULL DEFAULT '',
  PRIMARY KEY (`sn`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

/*Data for the table `guest_action_recode` */

/*Table structure for table `robot_dialog_collector` */

DROP TABLE IF EXISTS `robot_dialog_collector`;

CREATE TABLE `robot_dialog_collector` (
  `sn` int(11) NOT NULL AUTO_INCREMENT,
  `s_string` varchar(500) NOT NULL,
  PRIMARY KEY (`sn`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

/*Data for the table `robot_dialog_collector` */

/*Table structure for table `teacheradmin` */

DROP TABLE IF EXISTS `teacheradmin`;

CREATE TABLE `teacheradmin` (
  `t_Id` int(11) NOT NULL AUTO_INCREMENT,
  `t_AccountName` varchar(45) NOT NULL,
  `t_AccountPassword` varchar(100) NOT NULL,
  `can_login` int(11) NOT NULL DEFAULT '1',
  `phone` varchar(11) NOT NULL DEFAULT '',
  `t_Name` varchar(45) NOT NULL DEFAULT '',
  PRIMARY KEY (`t_Id`),
  UNIQUE KEY `t_AccountName_uq` (`t_AccountName`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4;

/*Data for the table `teacheradmin` */

insert  into `teacheradmin`(`t_Id`,`t_AccountName`,`t_AccountPassword`,`can_login`,`phone`,`t_Name`) values (1,'admin_user','e10adc3949ba59abbe56e057f20f883e',1,'',''),(2,'admin_01','e10adc3949ba59abbe56e057f20f883e',1,'','');

/*Table structure for table `teacherinfo` */

DROP TABLE IF EXISTS `teacherinfo`;

CREATE TABLE `teacherinfo` (
  `t_id` int(11) NOT NULL AUTO_INCREMENT,
  `t_name` varchar(45) NOT NULL DEFAULT '',
  `t_nickname` varchar(45) NOT NULL DEFAULT '',
  `t_title` varchar(45) NOT NULL DEFAULT '',
  `t_description` varchar(500) NOT NULL DEFAULT '',
  `t_password` varchar(100) NOT NULL,
  `t_CreateTime` datetime NOT NULL,
  `t_can_use` int(11) NOT NULL DEFAULT '1',
  `t_Level` int(11) NOT NULL DEFAULT '1',
  `t_in_class` int(11) NOT NULL DEFAULT '1',
  `t_account` varchar(45) NOT NULL,
  PRIMARY KEY (`t_id`),
  UNIQUE KEY `t_account_uq` (`t_account`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

/*Data for the table `teacherinfo` */

/*Table structure for table `userinfo` */

DROP TABLE IF EXISTS `userinfo`;

CREATE TABLE `userinfo` (
  `u_Id` int(11) NOT NULL AUTO_INCREMENT,
  `u_AccountName` varchar(45) DEFAULT NULL,
  `u_AccountPassword` varchar(100) NOT NULL,
  `u_phone` varchar(11) NOT NULL,
  `u_RealName` varchar(45) NOT NULL DEFAULT '',
  `u_CreateTime` datetime NOT NULL,
  `u_CanUse` int(11) NOT NULL DEFAULT '1',
  `u_Level` int(11) NOT NULL DEFAULT '1',
  `u_Sex` varchar(4) NOT NULL DEFAULT '',
  `u_LastTime` datetime DEFAULT NULL,
  PRIMARY KEY (`u_Id`),
  UNIQUE KEY `u_phone_uq` (`u_phone`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4;

/*Data for the table `userinfo` */

insert  into `userinfo`(`u_Id`,`u_AccountName`,`u_AccountPassword`,`u_phone`,`u_RealName`,`u_CreateTime`,`u_CanUse`,`u_Level`,`u_Sex`,`u_LastTime`) values (1,'ere','123456','13333333333','哈哈','2017-07-23 04:59:00',1,5,'',NULL);

/*Table structure for table `userlevel` */

DROP TABLE IF EXISTS `userlevel`;

CREATE TABLE `userlevel` (
  `u_Id` int(11) NOT NULL AUTO_INCREMENT,
  `u_level_number` int(11) NOT NULL,
  `u_Name` varchar(45) NOT NULL,
  `u_img_path` varchar(100) NOT NULL DEFAULT '',
  PRIMARY KEY (`u_Id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

/*Data for the table `userlevel` */

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;
