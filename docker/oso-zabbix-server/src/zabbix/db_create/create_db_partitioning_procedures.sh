#!/bin/bash

##############################################
# procedure: partition_create
##############################################
PROCEDURE=partition_create

/usr/bin/mysql -h${MYSQL_HOST} -u${MYSQL_USER} -p${MYSQL_PASSWORD} zabbix -e "show procedure status" | /usr/bin/grep -q ${PROCEDURE}

if [ "$?" != 0 ]; then
  /usr/bin/mysql -u${MYSQL_USER} -p${MYSQL_PASSWORD} -h${MYSQL_HOST} zabbix -t <<'EOF'
DELIMITER $$
CREATE PROCEDURE `partition_create`(SCHEMANAME varchar(64), TABLENAME varchar(64), PARTITIONNAME varchar(64), CLOCK int)
BEGIN
        /*
           SCHEMANAME = The DB schema in which to make changes
           TABLENAME = The table with partitions to potentially delete
           PARTITIONNAME = The name of the partition to create
        */
        /*
           Verify that the partition does not already exist
        */

        DECLARE RETROWS INT;
        SELECT COUNT(1) INTO RETROWS
        FROM information_schema.partitions
        WHERE table_schema = SCHEMANAME AND table_name = TABLENAME AND partition_description >= CLOCK;

        IF RETROWS = 0 THEN
                /*
                   1. Print a message indicating that a partition was created.
                   2. Create the SQL to create the partition.
                   3. Execute the SQL from #2.
                */
                SELECT CONCAT( "partition_create(", SCHEMANAME, ",", TABLENAME, ",", PARTITIONNAME, ",", CLOCK, ")" ) AS msg;
                SET @sql = CONCAT( 'ALTER TABLE ', SCHEMANAME, '.', TABLENAME, ' ADD PARTITION (PARTITION ', PARTITIONNAME, ' VALUES LESS THAN (', CLOCK, '));' );
                PREPARE STMT FROM @sql;
                EXECUTE STMT;
                DEALLOCATE PREPARE STMT;
        END IF;
END$$
DELIMITER ;
EOF

else
  echo "Procedure: '${PROCEDURE}' exists.  Skipping setup."
fi

##############################################
# procedure: partition_drop
##############################################
PROCEDURE=partition_drop

/usr/bin/mysql -h${MYSQL_HOST} -u${MYSQL_USER} -p${MYSQL_PASSWORD} zabbix -e "show procedure status" | /usr/bin/grep -q ${PROCEDURE}

if [ "$?" != 0 ]; then
  /usr/bin/mysql -u${MYSQL_USER} -p${MYSQL_PASSWORD} -h${MYSQL_HOST} zabbix -t <<'EOF'
DELIMITER $$
CREATE PROCEDURE `partition_drop`(SCHEMANAME VARCHAR(64), TABLENAME VARCHAR(64), DELETE_BELOW_PARTITION_DATE BIGINT)
BEGIN
        /*
           SCHEMANAME = The DB schema in which to make changes
           TABLENAME = The table with partitions to potentially delete
           DELETE_BELOW_PARTITION_DATE = Delete any partitions with names that are dates older than this one (yyyy-mm-dd)
        */
        DECLARE done INT DEFAULT FALSE;
        DECLARE drop_part_name VARCHAR(16);

        /*
           Get a list of all the partitions that are older than the date
           in DELETE_BELOW_PARTITION_DATE.  All partitions are prefixed with
           a "p", so use SUBSTRING TO get rid of that character.
        */
        DECLARE myCursor CURSOR FOR
                SELECT partition_name
                FROM information_schema.partitions
                WHERE table_schema = SCHEMANAME AND table_name = TABLENAME AND CAST(SUBSTRING(partition_name FROM 2) AS UNSIGNED) < DELETE_BELOW_PARTITION_DATE;
        DECLARE CONTINUE HANDLER FOR NOT FOUND SET done = TRUE;

        /*
           Create the basics for when we need to drop the partition.  Also, create
           @drop_partitions to hold a comma-delimited list of all partitions that
           should be deleted.
        */
        SET @alter_header = CONCAT("ALTER TABLE ", SCHEMANAME, ".", TABLENAME, " DROP PARTITION ");
        SET @drop_partitions = "";

        /*
           Start looping through all the partitions that are too old.
        */
        OPEN myCursor;
        read_loop: LOOP
                FETCH myCursor INTO drop_part_name;
                IF done THEN
                        LEAVE read_loop;
                END IF;
                SET @drop_partitions = IF(@drop_partitions = "", drop_part_name, CONCAT(@drop_partitions, ",", drop_part_name));
        END LOOP;
        IF @drop_partitions != "" THEN
                /*
                   1. Build the SQL to drop all the necessary partitions.
                   2. Run the SQL to drop the partitions.
                   3. Print out the table partitions that were deleted.
                */
                SET @full_sql = CONCAT(@alter_header, @drop_partitions, ";");
                PREPARE STMT FROM @full_sql;
                EXECUTE STMT;
                DEALLOCATE PREPARE STMT;

                SELECT CONCAT(SCHEMANAME, ".", TABLENAME) AS `table`, @drop_partitions AS `partitions_deleted`;
        ELSE
                /*
                   No partitions are being deleted, so print out "N/A" (Not applicable) to indicate
                   that no changes were made.
                */
                SELECT CONCAT(SCHEMANAME, ".", TABLENAME) AS `table`, "N/A" AS `partitions_deleted`;
        END IF;
