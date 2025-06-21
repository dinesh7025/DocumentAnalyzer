@echo off
echo 🛑 Stopping Kafka and Zookeeper...

REM Killing Kafka process
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":9092"') do taskkill /PID %%a /F >nul 2>&1
echo ✅ Kafka process stopped (if running on port 9092)

REM Killing Zookeeper process
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":2181"') do taskkill /PID %%a /F >nul 2>&1
echo ✅ Zookeeper process stopped (if running on port 2181)

echo 🎉 All done.
pause
