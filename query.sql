-- Find changes (open port becomes closed and vice versa)
SELECT log3.remoteServerIP,
log3.remoteServerPort,
log5.remoteServerLabel,
log3.id AS id1,
log4.id AS id2,
log5.atDate AS atDate1,
log5.isOpen AS isOpen1,
log4.atDate AS atDate2,
log4.isOpen AS atOpen2,
CAST((julianday(log4.atDate) - julianday(log5.atDate)) * 86400.0 as integer) AS timeDiffInSec
-- CAST(strftime('%s', log4.atDate) as integer) - CAST(strftime('%s', log5.atDate) as integer) AS timeDiffInSec
FROM
(
	SELECT log1.remoteServerIP, log1.remoteServerPort, log1.id, min(log2.atDate) AS atDate2
	FROM log AS log1, log AS log2
	WHERE log1.remoteServerIP = log2.remoteServerIP AND
	log1.remoteServerPort = log2.remoteServerPort AND
	log1.atDate < log2.atDate
	GROUP BY log1.remoteServerIP, log1.remoteServerPort, log1.id
) AS log3
INNER JOIN log AS log4
ON log3.remoteServerIP = log4.remoteServerIP AND
log3.remoteServerPort = log4.remoteServerPort AND
log3.atDate2 = log4.atDate
INNER JOIN log AS log5
ON log3.id = log5.id
WHERE log4.isOpen <> log5.isOpen;

-- Separate different scenarios on interval
-- isOpen1, isOpen2, |  intervalType,  comment
-- 0        0        |  0              port closed, no changes
-- 0        1        |  1              port opened
-- 1        0        |  2              port closed
-- 1        1        |  3              port open, no changes
--
SELECT log3.remoteServerIP,
log3.remoteServerPort,
log5.remoteServerLabel,
log3.id AS id1,
log4.id AS id2,
log5.atDate AS atDate1,
log5.isOpen AS isOpen1,
log4.atDate AS atDate2,
log4.isOpen AS atOpen2,
CAST((julianday(log4.atDate) - julianday(log5.atDate)) * 86400.0 as integer) AS timeDiffInSec,
CAST(log5.isOpen as integer) * 2 + CAST(log4.isOpen as integer) AS intervalType
-- CAST(strftime('%s', log4.atDate) as integer) - CAST(strftime('%s', log5.atDate) as integer) AS timeDiffInSec
FROM
(
	SELECT log1.remoteServerIP, log1.remoteServerPort, log1.id, min(log2.atDate) AS atDate2
	FROM log AS log1, log AS log2
	WHERE log1.remoteServerIP = log2.remoteServerIP AND
	log1.remoteServerPort = log2.remoteServerPort AND
	log1.atDate < log2.atDate
	GROUP BY log1.remoteServerIP, log1.remoteServerPort, log1.id
) AS log3
INNER JOIN log AS log4
ON log3.remoteServerIP = log4.remoteServerIP AND
log3.remoteServerPort = log4.remoteServerPort AND
log3.atDate2 = log4.atDate
INNER JOIN log AS log5
ON log3.id = log5.id;

-- Group different scenarios on interval and sum time
-- isOpen1, isOpen2, |  intervalType,  comment
-- 0        0        |  0              port closed, no changes
-- 0        1        |  1              port opened
-- 1        0        |  2              port closed
-- 1        1        |  3              port open, no changes
--
SELECT log3.remoteServerIP,
log3.remoteServerPort,
log5.remoteServerLabel,
sum(CAST((julianday(log4.atDate) - julianday(log5.atDate)) * 86400.0 as integer)) AS sumTimeDiffInSec,
CAST(log5.isOpen as integer) * 2 + CAST(log4.isOpen as integer) AS intervalType
-- CAST(strftime('%s', log4.atDate) as integer) - CAST(strftime('%s', log5.atDate) as integer) AS timeDiffInSec
FROM
(
	SELECT log1.remoteServerIP, log1.remoteServerPort, log1.id, min(log2.atDate) AS atDate2
	FROM log AS log1, log AS log2
	WHERE log1.remoteServerIP = log2.remoteServerIP AND
	log1.remoteServerPort = log2.remoteServerPort AND
	log1.atDate < log2.atDate
	GROUP BY log1.remoteServerIP, log1.remoteServerPort, log1.id
) AS log3
INNER JOIN log AS log4
ON log3.remoteServerIP = log4.remoteServerIP AND
log3.remoteServerPort = log4.remoteServerPort AND
log3.atDate2 = log4.atDate
INNER JOIN log AS log5
ON log3.id = log5.id
GROUP BY log3.remoteServerIP,
log3.remoteServerPort,
log5.remoteServerLabel,
intervalType;

-- (Correct datetime format)
-- UPDATE log SET atDate = REPLACE(atDate,".","-");

SELECT * FROM log WHERE remoteServerIP = "192.168.254.12";