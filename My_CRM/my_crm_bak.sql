/*
SQLyog Ultimate v11.27 (32 bit)
MySQL - 5.7.18-0ubuntu0.16.04.1 : Database - my_crm_bak
*********************************************************************
*/

/*!40101 SET NAMES utf8 */;

/*!40101 SET SQL_MODE=''*/;

/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;
CREATE DATABASE /*!32312 IF NOT EXISTS*/`my_crm_bak` /*!40100 DEFAULT CHARACTER SET utf8mb4 */;

USE `my_crm_bak`;

/*Table structure for table `customer_info` */

DROP TABLE IF EXISTS `customer_info`;

CREATE TABLE `customer_info` (
  `user_sn` int(11) NOT NULL AUTO_INCREMENT,
  `user_name` varchar(45) NOT NULL DEFAULT '' COMMENT '用户注册的名字',
  `user_phone` varchar(45) NOT NULL COMMENT '手机',
  `page_url` varchar(1000) NOT NULL DEFAULT '' COMMENT '用户注册的网址',
  `create_date` datetime NOT NULL,
  `team_sn` int(11) NOT NULL DEFAULT '0' COMMENT '分配给的团队的sn，如果和company_sn列相同。标识只分配道分公司没分配到团队,',
  `source_sn` int(11) DEFAULT '1' COMMENT '来源类型，默认是1,注册',
  `company_sn` int(11) DEFAULT '0' COMMENT '公司sn，默认0，没分配，,如果分配了，这里就是分公司对应的sn',
  `customer_description` varchar(500) DEFAULT '' COMMENT '备注',
  `in_count` int(11) DEFAULT '1',
  `employee_sn` int(11) NOT NULL DEFAULT '0',
  PRIMARY KEY (`user_sn`),
  UNIQUE KEY `user_phone_UNIQUE` (`user_phone`),
  KEY `source_info.sn` (`source_sn`),
  CONSTRAINT `source_info.sn` FOREIGN KEY (`source_sn`) REFERENCES `source_type` (`sn`)
) ENGINE=InnoDB AUTO_INCREMENT=793 DEFAULT CHARSET=utf8mb4 COMMENT='存储注册用户信息的表';

/*Data for the table `customer_info` */

