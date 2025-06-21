@echo off
echo 🔁 Starting ZooKeeper...
start cmd /k "cd /d D:\Kafka\kafka_2.13-3.9.1\bin\windows && zookeeper-server-start.bat ..\..\config\zookeeper.properties"

timeout /t 20 /nobreak >nul

echo 🚀 Starting Kafka Broker...
start cmd /k "cd /d D:\Kafka\kafka_2.13-3.9.1\bin\windows && kafka-server-start.bat ..\..\config\server.properties"