END$$
DELIMITER ;
EOF

else
  echo "Procedure: '${PROCEDURE}' exists.  Skipping setup."
fi

##############################################
# procedure: partition_maintenance
##############################################
PROCEDURE=partition_maintenance

/usr/bin/mysql -h${MYSQL_HOST} -u${MYSQL_USER} -p${MYSQL_PASSWORD} zabbix -e "show procedure status" | /usr/bin/grep -q ${PROCEDURE}

if [ "$?" != 0 ]; then
  /usr/bin/mysql -u${MYSQL_USER} -p${MYSQL_PASSWORD} -h${MYSQL_HOST} zabbix -t <<'EOF'
DELIMITER $$
CREATE PROCEDURE `partition_maintenance`(SCHEMA_NAME VARCHAR(32), TABLE_NAME VARCHAR(32), KEEP_DATA_DAYS INT, HOURLY_INTERVAL INT, CREATE_NEXT_INTERVALS INT)
BEGIN
        DECLARE OLDER_THAN_PARTITION_DATE VARCHAR(16);
        DECLARE PARTITION_NAME VARCHAR(16);
        DECLARE OLD_PARTITION_NAME VARCHAR(16);
        DECLARE LESS_THAN_TIMESTAMP INT;
        DECLARE CUR_TIME INT;

        CALL partition_verify(SCHEMA_NAME, TABLE_NAME, HOURLY_INTERVAL);
        SET CUR_TIME = UNIX_TIMESTAMP(DATE_FORMAT(NOW(), '%Y-%m-%d 00:00:00'));

        SET @__interval = 1;
        create_loop: LOOP
                IF @__interval > CREATE_NEXT_INTERVALS THEN
                        LEAVE create_loop;
                END IF;

                SET LESS_THAN_TIMESTAMP = CUR_TIME + (HOURLY_INTERVAL * @__interval * 3600);
                SET PARTITION_NAME = FROM_UNIXTIME(CUR_TIME + HOURLY_INTERVAL * (@__interval - 1) * 3600, 'p%Y%m%d%H00');
                IF(PARTITION_NAME != OLD_PARTITION_NAME) THEN
                        CALL partition_create(SCHEMA_NAME, TABLE_NAME, PARTITION_NAME, LESS_THAN_TIMESTAMP);
                END IF;
                SET @__interval=@__interval+1;
                SET OLD_PARTITION_NAME = PARTITION_NAME;
        END LOOP;

        SET OLDER_THAN_PARTITION_DATE=DATE_FORMAT(DATE_SUB(NOW(), INTERVAL KEEP_DATA_DAYS DAY), '%Y%m%d0000');
        CALL partition_drop(SCHEMA_NAME, TABLE_NAME, OLDER_THAN_PARTITION_DATE);

END$$
DELIMITER ;
EOF

else
  echo "Procedure: '${PROCEDURE}' exists.  Skipping setup."
fi

##############################################
# procedure: partition_verify
##############################################
PROCEDURE=partition_verify

/usr/bin/mysql -h${MYSQL_HOST} -u${MYSQL_USER} -p${MYSQL_PASSWORD} zabbix -e "show procedure status" | /usr/bin/grep -q ${PROCEDURE}

if [ "$?" != 0 ]; then
  /usr/bin/mysql -u${MYSQL_USER} -p${MYSQL_PASSWORD} -h${MYSQL_HOST} zabbix -t <<'EOF'