insert  into `customer_info`(`user_sn`,`user_name`,`user_phone`,`page_url`,`create_date`,`team_sn`,`source_sn`,`company_sn`,`customer_description`,`in_count`,`employee_sn`) values (23,'蔡方正','18808323918','http://ly.caifuby.cn/index1.html','2017-06-15 17:53:56',0,1,0,'',1,0),(29,'冯艳','15812411878','http://ly.caifuby.cn/index3.html','2017-06-15 18:06:24',0,1,0,'',1,0),(30,'颜继堂','13897870533','http://ly.caifuby.cn/index3.html','2017-06-15 18:23:46',0,1,0,'',1,0),(31,'汤殿永','13160889813','http://ly.caifuby.cn/index2.html','2017-06-15 18:24:39',0,1,0,'',1,0),(34,'张民照','15126817729','http://ly.caifuby.cn/index1.html','2017-06-15 18:25:44',0,1,0,'',1,0),(37,'彭亦文','13897260901','http://ly.caifuby.cn/index1.html','2017-06-15 18:49:00',0,1,0,'',1,0),(39,'盛营光','13575305701','http://ly.caifuby.cn/index1.html','2017-06-15 19:02:39',0,1,0,'',1,0),(43,'凌博','18156180900','http://ly.caifuby.cn/index1.html','2017-06-15 19:20:35',0,1,0,'',1,0),(44,'田波','13818439630','http://ly.caifuby.cn/index3.html','2017-06-15 19:23:17',0,1,0,'',1,0),(49,'zhoujun','13972385086','http://ly.caifuby.cn/index3.html','2017-06-15 19:30:13',0,1,0,'',1,0),(50,'王晓阳','18035167596','http://ly.caifuby.cn/index3.html','2017-06-15 19:34:30',0,1,0,'',1,0),(54,'吴玉献','13956430880','http://ly.caifuby.cn/index1.html','2017-06-15 20:33:29',0,1,0,'',1,0),(55,'刘洪哲','13304062688','http://ly.caifuby.cn/index1.html','2017-06-15 20:50:38',0,1,0,'',1,0),(56,'杨琦','18727997452','http://ly.caifuby.cn/index2.html','2017-06-16 16:27:13',0,1,0,'',1,0),(57,'张亮','15022906910','http://ly.caifuby.cn/index1.html','2017-06-16 16:50:04',0,1,0,'',1,0),(66,'彭','13902357699','http://ly.caifuby.cn/index1.html','2017-06-16 18:07:36',0,1,0,'',1,0),(67,'夏立红','18513229287','http://ly.caifuby.cn/index2.html','2017-06-16 18:31:56',0,1,0,'',1,0),(68,'刘世海','13619083938','http://ly.caifuby.cn/index1.html','2017-06-16 19:44:39',0,1,0,'',1,0),(69,'安鸿','13641764547','http://ly.caifuby.cn/index3.html','2017-06-16 20:05:29',0,1,0,'',1,0),(71,'史立辉','13613313377','http://ly.caifuby.cn/index2.html','2017-06-17 16:41:30',0,1,0,'',1,0),(72,'吴方权','13905783345','http://ly.caifuby.cn/index3.html','2017-06-17 16:45:14',0,1,0,'',1,0),(73,'宋德志','13782759322','http://ly.caifuby.cn/index3.html','2017-06-17 16:51:48',0,1,0,'',1,0),(78,'远东','15077134662','http://ly.caifuby.cn/index1.html','2017-06-17 17:36:57',0,1,0,'',1,0),(81,'朱伟杰','15936330524','http://ly.caifuby.cn/index1.html','2017-06-17 18:32:48',0,1,0,'',1,0),(82,'朱伟杰','15036330524','http://ly.caifuby.cn/index1.html','2017-06-17 18:33:37',0,1,0,'',1,0),(83,'王君','13039213557','http://ly.caifuby.cn/index1.html','2017-06-17 18:49:37',0,1,0,'',1,0),(84,'张坤','15709155569','http://ly.caifuby.cn/index2.html','2017-06-18 17:47:24',0,1,0,'',1,0),(85,'游文龙','18270612956','http://ly.caifuby.cn/index1.html','2017-06-18 18:02:58',0,1,0,'',1,0),(86,'彭川','13606175589','http://ly.caifuby.cn/index1.html','2017-06-18 18:31:18',0,1,0,'',1,0),(87,'李新江','15867581980','http://ly.caifuby.cn/index2.html','2017-06-18 18:36:58',0,1,0,'',1,0),(88,'张绪浪','13639878201','http://ly.caifuby.cn/index1.html','2017-06-18 18:38:38',0,1,0,'',1,0),(92,'李发新','13572606021','http://ly.caifuby.cn/index3.html','2017-06-18 19:46:41',0,1,0,'',1,0),(100,'测试账户','13013001321','','2017-06-19 15:23:49',2,1,2,'',1,0),(103,'测试账户','13013001323','','2017-06-19 15:25:07',2,1,2,'',1,0),(104,'外网测试账户','15000150015','http://ly.caifuby.cn/index3.html','2017-06-19 15:29:53',0,1,0,'',1,0),(119,'彭得力','18301512597','http://ly.caifuby.cn/index1.html?sr=ch2&sgjj6sj-11806','2017-06-19 16:03:54',2,1,2,'',1,0),(122,'彭得力','18664323317','http://ly.caifuby.cn/index1.html?sr=ch2&sgjj6sj-11806','2017-06-19 16:05:12',8,1,8,'',1,0),(124,'彭得力','13392448816','http://ly.caifuby.cn/index1.html?sr=ch2&sgjj6sj-11806','2017-06-19 16:07:00',2,1,2,'',1,0),(127,'石先生','15826980598','http://ly.caifuby.cn/index1.html?sr=ch2&sgjj6sj-31012','2017-06-19 16:59:37',8,1,8,'',1,0),(128,'余本增','13750810458','http://ly.caifuby.cn/index2.html?sr=ch2&sgjj6sj-07200','2017-06-19 17:03:07',2,1,2,'',1,0),(129,'卫安稳','13653434378','http://ly.caifuby.cn/index1.html?sr=ch2&sgjj6sj-31012','2017-06-19 17:50:24',8,1,8,'',1,0),(130,'李涛','13888327879','http://ly.caifuby.cn/index2.html?sr=ch2&sgjj6sj-19691','2017-06-19 18:56:34',8,1,8,'',1,0),(132,'廖涵','15205787148','http://ly.caifuby.cn/index3.html?sr=ch1&sgjj6pc-30289','2017-06-19 19:41:37',8,1,8,'',1,0),(137,'叶邦俊','13566499959','http://ly.caifuby.cn/index3.html?sr=ch1&sgjj6pc-02416','2017-06-20 15:11:16',8,1,8,'',1,0),(138,'喻旭','13764009865','http://ly.caifuby.cn/index3.html?sr=ch1&sgjj6pc-02360','2017-06-20 15:20:51',2,1,2,'',1,0),(139,'超哥','18996815788','http://ly.caifuby.cn/index1.html?sr=ch2&sgjj6sj-02562','2017-06-20 15:38:16',8,1,8,'',1,0),(140,'李强','13848639598','http://vip.jxy77.cn/index6.html?sr=ch1&360jj6pc-09439','2017-06-20 16:08:38',2,1,2,'',1,0),(143,'秦康乐','18070123387','http://vip.jxy77.cn/index6.html?sr=ch1&360jj6pc-25059','2017-06-20 16:17:39',8,1,8,'',1,0),(144,'凯轮','15027218626','http://vip.jxy77.cn/index6.html?sr=ch1&360jj6pc-25278','2017-06-20 16:18:11',2,1,2,'',1,0),(147,'姚双','18522424799','http://ly.caifuby.cn/index3.html?sr=ch1&sgjj6pc-01976','2017-06-20 16:20:52',8,1,8,'',1,0),(149,'李君月','15533973037','http://ly.caifuby.cn/index3.html?sr=ch1&sgjj6pc-66133','2017-06-20 16:28:00',2,1,2,'',1,0),(150,'康景煌','13467856614','http://vip.jxy77.cn/index6.html?sr=ch1&360jj6pc-09497','2017-06-20 16:28:06',8,1,8,'',1,0),(152,'康景煌','13473561112','http://vip.jxy77.cn/index6.html?sr=ch1&360jj6pc-09497','2017-06-20 16:28:42',2,1,2,'',1,0),(157,'陈庆东','15221566510','http://ly.caifuby.cn/index2.html?sr=ch2&sgjj6sj-24443','2017-06-20 16:33:25',8,1,8,'',1,0),(158,'高林','18930914608','http://ly.caifuby.cn/index2.html?sr=ch2&sgjj6sj-24443','2017-06-20 16:34:04',2,1,2,'',1,0),(159,'柯妙红','13826446001','http://ly.caifuby.cn/index3.html?sr=ch1&sgjj6pc-07915','2017-06-20 16:36:05',8,1,8,'',1,0),(169,'景玉成','15004233369','http://vip.jxy77.cn/index6.html?sr=ch1&360jj6pc-09277','2017-06-20 17:06:17',2,1,2,'',1,0),(171,'颜英健','18328816204','http://ly.caifuby.cn/index3.html?sr=ch1&sgjj6pc-03751','2017-06-20 17:24:25',8,1,8,'',1,0),(172,'孙阳','15618388832','http://ly.caifuby.cn/index3.html?sr=ch1&sgjj6pc-06737','2017-06-20 17:29:19',2,1,2,'',1,0),(175,'吕','13505048977','http://vip.jxy77.cn/index6.html?sr=ch1&360jj6pc-09526','2017-06-20 17:34:12',8,1,8,'',1,0),(176,'冯军','13160828258','http://vip.jxy77.cn/index6.html?sr=ch1&360jj6pc-09543','2017-06-20 17:51:32',2,1,2,'',1,0),(180,'李天','13755642756','http://ly.caifuby.cn/index3.html?sr=ch1&sgjj6pc-30289','2017-06-20 17:54:43',8,1,8,'',1,0),(184,'李江华','13600315343','http://vip.jxy77.cn/index6.html?sr=ch1&360jj6pc-09382','2017-06-21 16:04:59',2,1,2,'',1,0),(185,'张悠','13299040520','http://vip.jxy77.cn/index6.html?sr=ch1&360jj6pc-04244','2017-06-21 16:10:24',8,1,8,'',1,0),(188,'张悠','13227710798','http://vip.jxy77.cn/index6.html?sr=ch1&360jj6pc-04244','2017-06-21 16:11:00',2,1,2,'',1,0),(190,'耿继英','13831035696','http://vip.jxy77.cn/index6.html?sr=ch1&360jj6pc-26302','2017-06-21 16:13:31',8,1,8,'',1,0),(192,'韩云宁','13964153007','http://vip.jxy77.cn/index6.html?sr=ch1&360jj6pc-09426','2017-06-21 16:16:55',2,1,2,'',1,0),(193,'陈德根','13972254527','http://vip.jxy77.cn/index6.html?sr=ch1&360jj6pc-25627','2017-06-21 16:18:22',8,1,8,'',1,0),(197,'王恩颂','18218986101','http://ly.caifuby.cn/index3.html?sr=ch1&sgjj6pc-02566','2017-06-21 16:25:04',2,1,2,'',1,0),(200,'金京双','13603570039','http://vip.jxy77.cn/index6.html?sr=ch1&360jj6pc-24574','2017-06-21 16:26:11',8,1,8,'',1,0),(201,'赵铭','13909511478','http://vip.jxy77.cn/index6.html?sr=ch1&360jj6pc-25193','2017-06-21 16:36:42',2,1,2,'',1,0),(203,'李三千','13467954943','http://vip.jxy77.cn/index6.html?sr=ch1&360jj6pc-09464','2017-06-21 17:05:49',2,1,2,'',1,0),(206,'林丽','13400603137','http://vip.jxy77.cn/index6.html?sr=ch1&360jj6pc-09527','2017-06-21 17:30:33',8,1,8,'',1,0),(207,'张国强','13834106089','http://ly.caifuby.cn/index1.html?sr=ch2&sgjj6sj-34455','2017-06-21 18:01:44',8,1,8,'',1,0),(210,'姚幸伟','18368853466','http://vip.jxy77.cn/index6.html?sr=ch1&360jj6pc-09224','2017-06-21 18:03:16',2,1,2,'',1,0),(213,'赵新红','15231183888','http://ly.caifuby.cn/index3.html?sr=ch1&sgjj6pc-30289','2017-06-21 19:35:47',8,1,8,'',1,0),(214,'杨正友','13595630698','http://ly.caifuby.cn/index3.html?sr=ch1&sgjj6pc-30289','2017-06-24 16:13:10',2,1,2,'',1,0),(217,'张生','18878766258','http://ly.caifuby.cn/index1.html?sr=ch2&sgjj6sj-34455','2017-06-24 16:28:19',8,1,8,'',1,0),(219,'uh','13678155320','http://vip8.ychuday.cn/index9.html','2017-06-24 16:36:16',2,1,2,'',1,0),(220,'王八蛋','18295086980','http://ly.caifuby.cn/index3.html?sr=ch1&sgjj6pc-65519','2017-06-24 16:39:02',8,1,8,'',1,0),(221,'高磊','13641976118','http://ly.caifuby.cn/index2.html?sr=ch2&sgjj6sj-19721','2017-06-24 16:39:31',2,1,2,'',1,0),(222,'姜国平','13785165673','http://ly.caifuby.cn/index3.html?sr=ch1&sgjj6pc-07915','2017-06-24 16:40:15',8,1,8,'',1,0),(230,'柴建林','18258336531','http://vip8.ychuday.cn/index9.html','2017-06-24 16:47:44',8,1,8,'',1,0),(233,'阳伟','18354518822','http://ly.caifuby.cn/index2.html?sr=ch2&sgjj6sj-02723','2017-06-24 17:01:33',2,1,2,'',1,0),(237,'刘海龙','18937857391','http://ly.caifuby.cn/index1.html?sr=ch2&sgjj6sj-34455','2017-06-24 17:22:55',8,1,8,'',1,0),(238,'张煜新','15335088365','http://vip8.ychuday.cn/index9.html','2017-06-24 17:23:45',2,1,2,'',1,0),(241,'黄浩','13563215637','http://ly.caifuby.cn/index2.html?sr=ch2&sgjj6sj-23598','2017-06-24 17:29:13',8,1,8,'',1,0),(242,'韩国帅','18401441190','http://ly.caifuby.cn/index2.html?sr=ch2&sgjj6sj-06185','2017-06-24 17:29:21',2,1,2,'',1,0),(243,'潘先生','13324110597','http://vip8.ychuday.cn/index9.html','2017-06-24 17:30:44',8,1,8,'',1,0),(244,'张勇','13438032290','http://vip8.ychuday.cn/index9.html','2017-06-24 17:34:41',2,1,2,'',1,0),(247,'熊珂','18587565516','http://vip8.ychuday.cn/index9.html','2017-06-26 16:09:16',8,1,8,'',1,0),(248,'王金保','18703534307','http://ly.caifuby.cn/index1.html?sr=ch2&sgjj6sj-31012','2017-06-26 16:15:09',2,1,2,'',1,0),(249,'李少云','13858861969','http://vip8.ychuday.cn/index9.html?sr=ch1&360jj6pc-09123','2017-06-26 16:20:08',8,1,8,'',1,0),(251,'吕德林','13759142617','http://vip8.ychuday.cn/index9.html?sr=ch1&360jj6pc-09505','2017-06-26 16:46:07',2,1,2,'',1,0),(252,'李月娥','15980823373','http://vip8.ychuday.cn/index9.html?sr=ch1&360jj6pc-09156','2017-06-26 16:49:21',8,1,8,'',1,0),(255,'黄河','13541082118','http://vip8.ychuday.cn/index9.html?sr=ch1&360jj6pc-09262','2017-06-26 17:29:38',2,1,2,'',1,0),(256,'张涛','15872991227','http://ly.caifuby.cn/index2.html?sr=ch2&sgjj6sj-06185','2017-06-26 17:43:51',8,1,8,'',1,0),(257,'xpj','13951630068','http://vip8.ychuday.cn/index9.html?sr=ch1&360jj6pc-09505','2017-06-26 17:44:53',2,1,2,'',1,0),(258,'贾玉军','13948165755','http://ly.caifuby.cn/index1.html?sr=ch2&sgjj6sj-31012','2017-06-26 17:48:40',8,1,8,'',1,0),(259,'李刚民','18638229858','http://vip8.ychuday.cn/index9.html?sr=ch1&360jj6pc-09224','2017-06-26 17:49:18',2,1,2,'',1,0),(275,'仇建武','13738735187','http://ly.caifuby.cn/index1.html?sr=ch1&sgjj6sj-66133','2017-06-26 18:43:58',8,1,8,'',1,0),(276,'付文胜','18766708089','http://ly.caifuby.cn/index1.html?sr=ch2&sgjj6sj-34455','2017-06-26 18:45:54',2,1,2,'',1,0),(278,'123','18102131122','http://ly.caifuby.cn/index1.html?sr=ch2&sgjj6sj-34455','2017-06-26 19:17:34',8,1,8,'',1,0),(279,'徐亚康','13586694036','http://vip8.ychuday.cn/index9.html?sr=ch1&360jj6pc-04243','2017-06-26 19:42:02',2,1,2,'',1,0),(280,'韩利辉','13946668266','http://ly.caifuby.cn/index3.html?sr=ch1&sgjj6pc-30289','2017-06-26 19:46:57',8,1,8,'',1,0),(282,'冯云','18358614000','http://ly.caifuby.cn/index2.html?sr=ch2&sgjj6sj-06128','2017-06-26 19:51:49',2,1,2,'',1,0),(283,'陈牛','15951100557','http://ly.caifuby.cn/index2.html?sr=ch2&sgjj6sj-03598','2017-06-26 19:53:24',8,1,8,'',1,0),(284,'黄片','15250446090','http://ly.caifuby.cn/index2.html?sr=ch2&sgjj6sj-03598','2017-06-26 19:55:13',2,1,2,'',1,0),(285,'陈新尧','13989569626','http://vip8.ychuday.cn/index9.html?sr=ch1&360jj6pc-25231','2017-06-26 20:32:27',8,1,8,'',1,0),(286,'张立志','13845186293','http://vip8.ychuday.cn/index9.html?sr=ch1&360jj6pc-09199','2017-06-26 20:43:20',2,1,2,'',1,0),(287,'程琳','13124257245','http://vip8.ychuday.cn/index9.html?sr=ch1&360jj6pc-24164','2017-06-26 20:43:27',8,1,8,'',1,0),(290,'戴万华','13467381239','http://vip8.ychuday.cn/index9.html?sr=ch1&360jj6pc-26348','2017-06-26 20:48:57',2,1,2,'',1,0),(291,'张博','15618557770','http://vip8.ychuday.cn/index9.html?sr=ch1&360jj6pc-25423','2017-06-27 10:15:34',8,1,8,'',1,0),(292,'游建平','15267139297','http://vip8.ychuday.cn/index9.html?sr=ch1&360jj6pc-25423','2017-06-27 10:15:56',2,1,2,'',1,0),(293,'杭婷','18555044100','http://vip8.ychuday.cn/index9.html?sr=ch1&360jj6pc-09505','2017-06-27 15:05:17',8,1,8,'',1,0),(316,'hu','13291146320','http://ly.caifuby.cn/index3.html?sr=ch1&sgjj6pc-29325','2017-06-27 15:38:26',2,1,2,'',1,0),(318,'胡述梁','18626180535','http://ly.caifuby.cn/index3.html?sr=ch1&sgjj6pc-29325','2017-06-27 15:41:48',8,1,8,'',1,0),(319,'谢浩','13890779896','http://vip8.ychuday.cn/index9.html?sr=ch1&360jj6pc-04179','2017-06-27 15:45:03',2,1,2,'',1,0),(322,'丁邦法','13275775301','http://vip8.ychuday.cn/index9.html?sr=ch1&360jj6pc-03801','2017-06-27 16:23:34',8,1,8,'',1,0),(324,'郭','18935622208','http://vip8.ychuday.cn/index9.html?sr=ch1&360jj6pc-09430','2017-06-27 16:27:00',2,1,2,'',1,0),(325,'侯鹏飞','17638153852','http://ly.caifuby.cn/index3.html?sr=ch1&sgjj6pc-07915','2017-06-27 16:34:52',8,1,8,'',1,0),(326,'赵春付','18358056689','http://ly.caifuby.cn/index1.html?sr=ch2&sgjj6sj-00952','2017-06-27 17:06:39',2,1,2,'',1,0),(329,'王俊清','13453608507','http://ly.caifuby.cn/index1.html?sr=ch2&sgjj6sj-01811','2017-06-27 17:36:23',8,1,8,'',1,0),(331,'13398153621','13398153621','http://ly.caifuby.cn/index3.html?sr=ch1&sgjj6pc-07915','2017-06-27 18:42:05',8,1,8,'',1,0),(337,'李政伟','15871564405','http://ly.caifuby.cn/index3.html?sr=ch1&sgjj6pc-66133','2017-06-27 20:06:27',2,1,2,'',1,0),(339,'gygbhb','13402044806','http://ly.caifuby.cn/index3.html?sr=ch1&sgjj6pc-30289','2017-06-27 20:39:33',8,1,8,'',1,0),(340,'潘健都','13402023805','http://ly.caifuby.cn/index3.html?sr=ch1&sgjj6pc-30289','2017-06-27 20:40:18',2,1,2,'',1,0),(342,'张传舵','18953917989','http://ly.caifuby.cn/index2.html?sr=ch2&sgjj6sj-61602','2017-06-28 12:44:41',8,1,8,'',1,0),(343,'李金跃','13342002007','http://ly.caifuby.cn/index3.html?sr=ch1&sgjj6pc-03477','2017-06-28 13:02:02',2,1,2,'',1,0),(345,'陈静怡','17741117147','http://ly.caifuby.cn/index3.html?sr=ch1&sgjj6pc-02566','2017-06-28 13:45:00',8,1,8,'',1,0),(346,'陈胜军','15197578009','http://ly.caifuby.cn/index2.html?sr=ch2&sgjj6sj-06185','2017-06-28 14:07:43',2,1,2,'',1,0),(348,'归先生','17715381049','http://ly.caifuby.cn/index2.html?sr=ch2&sgjj6sj-06185','2017-06-28 14:12:55',8,1,8,'',1,0),(352,'黄成','18577130049','http://ly.caifuby.cn/index2.html?sr=ch2&sgjj6sj-21757','2017-06-28 14:16:26',2,1,2,'',1,0),(359,'wxf','13994250536','http://ly.caifuby.cn/index3.html?sr=ch1&sgjj6pc-08775','2017-06-28 14:34:55',8,1,8,'',1,0),(361,'杨保龙','18736297927','http://ly.caifuby.cn/index2.html?sr=ch2&sgjj6sj-48444','2017-06-28 15:35:49',2,1,2,'',1,0),(364,'胡建威','13666552635','http://ly.caifuby.cn/index3.html?sr=ch1&sgjj6pc-66133','2017-06-28 15:40:37',8,1,8,'',1,0),(365,'随缘','13842635257','http://ly.caifuby.cn/index3.html?sr=ch1&sgjj6pc-02566','2017-06-28 15:55:22',2,1,2,'',1,0),(366,'无敌男一号','13187876254','http://m.bl150.com/a123/','2017-06-28 15:55:41',8,1,8,'',1,0),(368,'刘文飞','15016182979','http://ly.caifuby.cn/index3.html?sr=ch1&sgjj6pc-07915','2017-06-28 16:00:58',2,1,2,'',1,0),(395,'123','15021251933','http://m.bl150.com/a123/','2017-06-28 16:04:22',8,1,8,'',1,0),(396,'111','15021251333','http://m.bl150.com/a123/','2017-06-28 16:07:45',2,1,2,'',1,0),(397,'文金梅','13222507398','http://ly.caifuby.cn/index2.html?sr=ch2&sgjj6sj-11513','2017-06-28 16:07:56',8,1,8,'',1,0),(401,'朱红','15692094673','http://vip8.ychuday.cn/index9.html?sr=ch1&360jj6pc-03936','2017-06-28 16:18:41',2,1,2,'',1,0),(402,'龙云','13266887839','http://ly.caifuby.cn/index1.html?sr=ch2&sgjj6sj-05752','2017-06-28 16:28:19',8,1,8,'',1,0),(406,'王静驳','15957876767','http://vip8.ychuday.cn/index9.html?sr=ch1&360jj6pc-09439','2017-06-28 16:42:26',2,1,2,'',1,0),(409,'上海嘉虎红熹投资管理有限公司','18930808877','http://vip8.ychuday.cn/index9.html?sr=ch1&360jj6pc-09468','2017-06-28 16:51:14',8,1,8,'',1,0),(410,'11','13587391550','http://vip8.ychuday.cn/index9.html?sr=ch1&360jj6pc-09439','2017-06-28 16:56:28',2,1,2,'',1,0),(412,'田呈','18232420742','http://vip8.ychuday.cn/index9.html?sr=ch1&360jj6pc-09517','2017-06-28 17:10:25',8,1,8,'',1,0),(413,'鲁泰山','15698128033','http://vip8.ychuday.cn/index9.html?sr=ch1&360jj6pc-04094','2017-06-28 17:31:34',2,1,2,'',1,0),(414,'黄寿元','13860251323','http://vip8.ychuday.cn/index9.html?sr=ch1&360jj6pc-09517','2017-06-28 17:35:23',8,1,8,'',1,0),(415,'周祥','15996641887','http://vip8.ychuday.cn/index9.html?sr=ch1&360jj6pc-09387','2017-06-28 17:41:53',2,1,2,'',1,0),(416,'魏云海','13130984808','http://vip8.ychuday.cn/index9.html?sr=ch1&360jj6pc-09517','2017-06-28 17:45:03',8,1,8,'',1,0),(417,'李伟','15223313993','http://ly.caifuby.cn/index1.html?sr=ch2&sgjj6sj-02920','2017-06-28 17:54:48',2,1,2,'',1,0),(418,'梁炳威','13926031012','http://vip8.ychuday.cn/index9.html?sr=ch1&360jj6pc-09156','2017-06-28 18:52:10',8,1,8,'',1,0),(419,'宋蕾','13526585759','http://vip8.ychuday.cn/index9.html?sr=ch1&360jj6pc-09505','2017-06-28 18:52:53',2,1,2,'',1,0),(420,'郭怡君','13571500782','http://vip8.ychuday.cn/index9.html?sr=ch1&360jj6pc-04093','2017-06-28 19:26:41',8,1,8,'',1,0),(423,'刘浩','18117837746','http://vip8.ychuday.cn/index9.html?sr=ch1&360jj6pc-09479','2017-06-28 19:30:12',2,1,2,'',1,0),(424,'高翔','15667267408','http://vip8.ychuday.cn/index9.html?sr=ch1&360jj6pc-09156','2017-06-28 19:31:51',8,1,8,'',1,0),(427,'wang','18657191975','http://vip8.ychuday.cn/index9.html?sr=ch1&360jj6pc-04093','2017-06-28 19:38:59',2,1,2,'',1,0),(428,'何美婷','15968305516','http://vip8.ychuday.cn/index9.html?sr=ch1&360jj6pc-04277','2017-06-28 19:39:49',8,1,8,'',1,0),(429,'孙亮','18806153152','http://vip8.ychuday.cn/index9.html?sr=ch1&360jj6pc-09156','2017-06-28 19:40:42',2,1,2,'',1,0),(431,'系统嗯嗯','15954376117','http://ly.caifuby.cn/index3.html?sr=ch1&sgjj6pc-33654','2017-06-29 11:08:25',8,1,8,'',1,0),(432,'嗯嗯','13905436218','http://ly.caifuby.cn/index3.html?sr=ch1&sgjj6pc-33654','2017-06-29 11:10:42',2,1,2,'',1,0),(433,'王德明','13005172112','http://ly.caifuby.cn/index2.html?sr=ch2&sgjj6sj-64698','2017-06-29 11:23:19',8,1,8,'',1,0),(436,'李先生','13501389597','http://ly.caifuby.cn/index3.html?sr=ch1&sgjj6pc-02566','2017-06-29 13:13:59',2,1,2,'',1,0),(439,'地方十几个','15236221789','http://ly.caifuby.cn/index3.html?sr=ch1&sgjj6pc-66133','2017-06-29 15:36:43',8,1,8,'',1,0),(441,'李光强','15236217519','http://ly.caifuby.cn/index3.html?sr=ch1&sgjj6pc-66133','2017-06-29 15:39:15',2,1,2,'',1,0),(442,'郭涛','15208712274','http://ly.caifuby.cn/index3.html?sr=ch1&sgjj6pc-02566','2017-06-29 15:39:44',8,1,8,'',1,0),(443,'李丽娟','13597978451','http://vip8.ychuday.cn/index9.html?sr=ch1&360jj6pc-09505','2017-06-29 16:15:29',2,1,2,'',1,0),(444,'李丽娟','13578945215','http://vip8.ychuday.cn/index9.html?sr=ch1&360jj6pc-09505','2017-06-29 16:15:55',8,1,8,'',1,0),(445,'梁云','15806199412','http://vip8.ychuday.cn/index9.html?sr=ch1&360jj6pc-09505','2017-06-29 16:16:09',2,1,2,'',1,0),(447,'孙松','15245789658','http://ly.caifuby.cn/index3.html?sr=ch1&sgjj6pc-02566','2017-06-29 16:29:54',8,1,8,'',1,0),(448,'周瑜','15093430365','http://vip8.ychuday.cn/index9.html?sr=ch1&360jj6pc-09372','2017-06-29 16:30:59',2,1,2,'',1,0),(450,'张先生','15623132669','http://vip8.ychuday.cn/index9.html?sr=ch1&360jj6pc-09431','2017-06-29 16:33:51',8,1,8,'',1,0),(453,'琳琳','13433343509','http://ly.caifuby.cn/index3.html?sr=ch1&sgjj6pc-07915','2017-06-29 16:42:30',2,1,2,'',1,0),(454,'谭茜','13026308500','http://vip8.ychuday.cn/index9.html?sr=ch1&360jj6pc-09156','2017-06-29 16:44:56',8,1,8,'',1,0),(455,'黄明文','13507699987','http://vip8.ychuday.cn/index9.html?sr=ch1&360jj6pc-09497','2017-06-29 16:48:56',2,1,2,'',1,0),(458,'林堂鸿','13352688979','http://vip8.ychuday.cn/index9.html?sr=ch1&360jj6pc-09372','2017-06-29 16:53:54',8,1,8,'',1,0),(460,'徐庆平','15679197832','http://ly.caifuby.cn/index2.html?sr=ch2&sgjj6sj-04617','2017-06-29 17:12:21',2,1,2,'',1,0),(464,'李海涛','18356128193','http://ly.caifuby.cn/index3.html?sr=ch1&sgjj6pc-03070','2017-06-29 17:30:55',8,1,8,'',1,0),(468,'曹天宇','18742362474','http://ly.caifuby.cn/index3.html?sr=ch1&sgjj6pc-33732','2017-06-29 17:31:57',2,1,2,'',1,0),(471,'马洪峰','13940269532','http://ly.caifuby.cn/index1.html?sr=ch2&sgjj6sj-32849','2017-06-29 17:43:02',8,1,8,'',1,0),(472,'苏丹','18022843870','http://vip8.ychuday.cn/index9.html?sr=ch1&360jj6pc-09430','2017-06-29 17:47:54',2,1,2,'',1,0),(473,'林桃园','13703362619','http://vip8.ychuday.cn/index9.html?sr=ch1&360jj6pc-09372','2017-06-29 17:58:04',8,1,8,'',1,0),(474,'林金花','18396027298','http://vip8.ychuday.cn/index9.html?sr=ch1&360jj6pc-04277','2017-06-29 18:11:27',2,1,2,'',1,0),(480,'杨剑','13717988454','http://ly.caifuby.cn/index1.html?sr=ch2&sgjj6sj-09928','2017-06-29 18:36:47',8,1,8,'',1,0),(483,'张春波','15164555148','http://vip8.ychuday.cn/index9.html?sr=ch1&360jj6pc-09395','2017-06-29 18:48:18',2,1,2,'',1,0),(486,'lixiao','18909941688','http://vip8.ychuday.cn/index9.html?sr=ch1&360jj6pc-09527','2017-06-29 18:54:55',8,1,8,'',1,0),(487,'赵旭东','18584353358','http://vip8.ychuday.cn/index9.html?sr=ch1&360jj6pc-26058','2017-06-29 18:58:52',2,1,2,'',1,0),(488,'wbw','18547144133','http://vip8.ychuday.cn/index9.html?sr=ch1&360jj6pc-09320','2017-06-29 19:09:31',8,1,8,'',1,0),(489,'200800gxc','13687002705','http://vip8.ychuday.cn/index9.html?sr=ch1&360jj6pc-09134','2017-06-29 19:13:37',2,1,2,'',1,0),(494,'ddd','18638014888','','2017-06-29 20:08:26',8,1,8,'',1,0),(495,'刘伟','18067338336','http://ly.caifuby.cn/index3.html?sr=ch1&sgjj6pc-66133','2017-06-29 20:20:16',2,1,2,'',1,0),(496,'测试','13296093956','http://3g.cjmex229.com/index.html','2017-06-29 21:37:19',8,1,8,'',1,0),(502,'鲁楚国','18638014588','http://3g.cjmex229.com/index.html','2017-06-29 21:40:56',2,1,2,'',1,0),(503,'是是是','18638014855','http://3g.cjmex229.com/index.html','2017-06-29 21:42:15',8,1,8,'',1,0),(504,'艾永浩','18380233219','http://ly.caifuby.cn/index3.html?sr=ch1&sgjj6pc-02733','2017-06-30 13:23:35',2,1,2,'',1,0),(506,'火龙果','13649986006','http://ly.caifuby.cn/index1.html?sr=ch2&sgjj6sj-03060','2017-06-30 13:38:31',8,1,8,'',1,0),(507,'邵泽江','18804338365','http://ly.caifuby.cn/index3.html?sr=ch1&sgjj6pc-07915','2017-06-30 14:46:04',2,1,2,'',1,0),(516,'丁健','18097415555','http://ly.caifuby.cn/index3.html?sr=ch1&sgjj6pc-07915','2017-06-30 14:53:04',8,1,8,'',1,0),(520,'王海天','15318778729','http://ly.caifuby.cn/index3.html?sr=ch1&sgjj6pc-02733','2017-06-30 14:54:49',2,1,2,'',1,0),(521,'薛广兴','18659303168','http://ly.caifuby.cn/index3.html?sr=ch1&sgjj6pc-07915','2017-06-30 15:18:46',8,1,8,'',1,0),(522,'黄健','15016583449','http://ly.caifuby.cn/index3.html?sr=ch1&sgjj6pc-65424','2017-06-30 15:42:24',2,1,2,'',1,0),(523,'王飞','13624510535','http://ly.caifuby.cn/index3.html?sr=ch1&sgjj6pc-07915','2017-06-30 15:55:21',8,1,8,'',1,0),(524,'王小贱','13020962586','http://vip8.ychuday.cn/index9.html?sr=ch1&360jj6pc-09156','2017-06-30 16:09:51',2,1,2,'',1,0),(526,'祝建红','15325839667','http://vip8.ychuday.cn/index9.html?sr=ch1&360jj6pc-09401','2017-06-30 16:16:41',8,1,8,'',1,0),(527,'666','18641151715','http://vip8.ychuday.cn/index9.html?sr=ch1&360jj6pc-09430','2017-06-30 16:23:56',2,1,2,'',1,0),(528,'杨女士','18003021175','http://vip8.ychuday.cn/index9.html?sr=ch1&360jj6pc-04026','2017-06-30 16:28:25',8,1,8,'',1,0),(529,'宏晟','13901568781','http://vip8.ychuday.cn/index9.html?sr=ch1&360jj6pc-09369','2017-06-30 16:29:25',2,1,2,'',1,0),(530,'徐雷','18627144550','http://vip8.ychuday.cn/index9.html?sr=ch1&360jj6pc-09467','2017-06-30 16:43:44',8,1,8,'',1,0),(535,'魏连生','13804109898','http://vip8.ychuday.cn/index9.html?sr=ch1&360jj6pc-09124','2017-06-30 16:48:28',2,1,2,'',1,0),(536,'13521349105','13521349105','http://vip8.ychuday.cn/index9.html?sr=ch1&360jj6pc-09512','2017-06-30 17:05:53',8,1,8,'',1,0),(537,'喜子','13231716767','http://vip8.ychuday.cn/index9.html?sr=ch1&360jj6pc-09467','2017-06-30 17:09:07',2,1,2,'',1,0),(538,'陶敏华','15079553501','http://vip8.ychuday.cn/index9.html?sr=ch1&360jj6pc-04093','2017-06-30 17:09:42',8,1,8,'',1,0),(541,'董小雪','13564265497','http://vip8.ychuday.cn/index9.html?sr=ch1&360jj6pc-09430','2017-06-30 17:11:19',2,1,2,'',1,0),(544,'徐子陵','17601448648','http://vip8.ychuday.cn/index9.html?sr=ch1&360jj6pc-09551','2017-06-30 17:13:18',8,1,8,'',1,0),(545,'喂喂喂','16854702799','http://vip8.ychuday.cn/index9.html?sr=ch1&360jj6pc-04093','2017-06-30 17:20:45',2,1,2,'',1,0),(546,'喂喂喂','17853702799','http://vip8.ychuday.cn/index9.html?sr=ch1&360jj6pc-04093','2017-06-30 17:22:32',8,1,8,'',1,0),(547,'李勇','13863772371','http://vip8.ychuday.cn/index9.html?sr=ch1&360jj6pc-09156','2017-06-30 17:28:16',2,1,2,'',1,0),(548,'贝钰铭','13755633738','http://ly.caifuby.cn/index3.html?sr=ch1&sgjj6pc-19042','2017-06-30 17:33:58',8,1,8,'',1,0),(550,'龙佳佳','18249922440','http://ly.caifuby.cn/index1.html?sr=ch2&sgjj6sj-03016','2017-06-30 17:36:12',2,1,2,'',1,0),(551,'陈','18025100431','http://ly.caifuby.cn/index3.html?sr=ch1&sgjj6pc-07915','2017-06-30 17:36:48',8,1,8,'',1,0),(552,'罗生','13827527033','http://vip8.ychuday.cn/index9.html?sr=ch1&360jj6pc-04094','2017-06-30 17:40:22',2,1,2,'',1,0),(553,'蓝刚','15192650111','http://vip8.ychuday.cn/index9.html?sr=ch1&360jj6pc-26034','2017-06-30 17:46:16',8,1,8,'',1,0),(554,'陈木秋','13995214441','http://ly.caifuby.cn/index1.html?sr=ch2&sgjj6sj-03007','2017-06-30 18:05:43',2,1,2,'',1,0),(555,'伍先生','13907979956','http://vip8.ychuday.cn/index9.html?sr=ch1&360jj6pc-03961','2017-06-30 18:06:16',8,1,8,'',1,0),(556,'伍','13207975563','http://vip8.ychuday.cn/index9.html?sr=ch1&360jj6pc-03961','2017-06-30 18:06:58',2,1,2,'',1,0),(557,'杜香华','13950801173','http://vip8.ychuday.cn/index9.html?sr=ch1&360jj6pc-09369','2017-06-30 18:48:40',8,1,8,'',1,0),(558,'岳国彦','15905846299','http://vip8.ychuday.cn/index9.html?sr=ch1&360jj6pc-04026','2017-06-30 19:24:37',2,1,2,'',1,0),(559,'徐国庆','13803783476','http://vip8.ychuday.cn/index9.html?sr=ch1&360jj6pc-09224','2017-06-30 19:25:52',8,1,8,'',1,0),(560,'张向宇','18768856889','http://ly.caifuby.cn/index3.html?sr=ch1&sgjj6pc-01445','2017-06-30 19:39:20',2,1,2,'',1,0),(563,'刘娇娇','15610677758','http://ly.caifuby.cn/index2.html?sr=ch2&sgjj6sj-02666','2017-06-30 19:53:58',8,1,8,'',1,0),(564,'王茂','13639170668','http://vip8.ychuday.cn/index9.html?sr=ch1&360jj6pc-09199','2017-06-30 20:28:05',2,1,2,'',1,0),(565,'高','13023823056','http://vip8.ychuday.cn/index9.html?sr=ch1&360jj6pc-09372','2017-06-30 20:31:13',8,1,8,'',1,0),(566,'李嘉俊','17666297851','http://vip8.ychuday.cn/index9.html?sr=ch1&360jj6pc-04277','2017-06-30 20:32:57',2,1,2,'',1,0),(567,'列举','13589638096','http://ly.caifuby.cn/index2.html?sr=ch2&sgjj6sj-07235','2017-07-01 13:10:28',8,1,8,'',1,0),(568,'王玉','15264376756','http://ly.caifuby.cn/index3.html?sr=ch1&sgjj6pc-09863','2017-07-01 13:42:16',2,1,2,'',1,0),(569,'陈辉','13608878283','http://ly.caifuby.cn/index2.html?sr=ch2&sgjj6sj-03489','2017-07-01 14:10:10',8,1,8,'',1,0),(570,'施青林','13987795820','http://vip8.ychuday.cn/index9.html?sr=ch1&360jj6pc-09250','2017-07-01 15:17:31',2,1,2,'',1,0),(572,'陈平','15087019397','http://vip8.ychuday.cn/index9.html?sr=ch1&360jj6pc-09372','2017-07-01 15:56:23',8,1,8,'',1,0),(575,'杨天祥','13779992638','http://vip8.ychuday.cn/index9.html?sr=ch1&360jj6pc-09505','2017-07-01 16:00:10',2,1,2,'',1,0),(576,'姚艳梅','18604986777','http://vip8.ychuday.cn/index9.html?sr=ch1&360jj6pc-09505','2017-07-01 16:01:01',8,1,8,'',1,0),(577,'张受军','13853300826','http://ly.caifuby.cn/index3.html?sr=ch1&sgjj6pc-02566','2017-07-01 16:03:37',2,1,2,'',1,0),(580,'伍麟祥','15118007940','http://ly.caifuby.cn/index3.html?sr=ch1&sgjj6pc-66133','2017-07-01 16:05:16',8,1,8,'',1,0),(583,'高哲','13020869707','http://ly.caifuby.cn/index3.html?sr=ch1&sgjj6pc-66133','2017-07-01 16:35:40',2,1,2,'',1,0),(588,'胡威','18627248483','http://vip8.ychuday.cn/index9.html?sr=ch1&360jj6pc-09442','2017-07-01 16:40:34',8,1,8,'',1,0),(589,'老王','15262133210','http://vip8.ychuday.cn/index9.html?sr=ch1&360jj6pc-03799','2017-07-01 17:03:54',2,1,2,'',1,0),(590,'钟','18623438030','http://vip8.ychuday.cn/index9.html?sr=ch1&360jj6pc-26023','2017-07-01 17:11:07',8,1,8,'',1,0),(591,'姜伟','13592522528','http://ly.caifuby.cn/index3.html?sr=ch1&sgjj6pc-66133','2017-07-01 17:53:53',2,1,2,'',1,0),(595,'小王八','15071506330','http://ly.caifuby.cn/index2.html?sr=ch2&sgjj6sj-62876','2017-07-03 10:25:20',8,1,8,'',1,0),(600,'武帝','18055586999','http://ly.caifuby.cn/index3.html?sr=ch1&sgjj6pc-07915','2017-07-03 10:35:49',2,1,2,'',1,0),(602,'徐向亮','18853109063','http://ly.caifuby.cn/index3.html?sr=ch1&sgjj6pc-07915','2017-07-03 10:58:31',8,1,8,'',1,0),(603,'张花花','18810638563','http://ly.caifuby.cn/index3.html?sr=ch1&sgjj6pc-07915','2017-07-03 11:11:13',2,1,2,'',1,0),(604,'加放假','18810638532','http://ly.caifuby.cn/index3.html?sr=ch1&sgjj6pc-07915','2017-07-03 11:11:41',8,1,8,'',1,0),(605,'宋总','18720079352','http://ly.caifuby.cn/index3.html?sr=ch1&sgjj6pc-03477','2017-07-03 11:21:45',2,1,2,'',1,0),(606,'高慧晨','13817088990','http://ly.caifuby.cn/index3.html?sr=ch1&sgjj6pc-09000','2017-07-03 11:40:51',8,1,8,'',1,0),(639,'孙宝宣','15963931567','http://ly.caifuby.cn/index1.html?sr=ch2&sgjj6sj-03008','2017-07-03 11:47:34',2,1,2,'',1,0),(640,'高新月','13131823925','http://ly.caifuby.cn/index3.html?sr=ch1&sgjj6pc-02733','2017-07-03 12:03:25',8,1,8,'',1,0),(641,'廖','18974134089','http://ly.caifuby.cn/index2.html?sr=ch2&sgjj6sj-63560','2017-07-03 12:21:16',2,1,2,'',1,0),(642,'吴志斌','13807256716','http://ly.caifuby.cn/index3.html?sr=ch1&sgjj6pc-65363','2017-07-03 12:26:06',8,1,8,'',1,0),(643,'周志斌','13825771267','http://ly.caifuby.cn/index3.html?sr=ch1&sgjj6pc-01483','2017-07-03 12:52:36',2,1,2,'',1,0),(644,'陈家兵','15828867666','http://ly.caifuby.cn/index3.html?sr=ch1&sgjj6pc-66133','2017-07-03 13:17:11',8,1,8,'',1,0),(645,'叶亚军','17631325761','http://ly.caifuby.cn/index2.html?sr=ch2&sgjj6sj-64698','2017-07-03 13:44:20',2,1,2,'',1,0),(646,'大饭店发','15000001111','','2017-07-03 13:44:22',8,1,8,'',1,0),(647,'符海峰','13593243168','http://ly.caifuby.cn/index1.html?sr=ch2&sgjj6sj-02818','2017-07-03 13:44:38',2,1,2,'',1,0),(650,'龙生','13566678526','http://ly.caifuby.cn/index3.html?sr=ch1&sgjj6pc-66133','2017-07-03 13:50:03',8,1,8,'',1,0),(651,'龙生','13666789526','http://ly.caifuby.cn/index3.html?sr=ch1&sgjj6pc-66133','2017-07-03 13:50:48',2,1,2,'',1,0),(655,'任昌明','13678699227','http://ly.caifuby.cn/index3.html?sr=ch1&sgjj6pc-66133','2017-07-03 14:06:54',8,1,8,'',1,0),(669,'江鹏','13986899823','http://vip8.ychuday.cn/index9.html?sr=ch1&360jj6pc-09408','2017-07-03 16:54:56',2,1,2,'',1,0),(670,'刘亮','15152135628','http://vip8.ychuday.cn/index9.html?sr=ch1&360jj6pc-09372','2017-07-03 17:01:00',8,1,8,'',1,0),(672,'李艾克','18959839273','http://ly.caifuby.cn/index3.html?sr=ch1&sgjj6pc-02733','2017-07-03 17:13:20',2,1,2,'',1,0),(673,'李艾克','18995839273','http://ly.caifuby.cn/index3.html?sr=ch1&sgjj6pc-02733','2017-07-03 17:13:54',8,1,8,'',1,0),(674,'xuxinzh','13758212157','http://vip8.ychuday.cn/index9.html?sr=ch1&360jj6pc-09220','2017-07-03 17:21:26',2,1,2,'',1,0),(675,'高颖慧','13373363522','http://vip8.ychuday.cn/index9.html?sr=ch1&360jj6pc-09517','2017-07-03 17:24:04',8,1,8,'',1,0),(681,'宝爷','13931568042','http://ly.caifuby.cn/index1.html?sr=ch2&sgjj6sj-02819','2017-07-03 17:26:17',2,1,2,'',1,0),(690,'杜洪柱','18864907631','http://vip8.ychuday.cn/index9.html?sr=ch1&360jj6pc-09249','2017-07-03 17:29:28',8,1,8,'',1,0),(692,'李玮','13870222587','http://ly.caifuby.cn/index3.html?sr=ch1&sgjj6pc-37812','2017-07-03 17:33:07',2,1,2,'',1,0),(693,'刘彩佳','13424961262','http://vip8.ychuday.cn/index9.html?sr=ch1&360jj6pc-04125','2017-07-03 17:49:27',8,1,8,'',1,0),(694,'周家发','13914250566','http://ly.caifuby.cn/index1.html?sr=ch2&sgjj6sj-02794','2017-07-03 17:53:31',2,1,2,'',1,0),(695,'肖小','15879640566','http://vip8.ychuday.cn/index9.html?sr=ch1&360jj6pc-09395','2017-07-03 18:01:41',8,1,8,'',1,0),(696,'周溪瑶','13921060718','http://vip8.ychuday.cn/index9.html?sr=ch1&360jj6pc-09372','2017-07-03 18:18:01',2,1,2,'',1,0),(697,'张点点','13258210676','http://ly.caifuby.cn/index1.html?sr=ch1&sgjj6sj-66133','2017-07-03 18:27:36',8,1,8,'',1,0),(701,'吴晓叶','17635047209','http://vip8.ychuday.cn/index9.html?sr=ch1&360jj6pc-04125','2017-07-03 18:35:33',2,1,2,'',1,0),(705,'马郡','13899937598','http://vip8.ychuday.cn/index9.html?sr=ch1&360jj6pc-09505','2017-07-03 18:56:49',8,1,8,'',1,0),(707,'陈必强','13858666682','http://vip8.ychuday.cn/index9.html?sr=ch1&360jj6pc-09430','2017-07-03 19:12:22',2,1,2,'',1,0),(710,'邱远简','15215891968','http://vip8.ychuday.cn/index9.html?sr=ch1&360jj6pc-25959','2017-07-03 19:22:59',8,1,8,'',1,0),(713,'徐梦麟','15185175103','http://ly.caifuby.cn/index3.html?sr=ch1&sgjj6pc-07915','2017-07-04 10:06:57',2,1,2,'',1,0),(714,'王擎辉','18561513335','http://ly.caifuby.cn/index3.html?sr=ch1&sgjj6pc-07915','2017-07-04 10:25:12',8,1,8,'',1,0),(715,'吴宝金','13952140511','http://ly.caifuby.cn/index2.html?sr=ch2&sgjj6sj-65589','2017-07-04 10:26:02',2,1,2,'',1,0),(716,'高海超','13911513795','http://ly.caifuby.cn/index3.html?sr=ch1&sgjj6pc-02733','2017-07-04 10:58:30',8,1,8,'',1,0),(719,'郎丽娟','13677568330','http://ly.caifuby.cn/index3.html?sr=ch1&sgjj6pc-02733','2017-07-04 11:02:51',2,1,2,'',1,0),(736,'刘跃平','15668949211','http://ly.caifuby.cn/index2.html?sr=ch2&sgjj6sj-06185','2017-07-04 11:50:13',2,1,2,'',1,0),(738,'狗仙胜','15730128456','http://ly.caifuby.cn/index2.html?sr=ch2&sgjj6sj-59202','2017-07-04 11:58:44',2,1,2,'',1,0),(742,'胡春发','15046018794','http://ly.caifuby.cn/index1.html?sr=ch2&sgjj6sj-03016','2017-07-04 12:10:57',8,1,8,'',1,0),(745,'宋涛','17620386766','http://ly.caifuby.cn/index2.html?sr=ch2&sgjj6sj-03501','2017-07-04 12:12:07',2,1,2,'',1,0);

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;
