USE mysql ;
FLUSH PRIVILEGES ;
GRANT ALL ON *.* TO 'user'@'%' identified by 'password' WITH GRANT OPTION ;
FLUSH PRIVILEGES ;