DELIMITER $$
CREATE PROCEDURE `partition_verify`(SCHEMANAME VARCHAR(64), TABLENAME VARCHAR(64), HOURLYINTERVAL INT(11))
BEGIN
        DECLARE PARTITION_NAME VARCHAR(16);
        DECLARE RETROWS INT(11);
        DECLARE FUTURE_TIMESTAMP TIMESTAMP;

        /*
         * Check if any partitions exist for the given SCHEMANAME.TABLENAME.
         */
        SELECT COUNT(1) INTO RETROWS
        FROM information_schema.partitions
        WHERE table_schema = SCHEMANAME AND table_name = TABLENAME AND partition_name IS NULL;

        /*
         * If partitions do not exist, go ahead and partition the table
         */
        IF RETROWS = 1 THEN
                /*
                 * Take the current date at 00:00:00 and add HOURLYINTERVAL to it.  This is the timestamp below which we will store values.
                 * We begin partitioning based on the beginning of a day.  This is because we don't want to generate a random partition
                 * that won't necessarily fall in line with the desired partition naming (ie: if the hour interval is 24 hours, we could
                 * end up creating a partition now named "p201403270600" when all other partitions will be like "p201403280000").
                 */
                SET FUTURE_TIMESTAMP = TIMESTAMPADD(HOUR, HOURLYINTERVAL, CONCAT(CURDATE(), " ", '00:00:00'));
                SET PARTITION_NAME = DATE_FORMAT(CURDATE(), 'p%Y%m%d%H00');

                -- Create the partitioning query
                SET @__PARTITION_SQL = CONCAT("ALTER TABLE ", SCHEMANAME, ".", TABLENAME, " PARTITION BY RANGE(`clock`)");
                SET @__PARTITION_SQL = CONCAT(@__PARTITION_SQL, "(PARTITION ", PARTITION_NAME, " VALUES LESS THAN (", UNIX_TIMESTAMP(FUTURE_TIMESTAMP), "));");

                -- Run the partitioning query
                PREPARE STMT FROM @__PARTITION_SQL;
                EXECUTE STMT;
                DEALLOCATE PREPARE STMT;
        END IF;
END$$
DELIMITER ;
EOF

else
  echo "Procedure: '${PROCEDURE}' exists.  Skipping setup."
fi

##############################################
# procedure: partition_maintenance_all
##############################################
PROCEDURE=partition_maintenance_all

/usr/bin/mysql -h${MYSQL_HOST} -u${MYSQL_USER} -p${MYSQL_PASSWORD} zabbix -e "show procedure status" | /usr/bin/grep -q ${PROCEDURE}

if [ "$?" != 0 ]; then
  /usr/bin/mysql -u${MYSQL_USER} -p${MYSQL_PASSWORD} -h${MYSQL_HOST} zabbix -t <<'EOF'
DELIMITER $$
CREATE PROCEDURE `partition_maintenance_all`(SCHEMA_NAME VARCHAR(32))
BEGIN
                CALL partition_maintenance(SCHEMA_NAME, 'history', 14, 24, 14);
                CALL partition_maintenance(SCHEMA_NAME, 'history_log', 14, 24, 14);
                CALL partition_maintenance(SCHEMA_NAME, 'history_str', 14, 24, 14);
                CALL partition_maintenance(SCHEMA_NAME, 'history_text', 14, 24, 14);
                CALL partition_maintenance(SCHEMA_NAME, 'history_uint', 14, 24, 14);
                CALL partition_maintenance(SCHEMA_NAME, 'trends', 390, 24, 14);
                CALL partition_maintenance(SCHEMA_NAME, 'trends_uint', 390, 24, 14);
END$$
DELIMITER ;
EOF

  #  Putting the initial 'ALTER' queries here

  /usr/bin/mysql -h${MYSQL_HOST} -u${MYSQL_USER} -p${MYSQL_PASSWORD} zabbix -e 'Alter table history_text drop primary key, add index (id), drop index history_text_2, add index history_text_2 (itemid, id);'

  /usr/bin/mysql -h${MYSQL_HOST} -u${MYSQL_USER} -p${MYSQL_PASSWORD} zabbix -e 'Alter table history_log drop primary key, add index (id), drop index history_log_2, add index history_log_2 (itemid, id);'

else
  echo "Procedure: '${PROCEDURE}' exists.  Skipping setup."
fi
